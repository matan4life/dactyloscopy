#!/usr/bin/env python3
r"""Measure which warp family predicts a held-out correspondence, write the
aggregate as JSON and print the tables quality/INV-015 carries. Run inside
the container, with the corpus mounted and LABDATA set to where it resolves
there:

    docker run --rm -v "<repo>:/work" -v "$LABDATA/raw:/data/raw:ro" \
      -v "$LABDATA/derived:/data/derived" -w /work -e LABDATA=/data \
      dactyloscopy:dev python3 scripts/measure_warp_families.py fvc2002/DB1_B

This script produces no number of its own. It is the command form of
implementation/library/warp_families.py, with
implementation/library/warp_families_identity.py and
implementation/library/warp_families_report.py, which is where the
mechanism lives; it imports and calls and does nothing else, which is what
implementation/library/README.md and quality/REF-013 decision 3 require.

The subset is addressed by its manifest id and found through
MAN-fvc2002.v1; every image is verified against the subset's checksum list
before the instrument reads one. The aggregate is derived data (REF-015
decision 3) and goes under $LABDATA/derived/inv015/<subset>/ unless an
output path is given.

Usage: measure_warp_families.py <subset id> [<output json>]
"""
import argparse
import json
import os
import sys

# The modules come from the tree this file sits in, whatever the working
# directory and whatever PYTHONPATH says.
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from implementation.library import corpus
from implementation.library.warp_families import measure
from implementation.library.warp_families_identity import measure as identity
from implementation.library.warp_families_report import report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("subset", help="a subset id such as fvc2002/DB1_B")
    parser.add_argument("out", nargs="?", default=None,
                        help="where the aggregate is written, as JSON; by "
                             "default $LABDATA/derived/inv015/<subset>/"
                             "warp_families.json")
    args = parser.parse_args(argv)
    out = args.out
    if out is None:
        labdata = os.environ.get("LABDATA")
        if not labdata:
            raise SystemExit("FAIL: LABDATA is required when no output path "
                             "is given")
        out = os.path.join(labdata, "derived", "inv015",
                           args.subset.replace("/", "_"), "warp_families.json")
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)

    sub = corpus.subset(REPO, args.subset)
    n = corpus.verify_images(sub)
    print("%d images verified against %s" % (n, sub["checksum_list"]["path"]),
          flush=True)
    tag = args.subset.rsplit("/", 1)[-1]

    print("== the implementation check, P-3, on synthetic problems")
    identity()
    print()
    aggregate = measure(sub["subset_dir"], tag)
    with open(out, "w") as fp:
        json.dump(aggregate, fp)
    print("wrote %s" % out)
    print()
    report(aggregate, tag)


if __name__ == "__main__":
    main()
