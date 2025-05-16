import pandas as pd
from constants.db_names.names import data

field_sample_table_name = data.field_sample
archive_sample_table_name = data.edna_archive_sample
robot_sample_table_name = data.edna_robot_sample
wetlab_table_name = data.edna_wetlab_report
seqsheet_table_name = data.seq_sample_sheet
flowcell_table_name = data.flowcell
master_depth_table_name = data.master_depth
age_model_table_name = data.age_depth_model

field_sample_id_col_name = field_sample_table_name.field_sample_id()
archive_sample_id_col_name = archive_sample_table_name.archivesampleid()
robot_sample_id_col_name = robot_sample_table_name.robot_sample_id()
fastq_file_id_col_name = flowcell_table_name.fastq_file_id()
depth_id_col_name = master_depth_table_name.depth_id()
# fastqlane_id_flowcell_col_name = 'fastqlane_id'
# flowcell_lane_col_name = 'flowcell_lane'
wetlab_pk = wetlab_table_name.comp_id()
wetlab_lib_pool_tag = wetlab_table_name.library_pool_tag()
flowcell_lib_pool_tag = flowcell_table_name.library_pool_tag()

lc_suf = 'lc'

def merge_smdb(schema_name, engine, how='outer'):

    field_sample = (pd.read_sql(f'select * from "{schema_name}"."{field_sample_table_name()}"', engine)
                    .dropna(subset=field_sample_id_col_name, axis='index'))

    archive_sample = (pd.read_sql(f'select * from "{schema_name}"."{archive_sample_table_name()}"', engine)
                    .dropna(subset=archive_sample_id_col_name, axis='index'))

    robot_sample = (pd.read_sql(f'select * from "{schema_name}"."{robot_sample_table_name()}"', engine)
                    .dropna(subset=robot_sample_id_col_name, axis='index'))

    wetlab = (pd.read_sql(f'select * from "{schema_name}"."{wetlab_table_name()}"', engine)
                    .dropna(subset=wetlab_pk, axis='index'))

    # seqsheet = (pd.read_sql(f'select * from "{schema_name}"."{seqsheet_table_name()}"', engine)
    #                 .dropna(subset=fastq_file_id_col_name, axis='index'))

    flowcell = (pd.read_sql(f'select * from "{schema_name}"."{flowcell_table_name()}"', engine)
                    .dropna(subset=fastq_file_id_col_name, axis='index'))

    master_depth = (pd.read_sql(f'select * from "{schema_name}"."{master_depth_table_name()}"', engine)
                    .dropna(subset=archive_sample_id_col_name, axis='index'))

    age_model = (pd.read_sql(f'select * from "{schema_name}"."{age_model_table_name()}"', engine)
                    .dropna(subset=depth_id_col_name, axis='index'))

    # flowcell[f'{fastqlane_id_flowcell_col_name}{lc_suf}'] = flowcell[fastq_file_id_col_name].str.lower() + '_' + flowcell[flowcell_lane_col_name].astype(str)
    field_sample[f'{field_sample_id_col_name}{lc_suf}'] = field_sample[field_sample_id_col_name].str.lower()
    archive_sample[f'{field_sample_id_col_name}{lc_suf}'] = archive_sample[field_sample_id_col_name].str.lower()
    archive_sample[f'{archive_sample_id_col_name}{lc_suf}'] = archive_sample[archive_sample_id_col_name].str.lower()
    robot_sample[f'{archive_sample_id_col_name}{lc_suf}'] = robot_sample[archive_sample_id_col_name].str.lower()
    robot_sample[f'{robot_sample_id_col_name}{lc_suf}'] = robot_sample[robot_sample_id_col_name].str.lower()
    wetlab[f'{robot_sample_id_col_name}{lc_suf}'] = wetlab[robot_sample_id_col_name].str.lower()
    wetlab[f'{fastq_file_id_col_name}{lc_suf}'] = wetlab[fastq_file_id_col_name].str.lower()
    wetlab[f'{fastq_file_id_col_name}{lc_suf}'] = wetlab[fastq_file_id_col_name].str.lower()
    # seqsheet[f'{fastq_file_id_col_name}{lc_suf}'] = seqsheet[fastq_file_id_col_name].str.lower()
    flowcell[f'{fastq_file_id_col_name}{lc_suf}'] = flowcell[fastq_file_id_col_name].str.lower()
    master_depth[f'{archive_sample_id_col_name}{lc_suf}'] = master_depth[archive_sample_id_col_name].str.lower()
    master_depth[f'{depth_id_col_name}{lc_suf}'] = master_depth[depth_id_col_name].str.lower()
    age_model[f'{depth_id_col_name}{lc_suf}'] = age_model[depth_id_col_name].str.lower()

    result = field_sample.copy()
    result = pd.merge(result, 
                            archive_sample, 
                            on=f'{field_sample_id_col_name}{lc_suf}', 
                            how=how, 
                            suffixes=(f'@{field_sample_table_name()}', f'@{archive_sample_table_name()}'))
    
    test_df = result.copy()
    test_col1 = field_sample_id_col_name + f'@{field_sample_table_name()}'
    test_col2 = field_sample_id_col_name + f'@{archive_sample_table_name()}'
    test_df = test_df.dropna(subset=[test_col1, test_col2], how='any')

    assert (test_df[test_col1].str.lower() == test_df[test_col2].str.lower()).all(), 'Error, contact admin'

    result = pd.merge(result, 
                            robot_sample, 
                            on=f'{archive_sample_id_col_name}{lc_suf}', 
                            how=how, 
                            suffixes=(f'@{archive_sample_table_name()}', f'@{robot_sample_table_name()}'))
    
    test_df = result.copy()
    test_col1 = archive_sample_id_col_name + f'@{archive_sample_table_name()}'
    test_col2 = archive_sample_id_col_name + f'@{robot_sample_table_name()}'
    test_df = test_df.dropna(subset=[test_col1, test_col2], how='any')

    assert (test_df[test_col1].str.lower() == test_df[test_col2].str.lower()).all(), 'Error, contact admin'
    
    result[test_col1] = result[test_col1].fillna(test_col2)

    wetlab = wetlab.drop(columns=[data.edna_wetlab_report.archive_sample_id()])  # Drop archive as it is redundant here, and will only make it confusing
    result = pd.merge(result, 
                            wetlab, 
                            on=f'{robot_sample_id_col_name}{lc_suf}', 
                            how=how, 
                            suffixes=(f'@{robot_sample_table_name()}', f'@{wetlab_table_name()}'))
    
    test_df = result.copy()
    test_col1 = robot_sample_id_col_name + f'@{robot_sample_table_name()}'
    test_col2 = robot_sample_id_col_name + f'@{wetlab_table_name()}'
    test_df = test_df.dropna(subset=[test_col1, test_col2], how='any')

    assert (test_df[test_col1].str.lower() == test_df[test_col2].str.lower()).all(), 'Error, contact admin'

    # result_outer = pd.merge(result_outer, 
    #                         seqsheet, 
    #                         on=f'{fastq_file_id_col_name}{lc_suf}', 
    #                         how=how, 
    #                         suffixes=(f'@{wetlab_table_name()}', f'@{seqsheet_table_name()}'))  # Will cause cross join. TODO: Fix

    result = pd.merge(result, 
                            flowcell, on=f'{fastq_file_id_col_name}{lc_suf}', 
                            how=how, 
                            suffixes=(f'@{wetlab_table_name()}', f'@{flowcell_table_name()}'))  # Will cause cross join becasuse of multiple lanes and runs on different flowcells. TODO: Fix
    
    test_df = result.copy()
    test_col1 = fastq_file_id_col_name + f'@{wetlab_table_name()}'
    test_col2 = fastq_file_id_col_name + f'@{flowcell_table_name()}'
    test_df = test_df.dropna(subset=[test_col1, test_col2], how='any')

    assert (test_df[test_col1].str.lower() == test_df[test_col2].str.lower()).all(), 'Error, contact admin'
        
    result = pd.merge(result, 
                            master_depth, 
                            on=f'{archive_sample_id_col_name}{lc_suf}',
                            how=how,
                            suffixes=(None, f'@{master_depth_table_name()}'))
    
    test_df = result.copy()
    test_col1 = archive_sample_id_col_name
    test_col2 = archive_sample_id_col_name + f'@{archive_sample_table_name()}'
    test_df = test_df.dropna(subset=[test_col1, test_col2], how='any')

    assert (test_df[test_col1].str.lower() == test_df[test_col2].str.lower()).all(), 'Error, contact admin'

    result = pd.merge(result,
                            age_model,
                            on=f'{depth_id_col_name}{lc_suf}',
                            how=how,
                            suffixes=(None, f'@{age_model_table_name()}'))
    
    test_df = result.copy()
    test_col1 = depth_id_col_name
    test_col2 = depth_id_col_name + f'@{age_model_table_name()}'
    test_df = test_df.dropna(subset=[test_col1, test_col2], how='any')

    assert (test_df[test_col1].str.lower() == test_df[test_col2].str.lower()).all(), 'Error, contact admin'

    result = result.drop(columns=[
        f'{field_sample_id_col_name}{lc_suf}',
        f'{archive_sample_id_col_name}{lc_suf}',
        f'{robot_sample_id_col_name}{lc_suf}',
        f'{depth_id_col_name}{lc_suf}',
        f'{fastq_file_id_col_name}{lc_suf}'
    ])
    
    return result.dropna(how='all')