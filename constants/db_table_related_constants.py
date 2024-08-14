from constants.db_connections import SQL_ALCH_CONFIG
from constants.db_names.names import db_names
from constants.misc_constants import SHEET_TYPES
from utils import queries, misc
import inspect

db_names.edna_robot_sample()



class DBTableRelated:
    '''
    Contains all constants that contain names of database tables
    '''
    
    TABLE_TYPES_FOR_ENUM_VALIDATION = {"ENVIRONMENTAL": {"SAMPLE": [db_names.field_sample(), 
                                                                    db_names.edna_robot_sample(), 
                                                                    db_names.edna_archive_sample(), 
                                                                    db_names.master_depth(), 
                                                                    db_names.cgg_animal_plant(), 
                                                                    db_names.cgg_sediment_water(), 
                                                                    db_names.age_depth_model(), 
                                                                    db_names.initials_translator()],
                                                         "LIBRARY": [db_names.flowcell(), 
                                                                     db_names.seq_sample_sheet(), 
                                                                     db_names.top_unknown_seq_barcodes(), 
                                                                     db_names.adna_wetlab_report(), 
                                                                     db_names.edna_wetlab_report()]
                                                         }
                                       }

    # TODO: Fix hardcoding of sheet labels
    # Load tables from schema and check that they are all here:
    TABLE_SPLITTER = {
                        'field_sample': [db_names.field_sample()],
                        'edna_archive_sample': [db_names.edna_archive_sample()],
                        'edna_robot_sample': [db_names.edna_robot_sample()],
                        'edna_wetlab_report': [db_names.edna_wetlab_report()],
                        'adna_wetlab_report': [db_names.adna_wetlab_report()],
                        'cgg_sediment_water': [db_names.cgg_sediment_water()],
                        'cgg_animal_plant': [db_names.cgg_animal_plant()],
                        'lane_barcode_html': [db_names.flowcell(), db_names.top_unknown_seq_barcodes()],
                        'seq_sample_sheet': [db_names.seq_sample_sheet()],
                        'master_depth': [db_names.master_depth()],
                        'age_depth_model': [db_names.age_depth_model()],
                        'initials_translator': [db_names.initials_translator()]
                    }

    DB_GENERATED_COLUMNS = {db_names.top_unknown_seq_barcodes(): ['uid']}
        

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
        
        table_names = queries.get_table_names(schema_name=SQL_ALCH_CONFIG["schema_name"], database_name=SQL_ALCH_CONFIG["database"])
        TABLE_TYPES_FOR_ENUM_VALIDATION_LEAF_VALUES = sum(list(misc.extract_leaf_values_from_dict(DBTableRelated.TABLE_TYPES_FOR_ENUM_VALIDATION)), [])
        if set(table_names) != set(TABLE_TYPES_FOR_ENUM_VALIDATION_LEAF_VALUES):
            raise Exception("TABLE_TYPES_FOR_ENUM_VALIDATION needs to contain all tables from schema")
        else:
            print("TABLE_TYPES_FOR_ENUM_VALIDATION contains all tables from schema")
        
        TABLE_SPLITTER_VALUES = sum(DBTableRelated.TABLE_SPLITTER.values(), [])
        # TABLE_SPLITTER_VALUES = [str(val) for val in TABLE_SPLITTER_VALUES]
        
 
       
        if set(table_names) != set(TABLE_SPLITTER_VALUES):
            raise Exception("TABLE_SPLITTER needs to contain all tables from schema")
        else:
            print("TABLE_SPLITTER contains all tables from schema")
            
        
    