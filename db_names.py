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
from constants.db_connections import ENGINE, PSY_CONN



class NamedEntity():
	def __init__(self, db_id, db_name=None) -> None:
		self.__db_id = db_id
		self.__db_name = db_name

	def __str__(self):
		return self.__db_name

	def get_id(self):
		return self.__db_id

	@classmethod
	def get_class_variables(cls):
		return {k: v for k, v in cls.__dict__.items() if not callable(v) and not k.startswith('__')}



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
		sheet_template_name = "sheet_template_name"
		table_id = "table_id"
		schema_id = "schema_id"


	class schema_names(NamedEntity):
		def __init__(self):
			super().__init__(db_name="schema_names", db_id=21)
  
		# Columns:
		schema_name = "schema_name"
		schema_id = "schema_id"

def get_schema_name(schema_id: int):

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



def get_table_name(table_id: int, template=False):

        schema = name_maps()
        table = schema.table_names()
        select_col = table.table_name
        if template:
            select_col = table.sheet_template_name
        filter_col = table.table_id

        query = f'''SELECT "{select_col}" FROM "{schema}"."{table}" WHERE "{filter_col}" = '%s' '''

        result = queries.execute_query(query, PSY_CONN, params=(table_id,))

        if len(result) != 1:
            raise Exception("Admin error: Length of result not as expected")

        if len(result[0]) != 1:
            raise Exception("Admin error: Length of result not as expected")


        return str(result[0][0])


def get_column_name(column_id: int, template=False):
    
	'''
	If template is set to True, the column name returned will be the column name in the Excel template.
	'''

	schema = name_maps()
	table = schema.column_names()
	select_col = table.column_name_db
	if template:
		select_col = table.column_name_sheet
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
 	order by cn.{nm.column_names.table_id}, cn.{nm.column_names.column_id};

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
		print(f"class {key}(Table):")
		print(f"{tab}def __init__(self):")
		print(f'{tab}{tab}super().__init__(db_id={table_id})')
		print()
		print(f"{tab}#  Columns:")
		for ele in d[key]["cols"]:

			var: str = re.sub(r'\(.*?\)', '', ele[0].lower()).strip()
			var = re.sub(r'[^a-z]', ' ', var).strip()
			var = var.replace(" ", "_").lower().strip("_")

			id = ele[1]

			print(f"{tab}{var} = Column({id})")
		print()


# @classmethod
# def __str__(cls):
# 	return cls.__name

class Table(NamedEntity):
	def __str__(self):
		id = self.get_id()
		return get_table_name(id)


class Schema(NamedEntity):
	def __str__(self):
		id = self.get_id()
		return get_schema_name(id)


class Column(NamedEntity):
	def __str__(self):
		id = self.get_id()
		return get_column_name(id)


