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

    result_outer = field_sample.copy()
    result_outer = pd.merge(result_outer, 
                            archive_sample, 
                            on=f'{field_sample_id_col_name}{lc_suf}', 
                            how=how, 
                            suffixes=(f'@{field_sample_table_name()}', f'@{archive_sample_table_name()}'))

    result_outer = pd.merge(result_outer, 
                            robot_sample, 
                            on=f'{archive_sample_id_col_name}{lc_suf}', 
                            how=how, 
                            suffixes=(f'@{archive_sample_table_name()}', f'@{robot_sample_table_name()}'))

    result_outer = pd.merge(result_outer, 
                            wetlab, 
                            on=f'{robot_sample_id_col_name}{lc_suf}', 
                            how=how, 
                            suffixes=(f'@{robot_sample_table_name()}', f'@{wetlab_table_name()}'))

    # result_outer = pd.merge(result_outer, 
    #                         seqsheet, 
    #                         on=f'{fastq_file_id_col_name}{lc_suf}', 
    #                         how=how, 
    #                         suffixes=(f'@{wetlab_table_name()}', f'@{seqsheet_table_name()}'))  # Will cause cross join. TODO: Fix

    result_outer = pd.merge(result_outer, 
                            flowcell, on=f'{fastq_file_id_col_name}{lc_suf}', 
                            how=how, 
                            suffixes=(f'@{wetlab_table_name()}', f'@{flowcell_table_name()}'))  # Will cause cross join becasuse of multiple lanes and runs on different flowcells. TODO: Fix

    result_outer = pd.merge(result_outer, 
                            master_depth, 
                            on=f'{archive_sample_id_col_name}{lc_suf}',
                            how=how,
                            suffixes=(f'@{flowcell_table_name()}', f'@{master_depth_table_name()}'))

    result_outer = pd.merge(result_outer,
                            age_model,
                            on=f'{depth_id_col_name}{lc_suf}',
                            how=how,
                            suffixes=(f'@{master_depth_table_name()}', f'@{age_model_table_name()}'))




    result_outer = result_outer.drop(columns=[
        f'{field_sample_id_col_name}{lc_suf}',
        f'{archive_sample_id_col_name}{lc_suf}',
        f'{robot_sample_id_col_name}{lc_suf}',
        f'{depth_id_col_name}{lc_suf}',
        f'{fastq_file_id_col_name}{lc_suf}'
    ])
    
    return result_outer

