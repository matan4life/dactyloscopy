#!/usr/bin/env bash
# Place a finished run record into runs/, under the id REF-016 decision 5
# gives it, and print the trailers REF-016 decision 7 gives its commit. Run on
# the host, from the repository root, after `make run-matching`:
#
#   scripts/record_run.sh fvc2002/DB1_A
#   scripts/record_run.sh fvc2002/DB1_A iso-extract
#
# It refuses a record that is provisional, or whose revision is not HEAD, or
# whose observation does not digest to what the record says: a run: commit
# adds a record of a run made from exactly the tree the commit sits on. It
# copies and checks and does nothing else; nothing here computes a number.
#
# Usage: record_run.sh <subset id> [<extractor>]   (LABDATA must be set)

set -euo pipefail

SUBSET="${1:?a subset id such as fvc2002/DB1_A is required}"
EXTRACTOR="${2:-mindtct}"
: "${LABDATA:?LABDATA is required}"
SRC="$LABDATA/derived/matching/${SUBSET//\//_}_${EXTRACTOR}"
[ -f "$SRC/results.json" ] || { echo "FAIL: no results.json under $SRC" >&2; exit 1; }

HEAD_REV="$(git rev-parse HEAD)"
DIRTY="$(git status --porcelain | wc -l | tr -d ' ')"
[ "$DIRTY" = "0" ] || { echo "FAIL: the tree is dirty ($DIRTY paths); commit first" >&2; exit 1; }

python3 - "$SRC" "$HEAD_REV" "$SUBSET" "$EXTRACTOR" <<'PY'
import hashlib
import json
import os
import shutil
import sys

src, head, subset, extractor = sys.argv[1:5]
with open(os.path.join(src, "results.json"), encoding="utf-8") as fp:
    rec = json.load(fp)
if rec["record"]["provisional"]:
    raise SystemExit("FAIL: the record is provisional and cannot support a claim")
rev = rec["code"]["revision"]["value"]
if rev != head:
    raise SystemExit("FAIL: the record was made at %s and HEAD is %s; re-run"
                     % (rev[:7], head[:7]))
obs = open(os.path.join(src, "observation.json"), "rb").read()
if hashlib.sha256(obs).hexdigest() != rec["observation"]["sha256"]:
    raise SystemExit("FAIL: observation.json does not digest to what the record says")
if len(obs) > 5 * 1024 * 1024:
    raise SystemExit("FAIL: the observation is over 5 MB; REF-016 decision 5 "
                     "puts it under $LABDATA/derived/observations, not here")
if rec.get("extractor", "mindtct") != extractor:
    raise SystemExit("FAIL: the record is a %s run, not %s"
                     % (rec.get("extractor", "mindtct"), extractor))

# REF-017: the id carries the tool pair, so that two runs on one subset at
# one revision with different tools are two records
run_id = "%s-%s-%s-%s-%s" % (rec["record"]["created"].replace("-", ""),
                             subset.replace("/", "_"), extractor,
                             rec.get("matcher", "bozorth3"), rev[:7])
dst = os.path.join("runs", run_id)
if os.path.exists(dst):
    raise SystemExit("FAIL: %s exists; a run is never re-run under its own id" % dst)
os.makedirs(dst)
shutil.copyfile(os.path.join(src, "results.json"), os.path.join(dst, "results.json"))
shutil.copyfile(os.path.join(src, "observation.json"), os.path.join(dst, "observation.json"))
print("placed %s" % dst)
print()
print("subject:")
m = rec["metrics"]
print("  run: eer@1 %.4f on %s, %s + %s"
      % (m["eer@1"]["value"], subset, extractor, rec.get("matcher", "bozorth3")))
print("trailers:")
for name in ("eer@1", "auc@1"):
    print("  Result: %s %.6f" % (name, m[name]["value"]))
print("  Dataset: %s" % subset)
print("  Record: %s" % run_id)
PY
