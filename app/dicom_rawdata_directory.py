"""
DICOM rawdata directory
Author: Chi Kin Lam

Example:
python3 dicom_rawdata_directory.py -h
python3 dicom_rawdata_directory.py -dp ##### -odp #####
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
from lib_dicomrawdata import DicomRawdataDirectory


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
        description="usage example:\n1. $ python3 dicom_rawdata_listmode.py -dp ##### -odp #####",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    # Optional
    parser.add_argument(
        "-odp",
        "--optional_directory_path",
        help="Optional file path",
        default="",
    )
    parser.add_argument(
        "-ro", "--readonly", help="Read-only", action="store_true", default=False
    )
    parser.add_argument(
        "-vvvv", "--verbose", help="Verbose", action="store_true", default=False
    )
    # Required
    required_argument = parser.add_argument_group("required arguments")
    required_argument.add_argument(
        "-dp",
        "--directory_path",
        help="File path of DICOM rawdata",
        required=True,
    )
    arguments = parser.parse_args()
    return arguments


def main(args):
    if args.verbose:
        print("DICOM rawdata directory")
    #
    dp = Path(args.directory_path)
    odp = Path(args.optional_directory_path)
    dicom_rawdata = DicomRawdataDirectory(dp, odp)
    #
    if args.readonly:
        # readonly
        # directory_info
        print("directory_info")
        print(json.dumps(dicom_rawdata.directory_info, indent=4, default=str))
        print()
    else:
        # export
        dicom_rawdata.export_directory_summary()
    #
    if args.verbose:
        # directory_info
        print("directory_info")
        print(json.dumps(dicom_rawdata.directory_info, indent=4, default=str))
        print()
    #
    print("DONE")


if __name__ == "__main__":
    arguments = set_argument()
    main(arguments)
    sys.exit()
