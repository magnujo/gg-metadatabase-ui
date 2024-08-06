'''
Helper file to maintain db column names. 

If you want to change the naming of columns in the code simply refactor the variable names in this file.

If you want to change names in the database you can only do this if you also change the map tables in the database,
that map from code name to database name.
These are the maps that make sure that the code doesn't break if a column is renamed.

To make name callable without parentheses use a meta class like this:

# class MetaClass(type):
#      def __str__(cls):
#         return cls.name


'''
import re
import pandas as pd
from utils import queries
from constants.misc_constants import PSY_CONN

    

class NamedEntity():
    def __str__(self):
        return self.name
        
    @classmethod
    def get_class_variables(cls):
        return {k: v for k, v in cls.__dict__.items() if not callable(v) and not k.startswith('__')}
    
    @classmethod
    def __str__(cls):
        return cls.name
    
                
class name_maps(NamedEntity):
    id = 2
    name = "name_maps"  # This has to be hard coded and cannot be retrieved dynamically because the name would be inside it self, which would result in an infinite loop.

    class column_names(NamedEntity):   
        id = 20
        name = "column_names"
        # name = get_table_name(id)
        
        column_id = "column_id"
        column_name_db = "column_name_db"
        column_name_sheet = "column_name_sheet"
        table_id = "table_id"
        
        
    class table_names(NamedEntity):
        
        
        id = 19
        name = "table_names"
        
        # table_name = Column(358)
        # Columns:
        table_name = "table_name"
        table_id = "table_id"
        schema_id = "schema_id"
    
        
    class schema_names(NamedEntity):
        id = 21
        name = "schema_names"
        
        # Columns:
        schema_name = "schema_name"
        schema_id = "schema_id"
        

def get_schema_name(schema_id):
        
        schema_name = name_maps()
        table_name = schema_name.schema_names()
        select_col = table_name.schema_name
        filter_col = table_name.schema_id
        
        
        query = f'''SELECT "{select_col}" FROM "{schema_name}"."{table_name}" WHERE "{filter_col}" = '%s' '''
        
        
        result = queries.execute_query(query, PSY_CONN, params=(schema_id,))
        
        if len(result) != 1:
            raise Exception("Admin error: Length of result not as expected")

        if len(result[0]) != 1:
            raise Exception("Admin error: Length of result not as expected")
        
    
        return str(result[0][0])
    


def get_table_name(table_id):
    
        schema = name_maps()
        table = schema.table_names()
        select_col = table.table_name
        filter_col = table.table_id
        
        query = f'''SELECT "{select_col}" FROM "{schema}"."{table}" WHERE "{filter_col}" = '%s' '''

        result = queries.execute_query(query, PSY_CONN, params=(table_id,))
        
        if len(result) != 1:
            raise Exception("Admin error: Length of result not as expected")

        if len(result[0]) != 1:
            raise Exception("Admin error: Length of result not as expected")
        
        
        return str(result[0][0])
        

def get_column_name(column_id):
    
        schema = name_maps()
        table = schema.column_names()
        select_col = table.column_name_db
        filter_col = table.column_id
        
        query = f'''SELECT "{select_col}" FROM "{schema}"."{table}" WHERE "{filter_col}" = %s '''

        result = queries.execute_query(query, PSY_CONN, params=(column_id,))
        
        if len(result) != 1:
            raise Exception("Admin error: Length of result not as expected")

        if len(result[0]) != 1:
            raise Exception("Admin error: Length of result not as expected")
        
        return str(result[0][0])

