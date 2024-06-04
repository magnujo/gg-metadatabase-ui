from sqlalchemy import create_engine
import pandas as pd
from constants.misc_constants import ENGINE_READ_ONLY as ENGINE
import numpy as np

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

    raw_tables = {"CGG3": cgg_3, "Archive Sampling": archive_samples, "WetLabFinalReport": wet_lab_reports}

    # TODO: check that replacemants doesnt result in duplicate data
    # Cleaning input ids
    field_sample_IDs = list(map(lambda x: x.upper(), field_sample_IDs))
    field_sample_IDs = list(map(lambda x: x.strip(), field_sample_IDs))
    field_sample_IDs = list(map(lambda x: x.replace(" ", ""), field_sample_IDs))
    field_sample_IDs = list(map(lambda x: x.replace("," , "."), field_sample_IDs))
    field_sample_IDs = list(map(lambda x: x.replace("-" , "_"), field_sample_IDs))
    
    # Cleaning archive sample table
    archive_samples["BulkSampleID"] = archive_samples["BulkSampleID"].str.strip()
    archive_samples["BulkSampleID"] = archive_samples["BulkSampleID"].str.replace("-", "_")
    archive_samples["BulkSampleID"] = archive_samples["BulkSampleID"].str.replace(",", ".")
    archive_samples["BulkSampleID"] = archive_samples["BulkSampleID"].str.upper()
    archive_samples["BulkSampleID"] = archive_samples["BulkSampleID"].str.replace(" ", "")
    
    # Cleaning cgg Museum ID/sample ID
    cgg_3["Museum ID/sample ID"] = cgg_3["Museum ID/sample ID"].str.strip()
    cgg_3["Museum ID/sample ID"] = cgg_3["Museum ID/sample ID"].str.replace("," , ".")
    cgg_3["Museum ID/sample ID"] = cgg_3["Museum ID/sample ID"].str.replace("-" , "_")
    cgg_3["Museum ID/sample ID"] = cgg_3["Museum ID/sample ID"].str.upper()
    cgg_3["Museum ID/sample ID"] = cgg_3["Museum ID/sample ID"].str.replace(" ", "")
    
    # Cleaning CGG ID
    cgg_3["CGG ID"] = cgg_3["CGG ID"].str.strip()
    cgg_3["CGG ID"] = cgg_3["CGG ID"].str.replace("-" , "_")
    cgg_3["CGG ID"] = cgg_3["CGG ID"].str.upper()
    cgg_3["CGG ID"] = cgg_3["CGG ID"].str.replace(" ", "")
    
    # Cleaning Archive Sample ID from Wet lab report
    wet_lab_reports["Archive Sample ID"] = wet_lab_reports["Archive Sample ID"].str.strip()
    wet_lab_reports["Archive Sample ID"] = wet_lab_reports["Archive Sample ID"].str.replace("-", "_")
    wet_lab_reports["Archive Sample ID"] = wet_lab_reports["Archive Sample ID"].str.replace("," , ".")
    wet_lab_reports["Archive Sample ID"] = wet_lab_reports["Archive Sample ID"].str.replace(" ", "")
    wet_lab_reports["Archive Sample ID"] = wet_lab_reports["Archive Sample ID"].str.upper()
    
    wet_lab_reports = wet_lab_reports.fillna(np.nan)
    wet_lab_reports = wet_lab_reports.replace("NONE", np.nan)
    archive_samples = archive_samples.fillna(np.nan)
    archive_samples = archive_samples.replace("NONE", np.nan)
    cgg_3 = cgg_3.fillna(np.nan)
    cgg_3 = cgg_3.replace("NONE", np.nan)
    

    cgg_essential = cgg_3[["Museum ID/sample ID", 'CGG ID', "Depth", "height (m) asl.", "Age", "Geological age", "Country", "Lat", "Lon", "GPS"]]
        
    # Get all the rows where the fID matches 
    input_filter_cgg = cgg_3[cgg_3["Museum ID/sample ID"].isin(field_sample_IDs)]
    input_filter_asdf = archive_samples[archive_samples["BulkSampleID"].isin(field_sample_IDs)]
    input_filter_wldf = wet_lab_reports[wet_lab_reports["Archive Sample ID"].isin(field_sample_IDs)]

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

    my_list = list(input_filter_asdf["BulkSampleID"].unique()) + list(input_filter_cgg["Museum ID/sample ID"].unique())


    # Merging


    # Makes a new df that contains all aIDs from archive_samples and all aIDs from wet_lab_reports that matches an aID from asdf
    merged_on_aID = pd.merge(input_filter_asdf, wet_lab_reports, left_on='Archive Sample ID', right_on='Archive Sample ID', how='left')
    unmerged_aIDs_from_wlr = wet_lab_reports[~wet_lab_reports["Archive Sample ID"].isin(merged_on_aID["Archive Sample ID"].unique())]
    aIDs_not_in_wlr_filter = ~wet_lab_reports["Archive Sample ID"].isin(archive_samples["Archive Sample ID"])
    # aIDs_not_in_wlr = wet_lab_reports[filter]
    
    # Test:
    expected_vals_from_asdf = archive_samples[archive_samples["BulkSampleID"].isin(field_sample_IDs)]["Archive Sample ID"]
    expected_vals_from_wldf = wet_lab_reports[wet_lab_reports["Archive Sample ID"].isin(expected_vals_from_asdf)]["Archive Sample ID"]
    
    # assert len(merged_on_aID) == len(expected_vals_from_wldf) + len(expected_vals_from_asdf)
    # assert expected_vals_from_asdf.sort_values().equals(merged_on_aID["Archive Sample ID"].sort_values())
    # assert expected_vals_from_wldf.sort_values().equals(merged_on_aID["Archive Sample ID"].sort_values())
    
    assert merged_on_aID["Archive Sample ID"].isnull().all() == False
    

    merged_on_aID_essentials = merged_on_aID[['BulkSampleID', "Archive Sample ID", "Robot Sample ID", "Library ID", 'FastQ File ID', "DepthSampledCalTape"]]

    merged_on_CGG_ID = pd.merge(input_filter_cgg, wet_lab_reports, left_on='CGG ID', right_on='Archive Sample ID', how='left')
    merged_on_CGG_ID_essentials = merged_on_CGG_ID[["Museum ID/sample ID", 'CGG ID', "Library ID", 'FastQ File ID', "Depth", "height (m) asl.", "Age", "Geological age", "Country", "Lat", "Lon", "GPS"]]

    merged_on_museum_id = pd.merge(input_filter_cgg, wet_lab_reports, left_on='Museum ID/sample ID', right_on='Archive Sample ID', how='left')
    merged_on_museum_id_essentials = merged_on_museum_id[["Museum ID/sample ID", 'CGG ID', "Library ID", 'FastQ File ID', "Depth", "height (m) asl.", "Age", "Geological age", "Country", "Lat", "Lon", "GPS"]]

    merged_on_bulksampleid = pd.merge(input_filter_asdf, wet_lab_reports, left_on='BulkSampleID', right_on='Archive Sample ID', how='left') 

    merged_on_bulksampleid_essentials = merged_on_bulksampleid[['BulkSampleID', "Robot Sample ID", "Library ID", 'FastQ File ID', "DepthSampledCalTape"]]

    

    pd.set_option('future.no_silent_downcasting', True)

    # Making one big table with all the merges comined: 
    merged_on_aID = merged_on_aID.rename(columns={"BulkSampleID": "FieldSampleID"})
    merged_on_bulksampleid = merged_on_bulksampleid.rename(columns={"BulkSampleID": "FieldSampleID"})
    merged_on_CGG_ID.loc[:, "FieldSampleID"] = merged_on_CGG_ID.loc[:, "Museum ID/sample ID"]
    merged_on_museum_id.loc[:, "FieldSampleID"] = merged_on_museum_id.loc[:, "Museum ID/sample ID"]

    conc = pd.concat([merged_on_aID, merged_on_bulksampleid, merged_on_CGG_ID, merged_on_museum_id])
    conc = conc.reset_index()
    merged_df = pd.merge(conc, cgg_3, left_on="FieldSampleID", right_on="CGG ID", how='left')
    # Now replace NaN values in common columns of df1 with values from df2
    for column in conc.columns:
        if column in cgg_3.columns:
            merged_df[column+'_x'] = merged_df[column+'_x'].fillna(merged_df[column+'_y']).infer_objects(copy=False)
            merged_df = merged_df.drop(columns=[column+'_y'])

    # Rename the columns back to their original names
    full_merged_df = merged_df.rename(columns={col: col[:-2] for col in merged_df.columns if col.endswith('_x')})


    # Same as above but only with essential columns:

    merged_on_aID_essentials = merged_on_aID_essentials.rename(columns={"BulkSampleID": "FieldSampleID"})
    merged_on_bulksampleid_essentials = merged_on_bulksampleid_essentials.rename(columns={"BulkSampleID": "FieldSampleID"})
    merged_on_CGG_ID_essentials.loc[:, "FieldSampleID"] = merged_on_CGG_ID_essentials.loc[:, "Museum ID/sample ID"]
    merged_on_museum_id_essentials.loc[:, "FieldSampleID"] = merged_on_museum_id_essentials.loc[:, "Museum ID/sample ID"]

    conc = pd.concat([merged_on_aID_essentials, merged_on_bulksampleid_essentials, merged_on_CGG_ID_essentials, merged_on_museum_id_essentials])
    conc = conc.reset_index()

    # Merging back into cgg to get the meta data from the cgg numbers that have been reported as field sample ids
    merged_df = pd.merge(conc, cgg_essential, left_on="FieldSampleID", right_on="CGG ID", how='left')
    for column in conc.columns:
        if column in cgg_essential.columns:
            merged_df[column+'_x'] = merged_df[column+'_x'].fillna(merged_df[column+'_y'])
            merged_df = merged_df.drop(columns=[column+'_y'])

    # Rename the columns back to their original names
    essential_merged_df = merged_df.rename(columns={col: col[:-2] for col in merged_df.columns if col.endswith('_x')})
    
    # Test:
    
    
    return (essential_merged_df, full_merged_df, raw_tables)