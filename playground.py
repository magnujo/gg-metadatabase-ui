from utils import queries
import constants
p = queries.get_possible_datatypes('date')
print(p)

SELECT as2."FieldSampleID", as2."ArchiveSampleID", ers."Robot TUBE barcode", eas."eDNA ID", eas."Library ID", eas."Tube Tag Submitted to SeqC",
as2."DepthSampledCalTape", csw."Country", csw."Lat", csw."Lon", csw."Date collected"
FROM super_simple_db.edna_archive_sample as2 
join super_simple_db.edna_robot_sample ers ON as2."ArchiveSampleID" = ers."Archive TUBE barcode"
left JOIN super_simple_db.edna_wetlab_report eas ON ers."Robot TUBE barcode" = eas."LVL Tube Barcode"
left join super_simple_db.cgg_sediment_water csw on as2."FieldSampleID" = csw."CGG ID"