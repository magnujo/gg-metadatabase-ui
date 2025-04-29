'''
Scans the field_sample table and makes all the folder and subfolders. 

'''
import os
from constants import misc_constants
from pathlib import Path
from utils import misc
from utils import queries


df = queries.get_table_as_dataframe(engine=misc_constants.ENGINE, schema_name="data", table_name="field_sample", dtype=str)
samples_root_dir = r"n:\SUN-GI-metadb-test\Field Sample Geo Files\Sample specific files"
projects_root_dir = r"n:\SUN-GI-metadb-test\Field Sample Geo Files\Project specific files"
dirs_to_create = misc.generate_field_sample_dir_paths(df, projects_root_dir=projects_root_dir, 
                                                                                          samples_root_dir=samples_root_dir)

created_dirs = []
for path_ in dirs_to_create:
    if not os.path.exists(path_):
        path_)
        os.mkdir(path_)
        created_dirs.append(path_)