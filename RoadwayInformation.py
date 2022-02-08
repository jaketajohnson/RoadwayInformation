import arcpy
import os
import traceback
import sys
sys.path.insert(0, "C:/Scripts")
import Logging

# Environment
arcpy.env.overwriteOutput = True

# Paths
services = r"F:\Shares\FGDB_Services"
data = os.path.join(services, "Data")
database_connections = os.path.join(services, "DatabaseConnections")

# Publish
sde = os.path.join(database_connections, "COSPW@imSPFLD@MCWINTCWDB.sde")
facilities_streets_dataset = os.path.join(sde, "FacilitiesStreets")
roadway_info = os.path.join(facilities_streets_dataset, "RoadwayInformation")

# Views
cityworks_view = os.path.join(database_connections, "DA@mcwintcwdb.cwprod@CityworksView.sde")
paser_asphalt_view = os.path.join(cityworks_view, "CityworksView.dbo.vw_insPASER_ASPHALT")
paser_brick_view = os.path.join(cityworks_view, "CityworksView.dbo.vw_insPASER_BRICK")
paser_concrete_view = os.path.join(cityworks_view, "CityworksView.dbo.vw_insPASER_CONCRETE")
paser_sealcoat_view = os.path.join(cityworks_view, "CityworksView.dbo.vw_insPASER_SEALCOAT")

# RoadwayInfo.gdb
roadway_info_gdb = os.path.join(data, "RoadwayInfo.gdb")
facility_streets = os.path.join(roadway_info_gdb, "FacilitiesStreets")
pavement_segments = os.path.join(facility_streets, "PavementSegments")
pavement_inspections = os.path.join(facility_streets, "PavementInspections")

# PASER View Tables
paser_asphalt_table = os.path.join(roadway_info_gdb, "PASER_ASPHALT_table")
paser_brick_table = os.path.join(roadway_info_gdb, "PASER_BRICK_table")
paser_concrete_table = os.path.join(roadway_info_gdb, "PASER_CONCRETE_table")
paser_sealcoat_table = os.path.join(roadway_info_gdb, "PASER_SEALCOAT_table")

# PASER output layers
paser_merged = os.path.join(roadway_info_gdb, "PASER")
paser_asphalt = os.path.join(roadway_info_gdb, "PASER_ASPHALT")
paser_brick = os.path.join(roadway_info_gdb, "PASER_BRICK")
paser_concrete = os.path.join(roadway_info_gdb, "PASER_CONCRETE")
paser_sealcoat = os.path.join(roadway_info_gdb, "PASER_SEALCOAT")

# List of PASER tables/views/strings for iteration (view, table name, table path, output name, expression)
paser_list = [[paser_asphalt_view, "PASER_asphalt_table", paser_asphalt_table, "PASER_ASPHALT", "501"],  # ASPHALT
              [paser_brick_view, "PASER_BRICK_table", paser_brick_table, "PASER_BRICK", "800"],  # BRICK
              [paser_concrete_view, "PASER_CONCRETE_table", paser_concrete_table, "PASER_CONCRETE", "700"],  # CONCRETE
              [paser_sealcoat_view, "PASER_SEALCOAT_table", paser_sealcoat_table, "PASER_SEALCOAT", "300"]]  # SEALCOAT


def paser_loop(view, table_name, table, output_name, expression):
    """Loop through paster_list to create PASER output layers"""
    Logging.logger.info(f"------START {output_name}")
    arcpy.TableToTable_conversion(view, roadway_info_gdb, table_name)
    arcpy.MakeFeatureLayer_management(roadway_info, "roadway_info")
    arcpy.AddJoin_management("roadway_info", "SPI_NBR", table, "ENTITYUID", "KEEP_ALL")
    arcpy.FeatureClassToFeatureClass_conversion("roadway_info", roadway_info_gdb, output_name, f"MNT_TYPE LIKE '%5480%' AND SURF_TYP = '{expression}'")
    Logging.logger.info(f"------FINISH {output_name}")


@Logging.insert("Delete", 1)
def initial_delete():
    # Delete old output layers to avoid conflicts
    layers_to_delete = [pavement_segments, pavement_inspections,  # Pavement
                        paser_merged, paser_asphalt, paser_brick, paser_concrete, paser_sealcoat]  # PASER
    for layer in layers_to_delete:
        if arcpy.Exists(layer):
            arcpy.Delete_management(layer)


@Logging.insert("Roadway Information", 1)
def roadway_information():
    """Process roadway information segments into derivative information"""

    # Dissolve and filter roadway info
    Logging.logger.info("------START Dissolve")
    arcpy.MakeFeatureLayer_management(roadway_info, "roadway_info")
    selection = arcpy.SelectLayerByAttribute_management("roadway_info", "NEW_SELECTION", f"MNT_TYPE LIKE '%5480%'")
    arcpy.Dissolve_management(selection, pavement_inspections, ["SPI_NBR", "ROAD_NAME", "FC", "SURF_TYP"])
    arcpy.Dissolve_management(selection, pavement_segments, ["SPI_SEG", "ROAD_NAME", "FC", "SURF_TYP"])
    Logging.logger.info("------FINISH Dissolve")


