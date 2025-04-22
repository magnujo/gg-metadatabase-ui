import pandas as pd

def outer_merge(schema_name, engine):
    #TODO: Make dynamic
    field_sample_id_col_name = 'field_sample_id'
    archive_sample_id_col_name = 'archive_sample_id'
    robot_sample_id_col_name = 'robot_sample_id'
    fastq_file_id_col_name = 'fastq_file_id'
    depth_id_col_name = 'depth_id'
    fastqlane_id_flowcell_col_name = 'fastqlane_id'
    flowcell_lane_col_name = 'flowcell_lane'
    wetlab_pk = 'wet_lab_comp_id'

    lc_suf = 'lc'

    field_sample_table_name = 'field_sample'
    archive_sample_table_name = 'edna_archive_sample'
    robot_sample_table_name = 'edna_robot_sample'
    wetlab_table_name = 'edna_wetlab_report'
    seqsheet_table_name = 'seq_sample_sheet'
    flowcell_table_name = 'flowcell'
    master_depth_table_name = 'master_depth'
    age_model_table_name = 'age_depth_model' 

    field_sample = pd.read_sql(f'select * from "{schema_name}"."{field_sample_table_name}"', engine).dropna(subset=field_sample_id_col_name, axis='index')
    archive_sample = pd.read_sql(f'select * from "{schema_name}"."{archive_sample_table_name}"', engine).dropna(subset=archive_sample_id_col_name, axis='index')
    robot_sample = pd.read_sql(f'select * from "{schema_name}"."{robot_sample_table_name}"', engine).dropna(subset=robot_sample_id_col_name, axis='index')
    wetlab = pd.read_sql(f'select * from "{schema_name}"."{wetlab_table_name}"', engine).dropna(subset=wetlab_pk, axis='index')
    seqsheet = pd.read_sql(f'select * from "{schema_name}"."{seqsheet_table_name}"', engine).dropna(subset=fastq_file_id_col_name, axis='index')
    flowcell = pd.read_sql(f'select * from "{schema_name}"."{flowcell_table_name}"', engine).dropna(subset=fastq_file_id_col_name, axis='index')
    master_depth = pd.read_sql(f'select * from "{schema_name}"."{master_depth_table_name}"', engine).dropna(subset=archive_sample_id_col_name, axis='index')
    age_model = pd.read_sql(f'select * from "{schema_name}"."{age_model_table_name}"', engine).dropna(subset=depth_id_col_name, axis='index')

    flowcell[f'{fastqlane_id_flowcell_col_name}{lc_suf}'] = flowcell[fastq_file_id_col_name].str.lower() + '_' + flowcell[flowcell_lane_col_name].astype(str)
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

    result_outer = field_sample.copy()
    result_outer = pd.merge(result_outer, 
                            archive_sample, 
                            on=f'{field_sample_id_col_name}{lc_suf}', 
                            how='outer', 
                            suffixes=(f'@{field_sample_table_name}', f'@{archive_sample_table_name}'))

    result_outer = pd.merge(result_outer, 
                            robot_sample, 
                            on=f'{archive_sample_id_col_name}{lc_suf}', 
                            how='outer', 
                            suffixes=(f'@{archive_sample_table_name}', f'@{robot_sample_table_name}'))

    result_outer = pd.merge(result_outer, 
                            wetlab, 
                            on=f'{robot_sample_id_col_name}{lc_suf}', 
                            how='outer', 
                            suffixes=(f'@{robot_sample_table_name}', f'@{wetlab_table_name}'))

    result_outer = pd.merge(result_outer, 
                            seqsheet, 
                            on=f'{fastq_file_id_col_name}{lc_suf}', 
                            how='outer', 
                            suffixes=(f'@{wetlab_table_name}', f'@{seqsheet_table_name}'))  # Will cause cross join. TODO: Fix

    result_outer = pd.merge(result_outer, 
                            flowcell, on=f'{fastq_file_id_col_name}{lc_suf}', 
                            how='outer', 
                            suffixes=(f'@{seqsheet_table_name}', f'@{flowcell_table_name}'))  # Will cause cross join. TODO: Fix

    result_outer = pd.merge(result_outer, 
                            master_depth, 
                            on=f'{archive_sample_id_col_name}{lc_suf}',
                            how='outer',
                            suffixes=(f'@{flowcell_table_name}', f'@{master_depth_table_name}'))

    result_outer = pd.merge(result_outer,
                            age_model,
                            on=f'{depth_id_col_name}{lc_suf}',
                            how='outer',
                            suffixes=(f'@{master_depth_table_name}', f'@{age_model_table_name}'))

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
    schema_name = 'test_1'

    field_sample_id_col_name = 'field_sample_id'
    archive_sample_id_col_name = 'archive_sample_id'
    robot_sample_id_col_name = 'robot_sample_id'
    fastq_file_id_col_name = 'fastq_file_id'
    depth_id_col_name = 'depth_id'
    fastqlane_id_flowcell_col_name = 'fastqlane_id'
    flowcell_lane_col_name = 'flowcell_lane'

    lc_suf = 'lc'

    field_sample_table_name = 'field_sample'
    archive_sample_table_name = 'edna_archive_sample'
    robot_sample_table_name = 'edna_robot_sample'
    wetlab_table_name = 'edna_wetlab_report'
    seqsheet_table_name = 'seq_sample_sheet'
    flowcell_table_name = 'flowcell'
    master_depth_table_name = 'master_depth'
    age_model_table_name = 'age_depth_model'
    wetlab_pk = 'wet_lab_comp_id'

    field_sample = pd.read_sql(f'select * from "{schema_name}"."{field_sample_table_name}"', engine).dropna(subset=field_sample_id_col_name, axis='index')
    archive_sample = pd.read_sql(f'select * from "{schema_name}"."{archive_sample_table_name}"', engine).dropna(subset=archive_sample_id_col_name, axis='index')
    robot_sample = pd.read_sql(f'select * from "{schema_name}"."{robot_sample_table_name}"', engine).dropna(subset=robot_sample_id_col_name, axis='index')
    wetlab = pd.read_sql(f'select * from "{schema_name}"."{wetlab_table_name}"', engine).dropna(subset=wetlab_pk, axis='index')
    seqsheet = pd.read_sql(f'select * from "{schema_name}"."{seqsheet_table_name}"', engine).dropna(subset=fastq_file_id_col_name, axis='index')
    flowcell = pd.read_sql(f'select * from "{schema_name}"."{flowcell_table_name}"', engine).dropna(subset=fastq_file_id_col_name, axis='index')
    master_depth = pd.read_sql(f'select * from "{schema_name}"."{master_depth_table_name}"', engine).dropna(subset=archive_sample_id_col_name, axis='index')
    age_model = pd.read_sql(f'select * from "{schema_name}"."{age_model_table_name}"', engine).dropna(subset=depth_id_col_name, axis='index')

    flowcell[f'{fastqlane_id_flowcell_col_name}{lc_suf}'] = flowcell[fastq_file_id_col_name].str.lower() + '_' + flowcell[flowcell_lane_col_name].astype(str)
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
    result_inner = pd.merge(result_inner, archive_sample, on=f'{field_sample_id_col_name}{lc_suf}', how='inner', suffixes=(f'@{field_sample_table_name}', f'@{archive_sample_table_name}'), validate="one_to_many")
    result_inner = pd.merge(result_inner, robot_sample, on=f'{archive_sample_id_col_name}{lc_suf}', how='inner', suffixes=(f'@{archive_sample_table_name}', f'@{robot_sample_table_name}'), validate='one_to_many')
    result_inner = pd.merge(result_inner, wetlab, on=f'{robot_sample_id_col_name}{lc_suf}', how='inner', suffixes=(f'@{robot_sample_table_name}', f'@{wetlab_table_name}'), validate="one_to_many")
    result_inner = pd.merge(result_inner, seqsheet, on=f'{fastq_file_id_col_name}{lc_suf}', how='inner', suffixes=(f'@{wetlab_table_name}', f'@{seqsheet_table_name}'), validate='many_to_many')  # Will cause cross join. TODO: Fix
    result_inner = pd.merge(result_inner, flowcell, on=f'{fastq_file_id_col_name}{lc_suf}', how='inner', suffixes=(f'@{seqsheet_table_name}', f'@{flowcell_table_name}'), validate='many_to_many')  # Will cause cross join. TODO: Fix
    result_inner = pd.merge(result_inner, master_depth, on=f'{archive_sample_id_col_name}{lc_suf}', how='inner', suffixes=(f'@{flowcell_table_name}', f'@{master_depth_table_name}'), validate='many_to_one')
    result_inner = pd.merge(result_inner, age_model, on=f'{depth_id_col_name}{lc_suf}', how='inner', suffixes=(f'@{master_depth_table_name}', f'@{age_model_table_name}'), validate='many_to_one')

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