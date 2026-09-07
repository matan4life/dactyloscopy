#!/usr/bin/env bash
# Verify every manifest in this repository against the things it names, and
# report what it did not verify. Run inside the container: "make verify", or
# "make verify LABDATA=<root>" to include the corpus.
#
# This script produces no number that any result depends on. It is the command
# form of implementation/library/manifest_verify.py, which is where the
# mechanism lives; a run imports that module rather than calling this, which is
# what quality/REF-013 decision 3 and quality/REF-014 decision 5 between them
# require.
#
# It is driven by the tree and by the manifests, not by a list written here:
# the set of manifests is whatever manifests/MAN-*.json matches, and what is
# checked about each field is derived from the shape the field sits in.
# quality/REF-014 decision 1 decides that, and decision 3 requires the coverage
# report below.
#
# Usage: verify_manifests.sh [corpus root]

set -euo pipefail

REPO="${REPO:-/work}"
# A manifest that declares a distribution root finds its own data through
# $LABDATA; this argument is an override for the case where it does not.
CORPUS="${1:-}"

[ -d "$REPO/manifests" ] || { echo "FAIL: no manifests at $REPO/manifests" >&2; exit 1; }

python3 - "$REPO" "$CORPUS" <<'PY'
import glob
import os
import sys

sys.path.insert(0, sys.argv[1])
from implementation.library.manifest_verify import summarise, verify

repo, corpus = sys.argv[1], (sys.argv[2] or None)
if corpus and not os.path.isdir(corpus):
    print("the corpus root %s does not exist; the corpus is not checked"
          % corpus)
    corpus = None
if corpus is None and not os.environ.get("LABDATA"):
    print("LABDATA is not set, so a manifest that names its data through it")
    print("finds nothing and its corpus checks are reported as not run.")
    print()

manifests = sorted(glob.glob(os.path.join(repo, "manifests", "MAN-*.json")))
if not manifests:
    raise SystemExit("FAIL: manifests/MAN-*.json matched nothing")

grand = {"total": 0, "checked": 0, "failed": 0, "unchecked": 0}
failures = []

for path in manifests:
    name = os.path.basename(path)
    fields = verify(path, repo, image_root="/", corpus_root=corpus)
    summary = summarise(fields)
    for key in grand:
        grand[key] += summary[key]

    print("=== %s" % name)
    print("  %d fields with a value and a status: %d checked, %d not"
          % (summary["total"], summary["checked"], summary["unchecked"]))
    for cls in sorted(summary["by_class"]):
        entry = summary["by_class"][cls]
        print("    %-13s %3d fields, %3d checked, %d failed"
              % (cls, entry["total"], entry["checked"], entry["failed"]))

    checked = [f for f in fields if f.checked]
    if checked:
        print("  checked:")
        for f in checked:
            print("    %-4s %-11s %s  %s"
                  % ("ok" if f.ok else "FAIL", f.cls, f.path, f.detail))
    for f in checked:
        if not f.ok:
            failures.append("%s  %s  %s" % (name, f.path, f.detail))

    unchecked = [f for f in fields if not f.checked]
    if unchecked:
        print("  not checked here, %d fields:" % len(unchecked))
        reasons = {}
        for f in unchecked:
            reasons.setdefault(f.detail, []).append(f)
        for reason in sorted(reasons):
            group = reasons[reason]
            print("    %s (%d)" % (reason, len(group)))
            for f in group:
                print("      %-11s %s" % (f.cls, f.path))
    print()

print("=== coverage over every manifest")
print("  %d fields with a value and a status" % grand["total"])
print("  %d checked, %d of them failing" % (grand["checked"], grand["failed"]))
print("  %d not checked here" % grand["unchecked"])
print("  %.1f%% of fields checked" % (100.0 * grand["checked"] / grand["total"]))
if not os.environ.get("LABDATA") and corpus is None:
    print("  LABDATA was not set, so no corpus digest was verified")

if failures:
    print()
    print("FAIL: %d checks did not pass" % len(failures))
    for line in failures:
        print("  " + line)
    raise SystemExit(1)
print()
print("every check that ran, passed")
PY
