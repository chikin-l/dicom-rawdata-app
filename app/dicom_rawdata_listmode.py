"""
DICOM rawdata listmode
Author: Chi Kin Lam

Example:
python3 dicom_rawdata_listmode.py -h
python3 dicom_rawdata_listmode.py -fp ##### -ofp #####
"""

# Import
# Python:
import sys
import argparse
from pathlib import Path
from pathlib import PurePath
import json

# 3rd party:

# Internal:
from lib_dicomrawdata import DicomRawdataListmode


# Path to str
def conv(v):
    if isinstance(v, PurePath):
        return str(v)
    return v


def set_argument():
    """
    Set argument

    Returns
    -------
    arguments: Namespace
        Key-value of arguments
    """
    parser = argparse.ArgumentParser(
        description="usage example:\n1. $ python3 dicom_rawdata_listmode.py -fp ##### -ofp #####",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    # Optional
    parser.add_argument(
        "-ofp",
        "--optional_file_path",
        help="Optional file path",
        default="",
    )
    parser.add_argument(
        "-vvvv", "--verbose", help="Verbose", action="store_true", default=False
    )
    # Required
    required_argument = parser.add_argument_group("required arguments")
    required_argument.add_argument(
        "-fp",
        "--file_path",
        help="File path of DICOM rawdata",
        required=True,
    )
    arguments = parser.parse_args()
    return arguments


def main(args):
    if args.verbose:
        print("DICOM rawdata listmode")
    #
    fp = Path(args.file_path)
    ofp = Path(args.optional_file_path)
    dicom_rawdata = DicomRawdataListmode(fp, ofp)
    #
    # export
    dicom_rawdata.export_input_raw()
    dicom_rawdata.export_header_raw()
    dicom_rawdata.export_header_json()
    dicom_rawdata.export_private_header()
    dicom_rawdata.export_lm_database_header()
    dicom_rawdata.export_header_summary()
    #
    if args.verbose:
        # file_info
        print("file_info")
        dicom_rawdata.file_info["input_file"] = str(
            dicom_rawdata.file_info["input_file"]
        )
        dicom_rawdata.file_info["parent_folder"] = str(
            dicom_rawdata.file_info["parent_folder"]
        )
        print(json.dumps(dicom_rawdata.file_info, indent=4, default=str))
        print()
        #
        # participant_info
        print("participant_info")
        print(json.dumps(dicom_rawdata.participant_info, indent=4, default=str))
        print()
        #
        # scan_info
        print("scan_info")
        print(json.dumps(dicom_rawdata.scan_info, indent=4, default=str))
        print()
        #
        # data_quality
        print("data_quality")
        print(json.dumps(dicom_rawdata.data_quality, indent=4, default=str))
        print()
    #
    print("DONE")


if __name__ == "__main__":
    arguments = set_argument()
    main(arguments)
    sys.exit()
