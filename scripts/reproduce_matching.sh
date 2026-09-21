#!/usr/bin/env bash
# From a candidate run record and nothing else the record does not name, make
# the run again and compare every score with the observation. Run inside the
# container, with the corpus mounted and LABDATA set:
#
#   make reproduce-matching RECORD=$LABDATA/derived/inv017/fvc2002_DB1_B
#
# This script produces no number of its own. It is the command form of
# implementation/library/run_record.py's reproduce(), which is where the
# mechanism lives; it imports and calls and does nothing else, which is what
# implementation/library/README.md and quality/REF-013 decision 3 require.
#
# Usage: reproduce_matching.sh <record directory>

set -euo pipefail

REPO="${REPO:-/work}"
RECORD="${1:?a record directory holding results.json is required}"

[ -f "$RECORD/results.json" ] || { echo "FAIL: no results.json in $RECORD" >&2; exit 1; }

python3 - "$REPO" "$RECORD" <<'PY'
import json
import sys

sys.path.insert(0, sys.argv[1])
from implementation.library.run_record import reproduce

print(json.dumps(reproduce(sys.argv[2], sys.argv[1]), indent=1))
PY
