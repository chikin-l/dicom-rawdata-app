"""
Library of DICOM rawdata utility
Author: Chi Kin Lam

Prerequisite:
pydicom
URL - https://pydicom.github.io/
"""

# Static variables
CONFIG_FILE = "config.json"

# Import
# Python:
import sys
import os
from pathlib import Path
import json
import datetime
import re

# 3rd party:
from pydicom import dcmread


# Class
class DicomRawdata:
    def __init__(self, fp):
        # Initital
        self.lm_file = Path(fp)
        # Verify fp
        if not self.lm_file.exists() or not self.lm_file.is_file():
            print("Invalid file")
            sys.exit()
        # Read config
        try:
            with Path(CONFIG_FILE).open("r") as file_handler:
                self.CONFIG = json.loads(file_handler.read())
        except:
            print("Cannot read config")
            sys.exit()
        # Set variables
        self.parent_folder = self.lm_file.parent
        self.info = {}
        self.info["input_raw"] = {
            "data": b"",
            "found": False,
            "file": self.CONFIG["DEFAULT_LM_INPUT_RAW_FILENAME"],
        }
        self.info["header_raw"] = {
            "data": b"",
            "found": False,
            "file": self.CONFIG["DEFAULT_LM_HEADER_RAW_FILENAME"],
        }
        self.info["header_json"] = {
            "data": "",
            "found": False,
            "file": self.CONFIG["DEFAULT_LM_HEADER_JSON_FILENAME"],
        }
        self.info["private_header"] = {
            "data": "",
            "found": False,
            "file": self.CONFIG["DEFAULT_LM_PRIVATE_HEADER_FILENAME"],
        }
        self.info["lm_database_header"] = {
            "data": "",
            "found": False,
            "file": self.CONFIG["DEFAULT_LM_LM_DATABASE_HEADER_FILENAME"],
        }
        self.info["header_starting_position"] = 0
        self.max_search_size = 8192
        self.offset = 0
        self.bytes_to_read = 1
        self.buffer_size = 128
        self.file_size = 0
        self.remaining_size = 0
        self.reduced_size = 0
        self.overwrite = False
        self.debug = False
        #
        # Automatically run transform
        self.transform_listmode()

    def transform_listmode(self):
        # Start
        # Open LISTMODE file in binary format
        with self.lm_file.open("rb") as file_handler:
            # Set search from the end
            current_position = file_handler.seek(0, os.SEEK_END)
            self.file_size = self.remaining_size = file_handler.tell()
            self.offset = min(self.file_size, self.offset)
            if self.debug:
                print(f"lm_file: {self.lm_file}")
                print(f"file_size: {self.file_size}")
                print(f"offset: {self.offset}")
                print("")
            buffer_stack = []
            stop = False
            #
            # Start searching
            while self.remaining_size > 0 and stop == False:
                seek_position = self.remaining_size - self.offset
                current_position = file_handler.seek(seek_position)
                buffer = file_handler.read(min(self.remaining_size, self.bytes_to_read))
                if len(buffer_stack) < 128:
                    buffer_stack.append(buffer)
                elif len(buffer_stack) == 128:
                    buffer_pop = buffer_stack.pop(0)
                    buffer_stack.append(buffer)
                #
                if all(value == b"\x00" for value in buffer_stack):
                    self.info["input_raw"]["found"] = True
                    self.info["header_starting_position"] = (
                        self.remaining_size + self.buffer_size - len(buffer_stack)
                    )
                    stop = True
                self.remaining_size -= self.bytes_to_read
                reduced_size = self.file_size - self.remaining_size
                if reduced_size > self.max_search_size:
                    stop = True
                #
                if self.debug:
                    print(f"seek_position: {seek_position}")
                    print(f"current_position: {current_position}")
                    print(f"buffer: {buffer}")
                    print(f"buffer_stack: {buffer_stack}")
                    print(f"info[input_raw][found]: {self.info["input_raw"]["found"]}")
                    print(
                        f"info[header_starting_position]: {self.info["header_starting_position"]}"
                    )
                    print(f"remaining_size: {self.remaining_size}")
                    print(f"reduced_size: {reduced_size}")
                    print(f"stop: {stop}")
                    print("")
            #
            # Exit if LM header raw not found
            if not self.info["input_raw"]["found"]:
                return False
            #
            # Extract LM header in raw format
            if self.debug:
                print("Extract LM header in raw format - Start")
            current_position = file_handler.seek(self.info["header_starting_position"])
            self.info["input_raw"]["data"] = file_handler.read()
            if self.debug:
                print("Extract LM header in raw format - Done")
                print("")
            #
            # Extract LM private header in raw format
            if self.debug:
                print("Extract LM private header in raw format - Start")
            lm_private_header_result = re.findall(
                self.CONFIG["REGEX_PATTERN_PRIVATE_HEADER"].encode(),
                self.info["input_raw"]["data"],
            )
            if lm_private_header_result:
                try:
                    self.info["private_header"]["data"] = "".join(
                        item.strip().decode("utf-8", errors="ignore")
                        for item in lm_private_header_result[0]
                    )
                except:
                    pass
                if self.info["private_header"]["data"]:
                    self.info["private_header"]["found"] = True
            if self.debug:
                print(
                    f"info[private_header][data]: {self.info["private_header"]["data"]}"
                )
                print(
                    f"info[private_header][found]: {self.info["private_header"]["found"]}"
                )
                print("Extract LM private header in raw format - Done")
                print("")
            #
            # Extract LM LISTMODE database header in xml format
            if self.debug:
                print("Extract LM LISTMODE database header in xml format - Start")
            lm_listmode_database_header_result = re.findall(
                self.CONFIG["REGEX_PATTERN_LM_DATABASE_HEADER"].encode(),
                self.info["input_raw"]["data"],
            )
            if lm_listmode_database_header_result:
                try:
                    self.info["lm_database_header"]["data"] = "".join(
                        item.strip().decode("utf-8", errors="ignore")
                        for item in lm_listmode_database_header_result[0]
                    )
                    if self.info["lm_database_header"]["data"][-2:] == ">>":
                        self.info["lm_database_header"]["data"] = self.info[
                            "lm_database_header"
                        ]["data"][:-1]
                except:
                    pass
                if self.info["lm_database_header"]["data"]:
                    self.info["lm_database_header"]["found"] = True
            if self.debug:
                print(
                    f"info[lm_database_header][data]: {self.info["lm_database_header"]["data"]}"
                )
                print(
                    f"info[lm_database_header][found]: {self.info["lm_database_header"]["found"]}"
                )
                print("Extract LM LISTMODE database header in xml format - Done")
                print("")
            #
            # Extract LM header info in raw format
            if self.debug:
                print("Extract LM header info in raw format - Start")
            # Copy raw to json
            self.info["header_raw"]["data"] = self.info["input_raw"]["data"]
            # Remove private header
            if self.info["private_header"]["found"]:
                self.info["header_raw"]["data"] = self.info["header_raw"][
                    "data"
                ].replace(
                    self.info["private_header"]["data"].encode("utf-8"),
                    b"PRIVATE_HEADER",
                )
            # Remove listmode database header
            if self.info["lm_database_header"]["found"]:
                self.info["header_raw"]["data"] = self.info["header_raw"][
                    "data"
                ].replace(
                    self.info["lm_database_header"]["data"].encode("utf-8"),
                    b"LISTMODE_DATABASE_HEADER",
                )
            if self.info["header_raw"]["data"]:
                self.info["header_raw"]["found"] = True
            if self.debug:
                print(f"info[header_raw][data]: {self.info["header_raw"]["data"]}")
                print(f"info[header_raw][found]: {self.info["header_raw"]["found"]}")
                print("Extract LM header info in raw format - Done")
                print("")
            #
            # Export LM header info to system temp file
            if self.info["header_raw"]["found"]:
                with Path(self.CONFIG["SYS_TEMP_FILE"]).open("wb") as file_handler:
                    file_handler.write(self.info["header_raw"]["data"])
            else:
                print("Cannot find raw header")
                return False
            #
            # Extract LM header info in json format
            if self.debug:
                print("Extract LM header info in raw format - Start")
            try:
                with dcmread(
                    Path(self.CONFIG["SYS_TEMP_FILE"]),
                    force=True,
                ) as ds:
                    self.info["header_json"]["data"] = json.loads(ds.to_json())
            except:
                pass
            if self.info["header_json"]["data"]:
                self.info["header_json"]["found"] = True
            if self.debug:
                print(f"info[header_json][data]: {self.info["header_json"]["data"]}")
                print(f"info[header_json][found]: {self.info["header_json"]["found"]}")
                print("Extract LM header info in json format - Done")
                print("")
            #
            # Delete system temp file
            try:
                Path(self.CONFIG["SYS_TEMP_FILE"]).unlink()
            except:
                pass

    def export_input_raw(self):
        if self.info["input_raw"]["found"]:
            with Path(self.info["input_raw"]["file"]).open("wb") as file_handler:
                file_handler.write(self.info["input_raw"]["data"])
        else:
            print("Cannot find raw input")

    def export_header_raw(self):
        if self.info["header_raw"]["found"]:
            with Path(self.info["header_raw"]["file"]).open("wb") as file_handler:
                file_handler.write(self.info["header_raw"]["data"])
        else:
            print("Cannot find raw header")

    def export_header_json(self):
        if self.info["header_json"]["found"]:
            with Path(self.info["header_json"]["file"]).open("w") as file_handler:
                json.dump(self.info["header_json"]["data"], file_handler)
        else:
            print("Cannot find json header")

    def export_private_header(self):
        if self.info["private_header"]["found"]:
            with Path(self.info["private_header"]["file"]).open("w") as file_handler:
                file_handler.write(self.info["private_header"]["data"])
        else:
            print("Cannot find private header")

    def export_lm_database_header(self):
        if self.info["lm_database_header"]["found"]:
            with Path(self.info["lm_database_header"]["file"]).open(
                "w"
            ) as file_handler:
                file_handler.write(self.info["lm_database_header"]["data"])
        else:
            print("Cannot find listmode database header")