@Logging.insert("PASER", 1)
def paser():
    """Loop through paser_list then cleanup layers"""

    for paser_type in paser_list:
        paser_loop(paser_type[0], paser_type[1], paser_type[2], paser_type[3], paser_type[4])

    # Merge all PASER layers and remove unnecessary fields
    Logging.logger.info("------START MERGE")
    layers_to_merge = [paser_asphalt, paser_brick, paser_concrete, paser_sealcoat]
    fields_to_delete = ["RAVELING", "FLUSHING", "POLISHING", "RUTTING", "HEAVING", "SETTLING", "TRENCH", "PATCHES", "POTHOLES", "UTILITY", "REFLECTION", "SLIPPAGE", "LONGITUDINAL", "TRANSVERSE",
                        "PUMPING", "GRADE", "INFILTRATION", "LENGTH", "MATERIAL", "JOINTEROSION", "BROKEN", "GAPS", "BRICK", "WEAR", "MAP", "POPOUTS", "SCALING", "REINFORCING", "SPALLING", "BLOWUPS", "FAULTING",
                        "DEFORMATION", "TRAVERSE", "DCRACKS", "CORNER", "MEANDER", "MANHOLE", "PUMPING", "EDGE", "BLOCK", "ALLIGATOR", "VEGETATION", "DRAINAGE"]
    arcpy.Merge_management(layers_to_merge, paser_merged)
    arcpy.DeleteField_management(paser_merged, fields_to_delete)
    Logging.logger.info("------FINISH MERGE")


@Logging.insert("Final Delete", 1)
def final_delete():
    layers_to_delete = [paser_asphalt_table, paser_brick_table, paser_concrete_table, paser_sealcoat_table]
    for layer in layers_to_delete:
        if arcpy.Exists(layer):
            arcpy.Delete_management(layer)

    # Leave in until script is confirmed functional; I've abstracted this to paser/paser_loop
    """# Join PASER inspections to RoadwayInformation from Publish.gdb then export to RoadwayInfo.gdb
    Logging.logger.info("------START PASER_ASPHALT")
    arcpy.TableToTable_conversion(paser_asphalt_view, roadway_info_gdb, "PASER_asphalt_table")
    arcpy.MakeFeatureLayer_management(roadway_info, "roadway_info")
    arcpy.AddJoin_management("roadway_info", "SPI_NBR", paser_asphalt_table, "ENTITYUID", "KEEP_ALL")
    arcpy.FeatureClassToFeatureClass_conversion("roadway_info", roadway_info_gdb, "PASER_ASPHALT", "MNT_TYPE LIKE '%5480%' AND SURF_TYP = '501'")
    Logging.logger.info("------FINISH PASER_ASPHALT")

    # Join the exported PASER_ASPHALT table to PavementInspections then export to RoadwayInfo.gdb
    Logging.logger.info("------START PASER_BRICK")
    arcpy.TableToTable_conversion(paser_brick_view, roadway_info_gdb, "PASER_brick_table")
    arcpy.MakeFeatureLayer_management(roadway_info, "roadway_info")
    arcpy.AddJoin_management("roadway_info", "SPI_NBR", paser_brick_table, "ENTITYUID", "KEEP_ALL")
    arcpy.FeatureClassToFeatureClass_conversion("roadway_info", roadway_info_gdb, "PASER_BRICK", "MNT_TYPE LIKE '%5480%' AND SURF_TYP = '800'")
    Logging.logger.info("------FINISH PASER_BRICK")

    Logging.logger.info("------START PASER_CONCRETE")
    arcpy.TableToTable_conversion(paser_concrete_view, roadway_info_gdb, "PASER_concrete_table")
    arcpy.MakeFeatureLayer_management(roadway_info, "roadway_info")
    arcpy.AddJoin_management("roadway_info", "SPI_NBR", paser_concrete_table, "ENTITYUID", "KEEP_ALL")
    arcpy.FeatureClassToFeatureClass_conversion("roadway_info", roadway_info_gdb, "PASER_CONCRETE", "MNT_TYPE LIKE '%5480%' AND SURF_TYP = '700'")
    Logging.logger.info("------FINISH PASER_CONCRETE")

    Logging.logger.info("------START PASER_SEALCOAT")
    arcpy.TableToTable_conversion(paser_sealcoat_view, roadway_info_gdb, "PASER_sealcoat_table")
    arcpy.MakeFeatureLayer_management(roadway_info, "roadway_info")
    arcpy.AddJoin_management("roadway_info", "SPI_NBR", paser_sealcoat_table, "ENTITYUID", "KEEP_ALL")
    arcpy.FeatureClassToFeatureClass_conversion("roadway_info", roadway_info_gdb, "PASER_SEALCOAT", "MNT_TYPE LIKE '%5480%' AND SURF_TYP = '300'")
    Logging.logger.info("------FINISH PASER_SEALCOAT")"""


if __name__ == "__main__":
    traceback_info = traceback.format_exc()
    try:
        Logging.logger.info("Script Execution Started")
        initial_delete()
        roadway_information()
        paser()
        final_delete()
        Logging.logger.info("Script Execution Finished")
    except (IOError, NameError, KeyError, IndexError, TypeError, UnboundLocalError, ValueError):
        Logging.logger.info(traceback_info)
    except NameError:
        print(traceback_info)
    except arcpy.ExecuteError:
        Logging.logger.error(arcpy.GetMessages(2))
    except:
        Logging.logger.info("An unspecified exception occurred")
