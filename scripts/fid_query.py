from sqlalchemy import create_engine
import pandas as pd
from constants.misc_constants import ENGINE_READ_ONLY as ENGINE
import numpy as np
from utils.db_utils import get_ordinal_position_maps

def get_meta_data(field_sample_IDs):
    '''
    Gets all meta data connected to fIDs across WetLab, Archive and CGG sediment table
    '''
    
    wldf_q = "select * from test_1.edna_wetlab_report;"
    asdf_q = "select * from test_1.edna_archive_sample;"
    cgg_q = "select * from test_1.cgg_sediment_water;"
    wet_lab_reports = pd.read_sql(wldf_q, dtype=str, con=ENGINE)
    archive_samples = pd.read_sql(asdf_q, dtype=str, con=ENGINE)
    cgg_3 = pd.read_sql(cgg_q, dtype=str, con=ENGINE)
    
    ordinal_position_maps = {"edna_wetlab_report": get_ordinal_position_maps("edna_wetlab_report", "test_1", ENGINE),
                             "edna_archive_sample": get_ordinal_position_maps("edna_archive_sample", "test_1", ENGINE),
                             "cgg_sediment_water": get_ordinal_position_maps("cgg_sediment_water", "test_1", ENGINE)}
    
    # Renames all columns to their corresponding ordinal position in Postgres. To be renamed back before returned.
    # wet_lab_reports = wet_lab_reports.rename(columns=ordinal_position_maps["edna_wetlab_report"].col_to_pos)
    # archive_samples = archive_samples.rename(columns=ordinal_position_maps["edna_archive_sample"].col_to_pos)
    # cgg_3 = cgg_3.rename(columns=ordinal_position_maps["cgg_sediment_water"].col_to_pos)
    
    # Dynamic column names Wetlab Report
    library_id = ordinal_position_maps["edna_wetlab_report"].pos_to_col.get(23)
    assert library_id == "Library ID"
    
    fastq_file_id = ordinal_position_maps["edna_wetlab_report"].pos_to_col.get(51)
    assert fastq_file_id == "FastQ File ID"
    
    robot_sample_ID = ordinal_position_maps["edna_wetlab_report"].pos_to_col.get(9)
    assert robot_sample_ID == "Robot Sample ID"
    
    extraction_ID = ordinal_position_maps["edna_wetlab_report"].pos_to_col.get(16)
    assert extraction_ID == "eDNA ID"
    
    aID_wlr = ordinal_position_maps["edna_wetlab_report"].pos_to_col.get(10)
    assert aID_wlr == "Archive Sample ID"
    
    # Dynamic col names Archive Samples
    aID_as = ordinal_position_maps["edna_archive_sample"].pos_to_col.get(1)
    assert aID_as == "ArchiveSampleID"
    
    field_sample_ID = ordinal_position_maps["edna_archive_sample"].pos_to_col.get(5)
    assert field_sample_ID == "BulkSampleID"
    
    depth_as = ordinal_position_maps["edna_archive_sample"].pos_to_col.get(6)
    assert depth_as == depth_as
    
    # Dynamic col names CGG
    cgg_ID = ordinal_position_maps["cgg_sediment_water"].pos_to_col.get(1)
    museum_ID = ordinal_position_maps["cgg_sediment_water"].pos_to_col.get(2)
    depth_cgg = ordinal_position_maps["cgg_sediment_water"].pos_to_col.get(11)
    height = ordinal_position_maps["cgg_sediment_water"].pos_to_col.get(12)
    age = ordinal_position_maps["cgg_sediment_water"].pos_to_col.get(17)
    geological_age = ordinal_position_maps["cgg_sediment_water"].pos_to_col.get(18)
    country = ordinal_position_maps["cgg_sediment_water"].pos_to_col.get(23)
    lat = ordinal_position_maps["cgg_sediment_water"].pos_to_col.get(25)
    lon = ordinal_position_maps["cgg_sediment_water"].pos_to_col.get(26)
    gps = ordinal_position_maps["cgg_sediment_water"].pos_to_col.get(27)
    
    global_field_sample_id_col_name = "FieldSampleID"


    raw_tables = {"CGG3": cgg_3, "Archive Sampling": archive_samples, "WetLabFinalReport": wet_lab_reports}

    # TODO: check that replacemants doesnt result in duplicate data
    # Cleaning input ids
    field_sample_IDs = list(map(lambda x: x.upper(), field_sample_IDs))
    field_sample_IDs = list(map(lambda x: x.strip(), field_sample_IDs))
    field_sample_IDs = list(map(lambda x: x.replace(" ", ""), field_sample_IDs))
    field_sample_IDs = list(map(lambda x: x.replace("," , "."), field_sample_IDs))
    field_sample_IDs = list(map(lambda x: x.replace("-" , "_"), field_sample_IDs))
    
    # Cleaning archive sample table
    archive_samples[field_sample_ID] = archive_samples[field_sample_ID].str.strip()
    archive_samples[field_sample_ID] = archive_samples[field_sample_ID].str.replace("-", "_")
    archive_samples[field_sample_ID] = archive_samples[field_sample_ID].str.replace(",", ".")
    archive_samples[field_sample_ID] = archive_samples[field_sample_ID].str.upper()
    archive_samples[field_sample_ID] = archive_samples[field_sample_ID].str.replace(" ", "")
    
    # TODO: This seems dangerous:
    # Change archive sample ID to a common name.
    archive_sample_ID = aID_wlr
    archive_samples = archive_samples.rename(columns={aID_as: archive_sample_ID})
    
        
    # Cleaning cgg Museum ID/sample ID
    cgg_3[museum_ID] = cgg_3[museum_ID].str.strip()
    cgg_3[museum_ID] = cgg_3[museum_ID].str.replace("," , ".")
    cgg_3[museum_ID] = cgg_3[museum_ID].str.replace("-" , "_")
    cgg_3[museum_ID] = cgg_3[museum_ID].str.upper()
    cgg_3[museum_ID] = cgg_3[museum_ID].str.replace(" ", "")
    
    # Cleaning CGG ID
    cgg_3[cgg_ID] = cgg_3[cgg_ID].str.strip()
    cgg_3[cgg_ID] = cgg_3[cgg_ID].str.replace("-" , "_")
    cgg_3[cgg_ID] = cgg_3[cgg_ID].str.upper()
    cgg_3[cgg_ID] = cgg_3[cgg_ID].str.replace(" ", "")
    
    # Cleaning Archive Sample ID from Wet lab report
    wet_lab_reports[aID_wlr] = wet_lab_reports[aID_wlr].str.strip()
    wet_lab_reports[aID_wlr] = wet_lab_reports[aID_wlr].str.replace("-", "_")
    wet_lab_reports[aID_wlr] = wet_lab_reports[aID_wlr].str.replace("," , ".")
    wet_lab_reports[aID_wlr] = wet_lab_reports[aID_wlr].str.replace(" ", "")
    wet_lab_reports[aID_wlr] = wet_lab_reports[aID_wlr].str.upper()
    
    wet_lab_reports = wet_lab_reports.fillna(np.nan)
    wet_lab_reports = wet_lab_reports.replace("NONE", np.nan)
    archive_samples = archive_samples.fillna(np.nan)
    archive_samples = archive_samples.replace("NONE", np.nan)
    cgg_3 = cgg_3.fillna(np.nan)
    cgg_3 = cgg_3.replace("NONE", np.nan)
    

    cgg_essential = cgg_3[[museum_ID, cgg_ID, depth_cgg, height, age, geological_age, country, lat, lon, gps]]
        
    # Get all the rows where the fID matches 
    input_filter_cgg = cgg_3[cgg_3[museum_ID].isin(field_sample_IDs)]
    input_filter_asdf = archive_samples[archive_samples[field_sample_ID].isin(field_sample_IDs)]
    input_filter_wldf = wet_lab_reports[wet_lab_reports[aID_wlr].isin(field_sample_IDs)]

    # Finding duplicates in Jespers data that is also in the CGG database
    def find_duplicates(lst):
        seen = {}
        duplicates = []

        for item in lst:
            if item in seen:
                duplicates.append(item)
            else:
                seen[item] = 1

        return duplicates

    my_list = list(input_filter_asdf[field_sample_ID].unique()) + list(input_filter_cgg[museum_ID].unique())


    # Merging


    # Makes a new df that contains all aIDs from archive_samples and all aIDs from wet_lab_reports that matches an aID from asdf
    merged_on_aID = pd.merge(input_filter_asdf, wet_lab_reports, left_on=archive_sample_ID, right_on=archive_sample_ID, how='left')
    unmerged_aIDs_from_wlr = wet_lab_reports[~wet_lab_reports[archive_sample_ID].isin(merged_on_aID[archive_sample_ID].unique())]
    aIDs_not_in_wlr_filter = ~wet_lab_reports[archive_sample_ID].isin(archive_samples[archive_sample_ID])
    # aIDs_not_in_wlr = wet_lab_reports[filter]
    
    # Test:
    expected_vals_from_asdf = archive_samples[archive_samples[field_sample_ID].isin(field_sample_IDs)][archive_sample_ID]
    expected_vals_from_wldf = wet_lab_reports[wet_lab_reports[archive_sample_ID].isin(expected_vals_from_asdf)][archive_sample_ID]
    
    # assert len(merged_on_aID) == len(expected_vals_from_wldf) + len(expected_vals_from_asdf)
    # assert expected_vals_from_asdf.sort_values().equals(merged_on_aID["Archive Sample ID"].sort_values())
    # assert expected_vals_from_wldf.sort_values().equals(merged_on_aID["Archive Sample ID"].sort_values())    

    merged_on_aID_essentials = merged_on_aID[[field_sample_ID, archive_sample_ID, robot_sample_ID, library_id, fastq_file_id, depth_as]]

    merged_on_CGG_ID = pd.merge(input_filter_cgg, wet_lab_reports, left_on=cgg_ID, right_on=archive_sample_ID, how='left')
    merged_on_CGG_ID_essentials = merged_on_CGG_ID[[museum_ID, cgg_ID, library_id, fastq_file_id, depth_cgg, height, age, geological_age, country, lat, lon, gps]]

    merged_on_museum_id = pd.merge(input_filter_cgg, wet_lab_reports, left_on=museum_ID, right_on=archive_sample_ID, how='left')
    merged_on_museum_id_essentials = merged_on_museum_id[[museum_ID, cgg_ID, library_id, fastq_file_id, depth_cgg, height, age, geological_age, country, lat, lon, gps]]

    merged_on_bulksampleid = pd.merge(input_filter_asdf, wet_lab_reports, left_on=field_sample_ID, right_on=archive_sample_ID, how='left') 

    merged_on_bulksampleid_essentials = merged_on_bulksampleid[[field_sample_ID, robot_sample_ID, library_id, fastq_file_id, depth_as]]

    

    pd.set_option('future.no_silent_downcasting', True)

    # Making one big table with all the merges comined: 
    merged_on_aID = merged_on_aID.rename(columns={field_sample_ID: global_field_sample_id_col_name})
    merged_on_bulksampleid = merged_on_bulksampleid.rename(columns={field_sample_ID: global_field_sample_id_col_name})
    merged_on_CGG_ID.loc[:, global_field_sample_id_col_name] = merged_on_CGG_ID.loc[:, museum_ID]
    merged_on_museum_id.loc[:, global_field_sample_id_col_name] = merged_on_museum_id.loc[:, museum_ID]

    conc = pd.concat([merged_on_aID, merged_on_bulksampleid, merged_on_CGG_ID, merged_on_museum_id])
    conc = conc.reset_index()
    merged_df = pd.merge(conc, cgg_3, left_on=global_field_sample_id_col_name, right_on=cgg_ID, how='left')
    # Now replace NaN values in common columns of df1 with values from df2
    for column in conc.columns:
        if column in cgg_3.columns:
            merged_df[column+'_x'] = merged_df[column+'_x'].fillna(merged_df[column+'_y']).infer_objects(copy=False)
            merged_df = merged_df.drop(columns=[column+'_y'])

    # Rename the columns back to their original names
    full_merged_df = merged_df.rename(columns={col: col[:-2] for col in merged_df.columns if col.endswith('_x')})


    # Same as above but only with essential columns:

    merged_on_aID_essentials = merged_on_aID_essentials.rename(columns={field_sample_ID: global_field_sample_id_col_name})
    merged_on_bulksampleid_essentials = merged_on_bulksampleid_essentials.rename(columns={field_sample_ID: global_field_sample_id_col_name})
    merged_on_CGG_ID_essentials.loc[:, global_field_sample_id_col_name] = merged_on_CGG_ID_essentials.loc[:, museum_ID]
    merged_on_museum_id_essentials.loc[:, global_field_sample_id_col_name] = merged_on_museum_id_essentials.loc[:, museum_ID]

    conc = pd.concat([merged_on_aID_essentials, merged_on_bulksampleid_essentials, merged_on_CGG_ID_essentials, merged_on_museum_id_essentials])
    conc = conc.reset_index()

    # Merging back into cgg to get the meta data from the cgg numbers that have been reported as field sample ids
    merged_df = pd.merge(conc, cgg_essential, left_on=global_field_sample_id_col_name, right_on=cgg_ID, how='left')
    for column in conc.columns:
        if column in cgg_essential.columns:
            merged_df[column+'_x'] = merged_df[column+'_x'].fillna(merged_df[column+'_y'])
            merged_df = merged_df.drop(columns=[column+'_y'])

    # Rename the columns back to their original names
    essential_merged_df = merged_df.rename(columns={col: col[:-2] for col in merged_df.columns if col.endswith('_x')})
    
    # Test:
    
    
    return (essential_merged_df, full_merged_df, raw_tables)