import pandas as pd
from constants.db_names.names import db_names

def parse(df):
    flowcell_data = parse_sequencing_data(df)
    flowcell_data = flowcell_data.astype(str)
    top_unknown_barcodes = parse_top_unknown_barcodes(df)
    top_unknown_barcodes = top_unknown_barcodes.astype(str)
    
    return flowcell_data, top_unknown_barcodes


def parse_sequencing_data(df_full):
    df = df_full[2]
    df[db_names.flowcell.flowcell_id(template=True)] = df_full[0][0][0].split("/")[0].strip()
    flowcell_summary = df_full[1]

    for i, col in enumerate(flowcell_summary.columns):
        df[col] = flowcell_summary[col].iloc[0]
    return df

def parse_top_unknown_barcodes(df_full):
    col_names = db_names.top_unknown_seq_barcodes
    # flowcell_id_col_name = col_names.flowcell_id(template=True)
    flowcell_id_col_name = col_names.flowcell_id(template=True)
    lane_col_name = col_names.lane(template=True)
    count_col_name = col_names.count_(template=True)
    sequence_col_name = col_names.sequence(template=True)
    
    num_of_lanes = df_full[2][lane_col_name].max()
    df = df_full[3]
    flowcell_id = df_full[0][0][0].split("/")[0].strip()
    df[flowcell_id_col_name] = flowcell_id
    l = []
    for i in range(num_of_lanes-1):
        l.append(f'{sequence_col_name}.{i+1}')
    top_unknown_barcodes_full = df.dropna(axis='rows', subset=l)
    top_unknown_barcodes = top_unknown_barcodes_full[[lane_col_name, count_col_name, sequence_col_name]]
    for i in range(num_of_lanes-1):
        d = top_unknown_barcodes_full[[f'{lane_col_name}.{i+1}', f'{count_col_name}.{i+1}', f'{sequence_col_name}.{i+1}']]
        d.columns = top_unknown_barcodes.columns
        top_unknown_barcodes = pd.concat([top_unknown_barcodes, d], ignore_index=True)
    top_unknown_barcodes[lane_col_name] = top_unknown_barcodes[lane_col_name].astype(int)
    top_unknown_barcodes[count_col_name] = top_unknown_barcodes[count_col_name].astype(int)
    top_unknown_barcodes[flowcell_id_col_name] = flowcell_id
    return top_unknown_barcodes