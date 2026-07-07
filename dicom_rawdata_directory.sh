#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Error: missing input directory."
  echo "Usage: $0 /path/to/input-directory"
  exit 1
fi

FILE="$1"
VERBOSE=""
if [[ "$2" == "-vvvv" || "$2" == "--verbose" ]]; then
  VERBOSE="$2"
fi

docker compose run --rm \
  -v "$(dirname "$FILE"):/input" \
  dicom_rawdata_directory \
  python dicom_rawdata_directory.py -dp "/input/$(basename "$FILE")" -odp "$FILE" $VERBOSE \
  > >(grep -v '\[WARNING\]') 2> >(grep -Ev 'Container .* (Creating|Created)|\[WARNING\]' >&2)

exit 0