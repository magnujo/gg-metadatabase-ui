from sqlalchemy import create_engine
import pandas as pd
from constants import ENGINE_READ_ONLY as ENGINE

def get_meta_data(fIDs):
    '''
    Gets all meta data connected to fIDs across WetLab, Archive and CGG sediment table
    '''
    
    wldf_q = "select * from test_1.edna_wetlab_report;"
    asdf_q = "select * from test_1.edna_archive_sample;"
    cgg_q = "select * from test_1.cgg_sediment_water;"
    wldf = pd.read_sql(wldf_q, dtype=str, con=ENGINE)
    asdf = pd.read_sql(asdf_q, dtype=str, con=ENGINE)
    cgg = pd.read_sql(cgg_q, dtype=str, con=ENGINE)


    # TODO: check that replacemants doesnt result in duplicate data
    fIDs = list(map(lambda x: x.upper(), fIDs))
    fIDs = list(map(lambda x: x.replace(" ", ""), fIDs))
    fIDs = list(map(lambda x: x.replace("," , "."), fIDs))
    fIDs = list(map(lambda x: x.replace("-" , "_"), fIDs))
    asdf["BulkSampleID"] = asdf["BulkSampleID"].str.strip()
    asdf["BulkSampleID"] = asdf["BulkSampleID"].str.replace("-", "_")
    asdf["BulkSampleID"] = asdf["BulkSampleID"].str.replace(",", ".")
    asdf["BulkSampleID"] = asdf["BulkSampleID"].str.upper()
    asdf["BulkSampleID"] = asdf["BulkSampleID"].str.replace(" ", "")
    cgg["Museum ID/sample ID"] = cgg["Museum ID/sample ID"].str.strip()
    cgg["Museum ID/sample ID"] = cgg["Museum ID/sample ID"].str.replace("," , ".")
    cgg["Museum ID/sample ID"] = cgg["Museum ID/sample ID"].str.replace("-" , "_")
    cgg["Museum ID/sample ID"] = cgg["Museum ID/sample ID"].str.upper()
    cgg["Museum ID/sample ID"] = cgg["Museum ID/sample ID"].str.replace(" ", "")
    cgg["CGG ID"] = cgg["CGG ID"].str.strip()
    cgg["CGG ID"] = cgg["CGG ID"].str.replace("-" , "_")
    cgg["CGG ID"] = cgg["CGG ID"].str.upper()
    cgg["CGG ID"] = cgg["CGG ID"].str.replace(" ", "")
    wldf["Archive Sample ID"] = wldf["Archive Sample ID"].str.strip()
    wldf["Archive Sample ID"] = wldf["Archive Sample ID"].str.replace("-", "_")
    wldf["Archive Sample ID"] = wldf["Archive Sample ID"].str.replace("," , ".")
    wldf["Archive Sample ID"] = wldf["Archive Sample ID"].str.replace(" ", "")
    wldf["Archive Sample ID"] = wldf["Archive Sample ID"].str.upper()

    cgg_essential = cgg[["Museum ID/sample ID", 'CGG ID', "Depth", "height (m) asl.", "Age", "Geological age", "Lat", "Lon", "GPS"]]

    # Get all the rows where the fID matches 
    cores_kurt_cgg = cgg[cgg["Museum ID/sample ID"].isin(fIDs)]
    cores_kurt_asdf = asdf[asdf["BulkSampleID"].isin(fIDs)]

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

    my_list = list(cores_kurt_asdf["BulkSampleID"].unique()) + list(cores_kurt_cgg["Museum ID/sample ID"].unique())


    # Merging

    merged_on_aID = pd.merge(cores_kurt_asdf, wldf, left_on='Archive Sample ID', right_on='Archive Sample ID', how='left')
    merged_on_aID_essentials = merged_on_aID[['BulkSampleID', "Archive Sample ID", "Robot Sample ID", "Library ID", 'FastQ File ID', "DepthSampledCalTape"]]

    merged_on_CGG_ID = pd.merge(cores_kurt_cgg, wldf, left_on='CGG ID', right_on='Archive Sample ID', how='left')
    merged_on_CGG_ID_essentials = merged_on_CGG_ID[["Museum ID/sample ID", 'CGG ID', "Library ID", 'FastQ File ID', "Depth", "height (m) asl.", "Age", "Geological age", "Lat", "Lon", "GPS"]]

    merged_on_museum_id = pd.merge(cores_kurt_cgg, wldf, left_on='Museum ID/sample ID', right_on='Archive Sample ID', how='left')
    merged_on_museum_id_essentials = merged_on_museum_id[["Museum ID/sample ID", 'CGG ID', "Library ID", 'FastQ File ID', "Depth", "height (m) asl.", "Age", "Geological age", "Lat", "Lon", "GPS"]]

    merged_on_bulksampleid = pd.merge(cores_kurt_asdf, wldf, left_on='BulkSampleID', right_on='Archive Sample ID', how='left')
    merged_on_bulksampleid_essentials = merged_on_bulksampleid[['BulkSampleID', "Robot Sample ID", "Library ID", 'FastQ File ID', "DepthSampledCalTape"]]

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