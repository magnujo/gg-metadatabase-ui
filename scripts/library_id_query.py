from sqlalchemy import create_engine
import pandas as pd
from constants.misc_constants import ENGINE_READ_ONLY as ENGINE
import numpy as np

def get_meta_data(input_data):
    
    '''
    Gets all meta data associated with library ids, given a list of library ids 
    '''

    wldf_q = "select * from test_1.edna_wetlab_report;"
    asdf_q = "select * from test_1.edna_archive_sample;"
    cgg_q = "select * from test_1.cgg_sediment_water;"
    flowcell_q = "select * from test_1.flowcell;"

    wldf = pd.read_sql(wldf_q, dtype=str, con=ENGINE).map(lambda x: x.upper() if isinstance(x, str) else x)
    asdf = pd.read_sql(asdf_q, dtype=str, con=ENGINE).map(lambda x: x.upper() if isinstance(x, str) else x)
    cgg = pd.read_sql(cgg_q, dtype=str, con=ENGINE).map(lambda x: x.upper() if isinstance(x, str) else x)
    flowcell = pd.read_sql(flowcell_q, dtype=str, con=ENGINE).map(lambda x: x.upper() if isinstance(x, str) else x)


    # TODO: check that replacemants doesnt result in duplicate data
    input_data = list(map(lambda x: x.upper(), input_data))
    input_data = list(map(lambda x: x.replace(" ", ""), input_data))
    input_data = list(map(lambda x: x.replace("," , "."), input_data))
    input_data = list(map(lambda x: x.replace("-" , "_"), input_data))
    wldf = wldf.fillna(np.nan)
    wldf = wldf.replace("NONE", np.nan)
    asdf = asdf.fillna(np.nan)
    asdf = asdf.replace("NONE", np.nan)
    cgg = cgg.fillna(np.nan)
    cgg = cgg.replace("NONE", np.nan)
    flowcell = flowcell.fillna(np.nan)
    flowcell = flowcell.replace("NONE", np.nan)

    cgg_essential = cgg[["Museum ID/sample ID", 'CGG ID', "Depth", "height (m) asl.", "Age", "Geological age", "Lat", "Lon", "GPS"]]

    # Get all the rows where the fID matches 
    input_data_filter = wldf[wldf["Library ID"].isin(input_data)]

    # TODO: Check that Archive Sample ID is the same in both the input_data_filter and asdf
    aid_x_aid = pd.merge(input_data_filter, asdf, left_on='Archive Sample ID', right_on='Archive Sample ID', how='left')
    aid_x_aid_essentials = aid_x_aid[['BulkSampleID', "Archive Sample ID", "Robot Sample ID", "Library ID", 'FastQ File ID', "DepthSampledCalTape"]]


    fileid_x_sample = pd.merge(input_data_filter, flowcell, left_on='FastQ File ID', right_on='Sample', how='left')
    fileid_x_sample_essentials = fileid_x_sample[["Archive Sample ID", "Robot Sample ID", "Library ID", 'FastQ File ID', "Flowcell ID"]]

    aid_x_cggid = pd.merge(input_data_filter, cgg, left_on='Archive Sample ID', right_on='CGG ID', how='left')
    aid_x_cggid_essentials = aid_x_cggid[["Museum ID/sample ID", 'CGG ID', "Archive Sample ID", "Robot Sample ID", "Library ID", 'FastQ File ID', "Depth", "height (m) asl.", "Age", "Geological age", "Lat", "Lon"]]

    bulksampleid_x_cggid = pd.merge(aid_x_aid, cgg, left_on='BulkSampleID', right_on='CGG ID', how='left')
    bulksampleid_x_cggid_essentials = bulksampleid_x_cggid[["Museum ID/sample ID", 'CGG ID', "Robot Sample ID", "Library ID", 'FastQ File ID', "Depth", "height (m) asl.", "Age", "Geological age", "Lat", "Lon", "GPS"]]

    aID_x_mID = pd.merge(input_data_filter, cgg, left_on='Archive Sample ID', right_on='Museum ID/sample ID', how='left')
    aID_x_mID_essentials = aID_x_mID[["Museum ID/sample ID", 'CGG ID', "Robot Sample ID", "Library ID", 'FastQ File ID', "Depth", "height (m) asl.", "Age", "Geological age", "Lat", "Lon", "GPS"]]

    bulksampleid_x_mID = pd.merge(aid_x_aid, cgg, left_on='BulkSampleID', right_on='Museum ID/sample ID', how='left')
    bulksampleid_x_mID_essentials = bulksampleid_x_mID[["Museum ID/sample ID", 'CGG ID', "Robot Sample ID", "Library ID", 'FastQ File ID', "Depth", "height (m) asl.", "Age", "Geological age", "Lat", "Lon", "GPS"]]

    # m1 = pd.merge(aid_x_aid_essentials, fileid_x_sample_essentials, how='inner', on='Library ID')
    # m2 = pd.merge(aid_x_cggid_essentials, bulksampleid_x_cggid_essentials, how='inner', on='Library ID')
    # m3 = pd.merge(aID_x_mID_essentials, bulksampleid_x_mID_essentials, how='inner', on='Library ID')
    # m4 = pd.merge(m2, m3, how='inner', on='Library ID')
    # m5 = pd.merge(m4, m1, how='inner', on='Library ID')

    combined_essential = (aid_x_aid_essentials
    .combine_first(fileid_x_sample_essentials)
    .combine_first(aid_x_cggid_essentials)
    .combine_first(bulksampleid_x_cggid_essentials)
    .combine_first(aID_x_mID_essentials)
    .combine_first(bulksampleid_x_mID_essentials))

    combined = (aid_x_aid
    .combine_first(fileid_x_sample)
    .combine_first(aid_x_cggid)
    .combine_first(bulksampleid_x_cggid)
    .combine_first(aID_x_mID)
    .combine_first(bulksampleid_x_mID))
    
    return combined_essential, combined