from pprint import pprint
from constants.db_connections import SQL_ALCH_CONFIG, ENGINE
from constants.db_names.names import data
from constants.misc_constants import SHEET_TYPES
from utils import misc, queries
import inspect

data.edna_robot_sample()



class DBTableRelated:
    '''
    Contains all constants that contain names of database tables
    '''
    
    TABLE_TYPES_FOR_ENUM_VALIDATION = {"ENVIRONMENTAL": {"SAMPLE": [data.field_sample(), 
                                                                    data.edna_robot_sample(), 
                                                                    data.edna_archive_sample(), 
                                                                    data.master_depth(), 
                                                                    data.cgg_animal_plant(), 
                                                                    data.cgg_sediment_water(), 
                                                                    data.age_depth_model(), 
                                                                    data.initials_translator(),
                                                                    ],
                                                         "LIBRARY": [data.flowcell(), 
                                                                    #  data.seq_sample_sheet(), 
                                                                     data.top_unknown_seq_barcodes(), 
                                                                     data.adna_wetlab_report(), 
                                                                     data.edna_wetlab_report()]
                                                         
                                                         }
                                       }

    # TODO: Fix hardcoding of sheet labels
    # Load tables from schema and check that they are all here:
    TABLE_SPLITTER = {
                        'field_sample': [data.field_sample()],
                        'edna_archive_sample': [data.edna_archive_sample()],
                        'edna_robot_sample': [data.edna_robot_sample()],
                        'edna_wetlab_report': [data.edna_wetlab_report()],
                        'adna_wetlab_report': [data.adna_wetlab_report()],
                        'cgg_sediment_water': [data.cgg_sediment_water()],
                        'cgg_animal_plant': [data.cgg_animal_plant()],
                        'lane_barcode_html': [data.flowcell(), data.top_unknown_seq_barcodes()],
                        # 'seq_sample_sheet': [data.seq_sample_sheet()],
                        'master_depth': [data.master_depth()],
                        'age_depth_model': [data.age_depth_model()],
                        'initials_translator': [data.initials_translator()]
                    }
    
    UTIL_TABLES = {"MEGA": [
                            "outer_coalesced_mega_table_meta",
                            "outer_coalesced_mega_table_full",
                    ],
                    "QC": [
                        "plot_category",
                        "sample",
                        "plot_config",
                        "plot_data",
                        "report",
                        "report_meta",
                        "sample_data",
                        "sample_data_type"
                    ]}
    
    UTIL_TABLES_LEAFS = sum(list(misc.extract_leaf_values_from_dict(UTIL_TABLES)), [])
    
    # Keeps track of the parent IDs that tables depend on
    PARENTS = {
        data.edna_archive_sample(): { 
                data.edna_archive_sample.field_sample_id(): { 
                    data.field_sample(): [data.field_sample.field_sample_id()]
                    }
                },
        
        data.edna_robot_sample(): { \
                data.edna_robot_sample.archivesampleid(): { 
                    data.edna_archive_sample(): [data.edna_archive_sample.archivesampleid()]
                    }
                },
        
        data.edna_wetlab_report(): { 
                data.edna_wetlab_report.robot_sample_id(): { 
                    data.edna_robot_sample(): [data.edna_robot_sample.robot_sample_id()]
                    }
        },

        data.flowcell(): { 
                data.flowcell.fastq_file_id(): { 
                    data.edna_wetlab_report(): [data.edna_wetlab_report().fastq_file_id()]
        },
        
        # data.seq_sample_sheet(): { 
        #         data.seq_sample_sheet.fastq_file_id(): { 
        #             data.edna_wetlab_report(): [data.edna_wetlab_report().fastq_file_id()]
        #             }
        # },
        
        data.master_depth(): { 
                data.master_depth.master_field_sample_id(): { 
                    data.field_sample(): [data.field_sample.master_id_parent_sample_id()]
                    },
                data.master_depth.field_sample_id(): { 
                    data.field_sample(): [data.field_sample.field_sample_id()]
                    },
                data.master_depth.archive_sample_id(): { 
                    data.edna_archive_sample(): [data.edna_archive_sample.archivesampleid()]
                    }
                },
        
        data.age_depth_model(): { 
                data.age_depth_model.master_field_sample_id(): { 
                    data.field_sample(): [data.field_sample.master_id_parent_sample_id()]
                    }
                }
        }
    }

    DB_GENERATED_COLUMNS = {data.top_unknown_seq_barcodes(): ['uid'],
                            data.master_depth(): ['depth_id'],
                            data.age_depth_model(): ['depth_id'],
                            data.field_sample(): ['clean_id', 'field_sample_uuid'],
                            data.edna_wetlab_report(): ['wet_lab_comp_id']}

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
        
        table_names = set(queries.get_table_names(schema_name=SQL_ALCH_CONFIG["schema_name"], database_name=SQL_ALCH_CONFIG["database"], engine=ENGINE))
        TABLE_TYPES_FOR_ENUM_VALIDATION_LEAF_VALUES = sum(list(misc.extract_leaf_values_from_dict(DBTableRelated.TABLE_TYPES_FOR_ENUM_VALIDATION)), [])
        UTIL_TABLE_NAMES = set(sum(list(misc.extract_leaf_values_from_dict(DBTableRelated.UTIL_TABLES)), []))
        table_names = table_names - UTIL_TABLE_NAMES
        
        diff_ = set(TABLE_TYPES_FOR_ENUM_VALIDATION_LEAF_VALUES) ^ (set(table_names))

        if not len(diff_) == 0:
            raise Exception(f'''
                            TABLE_TYPES_FOR_ENUM_VALIDATION needs to contain all tables from schema.
                            Make sure to update either the UTIL_TABLES or the TABLE_TYPES_FOR_ENUM_VALIDATION.
                            Found the following discrepancies between the database and 
                            TABLE_TYPES_FOR_ENUM_VALIDATION: \n {diff_}''')
        else:
            print("TABLE_TYPES_FOR_ENUM_VALIDATION contains all tables from schema")
        
        TABLE_SPLITTER_VALUES = sum(DBTableRelated.TABLE_SPLITTER.values(), [])
        # TABLE_SPLITTER_VALUES = [str(val) for val in TABLE_SPLITTER_VALUES]
        
 
       
        if set(table_names) != set(TABLE_SPLITTER_VALUES):
            raise Exception("TABLE_SPLITTER needs to contain all tables from schema")
        else:
            print("TABLE_SPLITTER contains all tables from schema")
            
        
    