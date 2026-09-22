#!/usr/bin/env python3
r"""Measure which warp family predicts a held-out correspondence, write the
aggregate as JSON and print the tables quality/INV-015 carries. Run inside
the container, with the corpus mounted read-only.

    docker run --rm -v "<repo>:/work" -v "$LABDATA/raw:/data/raw:ro" \
      -w /work dactyloscopy:dev \
      python3 scripts/measure_warp_families.py \
        /data/raw/fvc2002/Dbs/Db1_b DB1_B out.json

This script produces no number of its own. It is the command form of
implementation/library/warp_families.py, with
implementation/library/warp_families_identity.py and
implementation/library/warp_families_report.py, which is where the
mechanism lives; it imports and calls and does nothing else, which is what
implementation/library/README.md and quality/REF-013 decision 3 require.

Usage: measure_warp_families.py <subset directory> <tag> <output json>
"""
import argparse
import json
import os
import sys

# The modules come from the tree this file sits in, whatever the working
# directory and whatever PYTHONPATH says.
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from implementation.library.warp_families import measure
from implementation.library.warp_families_identity import measure as identity
from implementation.library.warp_families_report import report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("subset", help="directory of the subset's images")
    parser.add_argument("tag", help="the subset's name in the aggregate")
    parser.add_argument("out", help="where the aggregate is written, as JSON")
    args = parser.parse_args(argv)
    if not os.path.isdir(args.subset):
        raise SystemExit("FAIL: no such subset directory: %s" % args.subset)

    print("== the implementation check, P-3, on synthetic problems")
    identity()
    print()
    aggregate = measure(args.subset, args.tag)
    with open(args.out, "w") as fp:
        json.dump(aggregate, fp)
    print("wrote %s" % args.out)
    print()
    report(aggregate, args.tag)


if __name__ == "__main__":
    main()
