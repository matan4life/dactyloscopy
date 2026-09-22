#!/usr/bin/env python3
r"""Measure the angle each extractor reports for a known orientation, write
the rows as JSON, print the period check, then compute the statistics of
quality/INV-012 F-2 to F-7 over the rows, write them beside the rows and
print them as tables. Run inside the container; no corpus image is needed,
and LABDATA names where the rows go:

    docker run --rm -v "<repo>:/work" -v "$LABDATA/derived:/data/derived" \
      -w /work -e LABDATA=/data dactyloscopy:dev \
      python3 scripts/measure_angle_conventions.py

This script produces no number of its own. It is the command form of
implementation/library/angle_conventions.py,
implementation/library/angle_conventions_periods.py and
implementation/library/angle_conventions_statistics.py, which is where the
mechanism lives; it imports and calls and does nothing else, which is what
implementation/library/README.md and quality/REF-013 decision 3 require.

The rows are derived data (REF-015 decision 3) and go to
$LABDATA/derived/inv012/angle_conventions.json unless an output path is
given, the statistics to angle_conventions_statistics.json beside them;
there is no subset in the path because the instrument reads no subset.

Usage: measure_angle_conventions.py [<output json>]
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
from implementation.library.angle_conventions_statistics import (
    report, statistics)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("out", nargs="?", default=None,
                        help="where the rows are written, as JSON; by "
                             "default $LABDATA/derived/inv012/"
                             "angle_conventions.json")
    args = parser.parse_args(argv)
    out = args.out
    if out is None:
        labdata = os.environ.get("LABDATA")
        if not labdata:
            raise SystemExit("FAIL: LABDATA is required when no output path "
                             "is given")
        out = os.path.join(labdata, "derived", "inv012",
                           "angle_conventions.json")
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)

    rows = measure()
    print()
    rows["periods"] = periods()
    with open(out, "w") as fp:
        json.dump(rows, fp)
    print("wrote %s" % out)
    print()

    stats = statistics(rows["rows"])
    stats_out = os.path.join(os.path.dirname(out),
                             "angle_conventions_statistics.json")
    with open(stats_out, "w") as fp:
        json.dump(stats, fp, indent=1)
    report(stats)
    print()
    print("wrote %s" % stats_out)


if __name__ == "__main__":
    main()
