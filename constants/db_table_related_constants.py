from constants.misc_constants import SHEET_TYPES, DATABASE_CONFIG
from utils import queries, misc
import inspect


class DBTableRelated:
    '''
    Contains all constants that contain names of database tables
    '''
    
    TABLE_TYPES_FOR_ENUM_VALIDATION = {"ENVIRONMENTAL": {"SAMPLE": ['field_sample', 'edna_robot_sample', 'edna_archive_sample', "master_depth", "cgg_animal_plant", "cgg_sediment_water", "age_depth_model", "initials_translator"],
                                                         "LIBRARY": ['flowcell', 'seq_sample_sheet', 'top_unknown_seq_barcodes', 'adna_wetlab_report', 'edna_wetlab_report']
                                                         }
                                       }

    # Load tables from schema and check that they are all here:
    TABLE_SPLITTER = {
                        'field_sample': ['field_sample'],
                        'edna_archive_sample': ['edna_archive_sample'],
                        'edna_robot_sample': ['edna_robot_sample'],
                        'edna_wetlab_report': ['edna_wetlab_report'],
                        'adna_wetlab_report': ['adna_wetlab_report'],
                        'cgg_sediment_water': ['cgg_sediment_water'],
                        'cgg_animal_plant': ['cgg_animal_plant'],
                        'lane_barcode_html': ['flowcell', 'top_unknown_seq_barcodes'],
                        'seq_sample_sheet': ['seq_sample_sheet'],
                        'master_depth': ['master_depth'],
                        'age_depth_model': ['age_depth_model'],
                        'initials_translator': ['initials_translator']
                    }

    DB_GENERATED_COLUMNS = {'top_unknown_seq_barcodes': ['uid']}
        

    def check_for_duplicates():
        print(f"\nRunning tests in {str(inspect.stack()[1].code_context[0]).strip()}...\n")
        
        potential_duplicates = sum(DBTableRelated.TABLE_SPLITTER.values(), [])
        no_duplicates = set(potential_duplicates)
        if len(potential_duplicates) == len(no_duplicates):
            print(f"No duplicate table names found in TABLE_SPLITTER")
        else:
            raise Exception("Duplicate table names found in TABLE_SPLITTER")
        
        potential_duplicates = sum(list(misc.extract_leaf_values_from_dict(DBTableRelated.TABLE_TYPES_FOR_ENUM_VALIDATION)), [])
        no_duplicates = set(potential_duplicates)
        if len(potential_duplicates) == len(no_duplicates):
            print(f"No duplicate table names found in TABLE_TYPES_FOR_ENUM_VALIDATION")
        else:
            raise Exception("Duplicate table names found in TABLE_TYPES_FOR_ENUM_VALIDATION")
    
    def check_for_table_name_inconsistencies():
        print(f"\nRunning tests in {str(inspect.stack()[1].code_context[0]).strip()}...\n")

        if set(SHEET_TYPES.keys()) == set(DBTableRelated.TABLE_SPLITTER.keys()):
            print("Sheet types matches table splitter")
        else:
            raise Exception("Sheet types doesnt match table splitter")
        
        table_names = queries.get_table_names(schema_name=DATABASE_CONFIG["schema_name"], database_name=DATABASE_CONFIG["database"])
        TABLE_TYPES_FOR_ENUM_VALIDATION_LEAF_VALUES = sum(list(misc.extract_leaf_values_from_dict(DBTableRelated.TABLE_TYPES_FOR_ENUM_VALIDATION)), [])
        if set(table_names) != set(TABLE_TYPES_FOR_ENUM_VALIDATION_LEAF_VALUES):
            raise Exception("TABLE_TYPES_FOR_ENUM_VALIDATION needs to contain all tables from schema")
        else:
            print("TABLE_TYPES_FOR_ENUM_VALIDATION contains all tables from schema")
        
        TABLE_SPLITTER_VALUES = sum(DBTableRelated.TABLE_SPLITTER.values(), [])
        if set(table_names) != set(TABLE_SPLITTER_VALUES):
            raise Exception("TABLE_SPLITTER needs to contain all tables from schema")
        else:
            print("TABLE_SPLITTER contains all tables from schema")
            
        
    