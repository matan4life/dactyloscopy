#!/usr/bin/env python3
r"""Measure how the two extractors differ on the same images and write the
aggregate as JSON. Run inside the container, with the corpus mounted and
LABDATA set to where it resolves there:

    docker run --rm -v "<repo>:/work" -v "$LABDATA/raw:/data/raw:ro" \
      -v "$LABDATA/derived:/data/derived" -w /work -e LABDATA=/data \
      dactyloscopy:dev python3 scripts/measure_extractor_difference.py \
        fvc2002/DB1_B

This script produces no number of its own. It is the command form of
implementation/library/extractor_difference.py, which is where the
mechanism lives; it imports and calls and does nothing else, which is what
implementation/library/README.md and quality/REF-013 decision 3 require.

The subset is addressed by its manifest id and found through
MAN-fvc2002.v1; every image is verified against the subset's checksum list
before the instrument reads one. The aggregate is derived data (REF-015
decision 3) and goes under $LABDATA/derived/inv014/<subset>/ unless an
output path is given.

Usage: measure_extractor_difference.py <subset id> [<output json>]
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
from implementation.library.extractor_difference import measure


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("subset", help="a subset id such as fvc2002/DB1_B")
    parser.add_argument("out", nargs="?", default=None,
                        help="where the aggregate is written, as JSON; by "
                             "default $LABDATA/derived/inv014/<subset>/"
                             "extractor_difference.json")
    args = parser.parse_args(argv)
    out = args.out
    if out is None:
        labdata = os.environ.get("LABDATA")
        if not labdata:
            raise SystemExit("FAIL: LABDATA is required when no output path "
                             "is given")
        out = os.path.join(labdata, "derived", "inv014",
                           args.subset.replace("/", "_"),
                           "extractor_difference.json")
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)

    sub = corpus.subset(REPO, args.subset)
    n = corpus.verify_images(sub)
    print("%d images verified against %s" % (n, sub["checksum_list"]["path"]),
          flush=True)
    tag = args.subset.rsplit("/", 1)[-1]
    with open(out, "w") as fp:
        json.dump(measure(sub["subset_dir"], tag), fp)
    print("wrote %s" % out)


if __name__ == "__main__":
    main()
