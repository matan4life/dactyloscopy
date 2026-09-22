#!/usr/bin/env python3
"""One matching run on a subset named by its manifest id, written as a
candidate run record with its observation, then read back to see what the
record can and cannot give a reader. Run inside the container, with the
corpus mounted and LABDATA set to where it resolves there:

    make run-matching SUBSET=fvc2002/DB1_B
    make run-matching SUBSET=fvc2002/DB1_B EXTRACTOR=iso-extract

which is the only form that also carries the host's provenance across -
the image has no git, so the code revision, the dirty flag, the branch and
the image id arrive as RUN_CODE_REVISION, RUN_TREE_DIRTY, RUN_BRANCH and
RUN_IMAGE_ID. Without them the record still forms, marks each missing field
UNVERIFIED and itself provisional, and says so.

This script produces no number of its own. It is the command form of
implementation/library/matching.py and implementation/library/run_record.py,
which is where the mechanism lives; it imports and calls and does nothing
else, which is what implementation/library/README.md and quality/REF-013
decision 3 require.

The record is derived data and goes under $LABDATA/derived, never into the
tree; scripts/record_run.py places a finished record under runs/ on the host.

Usage: run_matching.py <subset id> [<extractor>] [<output directory>]
  extractor: mindtct (default) or iso-extract, whose ISO template goes
  through implementation/library/iso_xyt.py under the conversion the record
  carries
"""
import argparse
import json
import os
import sys

# The modules come from the tree this file sits in, whatever the working
# directory and whatever PYTHONPATH says.
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from implementation.library.matching import measure
from implementation.library.run_record import compose, rederive, write


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("subset", help="a subset id such as fvc2002/DB1_B")
    parser.add_argument("extractor", nargs="?", default="mindtct",
                        help="mindtct (default) or iso-extract")
    parser.add_argument("out", nargs="?", default=None,
                        help="where the record and its observation are "
                             "written; by default $LABDATA/derived/matching/"
                             "<subset>_<extractor>")
    args = parser.parse_args(argv)
    out = args.out
    if out is None:
        labdata = os.environ.get("LABDATA")
        if not labdata:
            raise SystemExit("FAIL: LABDATA is required when no output "
                             "directory is given")
        out = os.path.join(labdata, "derived", "matching", "%s_%s" % (
            args.subset.replace("/", "_"), args.extractor))

    run = measure(REPO, args.subset, extractor=args.extractor)
    record, observation = compose(run, REPO)
    out = write(record, observation, out)
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


if __name__ == "__main__":
    main()
