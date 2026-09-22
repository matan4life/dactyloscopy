#!/usr/bin/env python3
r"""Measure the coordinate frame each extractor reports in, and print the
lines quality/INV-011 was written from. Run inside the container, with the
three fixture images mounted read-only.

    docker run --rm -v "<repo>:/work" -v "<fixture>:/fixture:ro" \
      -w /work dactyloscopy:dev \
      python3 scripts/measure_coordinate_frames.py /fixture

This script produces no number of its own. It is the command form of
implementation/library/coordinate_frames.py and
implementation/library/coordinate_frames_fixture.py, which is where the
mechanism lives; it imports and calls and does nothing else, which is what
implementation/library/README.md and quality/REF-013 decision 3 require.

Usage: measure_coordinate_frames.py <fixture directory>
"""
import argparse
import os
import sys

# The modules come from the tree this file sits in, whatever the working
# directory and whatever PYTHONPATH says.
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from implementation.library.coordinate_frames import measure as origin_test
from implementation.library.coordinate_frames_fixture import (
    measure as fixture)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("fixture", help="directory of the three fixture images")
    args = parser.parse_args(argv)
    if not os.path.isdir(args.fixture):
        raise SystemExit("FAIL: no such directory: %s" % args.fixture)

    origin_test()
    print()
    fixture(args.fixture, REPO)


if __name__ == "__main__":
    main()