class db_names:
	'''
	Helper class that gets column names from a mapper that maps column ids to names.
	This doesn't necessarily contain all column names, as it only needs to contiain
 the ones that are used in the code. 
	The names are stored in variables that can be used in the code.
	The class (and therefore the app) expects column names in DB to be equal to column names in upload sheet template.'
	Usage example: To access a latitude column using the class simply do df[db_names.field_sample.latitude] 
	'''

	class data(Schema):
		def __init__(self) -> None:
			super().__init__(db_id=1)

		class edna_robot_sample(Table):
			def __init__(self):
				super().__init__(db_id=1)

			#  Columns:
			subsampleid = Column(1)
			rackname = Column(2)
			rackid = Column(3)
			positioninrack = Column(4)
			mass = Column(5)
			sampledby = Column(6)
			samplingdate = Column(7)
			remarkssubsampling = Column(8)
			archivesampleid = Column(9)
			submitter = Column(10)
			submissiondate = Column(11)
			remarkssubmission = Column(12)
			database_insert_by = Column(13)
			from_spreadsheet = Column(14)
			database_insert_datetime_utc = Column(15)
			upload_uuid = Column(16)

		class age_depth_model(Table):
			def __init__(self):
				super().__init__(db_id=2)

			#  Columns:
			depth = Column(17)
			min = Column(18)
			max = Column(19)
			mean = Column(20)
			database_insert_by = Column(21)
			from_spreadsheet = Column(22)
			database_insert_datetime_utc = Column(23)
			upload_uuid = Column(24)
			master_field_sample_id = Column(25)
			median = Column(26)

		class master_depth(Table):
			def __init__(self):
				super().__init__(db_id=3)

			#  Columns:
			archive_sample_id = Column(27)
			master_depth = Column(28)
			field_sample_id = Column(29)
			master_field_sample_id = Column(30)
			database_insert_by = Column(31)
			from_spreadsheet = Column(32)
			database_insert_datetime_utc = Column(33)
			upload_uuid = Column(34)

		class field_sample_types(Table):
			def __init__(self):
				super().__init__(db_id=4)

			#  Columns:
			name = Column(35)

		class cgg_animal_plant(Table):
			def __init__(self):
				super().__init__(db_id=5)

			#  Columns:
			cgg_id = Column(36)
			museum_id_sample_id = Column(37)
			lab_no = Column(38)
			stock_sample_left = Column(39)
			extraction = Column(40)
			extraction_date = Column(41)
			kind_of_library = Column(42)
			library_date = Column(43)
			intern_provider = Column(44)
			type = Column(45)
			class_ = Column(46)
			order = Column(47)
			genus = Column(48)
			species = Column(49)
			common_name = Column(50)
			sex = Column(51)
			age = Column(52)
			geological_age = Column(53)
			material_group = Column(54)
			material_type = Column(55)
			material_condition = Column(56)
			site = Column(57)
			site_info = Column(58)
			city_town_location = Column(59)
			state_province_region = Column(60)
			country = Column(61)
			continent = Column(62)
			lat = Column(63)
			lon = Column(64)
			gps = Column(65)
			sample_provider = Column(66)
			museum_institution = Column(67)
			contact_info = Column(68)
			return_date = Column(69)
			return_details = Column(70)
			date_excavated = Column(71)
			date_collected = Column(72)
			date_recieved = Column(73)
			date_returned = Column(74)
			cites_permit_needed = Column(75)
			cites_permit_obtained = Column(76)
			sample_location = Column(77)
			extraction_location = Column(78)
			in_care_of = Column(79)
			date_out = Column(80)
			project_name = Column(81)
			supervisor = Column(82)
			analyses_history = Column(83)
			genbank_ref = Column(84)
			publications = Column(85)
			references = Column(86)
			notes = Column(87)
			thawed_up = Column(88)
			database_insert_by = Column(89)
			from_spreadsheet = Column(90)
			database_insert_datetime_utc = Column(91)
			upload_uuid = Column(92)

		class country_ocean(Table):
			def __init__(self):
				super().__init__(db_id=6)

			#  Columns:
			name = Column(93)

		class field_sample_environment_types(Table):
			def __init__(self):
				super().__init__(db_id=7)

			#  Columns:
			name = Column(94)

		class edna_wetlab_report(Table):
			def __init__(self):
				super().__init__(db_id=8)

			#  Columns:
			customer_name = Column(95)
			order_date = Column(96)
			order_id = Column(97)
			no = Column(98)
			total_sample_quantity = Column(99)
			robot_sample_rack_name = Column(100)
			robot_sample_rack_barcode = Column(101)
			robot_sample_rack_position = Column(102)
			robot_sample_id = Column(103)
			archive_sample_id = Column(104)
			edna_lysate_plate_id = Column(105)
			edna_lysate_position = Column(106)
			lysis_date = Column(107)
			edna_plate_id = Column(108)
			edna_plate_position = Column(109)
			edna_id = Column(110)
			edna_concentration = Column(111)
			cleanup_date = Column(112)
			customer_attention_to_extraction = Column(113)
			library_plate_id = Column(114)
			library_plate_barcode = Column(115)
			library_plate_position = Column(116)
			library_id = Column(117)
			library_concentration = Column(118)
			library_peak_size = Column(119)
			library_leftover_volume = Column(120)
			library_qc_result = Column(121)
			library_start_date = Column(122)
			ct = Column(123)
			qpcr_date = Column(124)
			idt_index_no = Column(125)
			i__bases_in_adapter = Column(126)
			i__bases_in_adapter = Column(127)
			pcr_cycle = Column(128)
			indexing_pcr_date = Column(129)
			library_cleanup_date = Column(130)
			library_qc_date = Column(131)
			customer_attention_to_library_prep = Column(132)
			tube_tag_submitted_to_seqc = Column(133)
			dna_pooled = Column(134)
			expected_sequencing_data = Column(135)
			submitting_date = Column(136)
			return_dna = Column(137)
			return_library = Column(138)
			return_pool = Column(139)
			pool_to_seqc = Column(140)
			project_done_date = Column(141)
			database_insert_by = Column(142)
			from_spreadsheet = Column(143)
			database_insert_datetime_utc = Column(144)
			fastq_file_id = Column(145)
			upload_uuid = Column(146)
			library_prep_method = Column(147)

		class flowcell(Table):
			def __init__(self):
				super().__init__(db_id=9)

			#  Columns:
			lane = Column(148)
			project = Column(149)
			sample = Column(150)
			barcode_sequence = Column(151)
			pf_clusters = Column(152)
			of_the_lane = Column(153)
			perfect_barcode = Column(154)
			one_mismatch_barcode = Column(155)
			yield_1 = Column(156)
			pf_clusters = Column(157)
			q___bases = Column(158)
			mean_quality_score = Column(159)
			flowcell_id = Column(160)
			clusters = Column(161)
			clusters = Column(162)
			yield_2 = Column(163)
			database_insert_by = Column(164)
			from_spreadsheet = Column(165)
			database_insert_datetime_utc = Column(166)
			upload_uuid = Column(167)

		class cgg_sediment_water(Table):
			def __init__(self):
				super().__init__(db_id=10)

			#  Columns:
			cgg_id = Column(168)
			museum_id_sample_id = Column(169)
			lab_no = Column(170)
			stock_sample_left = Column(171)
			extraction = Column(172)
			extraction_date = Column(173)
			kind_of_library = Column(174)
			library_date = Column(175)
			intern_provider = Column(176)
			sample_type = Column(177)
			depth = Column(178)
			height__asl = Column(179)
			material_type = Column(180)
			sampled_as = Column(181)
			sample_size = Column(182)
			depositional_environment = Column(183)
			age = Column(184)
			geological_age = Column(185)
			site = Column(186)
			site_info = Column(187)
			city_town_location = Column(188)
			state_province_region = Column(189)
			country = Column(190)
			continent = Column(191)
			lat = Column(192)
			lon = Column(193)
			gps = Column(194)
			sample_provider = Column(195)
			museum_institution = Column(196)
			contact_info = Column(197)
			date_collected = Column(198)
			date_recieved = Column(199)
			date_returned = Column(200)
			sample_location = Column(201)
			extraction_location = Column(202)
			in_care_of = Column(203)
			date_out = Column(204)
			project_name = Column(205)
			supervisor = Column(206)
			analyses_history = Column(207)
			genbank_ref = Column(208)
			publications = Column(209)
			references = Column(210)
			notes = Column(211)
			thawed_up = Column(212)
			database_insert_by = Column(213)
			from_spreadsheet = Column(214)
			database_insert_datetime_utc = Column(215)

		class adna_wetlab_report(Table):
			def __init__(self):
				super().__init__(db_id=11)

			#  Columns:
			customer_name = Column(216)
			order_date = Column(217)
			order_id = Column(218)
			sample_number = Column(219)
			adna_plate_name = Column(220)
			no = Column(221)
			sample_position = Column(222)
			adna_sample_name = Column(223)
			library_plate_id = Column(224)
			library_plate_position = Column(225)
			library_id = Column(226)
			library_concentration = Column(227)
			library_volume = Column(228)
			library_qc_result = Column(229)
			library_start_date = Column(230)
			ct = Column(231)
			qpcr_date = Column(232)
			idt_index_no = Column(233)
			i__bases_in_adapter = Column(234)
			i__bases_in_adapter = Column(235)
			pcr_cycle = Column(236)
			indexing_pcr_date = Column(237)
			library_cleanup_date = Column(238)
			library_qc_date = Column(239)
			tube_tag_submitted_to_seqc = Column(240)
			dna_pooled = Column(241)
			expected_sequencing_data = Column(242)
			submitting_date = Column(243)
			return_library = Column(244)
			pool_to_seqc = Column(245)
			project_done_date = Column(246)
			database_insert_by = Column(247)
			from_spreadsheet = Column(248)
			database_insert_datetime_utc = Column(249)
			sequencing_file_id = Column(250)
			upload_uuid = Column(251)

		class field_sample_material_type(Table):
			def __init__(self):
				super().__init__(db_id=12)

			#  Columns:
			name = Column(252)

		class field_sample_setting_types(Table):
			def __init__(self):
				super().__init__(db_id=13)

			#  Columns:
			name = Column(253)

		class edna_archive_sample(Table):
			def __init__(self):
				super().__init__(db_id=14)

			#  Columns:
			archivesampleid = Column(254)
			positioninrack = Column(255)
			rackname = Column(256)
			rackid = Column(257)
			bulksampleid = Column(258)
			depthsampledcaltape = Column(259)
			depthorderedcaltape = Column(260)
			organiccontent = Column(261)
			surfaceexposed = Column(262)
			remarksarchivesampling = Column(263)
			sampledby = Column(264)
			samplingdate = Column(265)
			submitter = Column(266)
			submissiondate = Column(267)
			remarkssubmission = Column(268)
			database_insert_by = Column(269)
			from_spreadsheet = Column(270)
			database_insert_datetime_utc = Column(271)
			upload_uuid = Column(272)

		class initials_translator(Table):
			def __init__(self):
				super().__init__(db_id=15)

			#  Columns:
			initials = Column(273)
			full_name = Column(274)
			database_insert_by = Column(275)
			from_spreadsheet = Column(276)
			database_insert_datetime_utc = Column(277)
			upload_uuid = Column(278)

		class seq_sample_sheet(Table):
			def __init__(self):
				super().__init__(db_id=16)

			#  Columns:
			sample_id = Column(279)
			sample_name = Column(280)
			sample_plate = Column(281)
			sample_well = Column(282)
			i__index_id = Column(283)
			index = Column(284)
			i__index_id = Column(285)
			index = Column(286)
			sample_project = Column(287)
			iemfileversion = Column(288)
			date = Column(289)
			workflow = Column(290)
			application = Column(291)
			instrument_type = Column(292)
			assay = Column(293)
			index_adapters = Column(294)
			description = Column(295)
			chemistry = Column(296)
			reads = Column(297)
			reads = Column(298)
			database_insert_by = Column(299)
			from_spreadsheet = Column(300)
			database_insert_datetime_utc = Column(301)
			upload_uuid = Column(302)

		class field_sample(Table):
			def __init__(self):
				super().__init__(db_id=17)

			#  Columns:
			unique_sample_id = Column(303)
			country_ocean = Column(304)
			site_name = Column(305)
			latitude = Column(306)
			longitude = Column(307)
			sample_date = Column(308)
			sample_provider = Column(309)
			running_project_title = Column(310)
			sampling_depth = Column(311)
			sampling_interval___to = Column(312)
			water_depth = Column(313)
			sample_type = Column(314)
			sample_environment = Column(315)
			sample_context = Column(316)
			age_estimate___from = Column(317)
			elevation = Column(318)
			sample_storage_address = Column(319)
			sample_storage_setting = Column(320)
			sample_storage_location = Column(321)
			miscellaneous_sample_measurement_or_observation = Column(322)
			miscellaneous_environmental_measurement_or_observation = Column(323)
			link_to_images = Column(324)
			link_to_other_relevant_information = Column(325)
			comments = Column(326)
			database_insert_by = Column(327)
			from_spreadsheet = Column(328)
			database_insert_datetime_utc = Column(329)
			upload_uuid = Column(330)
			sampling_interval___from = Column(331)
			age_estimate___to = Column(332)
			sample_material = Column(333)
			alias = Column(334)
			cultural_affiliation = Column(335)
			museum_institution = Column(336)
			other_relevant_information = Column(337)
			pi = Column(338)
			sample_provider = Column(339)
			site_grid_elev = Column(340)
			site_grid_latitude = Column(341)
			site_grid_longitude = Column(342)
			master_id_parent_sample_id = Column(343)
			field_label = Column(344)
			sample_type_in_storage_at_gm = Column(345)
			permit_for_dna_analysis = Column(346)

		class top_unknown_seq_barcodes(Table):
			def __init__(self):
				super().__init__(db_id=18)

			#  Columns:
			lane = Column(347)
			count = Column(348)
			sequence = Column(349)
			flowcell_id = Column(350)
			database_insert_by = Column(351)
			from_spreadsheet = Column(352)
			database_insert_datetime_utc = Column(353)
			uid = Column(354)
			upload_uuid = Column(355)


