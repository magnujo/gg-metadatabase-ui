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
lib_pool_tag_col_name = wetlab_table_name.library_pool_tag()

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

    # Drop nan values in foreign keys, to avoid null null cross joins, because the outher merges creates null values.
    archive_sample = archive_sample.dropna(subset=field_sample_id_col_name, axis='index')
    robot_sample = robot_sample.dropna(subset=archive_sample_id_col_name, axis='index')
    wetlab = wetlab.dropna(subset=robot_sample_id_col_name, axis='index')
    flowcell = flowcell.dropna(subset=fastq_file_id_col_name, axis='index')
    master_depth = master_depth.dropna(subset=archive_sample_id_col_name, axis='index')
    age_model = age_model.dropna(subset=depth_id_col_name, axis='index')
    flowcell = flowcell.dropna(subset=lib_pool_tag_col_name, axis='index')

    # Drop archive as it is redundant here, and will only make it confusing
    wetlab = wetlab.drop(columns=[data.edna_wetlab_report.archive_sample_id()])  

    # Make lower versions of all the join keys

    # flowcell[f'{fastqlane_id_flowcell_col_name}{lc_suf}'] = flowcell[fastq_file_id_col_name].str.lower() + '_' + flowcell[flowcell_lane_col_name].astype(str)
    field_sample[f'{field_sample_id_col_name}{lc_suf}'] = field_sample[field_sample_id_col_name].str.lower()
    archive_sample[f'{field_sample_id_col_name}{lc_suf}'] = archive_sample[field_sample_id_col_name].str.lower()
    archive_sample[f'{archive_sample_id_col_name}{lc_suf}'] = archive_sample[archive_sample_id_col_name].str.lower()
    robot_sample[f'{archive_sample_id_col_name}{lc_suf}'] = robot_sample[archive_sample_id_col_name].str.lower()
    robot_sample[f'{robot_sample_id_col_name}{lc_suf}'] = robot_sample[robot_sample_id_col_name].str.lower()
    wetlab[f'{robot_sample_id_col_name}{lc_suf}'] = wetlab[robot_sample_id_col_name].str.lower()
    wetlab[f'{fastq_file_id_col_name}{lc_suf}'] = wetlab[fastq_file_id_col_name].str.lower()
    wetlab[f'{lib_pool_tag_col_name}{lc_suf}'] = wetlab[lib_pool_tag_col_name].str.lower()
    # seqsheet[f'{fastq_file_id_col_name}{lc_suf}'] = seqsheet[fastq_file_id_col_name].str.lower()
    flowcell[f'{fastq_file_id_col_name}{lc_suf}'] = flowcell[fastq_file_id_col_name].str.lower()
    flowcell[f'{lib_pool_tag_col_name}{lc_suf}'] = flowcell[lib_pool_tag_col_name].str.lower()
    master_depth[f'{archive_sample_id_col_name}{lc_suf}'] = master_depth[archive_sample_id_col_name].str.lower()
    master_depth[f'{depth_id_col_name}{lc_suf}'] = master_depth[depth_id_col_name].str.lower()
    age_model[f'{depth_id_col_name}{lc_suf}'] = age_model[depth_id_col_name].str.lower()
    result = field_sample.copy()
    merge_key = field_sample_id_col_name

    result = pd.merge(result, 
                            archive_sample, 
                            on=f'{merge_key}{lc_suf}', 
                            how=how, 
                            suffixes=(f'@{field_sample_table_name()}', f'@{archive_sample_table_name()}'))

    test_df = result.copy()
    test_col1 = field_sample_id_col_name + f'@{field_sample_table_name()}'
    test_col2 = field_sample_id_col_name + f'@{archive_sample_table_name()}'
    test_df = test_df.dropna(subset=[test_col1, test_col2], how='any')
    assert (test_df[test_col1].str.lower() == test_df[test_col2].str.lower()).all(), 'Error, contact admin'
    assert len(result) <= (len(field_sample) + len(archive_sample))
    merge_key = archive_sample_id_col_name

    len_before_merge = len(result)
    result = pd.merge(result, 
                            robot_sample, 
                            on=f'{merge_key}{lc_suf}', 
                            how=how, 
                            suffixes=(f'@{archive_sample_table_name()}', f'@{robot_sample_table_name()}'))

    test_df = result.copy()
    test_col1 = merge_key + f'@{archive_sample_table_name()}'
    test_col2 = merge_key + f'@{robot_sample_table_name()}'
    test_df = test_df.dropna(subset=[test_col1, test_col2], how='any')

    assert (test_df[test_col1].str.lower() == test_df[test_col2].str.lower()).all(), 'Error, contact admin'
    result[test_col1] = result[test_col1].fillna(test_col2)
    assert len(result) <= (len_before_merge + len(robot_sample))
    merge_key = robot_sample_id_col_name

    len_before_merge = len(result)
    result = pd.merge(result, 
                            wetlab, 
                            on=f'{merge_key}{lc_suf}', 
                            how=how, 
                            suffixes=(f'@{robot_sample_table_name()}', f'@{wetlab_table_name()}'))

    test_df = result.copy()
    test_col1 = merge_key + f'@{robot_sample_table_name()}'
    test_col2 = merge_key + f'@{wetlab_table_name()}'
    test_df = test_df.dropna(subset=[test_col1, test_col2], how='any')

    assert (test_df[test_col1].str.lower() == test_df[test_col2].str.lower()).all(), 'Error, contact admin'
    assert len(result) <= (len_before_merge + len(wetlab))
    merge_keys = [fastq_file_id_col_name, lib_pool_tag_col_name]
    len_before_merge = len(result)

    result = pd.merge(result, 
                            flowcell, on=[f'{merge_key}{lc_suf}' for merge_key in merge_keys], 
                            how=how, 
                            suffixes=(f'@{wetlab_table_name()}', f'@{flowcell_table_name()}'))  # Will cause cross join becasuse of multiple lanes and runs on different flowcells. TODO: Fix

    test_df = result.copy()

    for merge_key in merge_keys:
        test_col1 = merge_key + f'@{wetlab_table_name()}'
        test_col2 = merge_key + f'@{flowcell_table_name()}'
        test_df = test_df.dropna(subset=[test_col1, test_col2], how='any')

        assert (test_df[test_col1].str.lower() == test_df[test_col2].str.lower()).all(), 'Error, contact admin'
        
    assert len(result) <= (len_before_merge + len(flowcell))
    merge_key = archive_sample_id_col_name
    len_before_merge = len(result)
    result = pd.merge(result, 
                            master_depth, 
                            on=f'{merge_key}{lc_suf}',
                            how=how,
                            suffixes=(None, f'@{master_depth_table_name()}'))

    test_df = result.copy()
    test_col1 = merge_key
    test_col2 = merge_key + f'@{archive_sample_table_name()}'
    test_df = test_df.dropna(subset=[test_col1, test_col2], how='any')
    assert (test_df[test_col1].str.lower() == test_df[test_col2].str.lower()).all(), 'Error, contact admin'
    assert len(result) <= (len_before_merge + len(flowcell))
    merge_key = depth_id_col_name
    len_before_merge = len(result)
    result = pd.merge(result,
                            age_model,
                            on=f'{merge_key}{lc_suf}',
                            how=how,
                            suffixes=(None, f'@{age_model_table_name()}'))

    test_df = result.copy()
    test_col1 = merge_key
    test_col2 = merge_key + f'@{age_model_table_name()}'
    test_df = test_df.dropna(subset=[test_col1, test_col2], how='any')

    assert (test_df[test_col1].str.lower() == test_df[test_col2].str.lower()).all(), 'Error, contact admin'
    assert len(result) <= (len_before_merge + len(flowcell))
    result = result.drop(columns=[
        f'{field_sample_id_col_name}{lc_suf}',
        f'{archive_sample_id_col_name}{lc_suf}',
        f'{robot_sample_id_col_name}{lc_suf}',
        f'{depth_id_col_name}{lc_suf}',
        f'{fastq_file_id_col_name}{lc_suf}'
    ])
    
    return result.dropna(how='all')