class db_names:
    '''
        Helper class that gets column names from a mapper that maps column ids to names.
        The names are stored in variables that can be used in the code.
        The class (and therefore the app) expects column names in DB to be equal to column names in upload sheet template.'
        Usage example: To access a latitude column using the class simply do sheet_df[names.FieldSample.latitude] or db_df[names.FieldSample.latitude]
    ''' 
    
    class data(NamedEntity):
        id = 1
        name = get_schema_name(id)
        
        class edna_robot_sample(NamedEntity):
            id = 1
            name = get_table_name(id)

            #  Columns:
            subsampleid = get_column_name(1)
            rackname = get_column_name(2)
            rackid = get_column_name(3)
            positioninrack = get_column_name(4)
            mass = get_column_name(5)
            sampledby = get_column_name(6)
            samplingdate = get_column_name(7)
            remarkssubsampling = get_column_name(8)
            archivesampleid = get_column_name(9)
            submitter = get_column_name(10)
            submissiondate = get_column_name(11)
            remarkssubmission = get_column_name(12)
            database_insert_by = get_column_name(13)
            from_spreadsheet = get_column_name(14)
            database_insert_datetime_utc = get_column_name(15)
            upload_uuid = get_column_name(16)

        class age_depth_model(NamedEntity):
                id = 2
                name = get_table_name(id)

                #  Columns:
                depth = get_column_name(17)
                min = get_column_name(18)
                max = get_column_name(19)
                mean = get_column_name(20)
                database_insert_by = get_column_name(21)
                from_spreadsheet = get_column_name(22)
                database_insert_datetime_utc = get_column_name(23)
                upload_uuid = get_column_name(24)
                master_field_sample_id = get_column_name(25)
                median = get_column_name(26)

        class master_depth(NamedEntity):
                id = 3
                name = get_table_name(id)

                #  Columns:
                archive_sample_id = get_column_name(27)
                master_depth = get_column_name(28)
                field_sample_id = get_column_name(29)
                master_field_sample_id = get_column_name(30)
                database_insert_by = get_column_name(31)
                from_spreadsheet = get_column_name(32)
                database_insert_datetime_utc = get_column_name(33)
                upload_uuid = get_column_name(34)

        class field_sample_types(NamedEntity):
                id = 4
                name = get_table_name(id)

                #  Columns:
                name = get_column_name(35)

        class cgg_animal_plant(NamedEntity):
                id = 5
                name = get_table_name(id)

                #  Columns:
                cgg_id = get_column_name(36)
                museum_id_sample_id = get_column_name(37)
                lab_no = get_column_name(38)
                stock_sample_left = get_column_name(39)
                extraction = get_column_name(40)
                extraction_date = get_column_name(41)
                kind_of_library = get_column_name(42)
                library_date = get_column_name(43)
                intern_provider = get_column_name(44)
                type = get_column_name(45)
                class_ = get_column_name(46)
                order = get_column_name(47)
                genus = get_column_name(48)
                species = get_column_name(49)
                common_name = get_column_name(50)
                sex = get_column_name(51)
                age = get_column_name(52)
                geological_age = get_column_name(53)
                material_group = get_column_name(54)
                material_type = get_column_name(55)
                material_condition = get_column_name(56)
                site = get_column_name(57)
                site_info = get_column_name(58)
                city_town_location = get_column_name(59)
                state_province_region = get_column_name(60)
                country = get_column_name(61)
                continent = get_column_name(62)
                lat = get_column_name(63)
                lon = get_column_name(64)
                gps = get_column_name(65)
                sample_provider = get_column_name(66)
                museum_institution = get_column_name(67)
                contact_info = get_column_name(68)
                return_date = get_column_name(69)
                return_details = get_column_name(70)
                date_excavated = get_column_name(71)
                date_collected = get_column_name(72)
                date_recieved = get_column_name(73)
                date_returned = get_column_name(74)
                cites_permit_needed = get_column_name(75)
                cites_permit_obtained = get_column_name(76)
                sample_location = get_column_name(77)
                extraction_location = get_column_name(78)
                in_care_of = get_column_name(79)
                date_out = get_column_name(80)
                project_name = get_column_name(81)
                supervisor = get_column_name(82)
                analyses_history = get_column_name(83)
                genbank_ref = get_column_name(84)
                publications = get_column_name(85)
                references = get_column_name(86)
                notes = get_column_name(87)
                thawed_up = get_column_name(88)
                database_insert_by = get_column_name(89)
                from_spreadsheet = get_column_name(90)
                database_insert_datetime_utc = get_column_name(91)
                upload_uuid = get_column_name(92)

        class country_ocean(NamedEntity):
                id = 6
                name = get_table_name(id)

                #  Columns:
                name = get_column_name(93)

        class field_sample_environment_types(NamedEntity):
                id = 7
                name = get_table_name(id)

                #  Columns:
                name = get_column_name(94)

        class edna_wetlab_report(NamedEntity):
                id = 8
                name = get_table_name(id)

                #  Columns:
                customer_name = get_column_name(95)
                order_date = get_column_name(96)
                order_id = get_column_name(97)
                no = get_column_name(98)
                total_sample_quantity = get_column_name(99)
                robot_sample_rack_name = get_column_name(100)
                robot_sample_rack_barcode = get_column_name(101)
                robot_sample_rack_position = get_column_name(102)
                robot_sample_id = get_column_name(103)
                archive_sample_id = get_column_name(104)
                edna_lysate_plate_id = get_column_name(105)
                edna_lysate_position = get_column_name(106)
                lysis_date = get_column_name(107)
                edna_plate_id = get_column_name(108)
                edna_plate_position = get_column_name(109)
                edna_id = get_column_name(110)
                edna_concentration = get_column_name(111)
                cleanup_date = get_column_name(112)
                customer_attention_to_extraction = get_column_name(113)
                library_plate_id = get_column_name(114)
                library_plate_barcode = get_column_name(115)
                library_plate_position = get_column_name(116)
                library_id = get_column_name(117)
                library_concentration = get_column_name(118)
                library_peak_size = get_column_name(119)
                library_leftover_volume = get_column_name(120)
                library_qc_result = get_column_name(121)
                library_start_date = get_column_name(122)
                ct = get_column_name(123)
                qpcr_date = get_column_name(124)
                idt_index_no = get_column_name(125)
                i__bases_in_adapter = get_column_name(126)
                i__bases_in_adapter = get_column_name(127)
                pcr_cycle = get_column_name(128)
                indexing_pcr_date = get_column_name(129)
                library_cleanup_date = get_column_name(130)
                library_qc_date = get_column_name(131)
                customer_attention_to_library_prep = get_column_name(132)
                tube_tag_submitted_to_seqc = get_column_name(133)
                dna_pooled = get_column_name(134)
                expected_sequencing_data = get_column_name(135)
                submitting_date = get_column_name(136)
                return_dna = get_column_name(137)
                return_library = get_column_name(138)
                return_pool = get_column_name(139)
                pool_to_seqc = get_column_name(140)
                project_done_date = get_column_name(141)
                database_insert_by = get_column_name(142)
                from_spreadsheet = get_column_name(143)
                database_insert_datetime_utc = get_column_name(144)
                fastq_file_id = get_column_name(145)
                upload_uuid = get_column_name(146)
                library_prep_method = get_column_name(147)

        class flowcell(NamedEntity):
                id = 9
                name = get_table_name(id)

                #  Columns:
                lane = get_column_name(148)
                project = get_column_name(149)
                sample = get_column_name(150)
                barcode_sequence = get_column_name(151)
                pf_clusters = get_column_name(152)
                of_the_lane = get_column_name(153)
                perfect_barcode = get_column_name(154)
                one_mismatch_barcode = get_column_name(155)
                yield_ = get_column_name(156)
                pf_clusters = get_column_name(157)
                q_bases = get_column_name(158)
                mean_quality_score = get_column_name(159)
                flowcell_id = get_column_name(160)
                clusters = get_column_name(161)
                clusters = get_column_name(162)
                yield_2 = get_column_name(163)
                database_insert_by = get_column_name(164)
                from_spreadsheet = get_column_name(165)
                database_insert_datetime_utc = get_column_name(166)
                upload_uuid = get_column_name(167)

        class cgg_sediment_water(NamedEntity):
                id = 10
                name = get_table_name(id)

                #  Columns:
                cgg_id = get_column_name(168)
                museum_id_sample_id = get_column_name(169)
                lab_no = get_column_name(170)
                stock_sample_left = get_column_name(171)
                extraction = get_column_name(172)
                extraction_date = get_column_name(173)
                kind_of_library = get_column_name(174)
                library_date = get_column_name(175)
                intern_provider = get_column_name(176)
                sample_type = get_column_name(177)
                depth = get_column_name(178)
                height_asl = get_column_name(179)
                material_type = get_column_name(180)
                sampled_as = get_column_name(181)
                sample_size = get_column_name(182)
                depositional_environment = get_column_name(183)
                age = get_column_name(184)
                geological_age = get_column_name(185)
                site = get_column_name(186)
                site_info = get_column_name(187)
                city_town_location = get_column_name(188)
                state_province_region = get_column_name(189)
                country = get_column_name(190)
                continent = get_column_name(191)
                lat = get_column_name(192)
                lon = get_column_name(193)
                gps = get_column_name(194)
                sample_provider = get_column_name(195)
                museum_institution = get_column_name(196)
                contact_info = get_column_name(197)
                date_collected = get_column_name(198)
                date_recieved = get_column_name(199)
                date_returned = get_column_name(200)
                sample_location = get_column_name(201)
                extraction_location = get_column_name(202)
                in_care_of = get_column_name(203)
                date_out = get_column_name(204)
                project_name = get_column_name(205)
                supervisor = get_column_name(206)
                analyses_history = get_column_name(207)
                genbank_ref = get_column_name(208)
                publications = get_column_name(209)
                references = get_column_name(210)
                notes = get_column_name(211)
                thawed_up = get_column_name(212)
                database_insert_by = get_column_name(213)
                from_spreadsheet = get_column_name(214)
                database_insert_datetime_utc = get_column_name(215)

        class adna_wetlab_report(NamedEntity):
                id = 11
                name = get_table_name(id)

                #  Columns:
                customer_name = get_column_name(216)
                order_date = get_column_name(217)
                order_id = get_column_name(218)
                sample_number = get_column_name(219)
                adna_plate_name = get_column_name(220)
                no = get_column_name(221)
                sample_position = get_column_name(222)
                adna_sample_name = get_column_name(223)
                library_plate_id = get_column_name(224)
                library_plate_position = get_column_name(225)
                library_id = get_column_name(226)
                library_concentration = get_column_name(227)
                library_volume = get_column_name(228)
                library_qc_result = get_column_name(229)
                library_start_date = get_column_name(230)
                ct = get_column_name(231)
                qpcr_date = get_column_name(232)
                idt_index_no = get_column_name(233)
                i__bases_in_adapter = get_column_name(234)
                i__bases_in_adapter = get_column_name(235)
                pcr_cycle = get_column_name(236)
                indexing_pcr_date = get_column_name(237)
                library_cleanup_date = get_column_name(238)
                library_qc_date = get_column_name(239)
                tube_tag_submitted_to_seqc = get_column_name(240)
                dna_pooled = get_column_name(241)
                expected_sequencing_data = get_column_name(242)
                submitting_date = get_column_name(243)
                return_library = get_column_name(244)
                pool_to_seqc = get_column_name(245)
                project_done_date = get_column_name(246)
                database_insert_by = get_column_name(247)
                from_spreadsheet = get_column_name(248)
                database_insert_datetime_utc = get_column_name(249)
                sequencing_file_id = get_column_name(250)
                upload_uuid = get_column_name(251)

        class field_sample_material_type(NamedEntity):
                id = 12
                name = get_table_name(id)

                #  Columns:
                name = get_column_name(252)

        class field_sample_setting_types(NamedEntity):
                id = 13
                name = get_table_name(id)

                #  Columns:
                name = get_column_name(253)

        class edna_archive_sample(NamedEntity):
                id = 14
                name = get_table_name(id)

                #  Columns:
                archivesampleid = get_column_name(254)
                positioninrack = get_column_name(255)
                rackname = get_column_name(256)
                rackid = get_column_name(257)
                bulksampleid = get_column_name(258)
                depthsampledcaltape = get_column_name(259)
                depthorderedcaltape = get_column_name(260)
                organiccontent = get_column_name(261)
                surfaceexposed = get_column_name(262)
                remarksarchivesampling = get_column_name(263)
                sampledby = get_column_name(264)
                samplingdate = get_column_name(265)
                submitter = get_column_name(266)
                submissiondate = get_column_name(267)
                remarkssubmission = get_column_name(268)
                database_insert_by = get_column_name(269)
                from_spreadsheet = get_column_name(270)
                database_insert_datetime_utc = get_column_name(271)
                upload_uuid = get_column_name(272)

        class initials_translator(NamedEntity):
                id = 15
                name = get_table_name(id)

                #  Columns:
                initials = get_column_name(273)
                full_name = get_column_name(274)
                database_insert_by = get_column_name(275)
                from_spreadsheet = get_column_name(276)
                database_insert_datetime_utc = get_column_name(277)
                upload_uuid = get_column_name(278)

        class seq_sample_sheet(NamedEntity):
                id = 16
                name = get_table_name(id)

                #  Columns:
                sample_id = get_column_name(279)
                sample_name = get_column_name(280)
                sample_plate = get_column_name(281)
                sample_well = get_column_name(282)
                i__index_id = get_column_name(283)
                index = get_column_name(284)
                i__index_id = get_column_name(285)
                index = get_column_name(286)
                sample_project = get_column_name(287)
                iemfileversion = get_column_name(288)
                date = get_column_name(289)
                workflow = get_column_name(290)
                application = get_column_name(291)
                instrument_type = get_column_name(292)
                assay = get_column_name(293)
                index_adapters = get_column_name(294)
                description = get_column_name(295)
                chemistry = get_column_name(296)
                reads = get_column_name(297)
                reads = get_column_name(298)
                database_insert_by = get_column_name(299)
                from_spreadsheet = get_column_name(300)
                database_insert_datetime_utc = get_column_name(301)
                upload_uuid = get_column_name(302)

        class field_sample(NamedEntity):
                id = 17
                name = get_table_name(id)

                #  Columns:
                unique_sample_id = get_column_name(303)
                country_ocean = get_column_name(304)
                site_name = get_column_name(305)
                latitude = get_column_name(306)
                longitude = get_column_name(307)
                sample_date = get_column_name(308)
                sample_provider = get_column_name(309)
                running_project_title = get_column_name(310)
                sampling_depth = get_column_name(311)
                sampling_interval_to = get_column_name(312)
                water_depth = get_column_name(313)
                sample_type = get_column_name(314)
                sample_environment = get_column_name(315)
                sample_context = get_column_name(316)
                age_estimate_from = get_column_name(317)
                elevation = get_column_name(318)
                sample_storage_address = get_column_name(319)
                sample_storage_setting = get_column_name(320)
                sample_storage_location = get_column_name(321)
                miscellaneous_sample_measurement_or_observation = get_column_name(322)
                miscellaneous_environmental_measurement_or_observation = get_column_name(323)
                link_to_images = get_column_name(324)
                link_to_other_relevant_information = get_column_name(325)
                comments = get_column_name(326)
                database_insert_by = get_column_name(327)
                from_spreadsheet = get_column_name(328)
                database_insert_datetime_utc = get_column_name(329)
                upload_uuid = get_column_name(330)
                sampling_interval_from = get_column_name(331)
                age_estimate_to = get_column_name(332)
                sample_material = get_column_name(333)
                alias = get_column_name(334)
                cultural_affiliation = get_column_name(335)
                museum_institution = get_column_name(336)
                other_relevant_information = get_column_name(337)
                principal_investigator = get_column_name(338)
                sample_provider = get_column_name(339)
                site_grid_elev = get_column_name(340)
                site_grid_latitude = get_column_name(341)
                site_grid_longitude = get_column_name(342)
                master_id_parent_sample_id = get_column_name(343)
                field_label = get_column_name(344)
                sample_type_in_storage_at_gm = get_column_name(345)
                permit_for_dna_analysis = get_column_name(346)

        class top_unknown_seq_barcodes(NamedEntity):
                id = 18
                name = get_table_name(id)

                #  Columns:
                lane = get_column_name(347)
                count = get_column_name(348)
                sequence = get_column_name(349)
                flowcell_id = get_column_name(350)
                database_insert_by = get_column_name(351)
                from_spreadsheet = get_column_name(352)
                database_insert_datetime_utc = get_column_name(353)
                uid = get_column_name(354)
                upload_uuid = get_column_name(355)

        class schema_names(NamedEntity):
                id = 21
                name = get_table_name(id)

                #  Columns:
                schema_name = get_column_name(356)
                schema_id = get_column_name(357)

        class table_names(NamedEntity):
                id = 19
                name = get_table_name(id)

                #  Columns:
                table_name = get_column_name(358)
                table_id = get_column_name(359)
                schema_id = get_column_name(360)

        class column_names(NamedEntity):
                id = 20
                name = get_table_name(id)

                #  Columns:
                column_id = get_column_name(361)
                column_name = get_column_name(362)
                table_id = get_column_name(363)
            

def print_class_structure():
    '''
    Prints the class structure above by scraping the database 
    '''

    q = '''
    select * from name_maps.column_names cn 
    join name_maps.table_names tn on cn.table_id = tn.table_id ;

    '''
    res = queries.execute_query(q)

    d = {}

    for ele in res:
        
        col_id = ele[0]
        col_name = ele[1]
        table_id = ele[2]
        table_name = ele[4]
        schema_id = ele[5]
        
        if table_name not in d:
            d[table_name] = {"id": table_id, "cols": []}
        
        d[table_name]["cols"].append((col_name, col_id))


    for key in d:
        table_id = d[key]["id"]
        print(f"class {key}(NamedEntity):")
        print(f"\tid = {table_id}")
        print(f"\tname = get_table_name(id)")
        print()
        print("\t#  Columns:")
        for ele in d[key]["cols"]:
            
            var: str = re.sub(r'\(.*?\)', '', ele[0].lower()).strip()
            var = re.sub(r'[^a-z]', ' ', var).strip()
            var = var.replace(" ", "_").lower().strip("_")

            id = ele[1]
        
            print(f"\t{var} = get_column_name({id})")
    print()
