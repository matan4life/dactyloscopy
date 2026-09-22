#!/usr/bin/env bash
# Measure the angle each extractor reports for a known orientation and write
# the rows as JSON, then print the period check. Run inside the container; no
# corpus image is needed.
#
#   docker run --rm -v "<repo>:/work" -w /work dactyloscopy:dev \
#     bash scripts/measure_angle_conventions.sh out.json
#
# This script produces no number of its own. It is the command form of
# implementation/library/angle_conventions.py and
# implementation/library/angle_conventions_periods.py,
# which is where the mechanism lives; it imports and calls and does nothing
# else, which is what implementation/library/README.md and quality/REF-013
# decision 3 require.
#
# Usage: measure_angle_conventions.sh <output json>

set -euo pipefail

REPO="${REPO:-/work}"
OUT="${1:?an output path is required}"

python3 - "$REPO" "$OUT" <<'PY'
import json
import sys

sys.path.insert(0, sys.argv[1])
from implementation.library.angle_conventions import measure
from implementation.library.angle_conventions_periods import measure as periods

rows = measure()
print()
rows["periods"] = periods()
with open(sys.argv[2], "w") as fp:
    json.dump(rows, fp)
print("wrote %s" % sys.argv[2])
PY