def inner(schema_name, engine):
    #TODO: Make dynamic


    field_sample = pd.read_sql(f'select * from "{schema_name}"."{field_sample_table_name()}"', engine).dropna(subset=field_sample_id_col_name, axis='index')
    archive_sample = pd.read_sql(f'select * from "{schema_name}"."{archive_sample_table_name()}"', engine).dropna(subset=archive_sample_id_col_name, axis='index')
    robot_sample = pd.read_sql(f'select * from "{schema_name}"."{robot_sample_table_name()}"', engine).dropna(subset=robot_sample_id_col_name, axis='index')
    wetlab = pd.read_sql(f'select * from "{schema_name}"."{wetlab_table_name()}"', engine).dropna(subset=wetlab_pk, axis='index')
    seqsheet = pd.read_sql(f'select * from "{schema_name}"."{seqsheet_table_name()}"', engine).dropna(subset=fastq_file_id_col_name, axis='index')
    flowcell = pd.read_sql(f'select * from "{schema_name}"."{flowcell_table_name()}"', engine).dropna(subset=fastq_file_id_col_name, axis='index')
    master_depth = pd.read_sql(f'select * from "{schema_name}"."{master_depth_table_name()}"', engine).dropna(subset=archive_sample_id_col_name, axis='index')
    age_model = pd.read_sql(f'select * from "{schema_name}"."{age_model_table_name()}"', engine).dropna(subset=depth_id_col_name, axis='index')

    # flowcell[f'{fastqlane_id_flowcell_col_name}{lc_suf}'] = flowcell[fastq_file_id_col_name].str.lower() + '_' + flowcell[flowcell_lane_col_name].astype(str)
    field_sample[f'{field_sample_id_col_name}{lc_suf}'] = field_sample[field_sample_id_col_name].str.lower()
    archive_sample[f'{field_sample_id_col_name}{lc_suf}'] = archive_sample[field_sample_id_col_name].str.lower()
    archive_sample[f'{archive_sample_id_col_name}{lc_suf}'] = archive_sample[archive_sample_id_col_name].str.lower()
    robot_sample[f'{archive_sample_id_col_name}{lc_suf}'] = robot_sample[archive_sample_id_col_name].str.lower()
    robot_sample[f'{robot_sample_id_col_name}{lc_suf}'] = robot_sample[robot_sample_id_col_name].str.lower()
    wetlab[f'{robot_sample_id_col_name}{lc_suf}'] = wetlab[robot_sample_id_col_name].str.lower()
    wetlab[f'{fastq_file_id_col_name}{lc_suf}'] = wetlab[fastq_file_id_col_name].str.lower()
    seqsheet[f'{fastq_file_id_col_name}{lc_suf}'] = seqsheet[fastq_file_id_col_name].str.lower()
    flowcell[f'{fastq_file_id_col_name}{lc_suf}'] = flowcell[fastq_file_id_col_name].str.lower()
    master_depth[f'{archive_sample_id_col_name}{lc_suf}'] = master_depth[archive_sample_id_col_name].str.lower()
    master_depth[f'{depth_id_col_name}{lc_suf}'] = master_depth[depth_id_col_name].str.lower()
    age_model[f'{depth_id_col_name}{lc_suf}'] = age_model[depth_id_col_name].str.lower()

    result_inner = field_sample.copy()
    result_inner = pd.merge(result_inner, archive_sample, on=f'{field_sample_id_col_name}{lc_suf}', how='inner', suffixes=(f'@{field_sample_table_name()}', f'@{archive_sample_table_name()}'), validate="one_to_many")
    result_inner = pd.merge(result_inner, robot_sample, on=f'{archive_sample_id_col_name}{lc_suf}', how='inner', suffixes=(f'@{archive_sample_table_name()}', f'@{robot_sample_table_name()}'), validate='one_to_many')
    result_inner = pd.merge(result_inner, wetlab, on=f'{robot_sample_id_col_name}{lc_suf}', how='inner', suffixes=(f'@{robot_sample_table_name()}', f'@{wetlab_table_name()}'), validate="one_to_many")
    result_inner = pd.merge(result_inner, seqsheet, on=f'{fastq_file_id_col_name}{lc_suf}', how='inner', suffixes=(f'@{wetlab_table_name()}', f'@{seqsheet_table_name()}'), validate='many_to_many')  # Will cause cross join. TODO: Fix
    result_inner = pd.merge(result_inner, flowcell, on=f'{fastq_file_id_col_name}{lc_suf}', how='inner', suffixes=(f'@{seqsheet_table_name()}', f'@{flowcell_table_name()}'), validate='many_to_many')  # Will cause cross join. TODO: Fix
    result_inner = pd.merge(result_inner, master_depth, on=f'{archive_sample_id_col_name}{lc_suf}', how='inner', suffixes=(f'@{flowcell_table_name()}', f'@{master_depth_table_name()}'), validate='many_to_one')
    result_inner = pd.merge(result_inner, age_model, on=f'{depth_id_col_name}{lc_suf}', how='inner', suffixes=(f'@{master_depth_table_name()}', f'@{age_model_table_name()}'), validate='many_to_one')

    key_cols = [
        'field_sample_id@field_sample', 'archive_sample_id@edna_archive_sample', 'robot_sample_id@edna_robot_sample',
        'fastq_file_id@edna_wetlab_report', 'depth_id@master_depth'
    ]

    assert result_inner[key_cols].isnull().sum().sum() == 0

    result_inner = result_inner.drop(columns=[
        f'{field_sample_id_col_name}{lc_suf}',
        f'{archive_sample_id_col_name}{lc_suf}',
        f'{robot_sample_id_col_name}{lc_suf}',
        f'{depth_id_col_name}{lc_suf}',
        f'{fastq_file_id_col_name}{lc_suf}'
    ])
    
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
    multiqc_data = pd.read_sql(multiqc_data, engine)    
    multiqc_data['binf_details'] = multiqc_data['sample_name'].str.split('_').apply(lambda x: '_'.join(x[2:]))
    multiqc_data['library_id'] = multiqc_data['sample_name'].str.split('_').apply(lambda x: x[1])
    pivoted_df = multiqc_data.pivot(index=['library_id', 'report_id', 'binf_details'], columns='data_key', values='value')
    pivoted_df
    pivoted_df.columns.name = None
    pivoted_df = pivoted_df.reset_index()
    mega_qc = pivoted_df
    mega_qc = mega_qc.merge(report_meta_piv, on='report_id', how='inner', validate='m:1')
    mega_qc = mega_qc.rename(columns={'config_output_dir': 'binf_qc_report_path', 
                                        'report_id': 'binf_qc_report_id' }, errors='raise')
    # Move column 'C' to be after column 'A'
    col = mega_qc.pop('binf_qc_report_path')
    mega_qc.insert(mega_qc.columns.get_loc('binf_details') + 1, 'binf_qc_report_path', col)

    col = mega_qc.pop('binf_qc_report_id')
    mega_qc.insert(mega_qc.columns.get_loc('binf_details') + 1, 'binf_qc_report_id', col)
    
    return mega_qc