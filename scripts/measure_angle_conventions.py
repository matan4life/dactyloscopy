#!/usr/bin/env python3
r"""Measure the angle each extractor reports for a known orientation and write
the rows as JSON, then print the period check. Run inside the container; no
corpus image is needed.

    docker run --rm -v "<repo>:/work" -w /work dactyloscopy:dev \
      python3 scripts/measure_angle_conventions.py out.json

This script produces no number of its own. It is the command form of
implementation/library/angle_conventions.py and
implementation/library/angle_conventions_periods.py, which is where the
mechanism lives; it imports and calls and does nothing else, which is what
implementation/library/README.md and quality/REF-013 decision 3 require.

Usage: measure_angle_conventions.py <output json>
"""
import argparse
import json
import os
import sys

# The modules come from the tree this file sits in, whatever the working
# directory and whatever PYTHONPATH says.
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from implementation.library.angle_conventions import measure
from implementation.library.angle_conventions_periods import measure as periods


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("out", help="where the rows are written, as JSON")
    args = parser.parse_args(argv)

    rows = measure()
    print()
    rows["periods"] = periods()
    with open(args.out, "w") as fp:
        json.dump(rows, fp)
    print("wrote %s" % args.out)


if __name__ == "__main__":
    main()
