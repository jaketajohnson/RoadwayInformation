import arcpy
import os
import traceback
import sys
sys.path.insert(0, "Y:/Scripts")
import Logging


@Logging.insert("Roadway Information", 1)
def roadway_information():
    """Dissolve roadway information segments"""

    # Environment

    arcpy.env.overwriteOutput = True

    # Paths
    sde = r"F:\Shares\FGDB_Services\DatabaseConnections\COSPW@imSPFLD@MCWINTCWDB.sde"
    facilities_streets_sde = os.path.join(sde, "FacilitiesStreets")
    roadway_info = os.path.join(facilities_streets_sde, "RoadwayInformation")
    facility_streets = r"W:\RoadwayInfo.gdb\FacilitiesStreets"
    pavement_segments = os.path.join(facility_streets, "PavementSegments")
    pavement_inspections = os.path.join(facility_streets, "PavementInspections")

    Logging.logger.info("------START DELETE")
    if arcpy.Exists(pavement_segments):
        arcpy.Delete_management(pavement_segments)
    if arcpy.Exists(pavement_inspections):
        arcpy.Delete_management(pavement_inspections)
    Logging.logger.info("------FINISH DELETE")

    Logging.logger.info("------START Dissolve")
    arcpy.MakeFeatureLayer_management(roadway_info, "roadway_info")
    selection = arcpy.SelectLayerByAttribute_management("roadway_info", "NEW_SELECTION", f"MNT_TYPE LIKE '%5480%'")
    arcpy.Dissolve_management(selection, pavement_inspections, ["SPI_NBR", "ROAD_NAME", "FC", "SURF_TYP"])
    arcpy.Dissolve_management(selection, pavement_segments, ["SPI_SEG", "ROAD_NAME", "FC", "SURF_TYP"])
    Logging.logger.info("------FINISH Dissolve")


if __name__ == "__main__":
    traceback_info = traceback.format_exc()
    try:
        Logging.logger.info("Script Execution Started")
        roadway_information()
        Logging.logger.info("Script Execution Finished")
    except (IOError, NameError, KeyError, IndexError, TypeError, UnboundLocalError, ValueError):
        Logging.logger.info(traceback_info)
    except NameError:
        print(traceback_info)
    except arcpy.ExecuteError:
        Logging.logger.error(arcpy.GetMessages(2))
    except:
        Logging.logger.info("An unspecified exception occurred")
