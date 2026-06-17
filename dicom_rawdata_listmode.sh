#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Error: missing input file."
  echo "Usage: $0 /path/to/input-file"
  exit 1
fi

FILE="$1"

docker compose run --rm \
  -v "$(dirname "$FILE"):/input" \
  dicom_rawdata_listmode \
  python dicom_rawdata_listmode.py -fp "/input/$(basename "$FILE")"

exit 0