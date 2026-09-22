#!/usr/bin/env python3
"""From a candidate run record and nothing else the record does not name, make
the run again and compare every score with the observation. Run inside the
container, with the corpus mounted and LABDATA set:

    make reproduce-matching RECORD=matching/fvc2002_DB1_B_mindtct

This script produces no number of its own. It is the command form of
implementation/library/run_record.py's reproduce(), which is where the
mechanism lives; it imports and calls and does nothing else, which is what
implementation/library/README.md and quality/REF-013 decision 3 require.

Usage: reproduce_matching.py <record directory>
"""
import argparse
import json
import os
import sys

# The modules come from the tree this file sits in, whatever the working
# directory and whatever PYTHONPATH says.
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from implementation.library.run_record import reproduce


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("record", help="a directory holding results.json")
    args = parser.parse_args(argv)
    if not os.path.isfile(os.path.join(args.record, "results.json")):
        raise SystemExit("FAIL: no results.json in %s" % args.record)

    print(json.dumps(reproduce(args.record, REPO), indent=1))


if __name__ == "__main__":
    main()
