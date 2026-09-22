"""Compose a candidate run record from one matching run, and then find out
what a reader who has only that record can do with it.

This is the second half of `quality/INV-017`'s instrument. `matching.py`
makes the run; this module writes it down as a record with an observation
beside it, and then performs the two checks the record exists for:

  rederive    from the observation and the metric definitions in the record,
              and nothing else, compute the two numbers again;
  reproduce   from what the record names - the dataset id, the index-file
              digests, the tool identities - and the corpus and the image,
              make the run again and compare every score.

What each check needed that the record did not carry was the investigation's
finding, and `REF-016` decided the composition from it. The record this
module writes is stored as derived data outside the tree; nothing here
creates a `runs/` entry - `scripts/record_run.py` places a record there once
it is not provisional, under the id `REF-017` gives it.

Provenance that only the host can supply - the code revision, whether the
tree was dirty, the branch, the image id - arrives through the environment
from the command form's caller, because the image carries no git. A record
composed without it says so, field by field, rather than guessing.
"""
import datetime
import hashlib
import json
import os
import sys

from implementation.library import matching

RECORD_SCHEMA = "INV-017 candidate 1"

PROVENANCE_ENV = {
    "revision": "RUN_CODE_REVISION",
    "dirty": "RUN_TREE_DIRTY",
    "branch": "RUN_BRANCH",
    "image_id": "RUN_IMAGE_ID",
}


def _sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path):
    with open(path, "rb") as fp:
        return _sha256_bytes(fp.read())


def provenance(repo_root):
    """What the host told us, and what it did not.

    Each field carries a status: VERIFIED when the environment supplied it,
    UNVERIFIED when it did not. The module digests are computed here,
    because the code that produced the number is in this process."""
    out = {}
    for key, var in PROVENANCE_ENV.items():
        val = os.environ.get(var)
        if val is None or val == "":
            out[key] = {"value": None, "status": "UNVERIFIED",
                        "note": "%s was not set by the caller" % var}
        elif key == "dirty":
            out[key] = {"value": val not in ("0", "false", "clean", ""),
                        "status": "VERIFIED",
                        "note": "from %s=%r on the host" % (var, val)}
        else:
            out[key] = {"value": val, "status": "VERIFIED"}
    # Every module of the library this process has loaded when the record
    # is composed - the run, the record, the corpus, the pool, the conversion
    # if one ran - rather than a list written here that the code can outgrow;
    # the manifests are named by digest elsewhere.
    lib = os.path.abspath(os.path.join(repo_root, "implementation", "library"))
    mods = {}
    for module in list(sys.modules.values()):
        path = getattr(module, "__file__", None)
        if not path:
            continue
        path = os.path.abspath(path)
        if not path.startswith(lib + os.sep):
            continue
        rel = os.path.relpath(path, repo_root).replace(os.sep, "/")
        mods[rel] = _sha256_file(path)
    mods = dict(sorted(mods.items()))
    out["modules"] = {"value": mods, "status": "VERIFIED",
                      "note": "sha256 of every implementation/library module "
                              "loaded when the record was composed, which "
                              "pins the code that ran even when the revision "
                              "is missing"}
    provisional = any(out[k]["status"] != "VERIFIED"
                      for k in ("revision", "dirty")) or \
        bool(out["dirty"]["value"])
    return out, provisional


def compose(run, repo_root, created=None):
    """The record and the observation, as two documents."""
    res = run["resolution"]
    prov, provisional = provenance(repo_root)
    observation = run["observation"]
    obs_bytes = json.dumps(observation, indent=1, sort_keys=True).encode()
    record = {
        "record": {"kind": "run", "schema": RECORD_SCHEMA,
                   "created": created or datetime.date.today().isoformat(),
                   "provisional": provisional,
                   "provisional_note": (
                       "True when the code revision or the dirty flag is "
                       "unverified, or the tree was dirty. A provisional run "
                       "cannot support a claim.")},
        "dataset": {
            "id": res["subset_id"],
            "manifest": res["corpus_manifest"],
            "set": {"checksum_list": res["checksum_list"]["path"],
                    "sha256": res["checksum_list"]["sha256"],
                    "entries": res["checksum_list"]["entries"]},
            "images_used": run["n_images"],
            "every_image_verified_against_the_list": True,
        },
        "protocol": {
            "id": None,
            "note": ("No protocol manifest exists; MAN-fvc2002.v1 records the "
                     "organisers' index files by digest and says the protocol "
                     "they define is not its subject. The pairs are those "
                     "files, in their order, nothing added or removed."),
            "genuine": {k: v for k, v in res["index"]["MFR"].items()
                        if k != "path"},
            "impostor": {k: v for k, v in res["index"]["MFA"].items()
                         if k != "path"},
        },
        "extractor": run["extractor"],
        "matcher": run["matcher"],
        "conversion": run["conversion"],
        "tools": {
            tool: dict(t, sha256_measured=run["binaries_measured"][tool],
                       **({"library_sha256_measured":
                           run["binaries_measured"][tool + " library"]}
                          if "library" in t else {}))
            for tool, t in res["tools"].items()
        },
        "tools_manifest": res["tools_manifest"],
        "metrics_manifest": run["metrics_manifest"],
        "manifests_verified_before_run": run["manifests_verified"],
        "code": prov,
        "seed": {"value": run["seed"], "note": run["seed_note"]},
        "n_genuine": run["n_genuine"],
        "n_impostor": run["n_impostor"],
        "n_images": run["n_images"],
        "metrics": run["metrics"],
        "eer_readings": run["eer_readings"],
        "eer_readings_note": ("Every reading an equal-error rate admits, "
                              "side by side; the value under metrics is the "
                              "reading its definition text names."),
        "observation": {"path": "observation.json",
                        "sha256": _sha256_bytes(obs_bytes),
                        "bytes": len(obs_bytes)},
    }
    return record, obs_bytes


