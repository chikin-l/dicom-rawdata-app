"""
Library of DICOM rawdata utility
Author: Chi Kin Lam

Prerequisite:
pydicom
URL - https://pydicom.github.io/
"""

# Static variables
CONFIG_FILE = "config/config.json"

# Import
# Python:
import sys
import os
from pathlib import Path
import json
import re
from datetime import datetime
from xml.dom import minidom

# 3rd party:
from pydicom import dcmread

"""
DicomRawdataListmode
    transform_listmode(self)
    export_input_raw(self, fp=None)
    export_header_raw(self, fp=None)
    export_header_json(self, fp=None)
    export_private_header(self, fp=None)
    export_lm_database_header(self, fp=None)
    export_header_summary(self, fp=None)

DicomRawdataDirectory
    transform_folder(self)
"""


# Class
class DicomRawdataListmode:
    def __init__(self, fp, ofp):
        # Config
        try:
            with Path(CONFIG_FILE).open("r") as file_handler:
                self.CONFIG = json.loads(file_handler.read())
        except:
            print("Cannot read config")
            sys.exit()
        #
        # Initital
        self.file_info = {}
        self.dicom_rawdata_info = {}
        self.participant_info = {}
        self.scan_info = {}
        self.data_quality = {}
        #
        # File info
        self.file_info["input_file"] = None
        self.file_info["parent_folder"] = None
        self.file_info["optional_input_file"] = None
        self.file_info["optional_parent_folder"] = None
        self.file_info["sys_timestamp"] = datetime.now().isoformat()
        self.file_info["file_size"] = 0
        self.file_info["header_starting_position"] = 0
        self.file_info["remaining_size"] = 0
        self.file_info["reduced_size"] = 0
        #
        # DICOM rawdata info
        self.dicom_rawdata_info["input_raw"] = {
            "data": b"",
            "found": False,
            "file": self.CONFIG["DEFAULT_LM_INPUT_RAW_FILENAME"],
        }
        self.dicom_rawdata_info["header_raw"] = {
            "data": b"",
            "found": False,
            "file": self.CONFIG["DEFAULT_LM_HEADER_RAW_FILENAME"],
        }
        self.dicom_rawdata_info["header_json"] = {
            "data": "",
            "found": False,
            "file": self.CONFIG["DEFAULT_LM_HEADER_JSON_FILENAME"],
        }
        self.dicom_rawdata_info["private_header"] = {
            "data": "",
            "found": False,
            "file": self.CONFIG["DEFAULT_LM_PRIVATE_HEADER_FILENAME"],
        }
        self.dicom_rawdata_info["lm_database_header"] = {
            "data": "",
            "found": False,
            "file": self.CONFIG["DEFAULT_LM_LM_DATABASE_HEADER_FILENAME"],
        }
        #
        # Participant info
        self.participant_info["name"] = ""
        self.participant_info["initials"] = ""
        self.participant_info["mrn"] = ""
        self.participant_info["trust"] = ""
        self.participant_info["nhs_num"] = ""
        self.participant_info["dob"] = ""
        self.participant_info["age_at_scan"] = ""
        self.participant_info["age"] = 0
        self.participant_info["gender"] = ""
        self.participant_info["height"] = 0.0
        self.participant_info["weight"] = 0.0
        #
        # Scan info
        self.scan_info["accession_number"] = ""
        self.scan_info["study_date"] = ""
        self.scan_info["study_time"] = ""
        self.scan_info["acquisition_modality"] = ""
        self.scan_info["device_observer_manufacturer"] = ""
        self.scan_info["device_observer_name"] = ""
        self.scan_info["device_observer_model_name"] = ""
        self.scan_info["device_observer_serial_number"] = ""
        #
        # Data quality
        self.data_quality["bmi"] = 0
        self.data_quality["bmi_category"] = "Unknown"
        #
        # Verify fp
        if not (fp.exists() and fp.is_file() and fp.suffix == ".ptd"):
            print("Invalid file")
            sys.exit()
        #
        # Set fp
        self.file_info["input_file"] = fp
        self.file_info["parent_folder"] = fp.parent
        if ofp:
            self.file_info["optional_input_file"] = ofp.as_posix()
            self.file_info["optional_parent_folder"] = Path(ofp).parent.as_posix()
        #
        # Automatically run transform
        self.transform_listmode()

    def transform_listmode(self):
        # Start
        # Open LISTMODE file in binary format
        with self.file_info["input_file"].open("rb") as file_handler:
            # Set search from the end
            current_position = file_handler.seek(0, os.SEEK_END)
            self.file_info["file_size"] = self.file_info["remaining_size"] = (
                file_handler.tell()
            )
            self.CONFIG["DEFAULT_SETTING_OFFSET"] = min(
                self.file_info["file_size"], self.CONFIG["DEFAULT_SETTING_OFFSET"]
            )
            if self.CONFIG["DEFAULT_SETTING_DEBUG"]:
                print(f"lm_file: {self.file_info["input_file"]}")
                print(f"file_size: {self.file_info["file_size"]}")
                print(f"offset: {self.CONFIG["DEFAULT_SETTING_OFFSET"]}")
                print("")
            buffer_stack = []
            stop = False
            #
            # Start searching
            while self.file_info["remaining_size"] > 0 and stop == False:
                seek_position = (
                    self.file_info["remaining_size"]
                    - self.CONFIG["DEFAULT_SETTING_OFFSET"]
                )
                current_position = file_handler.seek(seek_position)
                buffer = file_handler.read(
                    min(
                        self.file_info["remaining_size"],
                        self.CONFIG["DEFAULT_SETTING_BYTES_TO_READ"],
                    )
                )
                if len(buffer_stack) < 128:
                    buffer_stack.append(buffer)
                elif len(buffer_stack) == 128:
                    buffer_pop = buffer_stack.pop(0)
                    buffer_stack.append(buffer)
                #
                if all(value == b"\x00" for value in buffer_stack):
                    self.dicom_rawdata_info["input_raw"]["found"] = True
                    self.file_info["header_starting_position"] = (
                        self.file_info["remaining_size"]
                        + self.CONFIG["DEFAULT_SETTING_BUFFER_SIZE"]
                        - len(buffer_stack)
                    )
                    stop = True
                self.file_info["remaining_size"] -= self.CONFIG[
                    "DEFAULT_SETTING_BYTES_TO_READ"
                ]
                self.file_info["reduced_size"] = (
                    self.file_info["file_size"] - self.file_info["remaining_size"]
                )
                if (
                    self.file_info["reduced_size"]
                    > self.CONFIG["DEFAULT_SETTING_MAX_SEARCH_SIZE"]
                ):
                    stop = True
                #
                if self.CONFIG["DEFAULT_SETTING_DEBUG"]:
                    print(f"seek_position: {seek_position}")
                    print(f"current_position: {current_position}")
                    print(f"buffer: {buffer}")
                    print(f"buffer_stack: {buffer_stack}")
                    print(
                        f"info[input_raw][found]: {self.dicom_rawdata_info["input_raw"]["found"]}"
                    )
                    print(
                        f"info[header_starting_position]: {self.file_info["header_starting_position"]}"
                    )
                    print(f"remaining_size: {self.file_info["remaining_size"]}")
                    print(f"reduced_size: {self.file_info["reduced_size"]}")
                    print(f"stop: {stop}")
                    print("")
            #
            # Exit if LM header raw not found
            if not self.dicom_rawdata_info["input_raw"]["found"]:
                return False
            #
            # Extract LM header in raw format
            if self.CONFIG["DEFAULT_SETTING_DEBUG"]:
                print("Extract LM header in raw format - Start")
            current_position = file_handler.seek(
                self.file_info["header_starting_position"]
            )
            self.dicom_rawdata_info["input_raw"]["data"] = file_handler.read()
            if self.CONFIG["DEFAULT_SETTING_DEBUG"]:
                print("Extract LM header in raw format - Done")
                print("")
            #
            # Extract LM private header in raw format
            if self.CONFIG["DEFAULT_SETTING_DEBUG"]:
                print("Extract LM private header in raw format - Start")
            lm_private_header_result = re.findall(
                self.CONFIG["REGEX_PATTERN_PRIVATE_HEADER"].encode(),
                self.dicom_rawdata_info["input_raw"]["data"],
            )
            if lm_private_header_result:
                try:
                    self.dicom_rawdata_info["private_header"]["data"] = "".join(
                        item.strip().decode("utf-8", errors="ignore")
                        for item in lm_private_header_result[0]
                    )
                except:
                    pass
                if self.dicom_rawdata_info["private_header"]["data"]:
                    self.dicom_rawdata_info["private_header"]["found"] = True
            if self.CONFIG["DEFAULT_SETTING_DEBUG"]:
                print(
                    f"info[private_header][data]: {self.dicom_rawdata_info["private_header"]["data"]}"
                )
                print(
                    f"info[private_header][found]: {self.dicom_rawdata_info["private_header"]["found"]}"
                )
                print("Extract LM private header in raw format - Done")
                print("")
            #
            # Extract LM LISTMODE database header in xml format
            if self.CONFIG["DEFAULT_SETTING_DEBUG"]:
                print("Extract LM LISTMODE database header in xml format - Start")
            lm_listmode_database_header_result = re.findall(
                self.CONFIG["REGEX_PATTERN_LM_DATABASE_HEADER"].encode(),
                self.dicom_rawdata_info["input_raw"]["data"],
            )
            if lm_listmode_database_header_result:
                try:
                    self.dicom_rawdata_info["lm_database_header"]["data"] = "".join(
                        item.strip().decode("utf-8", errors="ignore")
                        for item in lm_listmode_database_header_result[0]
                    )
                    if (
                        self.dicom_rawdata_info["lm_database_header"]["data"][-2:]
                        == ">>"
                    ):
                        self.dicom_rawdata_info["lm_database_header"]["data"] = (
                            self.dicom_rawdata_info["lm_database_header"]["data"][:-1]
                        )
                except:
                    pass
                if self.dicom_rawdata_info["lm_database_header"]["data"]:
                    self.dicom_rawdata_info["lm_database_header"]["found"] = True
            if self.CONFIG["DEFAULT_SETTING_DEBUG"]:
                print(
                    f"info[lm_database_header][data]: {self.dicom_rawdata_info["lm_database_header"]["data"]}"
                )
                print(
                    f"info[lm_database_header][found]: {self.dicom_rawdata_info["lm_database_header"]["found"]}"
                )
                print("Extract LM LISTMODE database header in xml format - Done")
                print("")
            #
            # Extract LM header info in raw format
            if self.CONFIG["DEFAULT_SETTING_DEBUG"]:
                print("Extract LM header info in raw format - Start")
            # Copy raw to json
            self.dicom_rawdata_info["header_raw"]["data"] = self.dicom_rawdata_info[
                "input_raw"
            ]["data"]
            # Remove private header
            if self.dicom_rawdata_info["private_header"]["found"]:
                self.dicom_rawdata_info["header_raw"]["data"] = self.dicom_rawdata_info[
                    "header_raw"
                ]["data"].replace(
                    self.dicom_rawdata_info["private_header"]["data"].encode("utf-8"),
                    self.CONFIG["DEFAULT_LM_PRIVATE_HEADER_REPLACED_TEXT"].encode(
                        "utf-8"
                    ),
                )
            # Remove listmode database header
            if self.dicom_rawdata_info["lm_database_header"]["found"]:
                self.dicom_rawdata_info["header_raw"]["data"] = self.dicom_rawdata_info[
                    "header_raw"
                ]["data"].replace(
                    self.dicom_rawdata_info["lm_database_header"]["data"].encode(
                        "utf-8"
                    ),
                    self.CONFIG["DEFAULT_LM_LM_DATABASE_HEADER_REPLACED_TEXT"].encode(
                        "utf-8"
                    ),
                )
            if self.dicom_rawdata_info["header_raw"]["data"]:
                self.dicom_rawdata_info["header_raw"]["found"] = True
            if self.CONFIG["DEFAULT_SETTING_DEBUG"]:
                print(
                    f"info[header_raw][data]: {self.dicom_rawdata_info["header_raw"]["data"]}"
                )
                print(
                    f"info[header_raw][found]: {self.dicom_rawdata_info["header_raw"]["found"]}"
                )
                print("Extract LM header info in raw format - Done")
                print("")
            #
            # Export LM header info to system temp file
            if self.dicom_rawdata_info["header_raw"]["found"]:
                with Path(self.CONFIG["SYS_TEMP_FILE"]).open("wb") as file_handler:
                    file_handler.write(self.dicom_rawdata_info["header_raw"]["data"])
            else:
                print("Cannot find raw header")
                return False
            #
            # Extract LM header info in json format
            if self.CONFIG["DEFAULT_SETTING_DEBUG"]:
                print("Extract LM header info in raw format - Start")
            try:
                with dcmread(
                    Path(self.CONFIG["SYS_TEMP_FILE"]),
                    force=True,
                ) as ds:
                    self.dicom_rawdata_info["header_json"]["data"] = json.loads(
                        ds.to_json()
                    )
            except:
                pass
            if self.dicom_rawdata_info["header_json"]["data"]:
                self.dicom_rawdata_info["header_json"]["found"] = True
            if self.CONFIG["DEFAULT_SETTING_DEBUG"]:
                print(
                    f"info[header_json][data]: {self.dicom_rawdata_info["header_json"]["data"]}"
                )
                print(
                    f"info[header_json][found]: {self.dicom_rawdata_info["header_json"]["found"]}"
                )
                print("Extract LM header info in json format - Done")
                print("")
            #
            #
            # Extract participant info
            # name 00100010
            if self.dicom_rawdata_info["header_json"]["data"].get("00100010"):
                try:
                    self.participant_info["name"] = (
                        self.dicom_rawdata_info["header_json"]["data"]
                        .get("00100010")
                        .get("Value")[0]
                        .get("Alphabetic")
                    )
                except:
                    pass
            #
            # initials
            if self.participant_info["name"]:
                name_list = " ".join(
                    self.participant_info["name"].strip().removesuffix(".").split("^")
                ).split(" ")
                if len(name_list) > 1 and any(
                    title in name_list[-1]
                    for title in ["MR", "MRS", "MS", "MISS", "DR"]
                ):
                    name_list = name_list[:-1]
                    self.participant_info["initials"] = "".join(
                        [initial[0] for initial in name_list]
                    )
            #
            # mrn 00100020
            if self.dicom_rawdata_info["header_json"]["data"].get("00100020"):
                try:
                    self.participant_info["mrn"] = (
                        self.dicom_rawdata_info["header_json"]["data"]
                        .get("00100020")
                        .get("Value")[0]
                    )
                except:
                    pass
            #
            # trust 00101002 0 00100021
            if self.dicom_rawdata_info["header_json"]["data"].get("00101002"):
                try:
                    self.participant_info["trust"] = (
                        self.dicom_rawdata_info["header_json"]["data"]
                        .get("00101002")
                        .get("Value")[0]
                        .get("00100021")
                        .get("Value")[0]
                    )
                except:
                    pass
            #
            # nhs_num 00101002 1 00100020
            if self.dicom_rawdata_info["header_json"]["data"].get("00101002"):
                try:
                    self.participant_info["nhs_num"] = (
                        self.dicom_rawdata_info["header_json"]["data"]
                        .get("00101002")
                        .get("Value")[1]
                        .get("00100020")
                        .get("Value")[0]
                    )
                except:
                    pass
            #
            # dob 00100030
            if self.dicom_rawdata_info["header_json"]["data"].get("00100030"):
                try:
                    self.participant_info["dob"] = (
                        self.dicom_rawdata_info["header_json"]["data"]
                        .get("00100030")
                        .get("Value")[0]
                    )
                except:
                    pass
            #
            # age_at_scan 00101010
            if self.dicom_rawdata_info["header_json"]["data"].get("00101010"):
                try:
                    self.participant_info["age_at_scan"] = (
                        self.dicom_rawdata_info["header_json"]["data"]
                        .get("00101010")
                        .get("Value")[0]
                    )
                    #
                    if "Y" in self.participant_info["age_at_scan"]:
                        self.participant_info["age"] = int(
                            self.participant_info["age_at_scan"].replace("Y", "")
                        )
                except:
                    pass
            #
            # gender 00100040
            if self.dicom_rawdata_info["header_json"]["data"].get("00100040"):
                try:
                    self.participant_info["gender"] = (
                        self.dicom_rawdata_info["header_json"]["data"]
                        .get("00100040")
                        .get("Value")[0]
                    )
                except:
                    pass
            #
            # height 00101020
            if self.dicom_rawdata_info["header_json"]["data"].get("00101020"):
                try:
                    self.participant_info["height"] = (
                        self.dicom_rawdata_info["header_json"]["data"]
                        .get("00101020")
                        .get("Value")[0]
                    )
                except:
                    pass
            #
            # weight 00101030
            if self.dicom_rawdata_info["header_json"]["data"].get("00101030"):
                try:
                    self.participant_info["weight"] = (
                        self.dicom_rawdata_info["header_json"]["data"]
                        .get("00101030")
                        .get("Value")[0]
                    )
                except:
                    pass
            #
            # accession_number 00080050
            if self.dicom_rawdata_info["header_json"]["data"].get("00080050"):
                try:
                    self.scan_info["accession_number"] = (
                        self.dicom_rawdata_info["header_json"]["data"]
                        .get("00080050")
                        .get("Value")[0]
                    )
                except:
                    pass
            #
            # study_date 00080020
            if self.dicom_rawdata_info["header_json"]["data"].get("00080020"):
                try:
                    self.scan_info["study_date"] = (
                        self.dicom_rawdata_info["header_json"]["data"]
                        .get("00080020")
                        .get("Value")[0]
                    )
                except:
                    pass
            #
            # study_time 00080030
            if self.dicom_rawdata_info["header_json"]["data"].get("00080030"):
                try:
                    self.scan_info["study_time"] = (
                        self.dicom_rawdata_info["header_json"]["data"]
                        .get("00080030")
                        .get("Value")[0]
                    )
                except:
                    pass
            #
            # acquisition_modality 00080060
            if self.dicom_rawdata_info["header_json"]["data"].get("00080060"):
                try:
                    self.scan_info["acquisition_modality"] = (
                        self.dicom_rawdata_info["header_json"]["data"]
                        .get("00080060")
                        .get("Value")[0]
                    )
                except:
                    pass
                #
                # device_observer_manufacturer 00080070
            if self.dicom_rawdata_info["header_json"]["data"].get("00080070"):
                try:
                    self.scan_info["device_observer_manufacturer"] = (
                        self.dicom_rawdata_info["header_json"]["data"]
                        .get("00080070")
                        .get("Value")[0]
                    )
                except:
                    pass
                #
                # device_observer_name 00081010
            if self.dicom_rawdata_info["header_json"]["data"].get("00081010"):
                try:
                    self.scan_info["device_observer_name"] = (
                        self.dicom_rawdata_info["header_json"]["data"]
                        .get("00081010")
                        .get("Value")[0]
                    )
                except:
                    pass
            #
            # device_observer_model_name 00081090
            if self.dicom_rawdata_info["header_json"]["data"].get("00081090"):
                try:
                    self.scan_info["device_observer_model_name"] = (
                        self.dicom_rawdata_info["header_json"]["data"]
                        .get("00081090")
                        .get("Value")[0]
                    )
                except:
                    pass
            #
            # device_observer_serial_number 00181000
            if self.dicom_rawdata_info["header_json"]["data"].get("00181000"):
                try:
                    self.scan_info["device_observer_serial_number"] = (
                        self.dicom_rawdata_info["header_json"]["data"]
                        .get("00181000")
                        .get("Value")[0]
                    )
                except:
                    pass
            #
            #
            #
            # Calculate age if age_at_scan not exist
            if self.participant_info["age"] == 0:
                if self.participant_info["dob"] and self.scan_info["study_date"]:
                    dob = datetime.strptime(self.participant_info["dob"], "%Y%m%d")
                    study_date = datetime.strptime(
                        self.scan_info["study_date"], "%Y%m%d"
                    )
                    self.participant_info["age"] = study_date.year - dob.year
                    if (study_date.month, study_date.day) < (dob.month, dob.day):
                        self.participant_info["age"] -= 1
            #
            #
            #
            # Calculate data quality
            # bmi
            # bmi_category
            # height^2 (Meter) / weight (KG)
            self.data_quality["bmi"] = (
                self.participant_info["weight"] / self.participant_info["height"] ** 2
            )
            if self.data_quality["bmi"] < 18.5:
                self.data_quality["bmi_category"] = "Underweight"
            elif self.data_quality["bmi"] >= 18.5 and self.data_quality["bmi"] < 25:
                self.data_quality["bmi_category"] = "Healthy weight"
            elif self.data_quality["bmi"] >= 25 and self.data_quality["bmi"] < 30:
                self.data_quality["bmi_category"] = "Overweight"
            elif self.data_quality["bmi"] >= 30 and self.data_quality["bmi"] < 50:
                self.data_quality["bmi_category"] = "Obese"
            else:
                self.data_quality["bmi_category"] = "Obese or Error"
            #
            # Delete system temp file
            try:
                Path(self.CONFIG["SYS_TEMP_FILE"]).unlink()
            except:
                pass

    def export_input_raw(self, fp=None):
        if self.dicom_rawdata_info["input_raw"]["found"]:
            if fp == None:
                fp = (
                    self.file_info["parent_folder"]
                    / self.dicom_rawdata_info["input_raw"]["file"]
                )
            with Path(fp).open("wb") as file_handler:
                file_handler.write(self.dicom_rawdata_info["input_raw"]["data"])
        else:
            print("Cannot find raw input")

    def export_header_raw(self, fp=None):
        if self.dicom_rawdata_info["header_raw"]["found"]:
            if fp == None:
                fp = (
                    self.file_info["parent_folder"]
                    / self.dicom_rawdata_info["header_raw"]["file"]
                )
            with Path(fp).open("wb") as file_handler:
                file_handler.write(self.dicom_rawdata_info["header_raw"]["data"])
        else:
            print("Cannot find raw header")

    def export_header_json(self, fp=None):
        if self.dicom_rawdata_info["header_json"]["found"]:
            if fp == None:
                fp = (
                    self.file_info["parent_folder"]
                    / self.dicom_rawdata_info["header_json"]["file"]
                )
            with Path(fp).open("w") as file_handler:
                json.dump(
                    self.dicom_rawdata_info["header_json"]["data"],
                    file_handler,
                    indent=self.CONFIG["JSON_INDENT"],
                    default=str,
                )
        else:
            print("Cannot find json header")

    def export_private_header(self, fp=None):
        if self.dicom_rawdata_info["private_header"]["found"]:
            if fp == None:
                fp = (
                    self.file_info["parent_folder"]
                    / self.dicom_rawdata_info["private_header"]["file"]
                )
            with Path(fp).open("w") as file_handler:
                file_handler.write(self.dicom_rawdata_info["private_header"]["data"])
        else:
            print("Cannot find private header")

    def export_lm_database_header(self, fp=None):
        if self.dicom_rawdata_info["lm_database_header"]["found"]:
            if fp == None:
                fp = (
                    self.file_info["parent_folder"]
                    / self.dicom_rawdata_info["lm_database_header"]["file"]
                )
            pretty_xml = (
                minidom.parseString(
                    self.dicom_rawdata_info["lm_database_header"]["data"]
                )
                .toprettyxml(indent="  ")
                .strip()
            )
            with Path(fp).open("w") as file_handler:
                file_handler.write(
                    # self.dicom_rawdata_info["lm_database_header"]["data"]
                    pretty_xml
                )
        else:
            print("Cannot find listmode database header")

    def export_header_summary(self, fp=None):
        if fp == None:
            fp = (
                self.file_info["parent_folder"]
                / self.CONFIG["DEFAULT_LM_HEADER_SUMMARY_JSON_FILENAME"]
            )
        with Path(fp).open("w") as file_handler:
            json.dump(
                {
                    "file_info": self.file_info,
                    "participant_info": self.participant_info,
                    "scan_info": self.scan_info,
                    "data_quality": self.data_quality,
                },
                file_handler,
                indent=self.CONFIG["JSON_INDENT"],
                default=str,
            )


