from sqlalchemy import create_engine
import pandas as pd
from constants import ENGINE_READ_ONLY as ENGINE

def get_meta_data(input_data):
    '''
    Gets all meta data connected to fIDs across WetLab, Archive and CGG sediment table
    '''
    
    wldf_q = "select * from test_1.edna_wetlab_report;"
    asdf_q = "select * from test_1.edna_archive_sample;"
    cgg_q = "select * from test_1.cgg_sediment_water;"
    flowcell_q = "select * from test_1.flowcell;"
    
    wldf = pd.read_sql(wldf_q, dtype=str, con=ENGINE).applymap(lambda x: x.upper() if isinstance(x, str) else x)
    asdf = pd.read_sql(asdf_q, dtype=str, con=ENGINE).applymap(lambda x: x.upper() if isinstance(x, str) else x)
    cgg = pd.read_sql(cgg_q, dtype=str, con=ENGINE).applymap(lambda x: x.upper() if isinstance(x, str) else x)
    flowcell = pd.read_sql(flowcell_q, dtype=str, con=ENGINE).applymap(lambda x: x.upper() if isinstance(x, str) else x)



    # TODO: check that replacemants doesnt result in duplicate data
    input_data = list(map(lambda x: x.upper(), input_data))
    input_data = list(map(lambda x: x.replace(" ", ""), input_data))
    input_data = list(map(lambda x: x.replace("," , "."), input_data))
    input_data = list(map(lambda x: x.replace("-" , "_"), input_data))

    cgg_essential = cgg[["Museum ID/sample ID", 'CGG ID', "Depth", "height (m) asl.", "Age", "Geological age", "Lat", "Lon", "GPS"]]

    # Get all the rows where the fID matches 
    input_data_filter = wldf[wldf["Library ID"].isin(input_data)]

    # Merging

    merged_on_aID = pd.merge(input_data_filter, asdf, left_on='Archive Sample ID', right_on='ArchiveSampleID', how='left')
    merged_on_aID_essentials = merged_on_aID[['BulkSampleID', "ArchiveSampleID", "Robot Sample ID", "Library ID", 'FastQ File ID', "DepthSampledCalTape"]]

    merged_on_CGG_ID = pd.merge(input_data_filter, cgg, left_on='CGG ID', right_on='Archive Sample ID', how='left')
    merged_on_CGG_ID_essentials = merged_on_CGG_ID[["Museum ID/sample ID", 'CGG ID', "Robot Sample ID", "Library ID", 'FastQ File ID', "Depth", "height (m) asl.", "Age", "Geological age", "Lat", "Lon", "GPS"]]

    merged_bulk_with_cgg = pd.merge(merged_on_aID, cgg, left_on='BulkSampleID', right_on='CGG ID', how='left')
    merged_flowcell = pd.merge(input_data_filter, flowcell, left_on='FastQ File ID', right_on='Sample')
    
    pd.set_option('future.no_silent_downcasting', True)

    # Making one big table with all the merges comined: 
    merged_on_aID = merged_on_aID.rename(columns={"BulkSampleID": "FieldSampleID"})
    merged_on_bulksampleid = merged_on_bulksampleid.rename(columns={"BulkSampleID": "FieldSampleID"})
    merged_on_CGG_ID.loc[:, "FieldSampleID"] = merged_on_CGG_ID.loc[:, "Museum ID/sample ID"]
    merged_on_museum_id.loc[:, "FieldSampleID"] = merged_on_museum_id.loc[:, "Museum ID/sample ID"]

    conc = pd.concat([merged_on_aID, merged_on_bulksampleid, merged_on_CGG_ID, merged_on_museum_id])
    conc = conc.reset_index()
    merged_df = pd.merge(conc, cgg, left_on="FieldSampleID", right_on="CGG ID", how='left')
    # Now replace NaN values in common columns of df1 with values from df2
    for column in conc.columns:
        if column in cgg.columns:
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
    
    return (essential_merged_df, full_merged_df)