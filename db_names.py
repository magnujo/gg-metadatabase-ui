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
	def __init__(self, db_name, db_id) -> None:
		self.__db_name = db_name
		self.__db_id = db_id

	def __str__(self):
		return self.__db_name


	def get_id(self):
		return self.__db_id

	@classmethod
	def get_class_variables(cls):
		return {k: v for k, v in cls.__dict__.items() if not callable(v) and not k.startswith('__')}

	# @classmethod
	# def __str__(cls):
	# 	return cls.__name


class name_maps(NamedEntity):
	def __init__(self):
		super().__init__(db_name="name_maps", db_id=2)

	class column_names(NamedEntity):
		def __init__(self):
			super().__init__(db_name="column_names", db_id=20)

		# Columns:
		column_id = "column_id"
		column_name_db = "column_name_db"
		column_name_sheet = "column_name_sheet"
		table_id = "table_id"


	class table_names(NamedEntity):
		def __init__(self):
			super().__init__(db_name="table_names", db_id=19)

		# Columns:
		table_name = "table_name"
		table_id = "table_id"
		schema_id = "schema_id"


	class schema_names(NamedEntity):
		def __init__(self):
			super().__init__(db_name="schema_names", db_id=21)
  
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

   

def print_class_structure(schema_id):
	'''
	Prints the class structure above by scraping the database
	'''

	nm = name_maps()
	columns = f"{nm.column_names.column_id}, {nm.column_names.column_name_db}, cn.{nm.column_names.table_id}, tn.{nm.table_names.table_id}, {nm.table_names.table_name}, {nm.table_names.schema_id}"


	q = f'''
	select {columns} from "{nm}"."{nm.column_names()}" cn
	join "{nm}"."{nm.table_names()}" tn on cn."{nm.column_names.table_id}" = tn."{nm.table_names.table_id}"
	where "{nm.table_names.schema_id}" = '{schema_id}'
 	order by cn.{nm.column_names.table_id};

	'''
	res = queries.execute_query(q, PSY_CONN)
 
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

	tab = "    "
	for key in d:
		table_id = d[key]["id"]
		print(f"class {key}(NamedEntity):")
		print(f"{tab}def __init__(self):")
		print(f'{tab}{tab}super().__init__(db_name="{key}", db_id={table_id})')
		print()
		print(f"{tab}#  Columns:")
		for ele in d[key]["cols"]:

			var: str = re.sub(r'\(.*?\)', '', ele[0].lower()).strip()
			var = re.sub(r'[^a-z]', ' ', var).strip()
			var = var.replace(" ", "_").lower().strip("_")

			id = ele[1]

			print(f"{tab}{var} = lambda: get_column_name({id})")
		print()
  