def write(record, obs_bytes, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "observation.json"), "wb") as fp:
        fp.write(obs_bytes)
    with open(os.path.join(out_dir, "results.json"), "w",
              encoding="utf-8") as fp:
        json.dump(record, fp, indent=1, sort_keys=True)
        fp.write("\n")
    return out_dir


# ------------------------------------------------------------- the checks
def rederive(record_dir):
    """From the record directory, by the instrument's own metric code: does
    the observation give back the numbers the record states?

    This checks that the observation is the observation of the record and
    that the record's counts and digests are the observation's. It does not
    check that the definition texts suffice on their own - that needs a
    reader who has not seen this code, and INV-017 F-4 is that check. The
    rank form of auc@1 is compared here with the direct pairwise count,
    which is the other half of its definition text."""
    with open(os.path.join(record_dir, "results.json"),
              encoding="utf-8") as fp:
        record = json.load(fp)
    obs_path = os.path.join(record_dir, record["observation"]["path"])
    with open(obs_path, "rb") as fp:
        obs_bytes = fp.read()
    report = {"observation_sha256_matches":
              _sha256_bytes(obs_bytes) == record["observation"]["sha256"]}
    obs = json.loads(obs_bytes)
    g = [row[3] for row in obs["pairs"] if row[2] == "genuine"]
    i = [row[3] for row in obs["pairs"] if row[2] == "impostor"]
    report["n_genuine_matches"] = len(g) == record["n_genuine"]
    report["n_impostor_matches"] = len(i) == record["n_impostor"]
    eer, at = matching.eer_at_1(g, i)
    auc = matching.auc_at_1(g, i)
    report["eer@1"] = {"recorded": record["metrics"]["eer@1"]["value"],
                       "rederived": eer,
                       "equal": eer == record["metrics"]["eer@1"]["value"],
                       "threshold_equal":
                           at["threshold"] ==
                           record["metrics"]["eer@1"]["at"]["threshold"]}
    pairwise = matching.auc_pairwise(g, i)
    report["auc@1"] = {"recorded": record["metrics"]["auc@1"]["value"],
                       "rederived": auc,
                       "equal": auc == record["metrics"]["auc@1"]["value"],
                       "pairwise": pairwise,
                       "pairwise_equals_rank_form": pairwise == auc}
    report["definitions_present"] = all(
        "definition" in record["metrics"][m] for m in ("eer@1", "auc@1"))
    report["metric_ids"] = {m: "%s@%s" % (record["metrics"][m]["id"].split("@")[0],
                                          record["metrics"][m]["version"])
                            for m in ("eer@1", "auc@1")}
    report["zero_genuine_rows_with_count_at_or_above_floor"] = [
        k for k, row in enumerate(obs["pairs"])
        if row[2] == "genuine" and row[3] == 0
        and min(obs["minutia_count"][row[0]],
                obs["minutia_count"][row[1]]) >= 10]
    return report


def reproduce(record_dir, repo_root, work=None):
    """From what the record names, make the run again and compare it.

    The record supplies the dataset id; the corpus and the image supply the
    rest. Every score is compared, and the digests the run measured are
    compared with the ones the record carries."""
    with open(os.path.join(record_dir, "results.json"),
              encoding="utf-8") as fp:
        record = json.load(fp)
    with open(os.path.join(record_dir, record["observation"]["path"]),
              encoding="utf-8") as fp:
        obs = json.load(fp)
    conv = record.get("conversion")
    if conv:
        conv = {k: v for k, v in conv.items() if k != "module"}
    again = matching.measure(repo_root, record["dataset"]["id"], work,
                             extractor=record.get("extractor", "mindtct"),
                             conversion=conv)
    scores_then = [row[3] for row in obs["pairs"]]
    scores_now = [row[3] for row in again["observation"]["pairs"]]
    pairs_then = [row[:3] for row in obs["pairs"]]
    pairs_now = [row[:3] for row in again["observation"]["pairs"]]
    diff = [k for k, (a, b) in enumerate(zip(scores_then, scores_now))
            if a != b]
    return {
        "pair_list_identical": pairs_then == pairs_now,
        "scores_identical": scores_then == scores_now
        and len(scores_then) == len(scores_now),
        "rows_differing": diff[:20], "n_rows_differing": len(diff),
        "minutia_counts_identical":
            obs["minutia_count"] == again["observation"]["minutia_count"],
        "binaries_identical": {
            tool: again["binaries_measured"][tool]
            == record["tools"][tool]["sha256_measured"]
            for tool in record["tools"]},
        "extractor_identical":
            again["extractor"] == record.get("extractor", "mindtct"),
        "set_identical":
            again["resolution"]["checksum_list"]["sha256"]
            == record["dataset"]["set"]["sha256"],
        "index_identical": {
            "genuine": again["resolution"]["index"]["MFR"]["sha256"]
            == record["protocol"]["genuine"]["sha256"],
            "impostor": again["resolution"]["index"]["MFA"]["sha256"]
            == record["protocol"]["impostor"]["sha256"]},
        "metrics_identical": {
            m: again["metrics"][m]["value"] == record["metrics"][m]["value"]
            for m in ("eer@1", "auc@1")},
    }
