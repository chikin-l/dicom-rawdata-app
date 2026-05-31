"""
DICOM rawdata listmode
Author: Chi Kin Lam

Example:
python3 dicom_rawdata_listmode.py -h
python3 dicom_rawdata_listmode.py -fp #####
"""

# Import
# Python:
import sys
import argparse
from pathlib import Path

# 3rd party:

# Internal:
from lib_dicomrawdata import DicomRawdata


def set_argument():
    """
    Set argument

    Returns
    -------
    arguments: Namespace
        Key-value of arguments
    """
    parser = argparse.ArgumentParser(
        description="usage example:\n1. $ python3 dicom_rawdata_listmode.py -fp #####",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    # Optional
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
    print("DICOM rawdata listmode")
    #
    fp = Path(args.file_path)
    dicom_rawdata = DicomRawdata(fp)
    # export
    dicom_rawdata.export_input_raw()
    dicom_rawdata.export_header_raw()
    dicom_rawdata.export_header_json()
    dicom_rawdata.export_private_header()
    dicom_rawdata.export_lm_database_header()
    #
    print("Done")


if __name__ == "__main__":
    arguments = set_argument()
    main(arguments)
    sys.exit()
