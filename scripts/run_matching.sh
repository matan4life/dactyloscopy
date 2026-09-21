#!/usr/bin/env bash
# One matching run on a subset named by its manifest id, written as a
# candidate run record with its observation, then read back to see what the
# record can and cannot give a reader. Run inside the container, with the
# corpus mounted and LABDATA set to where it resolves there:
#
#   make run-matching SUBSET=fvc2002/DB1_B
#
# which is the only form that also carries the host's provenance across -
# the image has no git, so the code revision, the dirty flag, the branch and
# the image id arrive as RUN_CODE_REVISION, RUN_TREE_DIRTY, RUN_BRANCH and
# RUN_IMAGE_ID. Without them the record still forms, marks each missing field
# UNVERIFIED and itself provisional, and says so.
#
# This script produces no number of its own. It is the command form of
# implementation/library/matching.py and implementation/library/run_record.py,
# which is where the mechanism lives; it imports and calls and does nothing
# else, which is what implementation/library/README.md and quality/REF-013
# decision 3 require.
#
# The record is derived data and goes under $LABDATA/derived, never into the
# tree: what a run record is composed of is open question M-1, and this run
# is the investigation of it, not its answer.
#
# Usage: run_matching.sh <subset id> [<output directory>]

set -euo pipefail

REPO="${REPO:-/work}"
SUBSET="${1:?a subset id such as fvc2002/DB1_B is required}"
OUT="${2:-${LABDATA:?LABDATA is required}/derived/inv017/${SUBSET//\//_}}"

python3 - "$REPO" "$SUBSET" "$OUT" <<'PY'
import json
import sys

sys.path.insert(0, sys.argv[1])
from implementation.library.matching import measure
from implementation.library.run_record import compose, rederive, write

run = measure(sys.argv[1], sys.argv[2])
record, observation = compose(run, sys.argv[1])
out = write(record, observation, sys.argv[3])
print("wrote %s/results.json and observation.json" % out)
print()
print("== the record, read back on its own")
report = rederive(out)
print(json.dumps(report, indent=1))
print()
print("== the numbers")
for m in ("eer@1", "auc@1"):
    print("%s %.6f" % (m, record["metrics"][m]["value"]))
print("provisional: %s" % record["record"]["provisional"])
PY
