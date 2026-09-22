"""One matching run of the baseline pair: `mindtct` templates, `bozorth3`
scores, over the comparison lists the corpus distribution ships.

This is the instrument of `quality/INV-017`, which asks what a run record must
carry for its headline number to be re-derived from the record alone. The way
to find out is to make a run, write down everything, and then see what a
reader who has only the record can and cannot do with it; `run_record.py`
does the second half. This module does the first: it turns one subset of the
corpus into a score vector and two metrics, and returns them with every
input that went into them.

Nothing here is a protocol decision. The pairs are the organisers' own
`.MFR` and `.MFA` index files, found under the distribution's `Dbs` directory
and each verified against the digest `MAN-fvc2002.v1` records for it before
a line is read; the tools are invoked exactly as `MAN-tools.v2`
freezes them; and the metric definitions are the ones `MAN-metrics.v1`
registers, by id and version, read from the manifest at run time and
compared with the text this module implements - a difference stops the run,
so the code and the registration cannot drift apart silently. The text
travels with the number.

Imported, never invoked as a command, as `REF-013` decision 3 requires; the
command form is `scripts/run_matching.sh`, which imports and calls.

`measure(repo_root, subset_id, work)` returns the observation and the
metrics. Every template stays inside this run: `.xyt` files are written to
scratch and deleted, and what comes back is file names, labels, integer
scores and a minutia count per image, never a position.
"""
import hashlib
import json
import multiprocessing
import os
import subprocess

import numpy as np
from PIL import Image

from implementation.library import manifest_verify

WORK = os.environ.get("INV017_WORK", "/tmp/inv017")

# The two metrics this module implements, as text. MAN-metrics.v1 registers
# each by id and version with the same text; metric_definitions() reads the
# manifest and refuses to proceed if the registered text is not this text, so
# the code below is the definition a reader can check the number against.
# Where an equal-error rate can be read more than one way, the choice is
# stated in the text rather than made silently, and INV-017 F-4 reports
# whether each choice moves the number.
METRICS = {
    "eer@1": (
        "Threshold sweep over the distinct scores observed, and one threshold "
        "above the largest, with a pair accepted when its score is at least "
        "the threshold. FMR(t) is the fraction of impostor pairs accepted and "
        "FNMR(t) the fraction of genuine pairs rejected. The operating "
        "threshold is the one that minimises |FMR(t) - FNMR(t)|; on a tie the "
        "smallest threshold is taken. EER = (FMR(t) + FNMR(t)) / 2 at that "
        "threshold, stored as a fraction."),
    "auc@1": (
        "Exact Mann-Whitney U with average ranks for ties: every genuine and "
        "impostor score is ranked together, tied scores sharing the mean of "
        "the ranks they span, U = R_genuine - n_genuine (n_genuine + 1) / 2, "
        "and AUC = U / (n_genuine n_impostor). Equal to the probability that "
        "a genuine score exceeds an impostor score, counting a tie as one "
        "half. Stored as a fraction."),
}

UNREADABLE = ("CONFLICT",)


