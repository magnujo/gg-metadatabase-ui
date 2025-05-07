import os, sys
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(parent_dir)
from constants.db_names.name_maps import get_column_name, get_schema_name, get_table_name


class Table(str):
	def __new__(cls, template=False):
		return super().__new__(cls, get_table_name(cls._db_id, template))
        

class Schema(str):
	def __new__(cls):
		return super().__new__(cls, get_schema_name(cls._db_id))

class data(Schema):
    _db_id = 1

    class edna_robot_sample(Table):
        _db_id = 1

        #  Columns:
        robot_sample_id = lambda template=False: get_column_name(1, template=template)
        rackname = lambda template=False: get_column_name(2, template=template)
        rackid = lambda template=False: get_column_name(3, template=template)
        positioninrack = lambda template=False: get_column_name(4, template=template)
        mass = lambda template=False: get_column_name(5, template=template)
        sampledby = lambda template=False: get_column_name(6, template=template)
        samplingdate = lambda template=False: get_column_name(7, template=template)
        remarkssubsampling = lambda template=False: get_column_name(8, template=template)
        archivesampleid = lambda template=False: get_column_name(9, template=template)
        submitter = lambda template=False: get_column_name(10, template=template)
        submissiondate = lambda template=False: get_column_name(11, template=template)
        remarkssubmission = lambda template=False: get_column_name(12, template=template)
        database_insert_by = lambda template=False: get_column_name(13, template=template)
        from_spreadsheet = lambda template=False: get_column_name(14, template=template)
        database_insert_datetime_utc = lambda template=False: get_column_name(15, template=template)
        upload_uuid = lambda template=False: get_column_name(16, template=template)

    class age_depth_model(Table):
        _db_id = 2

        #  Columns:
        depth = lambda template=False: get_column_name(17, template=template)
        min = lambda template=False: get_column_name(18, template=template)
        max = lambda template=False: get_column_name(19, template=template)
        mean = lambda template=False: get_column_name(20, template=template)
        database_insert_by = lambda template=False: get_column_name(21, template=template)
        from_spreadsheet = lambda template=False: get_column_name(22, template=template)
        database_insert_datetime_utc = lambda template=False: get_column_name(23, template=template)
        upload_uuid = lambda template=False: get_column_name(24, template=template)
        master_field_sample_id = lambda template=False: get_column_name(25, template=template)
        median = lambda template=False: get_column_name(26, template=template)
        depth_id = lambda template=False: get_column_name(385, template=template)

    class master_depth(Table):
        _db_id = 3

        #  Columns:
        archive_sample_id = lambda template=False: get_column_name(27, template=template)
        master_depth = lambda template=False: get_column_name(28, template=template)
        database_insert_by = lambda template=False: get_column_name(31, template=template)
        from_spreadsheet = lambda template=False: get_column_name(32, template=template)
        database_insert_datetime_utc = lambda template=False: get_column_name(33, template=template)
        upload_uuid = lambda template=False: get_column_name(34, template=template)
        master_field_sample_id = lambda template=False: get_column_name(376, template=template)
        field_sample_id = lambda template=False: get_column_name(377, template=template)
        master_field_sample_id_correction = lambda template=False: get_column_name(380, template=template)
        archive_sample_master_depth_comment = lambda template=False: get_column_name(381, template=template)
        depth_id = lambda template=False: get_column_name(384, template=template)
        

    class field_sample_types(Table):
        _db_id = 4

        #  Columns:
        name = lambda template=False: get_column_name(35, template=template)
        
    class field_sample_types_at_gm(Table):
        _db_id = 45

        #  Columns:
        name = lambda template=False: get_column_name(386, template=template)

    class cgg_animal_plant(Table):
        _db_id = 5

        #  Columns:
        cgg_id = lambda template=False: get_column_name(36, template=template)
        museum_id_sample_id = lambda template=False: get_column_name(37, template=template)
        lab_no = lambda template=False: get_column_name(38, template=template)
        stock_sample_left = lambda template=False: get_column_name(39, template=template)
        extraction = lambda template=False: get_column_name(40, template=template)
        extraction_date = lambda template=False: get_column_name(41, template=template)
        kind_of_library = lambda template=False: get_column_name(42, template=template)
        library_date = lambda template=False: get_column_name(43, template=template)
        intern_provider = lambda template=False: get_column_name(44, template=template)
        type = lambda template=False: get_column_name(45, template=template)
        class_ = lambda template=False: get_column_name(46, template=template)
        order = lambda template=False: get_column_name(47, template=template)
        genus = lambda template=False: get_column_name(48, template=template)
        species = lambda template=False: get_column_name(49, template=template)
        common_name = lambda template=False: get_column_name(50, template=template)
        sex = lambda template=False: get_column_name(51, template=template)
        age = lambda template=False: get_column_name(52, template=template)
        geological_age = lambda template=False: get_column_name(53, template=template)
        material_group = lambda template=False: get_column_name(54, template=template)
        material_type = lambda template=False: get_column_name(55, template=template)
        material_condition = lambda template=False: get_column_name(56, template=template)
        site = lambda template=False: get_column_name(57, template=template)
        site_info = lambda template=False: get_column_name(58, template=template)
        city_town_location = lambda template=False: get_column_name(59, template=template)
        state_province_region = lambda template=False: get_column_name(60, template=template)
        country = lambda template=False: get_column_name(61, template=template)
        continent = lambda template=False: get_column_name(62, template=template)
        lat = lambda template=False: get_column_name(63, template=template)
        lon = lambda template=False: get_column_name(64, template=template)
        gps = lambda template=False: get_column_name(65, template=template)
        sample_provider = lambda template=False: get_column_name(66, template=template)
        museum_institution = lambda template=False: get_column_name(67, template=template)
        contact_info = lambda template=False: get_column_name(68, template=template)
        return_date = lambda template=False: get_column_name(69, template=template)
        return_details = lambda template=False: get_column_name(70, template=template)
        date_excavated = lambda template=False: get_column_name(71, template=template)
        date_collected = lambda template=False: get_column_name(72, template=template)
        date_recieved = lambda template=False: get_column_name(73, template=template)
        date_returned = lambda template=False: get_column_name(74, template=template)
        cites_permit_needed = lambda template=False: get_column_name(75, template=template)
        cites_permit_obtained = lambda template=False: get_column_name(76, template=template)
        sample_location = lambda template=False: get_column_name(77, template=template)
        extraction_location = lambda template=False: get_column_name(78, template=template)
        in_care_of = lambda template=False: get_column_name(79, template=template)
        date_out = lambda template=False: get_column_name(80, template=template)
        project_name = lambda template=False: get_column_name(81, template=template)
        supervisor = lambda template=False: get_column_name(82, template=template)
        analyses_history = lambda template=False: get_column_name(83, template=template)
        genbank_ref = lambda template=False: get_column_name(84, template=template)
        publications = lambda template=False: get_column_name(85, template=template)
        references = lambda template=False: get_column_name(86, template=template)
        notes = lambda template=False: get_column_name(87, template=template)
        thawed_up = lambda template=False: get_column_name(88, template=template)
        database_insert_by = lambda template=False: get_column_name(89, template=template)
        from_spreadsheet = lambda template=False: get_column_name(90, template=template)
        database_insert_datetime_utc = lambda template=False: get_column_name(91, template=template)
        upload_uuid = lambda template=False: get_column_name(92, template=template)

    class country_ocean(Table):
        _db_id = 6

        #  Columns:
        name = lambda template=False: get_column_name(93, template=template)

    class field_sample_environment_types(Table):
        _db_id = 7

        #  Columns:
        name = lambda template=False: get_column_name(94, template=template)

    class edna_wetlab_report(Table):
        _db_id = 8

        #  Columns:
        customer_name = lambda template=False: get_column_name(95, template=template)
        order_date = lambda template=False: get_column_name(96, template=template)
        order_id = lambda template=False: get_column_name(97, template=template)
        no = lambda template=False: get_column_name(98, template=template)
        total_sample_quantity = lambda template=False: get_column_name(99, template=template)
        robot_sample_rack_name = lambda template=False: get_column_name(100, template=template)
        robot_sample_rack_barcode = lambda template=False: get_column_name(101, template=template)
        robot_sample_rack_position = lambda template=False: get_column_name(102, template=template)
        robot_sample_id = lambda template=False: get_column_name(103, template=template)
        archive_sample_id = lambda template=False: get_column_name(104, template=template)
        edna_lysate_plate_id = lambda template=False: get_column_name(105, template=template)
        edna_lysate_position = lambda template=False: get_column_name(106, template=template)
        lysis_date = lambda template=False: get_column_name(107, template=template)
        edna_plate_id = lambda template=False: get_column_name(108, template=template)
        edna_plate_position = lambda template=False: get_column_name(109, template=template)
        edna_id = lambda template=False: get_column_name(110, template=template)
        edna_concentration = lambda template=False: get_column_name(111, template=template)
        cleanup_date = lambda template=False: get_column_name(112, template=template)
        customer_attention_to_extraction = lambda template=False: get_column_name(113, template=template)
        library_plate_id = lambda template=False: get_column_name(114, template=template)
        library_plate_barcode = lambda template=False: get_column_name(115, template=template)
        library_plate_position = lambda template=False: get_column_name(116, template=template)
        library_id = lambda template=False: get_column_name(117, template=template)
        library_concentration = lambda template=False: get_column_name(118, template=template)
        library_peak_size = lambda template=False: get_column_name(119, template=template)
        library_leftover_volume = lambda template=False: get_column_name(120, template=template)
        library_qc_result = lambda template=False: get_column_name(121, template=template)
        library_start_date = lambda template=False: get_column_name(122, template=template)
        ct = lambda template=False: get_column_name(123, template=template)
        qpcr_date = lambda template=False: get_column_name(124, template=template)
        idt_index_no = lambda template=False: get_column_name(125, template=template)
        i__bases_in_adapter = lambda template=False: get_column_name(126, template=template)
        i__bases_in_adapter = lambda template=False: get_column_name(127, template=template)
        pcr_cycle = lambda template=False: get_column_name(128, template=template)
        indexing_pcr_date = lambda template=False: get_column_name(129, template=template)
        library_cleanup_date = lambda template=False: get_column_name(130, template=template)
        library_qc_date = lambda template=False: get_column_name(131, template=template)
        customer_attention_to_library_prep = lambda template=False: get_column_name(132, template=template)
        library_pool_tag = lambda template=False: get_column_name(133, template=template)
        dna_pooled = lambda template=False: get_column_name(134, template=template)
        expected_sequencing_data = lambda template=False: get_column_name(135, template=template)
        submitting_date = lambda template=False: get_column_name(136, template=template)
        return_dna = lambda template=False: get_column_name(137, template=template)
        return_library = lambda template=False: get_column_name(138, template=template)
        return_pool = lambda template=False: get_column_name(139, template=template)
        pool_to_seqc = lambda template=False: get_column_name(140, template=template)
        project_done_date = lambda template=False: get_column_name(141, template=template)
        database_insert_by = lambda template=False: get_column_name(142, template=template)
        from_spreadsheet = lambda template=False: get_column_name(143, template=template)
        database_insert_datetime_utc = lambda template=False: get_column_name(144, template=template)
        fastq_file_id = lambda template=False: get_column_name(145, template=template)
        upload_uuid = lambda template=False: get_column_name(146, template=template)
        library_prep_method = lambda template=False: get_column_name(147, template=template)
        comp_id = lambda template=False: get_column_name(394, template=template)
        fastq_tube_id = lambda template=False: get_column_name(407, template=template)

    class flowcell(Table):
        _db_id = 9

        #  Columns:
        lane = lambda template=False: get_column_name(148, template=template)
        project = lambda template=False: get_column_name(149, template=template)
        fastq_file_id = lambda template=False: get_column_name(150, template=template)
        barcode_sequence = lambda template=False: get_column_name(151, template=template)
        pf_clusters = lambda template=False: get_column_name(152, template=template)
        of_the_lane = lambda template=False: get_column_name(153, template=template)
        perfect_barcode = lambda template=False: get_column_name(154, template=template)
        one_mismatch_barcode = lambda template=False: get_column_name(155, template=template)
        yield_1 = lambda template=False: get_column_name(156, template=template)
        pf_clusters = lambda template=False: get_column_name(157, template=template)
        q___bases = lambda template=False: get_column_name(158, template=template)
        mean_quality_score = lambda template=False: get_column_name(159, template=template)
        flowcell_id = lambda template=False: get_column_name(160, template=template)
        clusters_pf_sum = lambda template=False: get_column_name(161, template=template)
        clusters_raw_sum = lambda template=False: get_column_name(162, template=template)
        yield_sum = lambda template=False: get_column_name(163, template=template)
        database_insert_by = lambda template=False: get_column_name(164, template=template)
        from_spreadsheet = lambda template=False: get_column_name(165, template=template)
        database_insert_datetime_utc = lambda template=False: get_column_name(166, template=template)
        upload_uuid = lambda template=False: get_column_name(167, template=template)
        library_pool_tag = lambda template=False: get_column_name(395, template=template)
        read_length = lambda template=False: get_column_name(397, template=template)
        sequencing_machine = lambda template=False: get_column_name(399, template=template)
        sequencing_date = lambda template=False: get_column_name(401, template=template)
        sequencing_run = lambda template=False: get_column_name(403, template=template)
        flowcell_position = lambda template=False: get_column_name(405, template=template)
        fastq_tube_id = lambda template=False: get_column_name(408, template=template)


    class cgg_sediment_water(Table):
        _db_id = 10

        #  Columns:
        cgg_id = lambda template=False: get_column_name(168, template=template)
        museum_id_sample_id = lambda template=False: get_column_name(169, template=template)
        lab_no = lambda template=False: get_column_name(170, template=template)
        stock_sample_left = lambda template=False: get_column_name(171, template=template)
        extraction = lambda template=False: get_column_name(172, template=template)
        extraction_date = lambda template=False: get_column_name(173, template=template)
        kind_of_library = lambda template=False: get_column_name(174, template=template)
        library_date = lambda template=False: get_column_name(175, template=template)
        intern_provider = lambda template=False: get_column_name(176, template=template)
        sample_type = lambda template=False: get_column_name(177, template=template)
        depth = lambda template=False: get_column_name(178, template=template)
        height__asl = lambda template=False: get_column_name(179, template=template)
        material_type = lambda template=False: get_column_name(180, template=template)
        sampled_as = lambda template=False: get_column_name(181, template=template)
        sample_size = lambda template=False: get_column_name(182, template=template)
        depositional_environment = lambda template=False: get_column_name(183, template=template)
        age = lambda template=False: get_column_name(184, template=template)
        geological_age = lambda template=False: get_column_name(185, template=template)
        site = lambda template=False: get_column_name(186, template=template)
        site_info = lambda template=False: get_column_name(187, template=template)
        city_town_location = lambda template=False: get_column_name(188, template=template)
        state_province_region = lambda template=False: get_column_name(189, template=template)
        country = lambda template=False: get_column_name(190, template=template)
        continent = lambda template=False: get_column_name(191, template=template)
        lat = lambda template=False: get_column_name(192, template=template)
        lon = lambda template=False: get_column_name(193, template=template)
        gps = lambda template=False: get_column_name(194, template=template)
        sample_provider = lambda template=False: get_column_name(195, template=template)
        museum_institution = lambda template=False: get_column_name(196, template=template)
        contact_info = lambda template=False: get_column_name(197, template=template)
        date_collected = lambda template=False: get_column_name(198, template=template)
        date_recieved = lambda template=False: get_column_name(199, template=template)
        date_returned = lambda template=False: get_column_name(200, template=template)
        sample_location = lambda template=False: get_column_name(201, template=template)
        extraction_location = lambda template=False: get_column_name(202, template=template)
        in_care_of = lambda template=False: get_column_name(203, template=template)
        date_out = lambda template=False: get_column_name(204, template=template)
        project_name = lambda template=False: get_column_name(205, template=template)
        supervisor = lambda template=False: get_column_name(206, template=template)
        analyses_history = lambda template=False: get_column_name(207, template=template)
        genbank_ref = lambda template=False: get_column_name(208, template=template)
        publications = lambda template=False: get_column_name(209, template=template)
        references = lambda template=False: get_column_name(210, template=template)
        notes = lambda template=False: get_column_name(211, template=template)
        thawed_up = lambda template=False: get_column_name(212, template=template)
        database_insert_by = lambda template=False: get_column_name(213, template=template)
        from_spreadsheet = lambda template=False: get_column_name(214, template=template)
        database_insert_datetime_utc = lambda template=False: get_column_name(215, template=template)

    class adna_wetlab_report(Table):
        _db_id = 11

        #  Columns:
        customer_name = lambda template=False: get_column_name(216, template=template)
        order_date = lambda template=False: get_column_name(217, template=template)
        order_id = lambda template=False: get_column_name(218, template=template)
        sample_number = lambda template=False: get_column_name(219, template=template)
        adna_plate_name = lambda template=False: get_column_name(220, template=template)
        no = lambda template=False: get_column_name(221, template=template)
        sample_position = lambda template=False: get_column_name(222, template=template)
        adna_sample_name = lambda template=False: get_column_name(223, template=template)
        library_plate_id = lambda template=False: get_column_name(224, template=template)
        library_plate_position = lambda template=False: get_column_name(225, template=template)
        library_id = lambda template=False: get_column_name(226, template=template)
        library_concentration = lambda template=False: get_column_name(227, template=template)
        library_volume = lambda template=False: get_column_name(228, template=template)
        library_qc_result = lambda template=False: get_column_name(229, template=template)
        library_start_date = lambda template=False: get_column_name(230, template=template)
        ct = lambda template=False: get_column_name(231, template=template)
        qpcr_date = lambda template=False: get_column_name(232, template=template)
        idt_index_no = lambda template=False: get_column_name(233, template=template)
        i__bases_in_adapter = lambda template=False: get_column_name(234, template=template)
        i__bases_in_adapter = lambda template=False: get_column_name(235, template=template)
        pcr_cycle = lambda template=False: get_column_name(236, template=template)
        indexing_pcr_date = lambda template=False: get_column_name(237, template=template)
        library_cleanup_date = lambda template=False: get_column_name(238, template=template)
        library_qc_date = lambda template=False: get_column_name(239, template=template)
        tube_tag_submitted_to_seqc = lambda template=False: get_column_name(240, template=template)
        dna_pooled = lambda template=False: get_column_name(241, template=template)
        expected_sequencing_data = lambda template=False: get_column_name(242, template=template)
        submitting_date = lambda template=False: get_column_name(243, template=template)
        return_library = lambda template=False: get_column_name(244, template=template)
        pool_to_seqc = lambda template=False: get_column_name(245, template=template)
        project_done_date = lambda template=False: get_column_name(246, template=template)
        database_insert_by = lambda template=False: get_column_name(247, template=template)
        from_spreadsheet = lambda template=False: get_column_name(248, template=template)
        database_insert_datetime_utc = lambda template=False: get_column_name(249, template=template)
        sequencing_file_id = lambda template=False: get_column_name(250, template=template)
        upload_uuid = lambda template=False: get_column_name(251, template=template)

    class field_sample_material_type(Table):
        _db_id = 12

        #  Columns:
        name = lambda template=False: get_column_name(252, template=template)

    class field_sample_context_types(Table):
        _db_id = 13

        #  Columns:
        name = lambda template=False: get_column_name(253, template=template)
        
    class field_sample_types_gm(Table):
        _db_id = 45

        #  Columns:
        name = lambda template=False: get_column_name(386, template=template)

    class edna_archive_sample(Table):
        _db_id = 14

        #  Columns:
        archivesampleid = lambda template=False: get_column_name(254, template=template)
        positioninrack = lambda template=False: get_column_name(255, template=template)
        rackname = lambda template=False: get_column_name(256, template=template)
        rackid = lambda template=False: get_column_name(257, template=template)
        field_sample_id = lambda template=False: get_column_name(258, template=template)
        depthsampledcaltape = lambda template=False: get_column_name(259, template=template)
        depthorderedcaltape = lambda template=False: get_column_name(260, template=template)
        organiccontent = lambda template=False: get_column_name(261, template=template)
        surfaceexposed = lambda template=False: get_column_name(262, template=template)
        remarksarchivesampling = lambda template=False: get_column_name(263, template=template)
        sampledby = lambda template=False: get_column_name(264, template=template)
        samplingdate = lambda template=False: get_column_name(265, template=template)
        submitter = lambda template=False: get_column_name(266, template=template)
        submissiondate = lambda template=False: get_column_name(267, template=template)
        remarkssubmission = lambda template=False: get_column_name(268, template=template)
        database_insert_by = lambda template=False: get_column_name(269, template=template)
        from_spreadsheet = lambda template=False: get_column_name(270, template=template)
        database_insert_datetime_utc = lambda template=False: get_column_name(271, template=template)
        upload_uuid = lambda template=False: get_column_name(272, template=template)
        exists_in_storage = lambda template=False: get_column_name(383, template=template)
        is_master_depth = lambda template=False: get_column_name(382, template=template)

    class initials_translator(Table):
        _db_id = 15

        #  Columns:
        initials = lambda template=False: get_column_name(273, template=template)
        full_name = lambda template=False: get_column_name(274, template=template)
        database_insert_by = lambda template=False: get_column_name(275, template=template)
        from_spreadsheet = lambda template=False: get_column_name(276, template=template)
        database_insert_datetime_utc = lambda template=False: get_column_name(277, template=template)
        upload_uuid = lambda template=False: get_column_name(278, template=template)

    class seq_sample_sheet(Table):
        _db_id = 16

        #  Columns:
        fastq_file_id = lambda template=False: get_column_name(279, template=template)
        sample_name = lambda template=False: get_column_name(280, template=template)
        sample_plate = lambda template=False: get_column_name(281, template=template)
        sample_well = lambda template=False: get_column_name(282, template=template)
        i__index_id = lambda template=False: get_column_name(283, template=template)
        index = lambda template=False: get_column_name(284, template=template)
        i__index_id = lambda template=False: get_column_name(285, template=template)
        index = lambda template=False: get_column_name(286, template=template)
        sample_project = lambda template=False: get_column_name(287, template=template)
        iemfileversion = lambda template=False: get_column_name(288, template=template)
        date = lambda template=False: get_column_name(289, template=template)
        workflow = lambda template=False: get_column_name(290, template=template)
        application = lambda template=False: get_column_name(291, template=template)
        instrument_type = lambda template=False: get_column_name(292, template=template)
        assay = lambda template=False: get_column_name(293, template=template)
        index_adapters = lambda template=False: get_column_name(294, template=template)
        description = lambda template=False: get_column_name(295, template=template)
        chemistry = lambda template=False: get_column_name(296, template=template)
        reads = lambda template=False: get_column_name(297, template=template)
        reads = lambda template=False: get_column_name(298, template=template)
        database_insert_by = lambda template=False: get_column_name(299, template=template)
        from_spreadsheet = lambda template=False: get_column_name(300, template=template)
        database_insert_datetime_utc = lambda template=False: get_column_name(301, template=template)
        upload_uuid = lambda template=False: get_column_name(302, template=template)

    class field_sample(Table):
        _db_id = 17

        #  Columns:
        field_sample_id = lambda template=False: get_column_name(303, template=template)
        country_ocean = lambda template=False: get_column_name(304, template=template)
        site_name = lambda template=False: get_column_name(305, template=template)
        latitude = lambda template=False: get_column_name(306, template=template)
        longitude = lambda template=False: get_column_name(307, template=template)
        sample_date = lambda template=False: get_column_name(308, template=template)
        sample_provider_name = lambda template=False: get_column_name(309, template=template)
        running_project_title = lambda template=False: get_column_name(310, template=template)
        sampling_depth = lambda template=False: get_column_name(311, template=template)
        sampling_interval___to = lambda template=False: get_column_name(312, template=template)
        water_depth = lambda template=False: get_column_name(313, template=template)
        sample_type = lambda template=False: get_column_name(314, template=template)
        sample_context = lambda template=False: get_column_name(316, template=template)
        sample_environment = lambda template=False: get_column_name(315, template=template)
        age_estimate___from = lambda template=False: get_column_name(317, template=template)
        elevation = lambda template=False: get_column_name(318, template=template)
        sample_storage_address = lambda template=False: get_column_name(319, template=template)
        sample_storage_setting = lambda template=False: get_column_name(320, template=template)
        sample_storage_location = lambda template=False: get_column_name(321, template=template)
        miscellaneous_sample_measurement_or_observation = lambda template=False: get_column_name(322, template=template)
        miscellaneous_environmental_measurement_or_observation = lambda template=False: get_column_name(323, template=template)
        link_to_images = lambda template=False: get_column_name(324, template=template)
        link_to_other_relevant_information = lambda template=False: get_column_name(325, template=template)
        comments = lambda template=False: get_column_name(326, template=template)
        database_insert_by = lambda template=False: get_column_name(327, template=template)
        from_spreadsheet = lambda template=False: get_column_name(328, template=template)
        database_insert_datetime_utc = lambda template=False: get_column_name(329, template=template)
        upload_uuid = lambda template=False: get_column_name(330, template=template)
        sampling_interval___from = lambda template=False: get_column_name(331, template=template)
        age_estimate___to = lambda template=False: get_column_name(332, template=template)
        sample_material = lambda template=False: get_column_name(333, template=template)
        alias = lambda template=False: get_column_name(334, template=template)
        cultural_affiliation = lambda template=False: get_column_name(335, template=template)
        museum_institution = lambda template=False: get_column_name(336, template=template)
        other_relevant_information = lambda template=False: get_column_name(337, template=template)
        pi = lambda template=False: get_column_name(338, template=template)
        sample_provider_contact = lambda template=False: get_column_name(339, template=template)
        site_grid_elev = lambda template=False: get_column_name(340, template=template)
        site_grid_latitude = lambda template=False: get_column_name(341, template=template)
        site_grid_longitude = lambda template=False: get_column_name(342, template=template)
        master_id_parent_sample_id = lambda template=False: get_column_name(343, template=template)
        field_label = lambda template=False: get_column_name(344, template=template)
        sample_type_in_storage_at_gm = lambda template=False: get_column_name(345, template=template)
        permit_for_dna_analysis = lambda template=False: get_column_name(346, template=template)

        sample_environment_secondary = lambda template=False: get_column_name(387, template=template)
    class top_unknown_seq_barcodes(Table):
        _db_id = 18

        #  Columns:
        lane = lambda template=False: get_column_name(347, template=template)
        count_ = lambda template=False: get_column_name(348, template=template)
        sequence = lambda template=False: get_column_name(349, template=template)
        flowcell_id = lambda template=False: get_column_name(350, template=template)
        database_insert_by = lambda template=False: get_column_name(351, template=template)
        from_spreadsheet = lambda template=False: get_column_name(352, template=template)
        database_insert_datetime_utc = lambda template=False: get_column_name(353, template=template)
        uid = lambda template=False: get_column_name(354, template=template)
        upload_uuid = lambda template=False: get_column_name(355, template=template)
        read_length = lambda template=False: get_column_name(398, template=template)
        sequencing_machine = lambda template=False: get_column_name(400, template=template)
        sequencing_date = lambda template=False: get_column_name(402, template=template)
        sequencing_run = lambda template=False: get_column_name(404, template=template)
        flowcell_position = lambda template=False: get_column_name(406, template=template)

    

class deleted_by_script(Schema):
    _db_id = 10