def qc(schema_name, engine):
    report_meta = f"select * from {schema_name}.report_meta where report_meta_key = 'config_output_dir'"
    report_meta = pd.read_sql(report_meta, engine)
    report_meta_piv = report_meta.pivot(columns='report_meta_key', index='report_id', values='report_meta_value')
    report_meta_piv.columns.name = None
    report_meta_piv = report_meta_piv.reset_index()
    multiqc_data = f'''
                SELECT s.sample_name, sdt.data_key, NULLIF(sd.value, 'None') AS value, sd.report_id
                FROM {schema_name}.sample_data sd
                JOIN {schema_name}.sample_data_type sdt ON sdt.sample_data_type_id = sd.sample_data_type_id
                JOIN {schema_name}.sample s ON sd.sample_id = s.sample_id
                WHERE sdt.data_section != 'general_stats' and sdt.data_section != 'bbmap_low_complexity'; 
            '''
    print('Executing multiqc_data query...')
    multiqc_data = pd.read_sql(multiqc_data, engine)
    print('Done executing.') 
    multiqc_data['binf_details'] = multiqc_data['sample_name'].str.split('_').apply(lambda x: '_'.join(x[2:]))
    multiqc_data['library_id'] = multiqc_data['sample_name'].str.split('_').apply(lambda x: x[1])
    print('Pivoting...')
    pivoted_df = multiqc_data.pivot(index=['library_id', 'report_id', 'binf_details'], columns='data_key', values='value')
    print('Done pivoting.')
    pivoted_df
    pivoted_df.columns.name = None
    pivoted_df = pivoted_df.reset_index()
    mega_qc = pivoted_df
    print('Merging...')
    mega_qc = mega_qc.merge(report_meta_piv, on='report_id', how='inner', validate='m:1')
    print('Done merging.')
    mega_qc = mega_qc.rename(columns={'config_output_dir': 'binf_qc_report_path', 
                                        'report_id': 'binf_qc_report_id' }, errors='raise')
    # Move column 'C' to be after column 'A'
    col = mega_qc.pop('binf_qc_report_path')
    mega_qc.insert(mega_qc.columns.get_loc('binf_details') + 1, 'binf_qc_report_path', col)

    col = mega_qc.pop('binf_qc_report_id')
    mega_qc.insert(mega_qc.columns.get_loc('binf_details') + 1, 'binf_qc_report_id', col)
    
    return mega_qc.dropna(how='all')
