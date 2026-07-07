#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Error: missing input file."
  echo "Usage: $0 /path/to/input-file"
  exit 1
fi

FILE="$1"
VERBOSE=""
if [[ "${2:-}" == "-vvvv" || "${2:-}" == "--verbose" ]]; then
  VERBOSE="$2"
fi

docker compose run --rm \
  -v "$(dirname "$FILE"):/input" \
  dicom-rawdata \
  python dicom_rawdata_listmode.py -fp "/input/$(basename "$FILE")" -ofp "$FILE" $VERBOSE \
  > >(grep -v '\[WARNING\]') 2> >(grep -Ev 'Container .* (Creating|Created)|\[WARNING\]' >&2)

exit 0