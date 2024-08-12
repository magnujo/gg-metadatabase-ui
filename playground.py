
from db_names import db_names
import pandas as pd

df = pd.DataFrame({"field_sample": [1,2,3]})

print(db_names.data.field_sample())
print([db_names.data.field_sample()])
print(db_names.data())
print([db_names.data()])
print(db_names.data.field_sample.alias)
print([db_names.data.field_sample.alias])

{'master_depth', 'adna_wetlab_report', 'field_sample', 'cgg_sediment_water', 'top_unknown_seq_barcodes', 'age_depth_model', 'cgg_animal_plant', 'edna_archive_sample', 'initials_translator', 'seq_sample_sheet', 'flowcell', 'edna_wetlab_report', 'edna_robot_sample'}
{edna_wetlab_report, cgg_animal_plant, seq_sample_sheet, initials_translator, edna_robot_sample, cgg_sediment_water, top_unknown_seq_barcodes, age_depth_model, field_sample, flowcell, master_depth, edna_archive_sample, adna_wetlab_report}