# ------------------------------------------------------------ the manifests
def _read(manifest, *path):
    """Read a value-and-status field, refusing a CONFLICT.

    `REF-014` decision 7: a field whose status is CONFLICT is never read. A
    run that needs such a field cannot proceed, and says so, rather than
    proceeding on a default."""
    node = manifest
    for key in path:
        node = node[key]
    status = node.get("status")
    if status in UNREADABLE:
        raise ValueError("%s has status %s and may not be read"
                         % ("/".join(path), status))
    return node["value"], status


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fp:
        for chunk in iter(lambda: fp.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_manifests_first(repo_root, corpus_root):
    """`REF-014` decision 5: a run that produces numbers verifies its
    dataset and tool manifests first, and does not start if verification
    fails. The metrics manifest is verified with them. Returns the summary
    per manifest; raises on any failed or refused check."""
    report = {}
    for name in ("MAN-fvc2002.v1.json", "MAN-tools.v2.json",
                 "MAN-metrics.v1.json"):
        path = os.path.join(repo_root, "manifests", name)
        fields = manifest_verify.verify(path, repo_root, image_root="/",
                                        corpus_root=corpus_root)
        summary = manifest_verify.summarise(fields)
        report[name] = {k: summary[k] for k in
                        ("total", "checked", "failed", "refused")}
        if summary["failed"] or summary["refused"]:
            bad = [f.path for f in fields if f.refused or
                   (f.checked and not f.ok)]
            raise ValueError("%s: %d failed, %d refused: %s" % (
                name, summary["failed"], summary["refused"], bad[:5]))
    return report


def metric_definitions(repo_root):
    """The registered metrics, from MAN-metrics.v1, checked against the text
    this module implements.

    A run record names its metrics by id and version and copies the
    registered definition beside each value. The registration is the
    manifest's; the implementation is this module's; and the only way to
    know they agree is to compare the text, which happens here on every run.
    A manifest whose text differs from METRICS is a manifest this module does
    not implement, and the run stops rather than compute one thing under the
    name of another."""
    mpath = os.path.join(repo_root, "manifests", "MAN-metrics.v1.json")
    with open(mpath, encoding="utf-8") as fp:
        man = json.load(fp)
    out = {}
    for name, text in METRICS.items():
        registered, _ = _read(man, "metrics", name, "definition")
        if registered != text:
            raise ValueError("MAN-metrics.v1 registers %s with a definition "
                             "this module does not implement" % name)
        mid, _ = _read(man, "metrics", name, "id")
        ver, _ = _read(man, "metrics", name, "version")
        out[name] = {"id": mid, "version": ver, "definition": registered}
    return {"path": "manifests/MAN-metrics.v1.json", "sha256": _sha256(mpath),
            "metrics": out}


def resolve(repo_root, subset_id):
    """Everything the run needs to locate, read from the manifests.

    The dataset is addressed by its manifest id and nothing else: the corpus
    root comes from `MAN-fvc2002.v1`'s `distribution.root`, which names
    `$LABDATA`, and the subset's directory from its `path` field. The two
    index files are found by the letter of the subset among the manifest's
    `index_files`, and each is verified against the sha256 the manifest
    carries before a single line of it is used."""
    mpath = os.path.join(repo_root, "manifests", "MAN-fvc2002.v1.json")
    with open(mpath, encoding="utf-8") as fp:
        corpus = json.load(fp)
    root_decl, _ = _read(corpus, "distribution", "root")
    root = os.path.expandvars(root_decl)
    if "$" in root:
        raise ValueError("the corpus root %r did not resolve; LABDATA is not "
                         "set" % root_decl)
    sub_rel, _ = _read(corpus, "subsets", subset_id, "path")
    subset_dir = os.path.join(root, sub_rel)
    # The set's identity is the digest of its per-file checksum list, which
    # the manifest carries beside the list's path. The list is checked
    # against that digest here, and every image the run reads is checked
    # against the list in measure(): a run on a directory that merely has the
    # subset's name is not a run on the subset.
    list_rel, _ = _read(corpus, "subsets", subset_id, "checksums")
    list_path = os.path.join(repo_root, list_rel)
    list_declared = corpus["subsets"][subset_id]["checksums"]["sha256"]
    list_got = _sha256(list_path)
    if list_got != list_declared:
        raise ValueError("%s: sha256 %s, manifest says %s"
                         % (list_rel, list_got, list_declared))
    expected = {}
    with open(list_path, encoding="ascii") as fp:
        for line in fp:
            digest, name = line.split()
            expected[name] = digest
    checksum_list = {"path": list_rel, "sha256": list_got,
                     "entries": len(expected), "expected": expected}

    letter = subset_id.rsplit("_", 1)[-1]          # DB1_B -> B
    index = {}
    for name, block in corpus["index_files"].items():
        if not name.startswith("index_"):
            continue
        stem = name[len("index_"):].split(".")[0]  # index_B.MFR -> B
        if stem.upper() != letter.upper():
            continue
        kind = name.rsplit(".", 1)[1]              # MFR or MFA
        declared, status = _read(corpus, "index_files", name, "sha256")
        path = os.path.join(root, "Dbs", name)
        got = _sha256(path)
        if got != declared:
            raise ValueError("%s: sha256 %s, manifest says %s"
                             % (name, got, declared))
        index[kind] = {"name": name, "path": path, "sha256": got,
                       "status": status}
    if set(index) != {"MFR", "MFA"}:
        raise ValueError("subset %s: expected one .MFR and one .MFA index, "
                         "found %s" % (subset_id, sorted(index)))

    tpath = os.path.join(repo_root, "manifests", "MAN-tools.v2.json")
    with open(tpath, encoding="utf-8") as fp:
        tools = json.load(fp)
    ident = {}
    for tool in ("mindtct", "bozorth3"):
        cmd, _ = _read(tools, "tools", tool, "invocation", "command")
        flags, _ = _read(tools, "tools", tool, "invocation", "flags")
        binary, _ = _read(tools, "tools", tool, "binary", "path")
        sha, _ = _read(tools, "tools", tool, "binary", "sha256")
        ident[tool] = {"command": cmd, "flags": flags, "binary": binary,
                       "sha256_manifest": sha}
    return {
        "corpus_manifest": {"path": "manifests/MAN-fvc2002.v1.json",
                            "sha256": _sha256(mpath)},
        "tools_manifest": {"path": "manifests/MAN-tools.v2.json",
                           "sha256": _sha256(tpath)},
        "subset_id": subset_id, "subset_dir": subset_dir,
        "checksum_list": checksum_list,
        "index": index, "tools": ident,
    }


def read_index(path):
    """The pairs an index file names, in file order. Every line is two names
    and a CRLF (`INV-005` F-7); nothing is reordered or de-duplicated, so a
    self-comparison the organisers' list contains stays in."""
    pairs = []
    with open(path, encoding="ascii", newline="") as fp:
        for line in fp:
            parts = line.rstrip("\r\n").split()
            if len(parts) != 2:
                raise ValueError("%s: a line with %d fields: %r"
                                 % (path, len(parts), line))
            pairs.append((parts[0], parts[1]))
    return pairs


# ---------------------------------------------------------------- the tools
def check_binaries(ident):
    """The binary in this image is the binary the manifest names, or the run
    stops: a score from a different bozorth3 is not this repository's
    number. Returns the digests actually measured."""
    got = {}
    for tool, t in ident.items():
        got[tool] = _sha256(t["binary"])
        if got[tool] != t["sha256_manifest"]:
            raise ValueError("%s at %s has sha256 %s; MAN-tools.v2 says %s"
                             % (tool, t["binary"], got[tool],
                                t["sha256_manifest"]))
    return got


def _scratch():
    d = os.path.join(WORK, str(os.getpid()))
    os.makedirs(d, exist_ok=True)
    return d


_JOB = {}


def _extract_work(name):
    """mindtct on one image, as the manifest freezes it: a PNG in, no flags.
    Returns the minutia count and the .xyt bytes; the .xyt is kept only in
    the run's own scratch, never returned to a caller outside it."""
    src = os.path.join(_JOB["subset_dir"], name)
    wk = _scratch()
    png = os.path.join(wk, "a.png")
    Image.open(src).convert("L").save(png)
    subprocess.run(["mindtct"] + _JOB["mindtct_flags"] + [png,
                    os.path.join(wk, "a")], check=True, capture_output=True)
    with open(os.path.join(wk, "a.xyt"), "rb") as fp:
        xyt = fp.read()
    for e in os.listdir(wk):
        os.remove(os.path.join(wk, e))
    count = sum(1 for line in xyt.splitlines() if line.strip())
    return {"name": name, "count": count, "xyt": xyt}


def _score_work(task):
    """bozorth3 on one pair, probe first, as the index file orders them.

    Both streams are kept. `MAN-tools.v2` records that on internal overflow
    the tool prints a score of 4000 - inside the range a real score occupies -
    and says so only on its error stream, so a run that reads stdout alone
    cannot tell an overflow from a very strong match."""
    a, b = task
    wk = _scratch()
    pa, pb = os.path.join(wk, "a.xyt"), os.path.join(wk, "b.xyt")
    with open(pa, "wb") as fp:
        fp.write(_JOB["xyt"][a])
    with open(pb, "wb") as fp:
        fp.write(_JOB["xyt"][b])
    run = subprocess.run(["bozorth3"] + _JOB["bozorth3_flags"] + [pa, pb],
                         check=True, capture_output=True, text=True)
    os.remove(pa)
    os.remove(pb)
    return int(run.stdout.strip()), run.stderr.strip()


def _cpus():
    try:
        n = len(os.sched_getaffinity(0))
    except AttributeError:
        n = os.cpu_count() or 1
    return max(1, n)


def _pool(tasks, fn):
    """Map fn over tasks in order. Both workers are pure functions of their
    input and the frozen binaries, so a pool moves no number; `imap`
    delivers in task order."""
    n = _cpus()
    if n < 2 or len(tasks) < 2 or os.environ.get("INV017_SERIAL"):
        for t in tasks:
            yield fn(t)
        return
    ctx = multiprocessing.get_context("fork")
    chunk = max(1, min(len(tasks) // (n * 4), 32))
    with ctx.Pool(n) as pool:
        for out in pool.imap(fn, tasks, chunksize=chunk):
            yield out


# -------------------------------------------------------------- the metrics
def eer_at_1(genuine, impostor):
    """`eer@1`, as METRICS["eer@1"] states it. Returns the EER and the
    threshold it was taken at, both needed to check the number."""
    g = np.asarray(genuine, dtype=np.int64)
    i = np.asarray(impostor, dtype=np.int64)
    thresholds = np.unique(np.concatenate([g, i]))
    thresholds = np.append(thresholds, thresholds[-1] + 1)
    best = None
    for t in thresholds:
        fmr = float((i >= t).sum()) / len(i)
        fnmr = float((g < t).sum()) / len(g)
        gap = abs(fmr - fnmr)
        # Strict less-than: on a tie the earlier, smaller threshold stays.
        if best is None or gap < best[0]:
            best = (gap, int(t), fmr, fnmr)
    _, t, fmr, fnmr = best
    return (fmr + fnmr) / 2.0, {"threshold": t, "fmr": fmr, "fnmr": fnmr}


def eer_variants(genuine, impostor):
    """Every reading an equal-error rate admits, computed side by side, so
    that INV-017 can say whether the choices METRICS["eer@1"] makes change
    the number on this data.

    The open choices: whether a pair at the threshold is accepted (>= or >),
    whether the sweep includes a threshold that rejects everything, and, on a
    tie in the gap |FMR - FNMR|, whether the smallest or the largest threshold
    is taken. Each combination is returned under a name; the reading
    METRICS["eer@1"] states is `>=, with reject-all, smallest`."""
    g = np.asarray(genuine, dtype=np.int64)
    i = np.asarray(impostor, dtype=np.int64)
    base = np.unique(np.concatenate([g, i]))
    out = {}
    for accept in (">=", ">"):
        for extra in ("with reject-all", "observed only"):
            ths = base if extra == "observed only" else np.append(base, base[-1] + 1)
            rows = []
            for t in ths:
                if accept == ">=":
                    fmr = float((i >= t).sum()) / len(i)
                    fnmr = float((g < t).sum()) / len(g)
                else:
                    fmr = float((i > t).sum()) / len(i)
                    fnmr = float((g <= t).sum()) / len(g)
                rows.append((abs(fmr - fnmr), int(t), fmr, fnmr))
            gap = min(r[0] for r in rows)
            tied = [r for r in rows if r[0] == gap]
            for rule, pick in (("smallest", tied[0]), ("largest", tied[-1])):
                _, t, fmr, fnmr = pick
                out["%s, %s, %s" % (accept, extra, rule)] = {
                    "eer": (fmr + fnmr) / 2.0, "threshold": t,
                    "fmr": fmr, "fnmr": fnmr, "n_tied": len(tied)}
    return out


def auc_at_1(genuine, impostor):
    """`auc@1`, as METRICS["auc@1"] states it: exact, by average ranks."""
    g = np.asarray(genuine, dtype=np.float64)
    i = np.asarray(impostor, dtype=np.float64)
    allv = np.concatenate([g, i])
    order = np.argsort(allv, kind="mergesort")
    ranks = np.empty(len(allv), dtype=np.float64)
    sorted_v = allv[order]
    k = 0
    while k < len(sorted_v):
        j = k
        while j + 1 < len(sorted_v) and sorted_v[j + 1] == sorted_v[k]:
            j += 1
        # ranks are 1-based; a run of ties from k to j shares their mean
        ranks[order[k:j + 1]] = (k + 1 + j + 1) / 2.0
        k = j + 1
    r_gen = float(ranks[:len(g)].sum())
    n_g, n_i = len(g), len(i)
    u = r_gen - n_g * (n_g + 1) / 2.0
    return u / (n_g * n_i)


def auc_pairwise(genuine, impostor):
    """The same quantity by direct enumeration, for the check in INV-017
    that the rank form and the definition's probability agree."""
    g = np.asarray(genuine, dtype=np.int64)
    i = np.asarray(impostor, dtype=np.int64)
    total = 0.0
    for chunk in range(0, len(g), 256):
        gg = g[chunk:chunk + 256][:, None]
        total += float((gg > i[None, :]).sum()) + 0.5 * float((gg == i[None, :]).sum())
    return total / (len(g) * len(i))


# ------------------------------------------------------------------ the run
def measure(repo_root, subset_id, work=None):
    """The whole run on one subset. Returns a dict with the resolution, the
    observation and the metrics; `run_record.py` composes the record."""
    if work:
        global WORK
        WORK = work
    os.makedirs(WORK, exist_ok=True)
    res = resolve(repo_root, subset_id)
    verified = verify_manifests_first(
        repo_root, os.path.dirname(os.path.dirname(res["subset_dir"])))
    print("  manifests verified: %s" % ", ".join(
        "%s %d/%d" % (k.replace(".json", ""), v["checked"], v["total"])
        for k, v in verified.items()), flush=True)
    metrics = metric_definitions(repo_root)
    digests = check_binaries(res["tools"])

    genuine = read_index(res["index"]["MFR"]["path"])
    impostor = read_index(res["index"]["MFA"]["path"])
    names = sorted({n for pr in genuine + impostor for n in pr})
    print("%s: %d genuine and %d impostor pairs over %d images"
          % (subset_id, len(genuine), len(impostor), len(names)), flush=True)

    expected = res["checksum_list"].pop("expected")
    for name in names:
        if name not in expected:
            raise ValueError("%s is named by an index file and absent from "
                             "the checksum list" % name)
        got = _sha256(os.path.join(res["subset_dir"], name))
        if got != expected[name]:
            raise ValueError("%s: sha256 %s, the checksum list says %s"
                             % (name, got, expected[name]))
    print("  %d images verified against %s"
          % (len(names), res["checksum_list"]["path"]), flush=True)

    _JOB.clear()
    _JOB.update({"subset_dir": res["subset_dir"],
                 "mindtct_flags": list(res["tools"]["mindtct"]["flags"]),
                 "bozorth3_flags": list(res["tools"]["bozorth3"]["flags"])})
    counts, xyt = {}, {}
    for out in _pool(names, _extract_work):
        counts[out["name"]] = out["count"]
        xyt[out["name"]] = out["xyt"]
    print("  extracted %d templates" % len(xyt), flush=True)
    _JOB["xyt"] = xyt

    tasks = genuine + impostor
    scored = list(_pool(tasks, _score_work))
    scores = [sc for sc, _ in scored]
    stderr = {k: err for k, (_, err) in enumerate(scored) if err}
    print("  scored %d pairs, %d with output on stderr"
          % (len(scores), len(stderr)), flush=True)
    del _JOB["xyt"]

    g_scores = scores[:len(genuine)]
    i_scores = scores[len(genuine):]
    eer, at = eer_at_1(g_scores, i_scores)
    auc = auc_at_1(g_scores, i_scores)

    pairs = ([[a, b, "genuine", s] for (a, b), s in zip(genuine, g_scores)]
             + [[a, b, "impostor", s] for (a, b), s in zip(impostor, i_scores)])
    return {
        "resolution": {k: v for k, v in res.items() if k != "subset_dir"},
        "manifests_verified": verified,
        "binaries_measured": digests,
        "observation": {
            "pairs": pairs,
            "minutia_count": counts,
            "stderr_by_row": stderr,
            "overflow_sentinel_rows": [k for k, s in enumerate(scores)
                                       if s == 4000],
            "note": ("One row per line of the index files, in their order: "
                     "probe, gallery, list, bozorth3 score. minutia_count is "
                     "the number of lines mindtct wrote to each .xyt, carried "
                     "because bozorth3 returns 0 both below its minminutiae "
                     "floor and on an empty template, and a zero is otherwise "
                     "indistinguishable from a non-match. stderr_by_row is "
                     "whatever bozorth3 wrote to its error stream, by row, "
                     "for the rows where it wrote anything; "
                     "overflow_sentinel_rows lists rows whose score is the "
                     "4000 the tool returns on overflow."),
        },
        "metrics_manifest": {"path": metrics["path"],
                             "sha256": metrics["sha256"]},
        "metrics": {
            "eer@1": dict(metrics["metrics"]["eer@1"], value=eer, at=at),
            "auc@1": dict(metrics["metrics"]["auc@1"], value=auc),
        },
        "eer_readings": eer_variants(g_scores, i_scores),
        "n_genuine": len(genuine), "n_impostor": len(impostor),
        "n_images": len(names),
        "seed": None,
        "seed_note": "No random number is drawn anywhere in this run.",
    }
