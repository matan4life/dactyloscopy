#!/usr/bin/env python3
r"""Measure what the ISO-to-.xyt conversion's choices do to the number, and
three properties of bozorth3 the conversion leans on; write the aggregate
as JSON. Run inside the container with the corpus mounted and LABDATA set:

    docker run --rm -v "<repo>:/work" -v "$LABDATA/raw:/data/raw:ro" \
      -v "$LABDATA/derived:/data/derived" -w /work -e LABDATA=/data \
      dactyloscopy:dev python3 scripts/measure_conversion.py fvc2002/DB1_B

This script produces no number of its own. It is the command form of
implementation/library/conversion_checks.py, which is where the mechanism
lives; it imports and calls and does nothing else, which is what
implementation/library/README.md and quality/REF-013 decision 3 require.
The aggregate is derived data (REF-015) and goes under
$LABDATA/derived/inv018/<subset>/.

Usage: measure_conversion.py <subset id> [<output json>]
"""
import argparse
import json
import os
import sys

# The modules come from the tree this file sits in, whatever the working
# directory and whatever PYTHONPATH says.
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from implementation.library.conversion_checks import bozorth3_properties, sweep


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("subset", help="a subset id such as fvc2002/DB1_B")
    parser.add_argument("out", nargs="?", default=None,
                        help="where the aggregate is written, as JSON; by "
                             "default $LABDATA/derived/inv018/<subset>/"
                             "conversion.json")
    args = parser.parse_args(argv)
    out = args.out
    if out is None:
        labdata = os.environ.get("LABDATA")
        if not labdata:
            raise SystemExit("FAIL: LABDATA is required when no output path "
                             "is given")
        out = os.path.join(labdata, "derived", "inv018",
                           args.subset.replace("/", "_"), "conversion.json")
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)

    print("== bozorth3, on a synthetic pair")
    props = bozorth3_properties("/tmp/inv018")
    for k, v in props.items():
        print("  %-36s %s" % (k, v))
    print()
    print("== %s under every reading of the conversion" % args.subset)
    readings = sweep(REPO, args.subset)
    with open(out, "w") as fp:
        json.dump({"subset": args.subset, "bozorth3": props,
                   "readings": readings}, fp, indent=1)
    print("wrote %s" % out)


if __name__ == "__main__":
    main()
