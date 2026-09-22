#!/usr/bin/env bash
# Measure what the ISO-to-.xyt conversion's choices do to the number, and
# three properties of bozorth3 the conversion leans on; write the aggregate
# as JSON. Run inside the container with the corpus mounted and LABDATA set:
#
#   docker run --rm -v "<repo>:/work" -v "$LABDATA/raw:/data/raw:ro" \
#     -v "$LABDATA/derived:/data/derived" -w /work -e LABDATA=/data \
#     dactyloscopy:dev bash scripts/measure_conversion.sh fvc2002/DB1_B
#
# This script produces no number of its own. It is the command form of
# implementation/library/conversion_checks.py, which is where the mechanism
# lives; it imports and calls and does nothing else, which is what
# implementation/library/README.md and quality/REF-013 decision 3 require.
# The aggregate is derived data (REF-015) and goes under
# $LABDATA/derived/inv018/<subset>/.
#
# Usage: measure_conversion.sh <subset id> [<output json>]

set -euo pipefail

REPO="${REPO:-/work}"
SUBSET="${1:?a subset id such as fvc2002/DB1_B is required}"
OUT="${2:-${LABDATA:?LABDATA is required}/derived/inv018/${SUBSET//\//_}/conversion.json}"
mkdir -p "$(dirname "$OUT")"

python3 - "$REPO" "$SUBSET" "$OUT" <<'PY'
import json
import sys

sys.path.insert(0, sys.argv[1])
from implementation.library.conversion_checks import bozorth3_properties, sweep

print("== bozorth3, on a synthetic pair")
props = bozorth3_properties("/tmp/inv018")
for k, v in props.items():
    print("  %-36s %s" % (k, v))
print()
print("== %s under every reading of the conversion" % sys.argv[2])
readings = sweep(sys.argv[1], sys.argv[2])
with open(sys.argv[3], "w") as fp:
    json.dump({"subset": sys.argv[2], "bozorth3": props, "readings": readings},
              fp, indent=1)
print("wrote %s" % sys.argv[3])
PY
