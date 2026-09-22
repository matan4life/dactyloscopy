#!/usr/bin/env python3
r"""Measure the coordinate frame each extractor reports in, and print the
lines quality/INV-011 was written from. Run inside the container, with the
corpus mounted and LABDATA set to where it resolves there; the three fixture
images are read from the subset the manifest id names.

    docker run --rm -v "<repo>:/work" -v "$LABDATA/raw:/data/raw:ro" \
      -w /work -e LABDATA=/data dactyloscopy:dev \
      python3 scripts/measure_coordinate_frames.py fvc2002/DB1_B

This script produces no number of its own. It is the command form of
implementation/library/coordinate_frames.py and
implementation/library/coordinate_frames_fixture.py, which is where the
mechanism lives; it imports and calls and does nothing else, which is what
implementation/library/README.md and quality/REF-013 decision 3 require.

The subset is addressed by its manifest id and found through
MAN-fvc2002.v1; every image is verified against the subset's checksum list
before the instrument reads one. Nothing is written: the instrument prints.

Usage: measure_coordinate_frames.py <subset id>
"""
import argparse
import os
import sys

# The modules come from the tree this file sits in, whatever the working
# directory and whatever PYTHONPATH says.
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from implementation.library import corpus
from implementation.library.coordinate_frames import measure as origin_test
from implementation.library.coordinate_frames_fixture import (
    measure as fixture)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("subset", help="a subset id such as fvc2002/DB1_B")
    args = parser.parse_args(argv)

    sub = corpus.subset(REPO, args.subset)
    n = corpus.verify_images(sub)
    print("%d images verified against %s" % (n, sub["checksum_list"]["path"]),
          flush=True)
    print()
    origin_test()
    print()
    fixture(sub["subset_dir"], REPO)


if __name__ == "__main__":
    main()