class db_names:
	'''
	Helper class that gets column names from a mapper that maps column ids to names.
	The names are stored in variables that can be used in the code.
	The class (and therefore the app) expects column names in DB to be equal to column names in upload sheet template.'
	Usage example: To access a latitude column using the class simply do sheet_df[names.FieldSample.latitude] or db_df[names.FieldSample.latitude]
	'''

	class data(NamedEntity):
		def __init__(self) -> None:
			super().__init__(db_name=get_schema_name(1), db_id=1)

		class edna_robot_sample(NamedEntity):
			def __init__(self):
				super().__init__(db_name="edna_robot_sample", db_id=1)

			#  Columns:
			database_insert_datetime_utc = lambda: get_column_name(15)
			upload_uuid = lambda: get_column_name(16)
			subsampleid = lambda: get_column_name(1)
			rackname = lambda: get_column_name(2)
			rackid = lambda: get_column_name(3)
			positioninrack = lambda: get_column_name(4)
			mass = lambda: get_column_name(5)
			sampledby = lambda: get_column_name(6)
			samplingdate = lambda: get_column_name(7)
			remarkssubsampling = lambda: get_column_name(8)
			archivesampleid = lambda: get_column_name(9)
			submitter = lambda: get_column_name(10)
			submissiondate = lambda: get_column_name(11)
			remarkssubmission = lambda: get_column_name(12)
			database_insert_by = lambda: get_column_name(13)
			from_spreadsheet = lambda: get_column_name(14)

		class age_depth_model(NamedEntity):
			def __init__(self):
				super().__init__(db_name="age_depth_model", db_id=2)

			#  Columns:
			upload_uuid = lambda: get_column_name(24)
			median = lambda: get_column_name(26)
			depth = lambda: get_column_name(17)
			min = lambda: get_column_name(18)
			max = lambda: get_column_name(19)
			mean = lambda: get_column_name(20)
			database_insert_by = lambda: get_column_name(21)
			from_spreadsheet = lambda: get_column_name(22)
			database_insert_datetime_utc = lambda: get_column_name(23)
			master_field_sample_id = lambda: get_column_name(25)

		class master_depth(NamedEntity):
			def __init__(self):
				super().__init__(db_name="master_depth", db_id=3)

			#  Columns:
			database_insert_datetime_utc = lambda: get_column_name(33)
			upload_uuid = lambda: get_column_name(34)
			archive_sample_id = lambda: get_column_name(27)
			master_depth = lambda: get_column_name(28)
			field_sample_id = lambda: get_column_name(29)
			master_field_sample_id = lambda: get_column_name(30)
			database_insert_by = lambda: get_column_name(31)
			from_spreadsheet = lambda: get_column_name(32)

		class field_sample_types(NamedEntity):
			def __init__(self):
				super().__init__(db_name="field_sample_types", db_id=4)

			#  Columns:
			name = lambda: get_column_name(35)

		class cgg_animal_plant(NamedEntity):
			def __init__(self):
				super().__init__(db_name="cgg_animal_plant", db_id=5)

			#  Columns:
			stock_sample_left = lambda: get_column_name(39)
			cgg_id = lambda: get_column_name(36)
			museum_id_sample_id = lambda: get_column_name(37)
			lab_no = lambda: get_column_name(38)
			extraction = lambda: get_column_name(40)
			extraction_date = lambda: get_column_name(41)
			kind_of_library = lambda: get_column_name(42)
			library_date = lambda: get_column_name(43)
			intern_provider = lambda: get_column_name(44)
			type = lambda: get_column_name(45)
			class_ = lambda: get_column_name(46)
			order = lambda: get_column_name(47)
			genus = lambda: get_column_name(48)
			species = lambda: get_column_name(49)
			common_name = lambda: get_column_name(50)
			sex = lambda: get_column_name(51)
			age = lambda: get_column_name(52)
			geological_age = lambda: get_column_name(53)
			material_group = lambda: get_column_name(54)
			material_type = lambda: get_column_name(55)
			material_condition = lambda: get_column_name(56)
			site = lambda: get_column_name(57)
			site_info = lambda: get_column_name(58)
			city_town_location = lambda: get_column_name(59)
			state_province_region = lambda: get_column_name(60)
			country = lambda: get_column_name(61)
			continent = lambda: get_column_name(62)
			lat = lambda: get_column_name(63)
			lon = lambda: get_column_name(64)
			gps = lambda: get_column_name(65)
			sample_provider = lambda: get_column_name(66)
			museum_institution = lambda: get_column_name(67)
			contact_info = lambda: get_column_name(68)
			return_date = lambda: get_column_name(69)
			return_details = lambda: get_column_name(70)
			date_excavated = lambda: get_column_name(71)
			date_collected = lambda: get_column_name(72)
			date_recieved = lambda: get_column_name(73)
			date_returned = lambda: get_column_name(74)
			cites_permit_needed = lambda: get_column_name(75)
			cites_permit_obtained = lambda: get_column_name(76)
			sample_location = lambda: get_column_name(77)
			extraction_location = lambda: get_column_name(78)
			in_care_of = lambda: get_column_name(79)
			date_out = lambda: get_column_name(80)
			project_name = lambda: get_column_name(81)
			supervisor = lambda: get_column_name(82)
			analyses_history = lambda: get_column_name(83)
			genbank_ref = lambda: get_column_name(84)
			publications = lambda: get_column_name(85)
			references = lambda: get_column_name(86)
			notes = lambda: get_column_name(87)
			thawed_up = lambda: get_column_name(88)
			database_insert_by = lambda: get_column_name(89)
			from_spreadsheet = lambda: get_column_name(90)
			database_insert_datetime_utc = lambda: get_column_name(91)
			upload_uuid = lambda: get_column_name(92)

		class country_ocean(NamedEntity):
			def __init__(self):
				super().__init__(db_name="country_ocean", db_id=6)

			#  Columns:
			name = lambda: get_column_name(93)

		class field_sample_environment_types(NamedEntity):
			def __init__(self):
				super().__init__(db_name="field_sample_environment_types", db_id=7)

			#  Columns:
			name = lambda: get_column_name(94)

		class edna_wetlab_report(NamedEntity):
			def __init__(self):
				super().__init__(db_name="edna_wetlab_report", db_id=8)

			#  Columns:
			lysis_date = lambda: get_column_name(107)
			pcr_cycle = lambda: get_column_name(128)
			indexing_pcr_date = lambda: get_column_name(129)
			library_cleanup_date = lambda: get_column_name(130)
			library_qc_date = lambda: get_column_name(131)
			customer_attention_to_library_prep = lambda: get_column_name(132)
			tube_tag_submitted_to_seqc = lambda: get_column_name(133)
			dna_pooled = lambda: get_column_name(134)
			expected_sequencing_data = lambda: get_column_name(135)
			submitting_date = lambda: get_column_name(136)
			return_dna = lambda: get_column_name(137)
			return_library = lambda: get_column_name(138)
			return_pool = lambda: get_column_name(139)
			pool_to_seqc = lambda: get_column_name(140)
			project_done_date = lambda: get_column_name(141)
			database_insert_by = lambda: get_column_name(142)
			from_spreadsheet = lambda: get_column_name(143)
			database_insert_datetime_utc = lambda: get_column_name(144)
			fastq_file_id = lambda: get_column_name(145)
			upload_uuid = lambda: get_column_name(146)
			library_prep_method = lambda: get_column_name(147)
			customer_name = lambda: get_column_name(95)
			order_date = lambda: get_column_name(96)
			order_id = lambda: get_column_name(97)
			no = lambda: get_column_name(98)
			total_sample_quantity = lambda: get_column_name(99)
			robot_sample_rack_name = lambda: get_column_name(100)
			robot_sample_rack_barcode = lambda: get_column_name(101)
			robot_sample_rack_position = lambda: get_column_name(102)
			robot_sample_id = lambda: get_column_name(103)
			archive_sample_id = lambda: get_column_name(104)
			edna_lysate_plate_id = lambda: get_column_name(105)
			edna_lysate_position = lambda: get_column_name(106)
			edna_plate_id = lambda: get_column_name(108)
			edna_plate_position = lambda: get_column_name(109)
			edna_id = lambda: get_column_name(110)
			edna_concentration = lambda: get_column_name(111)
			cleanup_date = lambda: get_column_name(112)
			customer_attention_to_extraction = lambda: get_column_name(113)
			library_plate_id = lambda: get_column_name(114)
			library_plate_barcode = lambda: get_column_name(115)
			library_plate_position = lambda: get_column_name(116)
			library_id = lambda: get_column_name(117)
			library_concentration = lambda: get_column_name(118)
			library_peak_size = lambda: get_column_name(119)
			library_leftover_volume = lambda: get_column_name(120)
			library_qc_result = lambda: get_column_name(121)
			library_start_date = lambda: get_column_name(122)
			ct = lambda: get_column_name(123)
			qpcr_date = lambda: get_column_name(124)
			idt_index_no = lambda: get_column_name(125)
			i__bases_in_adapter = lambda: get_column_name(126)
			i__bases_in_adapter = lambda: get_column_name(127)

		class flowcell(NamedEntity):
			def __init__(self):
				super().__init__(db_name="flowcell", db_id=9)

			#  Columns:
			yield_ = lambda: get_column_name(163)
			clusters = lambda: get_column_name(162)
			clusters = lambda: get_column_name(161)
			database_insert_by = lambda: get_column_name(164)
			from_spreadsheet = lambda: get_column_name(165)
			sample = lambda: get_column_name(150)
			barcode_sequence = lambda: get_column_name(151)
			pf_clusters = lambda: get_column_name(152)
			of_the_lane = lambda: get_column_name(153)
			perfect_barcode = lambda: get_column_name(154)
			one_mismatch_barcode = lambda: get_column_name(155)
			yield_ = lambda: get_column_name(156)
			pf_clusters = lambda: get_column_name(157)
			q___bases = lambda: get_column_name(158)
			mean_quality_score = lambda: get_column_name(159)
			flowcell_id = lambda: get_column_name(160)
			upload_uuid = lambda: get_column_name(167)
			lane = lambda: get_column_name(148)
			project = lambda: get_column_name(149)
			database_insert_datetime_utc = lambda: get_column_name(166)

		class cgg_sediment_water(NamedEntity):
			def __init__(self):
				super().__init__(db_name="cgg_sediment_water", db_id=10)

			#  Columns:
			kind_of_library = lambda: get_column_name(174)
			cgg_id = lambda: get_column_name(168)
			museum_id_sample_id = lambda: get_column_name(169)
			lab_no = lambda: get_column_name(170)
			stock_sample_left = lambda: get_column_name(171)
			extraction = lambda: get_column_name(172)
			extraction_date = lambda: get_column_name(173)
			library_date = lambda: get_column_name(175)
			intern_provider = lambda: get_column_name(176)
			sample_type = lambda: get_column_name(177)
			depth = lambda: get_column_name(178)
			height__asl = lambda: get_column_name(179)
			material_type = lambda: get_column_name(180)
			sampled_as = lambda: get_column_name(181)
			sample_size = lambda: get_column_name(182)
			depositional_environment = lambda: get_column_name(183)
			age = lambda: get_column_name(184)
			geological_age = lambda: get_column_name(185)
			site = lambda: get_column_name(186)
			site_info = lambda: get_column_name(187)
			city_town_location = lambda: get_column_name(188)
			state_province_region = lambda: get_column_name(189)
			country = lambda: get_column_name(190)
			continent = lambda: get_column_name(191)
			lat = lambda: get_column_name(192)
			lon = lambda: get_column_name(193)
			gps = lambda: get_column_name(194)
			sample_provider = lambda: get_column_name(195)
			museum_institution = lambda: get_column_name(196)
			contact_info = lambda: get_column_name(197)
			date_collected = lambda: get_column_name(198)
			date_recieved = lambda: get_column_name(199)
			date_returned = lambda: get_column_name(200)
			sample_location = lambda: get_column_name(201)
			extraction_location = lambda: get_column_name(202)
			in_care_of = lambda: get_column_name(203)
			date_out = lambda: get_column_name(204)
			project_name = lambda: get_column_name(205)
			supervisor = lambda: get_column_name(206)
			analyses_history = lambda: get_column_name(207)
			genbank_ref = lambda: get_column_name(208)
			publications = lambda: get_column_name(209)
			references = lambda: get_column_name(210)
			notes = lambda: get_column_name(211)
			thawed_up = lambda: get_column_name(212)
			database_insert_by = lambda: get_column_name(213)
			from_spreadsheet = lambda: get_column_name(214)
			database_insert_datetime_utc = lambda: get_column_name(215)

		class adna_wetlab_report(NamedEntity):
			def __init__(self):
				super().__init__(db_name="adna_wetlab_report", db_id=11)

			#  Columns:
			library_id = lambda: get_column_name(226)
			library_plate_id = lambda: get_column_name(224)
			library_plate_position = lambda: get_column_name(225)
			library_concentration = lambda: get_column_name(227)
			library_volume = lambda: get_column_name(228)
			library_qc_result = lambda: get_column_name(229)
			library_start_date = lambda: get_column_name(230)
			ct = lambda: get_column_name(231)
			qpcr_date = lambda: get_column_name(232)
			idt_index_no = lambda: get_column_name(233)
			i__bases_in_adapter = lambda: get_column_name(234)
			i__bases_in_adapter = lambda: get_column_name(235)
			pcr_cycle = lambda: get_column_name(236)
			indexing_pcr_date = lambda: get_column_name(237)
			library_cleanup_date = lambda: get_column_name(238)
			library_qc_date = lambda: get_column_name(239)
			tube_tag_submitted_to_seqc = lambda: get_column_name(240)
			dna_pooled = lambda: get_column_name(241)
			expected_sequencing_data = lambda: get_column_name(242)
			submitting_date = lambda: get_column_name(243)
			return_library = lambda: get_column_name(244)
			pool_to_seqc = lambda: get_column_name(245)
			project_done_date = lambda: get_column_name(246)
			database_insert_by = lambda: get_column_name(247)
			from_spreadsheet = lambda: get_column_name(248)
			database_insert_datetime_utc = lambda: get_column_name(249)
			sequencing_file_id = lambda: get_column_name(250)
			upload_uuid = lambda: get_column_name(251)
			customer_name = lambda: get_column_name(216)
			order_date = lambda: get_column_name(217)
			order_id = lambda: get_column_name(218)
			sample_number = lambda: get_column_name(219)
			adna_plate_name = lambda: get_column_name(220)
			no = lambda: get_column_name(221)
			sample_position = lambda: get_column_name(222)
			adna_sample_name = lambda: get_column_name(223)

		class field_sample_material_type(NamedEntity):
			def __init__(self):
				super().__init__(db_name="field_sample_material_type", db_id=12)

			#  Columns:
			name = lambda: get_column_name(252)

		class field_sample_setting_types(NamedEntity):
			def __init__(self):
				super().__init__(db_name="field_sample_setting_types", db_id=13)

			#  Columns:
			name = lambda: get_column_name(253)

		class edna_archive_sample(NamedEntity):
			def __init__(self):
				super().__init__(db_name="edna_archive_sample", db_id=14)

			#  Columns:
			depthsampledcaltape = lambda: get_column_name(259)
			depthorderedcaltape = lambda: get_column_name(260)
			organiccontent = lambda: get_column_name(261)
			surfaceexposed = lambda: get_column_name(262)
			submitter = lambda: get_column_name(266)
			submissiondate = lambda: get_column_name(267)
			remarkssubmission = lambda: get_column_name(268)
			database_insert_by = lambda: get_column_name(269)
			from_spreadsheet = lambda: get_column_name(270)
			database_insert_datetime_utc = lambda: get_column_name(271)
			upload_uuid = lambda: get_column_name(272)
			remarksarchivesampling = lambda: get_column_name(263)
			sampledby = lambda: get_column_name(264)
			samplingdate = lambda: get_column_name(265)
			archivesampleid = lambda: get_column_name(254)
			positioninrack = lambda: get_column_name(255)
			rackid = lambda: get_column_name(257)
			rackname = lambda: get_column_name(256)
			bulksampleid = lambda: get_column_name(258)

		class initials_translator(NamedEntity):
			def __init__(self):
				super().__init__(db_name="initials_translator", db_id=15)

			#  Columns:
			database_insert_datetime_utc = lambda: get_column_name(277)
			initials = lambda: get_column_name(273)
			upload_uuid = lambda: get_column_name(278)
			full_name = lambda: get_column_name(274)
			database_insert_by = lambda: get_column_name(275)
			from_spreadsheet = lambda: get_column_name(276)

		class seq_sample_sheet(NamedEntity):
			def __init__(self):
				super().__init__(db_name="seq_sample_sheet", db_id=16)

			#  Columns:
			database_insert_datetime_utc = lambda: get_column_name(301)
			sample_id = lambda: get_column_name(279)
			sample_name = lambda: get_column_name(280)
			sample_plate = lambda: get_column_name(281)
			sample_well = lambda: get_column_name(282)
			i__index_id = lambda: get_column_name(283)
			index = lambda: get_column_name(284)
			i__index_id = lambda: get_column_name(285)
			index = lambda: get_column_name(286)
			sample_project = lambda: get_column_name(287)
			iemfileversion = lambda: get_column_name(288)
			date = lambda: get_column_name(289)
			workflow = lambda: get_column_name(290)
			application = lambda: get_column_name(291)
			instrument_type = lambda: get_column_name(292)
			assay = lambda: get_column_name(293)
			index_adapters = lambda: get_column_name(294)
			description = lambda: get_column_name(295)
			chemistry = lambda: get_column_name(296)
			reads = lambda: get_column_name(297)
			reads = lambda: get_column_name(298)
			database_insert_by = lambda: get_column_name(299)
			from_spreadsheet = lambda: get_column_name(300)
			upload_uuid = lambda: get_column_name(302)

		class field_sample(NamedEntity):
			def __init__(self):
				super().__init__(db_name="field_sample", db_id=17)

			#  Columns:
			pi = lambda: get_column_name(338)
			country_ocean = lambda: get_column_name(304)
			site_name = lambda: get_column_name(305)
			latitude = lambda: get_column_name(306)
			longitude = lambda: get_column_name(307)
			sample_date = lambda: get_column_name(308)
			unique_sample_id = lambda: get_column_name(303)
			other_relevant_information = lambda: get_column_name(337)
			sample_provider = lambda: get_column_name(339)
			site_grid_elev = lambda: get_column_name(340)
			site_grid_latitude = lambda: get_column_name(341)
			site_grid_longitude = lambda: get_column_name(342)
			master_id_parent_sample_id = lambda: get_column_name(343)
			field_label = lambda: get_column_name(344)
			sample_type_in_storage_at_gm = lambda: get_column_name(345)
			permit_for_dna_analysis = lambda: get_column_name(346)
			sample_provider = lambda: get_column_name(309)
			running_project_title = lambda: get_column_name(310)
			sampling_depth = lambda: get_column_name(311)
			sampling_interval___to = lambda: get_column_name(312)
			water_depth = lambda: get_column_name(313)
			sample_type = lambda: get_column_name(314)
			sample_environment = lambda: get_column_name(315)
			sample_context = lambda: get_column_name(316)
			age_estimate___from = lambda: get_column_name(317)
			elevation = lambda: get_column_name(318)
			sample_storage_address = lambda: get_column_name(319)
			sample_storage_setting = lambda: get_column_name(320)
			sample_storage_location = lambda: get_column_name(321)
			miscellaneous_sample_measurement_or_observation = lambda: get_column_name(322)
			miscellaneous_environmental_measurement_or_observation = lambda: get_column_name(323)
			link_to_images = lambda: get_column_name(324)
			link_to_other_relevant_information = lambda: get_column_name(325)
			comments = lambda: get_column_name(326)
			database_insert_by = lambda: get_column_name(327)
			from_spreadsheet = lambda: get_column_name(328)
			database_insert_datetime_utc = lambda: get_column_name(329)
			upload_uuid = lambda: get_column_name(330)
			sampling_interval___from = lambda: get_column_name(331)
			age_estimate___to = lambda: get_column_name(332)
			sample_material = lambda: get_column_name(333)
			alias = lambda: get_column_name(334)
			cultural_affiliation = lambda: get_column_name(335)
			museum_institution = lambda: get_column_name(336)

		class top_unknown_seq_barcodes(NamedEntity):
			def __init__(self):
				super().__init__(db_name="top_unknown_seq_barcodes", db_id=18)

			#  Columns:
			database_insert_by = lambda: get_column_name(351)
			uid = lambda: get_column_name(354)
			flowcell_id = lambda: get_column_name(350)
			from_spreadsheet = lambda: get_column_name(352)
			upload_uuid = lambda: get_column_name(355)
			lane = lambda: get_column_name(347)
			count = lambda: get_column_name(348)
			sequence = lambda: get_column_name(349)
			database_insert_datetime_utc = lambda: get_column_name(353)