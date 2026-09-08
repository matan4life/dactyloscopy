#!/usr/bin/env bash
# Measure mindtct's localization noise floor under exact geometry and write the
# aggregate as JSON. Run inside the container, with the corpus mounted:
#
#   docker run --rm -v "<repo>:/work" -v "$LABDATA/raw:/data/raw:ro" \
#     -w /work dactyloscopy:dev \
#     bash scripts/measure_noise_floor.sh \n#       /data/raw/fvc2002/Dbs/Db1_b DB1_B out.json
#
# This script produces no number of its own. It is the command form of
# implementation/library/noise_floor.py, which is where the mechanism lives;
# it imports and calls and does nothing else, which is what
# implementation/library/README.md and quality/REF-013 decision 3 require.
#
# Usage: measure_noise_floor.sh <subset directory> <tag> <output json>

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
from implementation.library.noise_floor import measure

with open(sys.argv[4], "w") as fp:
    json.dump(measure(sys.argv[2], sys.argv[3]), fp)
print("wrote %s" % sys.argv[4])
PY
