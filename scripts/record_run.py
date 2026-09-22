#!/usr/bin/env python3
"""Place a finished run record into runs/, under the id REF-017 gives it, and
print the trailers REF-016 decision 7 gives its commit. Run on the host, from
the repository root, after `make run-matching`:

    make record-run SUBSET=fvc2002/DB1_A
    make record-run SUBSET=fvc2002/DB1_A EXTRACTOR=iso-extract

It refuses a record that is provisional, or whose revision is not HEAD, or
whose observation does not digest to what the record says: a run: commit
adds a record of a run made from exactly the tree the commit sits on. It
copies and checks and does nothing else; nothing here computes a number.

Usage: record_run.py <subset id> [<extractor>]   (LABDATA must be set)
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def git(*args):
    return subprocess.run(["git"] + list(args), cwd=REPO, check=True,
                          capture_output=True, text=True).stdout


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("subset", help="a subset id such as fvc2002/DB1_A")
    parser.add_argument("extractor", nargs="?", default="mindtct",
                        help="mindtct (default) or iso-extract")
    args = parser.parse_args(argv)
    subset, extractor = args.subset, args.extractor

    labdata = os.environ.get("LABDATA")
    if not labdata:
        raise SystemExit("FAIL: LABDATA is required")
    src = os.path.join(labdata, "derived", "matching",
                       "%s_%s" % (subset.replace("/", "_"), extractor))
    if not os.path.isfile(os.path.join(src, "results.json")):
        raise SystemExit("FAIL: no results.json under %s" % src)

    head = git("rev-parse", "HEAD").strip()
    dirty = len(git("status", "--porcelain").splitlines())
    if dirty:
        raise SystemExit("FAIL: the tree is dirty (%d paths); commit first"
                         % dirty)

    with open(os.path.join(src, "results.json"), encoding="utf-8") as fp:
        rec = json.load(fp)
    if rec["record"]["provisional"]:
        raise SystemExit("FAIL: the record is provisional and cannot support "
                         "a claim")
    rev = rec["code"]["revision"]["value"]
    if rev != head:
        raise SystemExit("FAIL: the record was made at %s and HEAD is %s; "
                         "re-run" % (rev[:7], head[:7]))
    with open(os.path.join(src, "observation.json"), "rb") as fp:
        obs = fp.read()
    if hashlib.sha256(obs).hexdigest() != rec["observation"]["sha256"]:
        raise SystemExit("FAIL: observation.json does not digest to what the "
                         "record says")
    if len(obs) > 5 * 1024 * 1024:
        raise SystemExit("FAIL: the observation is over 5 MB; REF-016 "
                         "decision 5 puts it under "
                         "$LABDATA/derived/observations, not here")
    if rec.get("extractor", "mindtct") != extractor:
        raise SystemExit("FAIL: the record is a %s run, not %s"
                         % (rec.get("extractor", "mindtct"), extractor))

    # REF-017: the id carries the tool pair, so that two runs on one subset
    # at one revision with different tools are two records
    matcher = rec.get("matcher", "bozorth3")
    run_id = "%s-%s-%s-%s-%s" % (rec["record"]["created"].replace("-", ""),
                                 subset.replace("/", "_"), extractor,
                                 matcher, rev[:7])
    dst = os.path.join(REPO, "runs", run_id)
    if os.path.exists(dst):
        raise SystemExit("FAIL: runs/%s exists; a run is never re-run under "
                         "its own id" % run_id)
    os.makedirs(dst)
    for name in ("results.json", "observation.json"):
        shutil.copyfile(os.path.join(src, name), os.path.join(dst, name))
    print("placed runs/%s" % run_id)
    print()
    print("subject:")
    m = rec["metrics"]
    print("  run: eer@1 %.4f on %s, %s + %s"
          % (m["eer@1"]["value"], subset, extractor, matcher))
    print("trailers:")
    for name in ("eer@1", "auc@1"):
        print("  Result: %s %.6f" % (name, m[name]["value"]))
    print("  Dataset: %s" % subset)
    print("  Record: %s" % run_id)


if __name__ == "__main__":
    main()