class DicomRawdataDirectory:
    def __init__(self, dp, odp):
        # Config
        try:
            with Path(CONFIG_FILE).open("r") as file_handler:
                self.CONFIG = json.loads(file_handler.read())
        except:
            print("Cannot read config")
            sys.exit()
        #
        # Initital
        self.directory_info = {}
        self.directory_info["input_directory"] = None
        self.directory_info["optional_input_directory"] = None
        self.directory_info["sys_timestamp"] = datetime.now().isoformat()
        self.directory_info["directory_name"] = ""
        self.directory_info["file_all_list"] = []
        self.directory_info["file_top_list"] = []
        self.directory_info["file_calibration"] = ""
        self.directory_info["file_countrate"] = ""
        self.directory_info["file_listmode"] = ""
        self.directory_info["file_modality"] = ""
        self.directory_info["file_physio"] = ""
        self.directory_info["file_count"] = 0
        self.directory_info["directory_size"] = 0
        self.directory_info["subdirectory"] = []
        #
        # Verify dp
        if not (dp.exists() and dp.is_dir()):
            print("Invalid directory")
            sys.exit()
        #
        # Set dp
        self.directory_info["input_directory"] = dp
        self.directory_info["optional_input_directory"] = odp
        self.directory_info["directory_name"] = dp.name
        if odp:
            self.directory_info["optional_input_directory"] = odp
        #
        # Automatically run transform
        self.transform_directory()

    #
    def transform_directory(self):
        # Exclude list
        exclude_list = []
        exclude_list.append(self.CONFIG["DEFAULT_DS_SUMMARY_JSON_FILENAME"])
        exclude_list.append(self.CONFIG["DEFAULT_LM_INPUT_RAW_FILENAME"])
        exclude_list.append(self.CONFIG["DEFAULT_LM_HEADER_RAW_FILENAME"])
        exclude_list.append(self.CONFIG["DEFAULT_LM_HEADER_JSON_FILENAME"])
        exclude_list.append(self.CONFIG["DEFAULT_LM_HEADER_SUMMARY_JSON_FILENAME"])
        exclude_list.append(self.CONFIG["DEFAULT_LM_LM_DATABASE_HEADER_FILENAME"])
        exclude_list.append(self.CONFIG["DEFAULT_LM_PRIVATE_HEADER_FILENAME"])
        # Walk
        for file_fp in self.directory_info["input_directory"].rglob("*"):
            if file_fp.is_file():
                # Exclude
                if file_fp.name in exclude_list:
                    continue
                self.directory_info["file_all_list"].append(file_fp.name)
                self.directory_info["file_count"] += 1
                self.directory_info["directory_size"] += file_fp.stat().st_size
                # CALIBRATION
                if (
                    re.search(self.CONFIG["DEFAULT_DS_REGEX_CALIBRATION"], file_fp.name)
                    and file_fp.suffix == ".ptd"
                ):
                    self.directory_info["file_calibration"] = file_fp.name
                # COUNTRATE
                if (
                    re.search(self.CONFIG["DEFAULT_DS_REGEX_COUNTRATE"], file_fp.name)
                    and file_fp.suffix == ".ptd"
                ):
                    self.directory_info["file_countrate"] = file_fp.name
                # LISTMODE
                if (
                    re.search(self.CONFIG["DEFAULT_DS_REGEX_LISTMODE"], file_fp.name)
                    and file_fp.suffix == ".ptd"
                ):
                    self.directory_info["file_listmode"] = file_fp.name
                # MODALITY
                if (
                    re.search(self.CONFIG["DEFAULT_DS_REGEX_MODALITY"], file_fp.name)
                    and file_fp.suffix == ".ptd"
                ):
                    self.directory_info["file_modality"] = file_fp.name
                # DEFAULT_DS_REGEX_PHYSIO
                if (
                    re.search(self.CONFIG["DEFAULT_DS_REGEX_PHYSIO"], file_fp.name)
                    and file_fp.suffix == ".ptd"
                ):
                    self.directory_info["file_physio"] = file_fp.name
            elif file_fp.is_dir():
                self.directory_info["subdirectory"].append(file_fp.name)
        #
        # Sort
        self.directory_info["file_all_list"].sort()
        # Extract top 3
        self.directory_info["file_top_list"] = self.directory_info["file_all_list"][0:3]

    def export_directory_summary(self, fp=None):
        if fp == None:
            fp = (
                self.directory_info["input_directory"]
                / self.CONFIG["DEFAULT_DS_SUMMARY_JSON_FILENAME"]
            )
        with Path(fp).open("w") as file_handler:
            json.dump(
                {"directory_info": self.directory_info},
                file_handler,
                indent=self.CONFIG["JSON_INDENT"],
                default=str,
            )
