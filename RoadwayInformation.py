import arcpy
import logging
import os
import sys
import traceback


def ScriptLogging():
    """Enables console and log file logging; see test script for comments on functionality"""
    current_directory = os.getcwd()
    script_filename = os.path.basename(sys.argv[0])
    log_filename = os.path.splitext(script_filename)[0]
    log_file = os.path.join(current_directory, f"{log_filename}.log")
    if not os.path.exists(log_file):
        with open(log_file, "w"):
            pass
    message_formatting = "%(asctime)s - %(levelname)s - %(message)s"
    date_formatting = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(fmt=message_formatting, datefmt=date_formatting)
    logging_output = logging.getLogger(f"{log_filename}")
    logging_output.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logging_output.addHandler(console_handler)
    logging.basicConfig(format=message_formatting, datefmt=date_formatting, filename=log_file, filemode="w", level=logging.INFO)
    return logging_output


def roadway_information():
    """Dissolve roadway information segments"""
    logger = ScriptLogging()
    logger.info("Script Execution Start")

    # Paths
    sde = r"F:\Shares\FGDB_Services\DatabaseConnections\COSPW@imSPFLD@MCWINTCWDB.sde"
    facilities_streets = os.path.join(sde, "FacilitiesStreets")
    roadway_info = os.path.join(facilities_streets, "RoadwayInformation")
    fgdb_folder = r"W:\RoadwayInfo.gdb\FacilitiesStreets"
    pavement_segments = os.path.join(fgdb_folder, "PavementSegments")
    pavement_inspections = os.path.join(fgdb_folder, "PavementInspections")
    arcpy.env.overwriteOutput = True

    # Try running the simple function below
    try:
        arcpy.MakeFeatureLayer_management(roadway_info, "roadway_info")
        selection = arcpy.SelectLayerByAttribute_management("roadway_info", "NEW_SELECTION", f"MNT_TYPE LIKE '%5480%'")
        arcpy.Dissolve_management(selection, pavement_inspections, ["SPI_NBR", "ROAD_NAME", "FC", "SURF_TYP"])
        arcpy.Dissolve_management(selection, pavement_segments, ["SPI_SEG", "ROAD_NAME", "FC", "SURF_TYP"])
    except (IOError, KeyError, NameError, IndexError, TypeError, UnboundLocalError, ValueError):
        traceback_info = traceback.format_exc()
        try:
            logger.info(traceback_info)
        except NameError:
            print(traceback_info)
    except arcpy.ExecuteError:
        try:
            logger.error(arcpy.GetMessages(2))
        except NameError:
            print(arcpy.GetMessages(2))
    except:
        logger.exception("Picked up an exception!")
    finally:
        try:
            logger.info("Script Execution Complete")
        except NameError:
            pass


def main():
    roadway_information()


if __name__ == '__main__':
    main()