def get_full_name_map():

    column_names = name_maps().column_names()
    table_names = name_maps().table_names()
    schema_names = name_maps().schema_names()

    q = f'''
	select * from "{name_maps()}"."{column_names}" cn 
	join "{name_maps()}"."{table_names}" tn on cn."{column_names.table_id}" = tn."{table_names.table_id}" 
	join "{name_maps()}"."{schema_names}" sn on tn."{table_names.schema_id}" = sn."{schema_names.schema_id}";
	'''

    df = pd.read_sql(q, ENGINE)

    return df


def get_rename_map(schema_name, table_name):
    column_names = name_maps().column_names()
    table_names = name_maps().table_names()
    schema_names = name_maps().schema_names()

    q = f'''
	select "{column_names.column_name_sheet}", "{column_names.column_name_db}" from "{name_maps()}"."{column_names}" cn 
	join "{name_maps()}"."{table_names}" tn on cn."{column_names.table_id}" = tn."{table_names.table_id}" 
	join "{name_maps()}"."{schema_names}" sn on tn."{table_names.schema_id}" = sn."{schema_names.schema_id}"
 	where sn."{schema_names.schema_name}" = '{schema_name}' and tn."{table_names.table_name}" = '{table_name}' 
  	and cn."{column_names.column_name_sheet}" is not null;
	'''
 


    df = pd.read_sql(q, ENGINE)
    d = {key: value for (key, value) in df.values}

    return d
  
