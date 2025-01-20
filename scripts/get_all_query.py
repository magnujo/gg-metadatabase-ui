from sqlalchemy import create_engine
import pandas as pd
import constants.db_connections as misc_constants
import numpy as np
from scripts import fid_query
ENGINE = misc_constants.ENGINE_READ_ONLY
from utils.db_utils import get_ordinal_position_maps
from constants.db_names.names import data

def get_all_fids():
    wldf_q = f'select * from "{data()}"."{data.edna_wetlab_report()}";'
    asdf_q = f'select * from "{data()}"."{data.edna_archive_sample()}";'
    cgg_q = f'select * from "{data()}"."{data.cgg_sediment_water()}";'
    wldf = pd.read_sql(wldf_q, dtype=str, con=ENGINE)
    asdf = pd.read_sql(asdf_q, dtype=str, con=ENGINE)
    cgg = pd.read_sql(cgg_q, dtype=str, con=ENGINE)
    
      
    field_sample_ID = data.edna_archive_sample.field_sample_id()
    museum_ID = data.cgg_sediment_water.museum_id_sample_id() 

    wldf = wldf.fillna(np.nan)
    wldf = wldf.replace("NONE", np.nan)
    asdf = asdf.fillna(np.nan)
    asdf = asdf.replace("NONE", np.nan)
    cgg = cgg.fillna(np.nan)
    cgg = cgg.replace("NONE", np.nan)
    all_fids = list(asdf[field_sample_ID].unique()) + list(cgg[museum_ID].unique())
    return all_fids

def get_all_meta_data_using_fids():
    all_fids = get_all_fids()
    essential, full, raws = fid_query.get_meta_data(all_fids)
    return essential, full, raws