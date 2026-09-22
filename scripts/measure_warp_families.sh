#!/usr/bin/env bash
# Measure which warp family predicts a held-out correspondence, write the
# aggregate as JSON and print the tables quality/INV-015 carries. Run inside
# the container, with the corpus mounted read-only.
#
#   docker run --rm -v "<repo>:/work" -v "$LABDATA/raw:/data/raw:ro" \
#     -w /work dactyloscopy:dev bash scripts/measure_warp_families.sh \
#     /data/raw/fvc2002/Dbs/Db1_b DB1_B out.json
#
# This script produces no number of its own. It is the command form of
# implementation/library/warp_families.py, with
# implementation/library/warp_families_identity.py and
# implementation/library/warp_families_report.py,
# which is where the mechanism lives; it imports and calls and does nothing
# else, which is what implementation/library/README.md and quality/REF-013
# decision 3 require.
#
# Usage: measure_warp_families.sh <subset directory> <tag> <output json>

set -euo pipefail

REPO="${REPO:-/work}"
SUBSET="${1:?a subset directory is required}"
TAG="${2:?a tag is required}"
OUT="${3:?an output path is required}"

[ -d "$SUBSET" ] || { echo "FAIL: no such subset directory: $SUBSET" >&2; exit 1; }

python3 - "$REPO" "$SUBSET" "$TAG" "$OUT" <<'PY'
import json
import sys

sys.path.insert(0, sys.argv[1])
from implementation.library.warp_families import measure
from implementation.library.warp_families_identity import measure as identity
from implementation.library.warp_families_report import report

print("== the implementation check, P-3, on synthetic problems")
identity()
print()
aggregate = measure(sys.argv[2], sys.argv[3])
with open(sys.argv[4], "w") as fp:
    json.dump(aggregate, fp)
print("wrote %s" % sys.argv[4])
print()
report(aggregate, sys.argv[3])
PY
