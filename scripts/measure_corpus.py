#!/usr/bin/env python3
r"""Measure the corpus: the tree's totals, every subset's counts, sizes and
digests, the index files and the TIFF tags, as quality/INV-005 reports
them; write the inventory as JSON and print the tables. Run inside the
container, with the corpus mounted and LABDATA set to where it resolves
there:

    docker run --rm -v "<repo>:/work" -v "$LABDATA/raw:/data/raw:ro" \
      -v "$LABDATA/derived:/data/derived" -w /work -e LABDATA=/data \
      dactyloscopy:dev python3 scripts/measure_corpus.py

This script produces no number of its own. It is the command form of
implementation/library/corpus_inventory.py, which is where the mechanism
lives; it imports and calls and does nothing else, which is what
implementation/library/README.md and quality/REF-013 decision 3 require.

The corpus is the one MAN-fvc2002.v1 names, every subset it lists, found
through implementation/library/corpus.py. The inventory is derived data
(REF-015 decision 3) and goes to $LABDATA/derived/inv005/inventory.json
unless an output path is given; there is no subset in the path because the
instrument reads them all.

Usage: measure_corpus.py [<output json>]
"""
import argparse
import json
import os
import sys

# The modules come from the tree this file sits in, whatever the working
# directory and whatever PYTHONPATH says.
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from implementation.library.corpus_inventory import measure, report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("out", nargs="?", default=None,
                        help="where the inventory is written, as JSON; by "
                             "default $LABDATA/derived/inv005/inventory.json")
    args = parser.parse_args(argv)
    out = args.out
    if out is None:
        labdata = os.environ.get("LABDATA")
        if not labdata:
            raise SystemExit("FAIL: LABDATA is required when no output path "
                             "is given")
        out = os.path.join(labdata, "derived", "inv005", "inventory.json")
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)

    inventory = measure(REPO)
    with open(out, "w") as fp:
        json.dump(inventory, fp, indent=1)
    report(inventory)
    print()
    print("wrote %s" % out)


if __name__ == "__main__":
    main()
