from scripts.update_compatible_sheets import generate_sheet_from_table
import constants

df = generate_sheet_from_table.query(database_config=constants.DATABASE_CONFIG_2, 
                                          database_name='aedna_metadata',
                                     table_name='field_sample_internal',
                                     schema_name='test')