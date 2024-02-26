import pandas as pd

def parse(df):
    flowcell_data = parse_sequencing_data(df)
    flowcell_data = flowcell_data.astype(str)
    top_unknown_barcodes = parse_top_unknown_barcodes(df)
    top_unknown_barcodes = top_unknown_barcodes.astype(str)
    
    return flowcell_data, top_unknown_barcodes


def parse_sequencing_data(df_full):
    df = df_full[2]
    df['Flowcell ID'] = df_full[0][0][0].split("/")[0].strip()
    flowcell_summary = df_full[1]

    for i, col in enumerate(flowcell_summary.columns):
        df[col] = flowcell_summary[col].iloc[0]
    return df

def parse_top_unknown_barcodes(df_full):
    num_of_lanes = df_full[2]['Lane'].max()
    df = df_full[3]
    df['Flowcell ID'] = df_full[0][0][0].split("/")[0].strip()
    l = []
    for i in range(num_of_lanes-1):
        l.append(f'Sequence.{i+1}')
    top_unknown_barcodes_full = df.dropna(axis='rows', subset=l)
    top_unknown_barcodes = top_unknown_barcodes_full[['Lane', 'Count', 'Sequence']]
    for i in range(num_of_lanes-1):
        d = top_unknown_barcodes_full[[f'Lane.{i+1}', f'Count.{i+1}', f'Sequence.{i+1}']]
        d.columns = top_unknown_barcodes.columns
        top_unknown_barcodes = pd.concat([top_unknown_barcodes, d], ignore_index=True)
    top_unknown_barcodes['Lane'] = top_unknown_barcodes['Lane'].astype(int)
    top_unknown_barcodes['Count'] = top_unknown_barcodes['Count'].astype(int)
    return top_unknown_barcodes