"""The instrument of `quality/INV-016`: mindtct's localization noise floor.

Two crops of the same pixels differing by an exact integer translation are
extracted independently and both outputs are mapped back into the source's own
.xyt frame, where the true displacement is zero everywhere. No pixel is
resampled and no border is invented, so the deviation that remains is the
extractor's, not a deformation's.

Imported, never invoked as a command, as `REF-013` decision 3 requires; the
command form is `scripts/measure_noise_floor.sh`, which imports and calls.

`measure(src_dir, tag)` returns the aggregate the record is written from. Every
minutia stays inside this run: positions are read, forked into the worker
processes of a pool and passed back between them over a pipe, and they reach
no file and no return value. What comes back is counts, histograms and
residual summaries, never a position.

The pool runs one image per task. It moves no number because this measurement
draws from no shared stream: N-3's noise comes from a generator built per
image and per sigma from the image's index in the sorted listing, so an image
is a pure function of its index and its file. Order still decides where values
land, and that is preserved - the pool returns in task order and the parent
merges in listing order, because `summ` reduces float32 arrays and the
accumulators' insertion order is the aggregate's key order. `INV016_SERIAL=1`
takes the sequential path.
"""
import filecmp
import math
import os
import subprocess
from array import array
from collections import Counter, defaultdict

import numpy as np
from PIL import Image

from implementation.library import pool

WORK = os.environ.get("INV016_WORK", "/tmp/inv016")

DS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 16]
SIGMAS = [1.0, 2.0, 4.0, 8.0]
PAIR_R = 15.0          # N-2's radius, used for the pairing throughout
MARGIN = 16            # px kept clear of either crop's own border
NMIN = 12              # images with fewer minutiae are excluded
QM_T = 1
BLOCK = 8
BANDS = [0, 30, 60, 90, 120, 150, 10 ** 9]
BANDNAMES = ["0-30", "30-60", "60-90", "90-120", "120-150", "150+"]
SEED = 20260908
EXTS = ["brw", "dm", "hcm", "lcm", "lfm", "min", "qm", "xyt"]


def band_of(r):
    for k in range(len(BANDS) - 1):
        if BANDS[k] <= r < BANDS[k + 1]:
            return k
    return len(BANDS) - 2


def run(img, root):
    wk = pool.scratch(WORK)
    p = "%s/%s.png" % (wk, root)
    img.save(p)
    subprocess.run(["mindtct", p, "%s/%s" % (wk, root)], check=True,
                   capture_output=True)
    return [tuple(float(v) for v in l.split())
            for l in open("%s/%s.xyt" % (wk, root))]


def mask_of(root, h):
    wk = pool.scratch(WORK)
    q = np.array([[int(v) for v in l.split()]
                  for l in open("%s/%s.qm" % (wk, root))])
    ys, xs = np.nonzero(q >= QM_T)
    if not len(xs):
        return None
    return (float(xs.mean() + 0.5) * BLOCK,
            h - float(ys.mean() + 0.5) * BLOCK,
            float(len(xs)) * BLOCK * BLOCK)


def pair(a, b, r=PAIR_R):
    """Mutual nearest neighbour within r, on source-frame positions."""
    if not len(a) or not len(b):
        return []
    A = np.asarray(a, dtype=float)
    B = np.asarray(b, dtype=float)
    d = np.hypot(A[:, None, 0] - B[None, :, 0], A[:, None, 1] - B[None, :, 1])
    na, nb = d.argmin(1), d.argmin(0)
    out = []
    for i in range(len(A)):
        j = na[i]
        if nb[j] == i and d[i, j] <= r:
            out.append((i, int(j), float(d[i, j])))
    return out


def summ(store, keyf):
    out = {}
    for kk, v in store.items():
        a = np.asarray(v)
        out[keyf(kk)] = {
            "n": int(len(a)),
            "rms": float(np.sqrt((a ** 2).mean())) if len(a) else None,
            "p90": float(np.percentile(a, 90)) if len(a) else None,
            "median": float(np.median(a)) if len(a) else None,
            "max": float(a.max()) if len(a) else None,
            "zero_frac": float((a == 0).mean()) if len(a) else None}
    return out


def k3(kk):
    return "%s|%d|%s" % (kk[0], kk[1], BANDNAMES[kk[2]])


def k2(kk):
    return "%g|%s" % (kk[0], BANDNAMES[kk[1]])


def pooled(store, keyf):
    agg = defaultdict(lambda: [0, 0.0])
    for kk, v in store.items():
        a = np.asarray(v)
        g = keyf(kk)
        agg[g][0] += len(a)
        agg[g][1] += float((a ** 2).sum())
    return {str(g): {"n": v[0], "rms": math.sqrt(v[1] / v[0]) if v[0] else None}
            for g, v in agg.items()}


def _image_work(task):
    """Everything one image contributes, as a pool task.

    The only random numbers this measurement draws are N-3's photometric
    noise, and they come from a generator built fresh per image and per sigma
    as `np.random.default_rng(SEED + int(sg) * 1000 + k)`, where `k` is the
    image's index in the sorted listing.  Nothing here reads a stream that
    another image advanced, so the noise an image sees is fixed by its place
    in the listing and not by when, or in what order, it is computed: an image
    is a pure function of its index and its file, and a pool moves no number.

    The accumulators below are the module's own, one image deep.  The caller
    merges them in listing order, so both the order values are appended in and
    the order keys are first inserted in are a sequential run's.  Both matter:
    `summ` and `pooled` reduce float32 arrays, where the sum depends on the
    order of the terms, and the accumulator dicts' insertion order is the key
    order of the JSON the record is written from."""
    k, path = task
    wk = pool.scratch(WORK)
    n1 = defaultdict(lambda: array('f'))
    n1e = defaultdict(lambda: array('f'))
    n2 = defaultdict(lambda: [0, 0, 0, 0])
    n2raw = defaultdict(lambda: [0, 0, 0, 0])
    n3 = defaultdict(lambda: array('f'))
    n3a = defaultdict(lambda: array('f'))
    n3n = defaultdict(lambda: [0, 0, 0, 0])
    cropA = defaultdict(lambda: array('f'))
    cropB = defaultdict(lambda: array('f'))
    null_dev = array('f')
    null_un = [0, 0]
    det = {"checked": 0, "identical": 0, "files": Counter()}
    img = Image.open(path).convert("L")
    W, H = img.size
    xs = run(img, "s")
    if len(xs) < NMIN:
        # As in the sequential form, an excluded image leaves its scratch
        # files behind: the next image's mindtct rewrites every one of them.
        return {"count": len(xs), "excluded": True}
    mc = mask_of("s", H)
    cx, cy, _ = mc
    S = [(p[0], p[1]) for p in xs]

    # ---- N-0, determinism: the same file twice, every output compared
    run(img, "s2")
    det["checked"] += 1
    same = True
    for e in EXTS:
        ok = filecmp.cmp("%s/s.%s" % (wk, e), "%s/s2.%s" % (wk, e),
                         shallow=False)
        if not ok:
            det["files"][e] += 1
            same = False
    det["identical"] += 1 if same else 0

    # ---- the null-shift control: d = 0, no noise, S against its own rerun
    S2 = [(float(v.split()[0]), float(v.split()[1]))
          for v in open("%s/s2.xyt" % wk)]
    pr = pair(S, S2)
    for i, j, dd in pr:
        null_dev.append(dd)
    null_un[0] += len(S) - len(pr)
    null_un[1] += len(S)

    for direction in ("h", "v"):
        for d in DS:
            if direction == "h":
                A = img.crop((d, 0, W, H))
                B = img.crop((0, 0, W - d, H))
                # source-frame maps
                def to_src_a(p, d=d):
                    return (p[0] + d, p[1])

                def to_src_b(p):
                    return (p[0], p[1])
                lo, hi = d + MARGIN, W - d - MARGIN
                axis = 0
            else:
                A = img.crop((0, d, W, H))
                B = img.crop((0, 0, W, H - d))

                def to_src_a(p):
                    return (p[0], p[1])

                def to_src_b(p, d=d):
                    return (p[0], p[1] + d)
                lo, hi = d + MARGIN, H - d - MARGIN
                axis = 1
            pa = [to_src_a(p) for p in run(A, "a")]
            pb = [to_src_b(p) for p in run(B, "b")]

            def keep(p, lo=lo, hi=hi, axis=axis):
                return lo <= p[axis] < hi
            ka = [p for p in pa if keep(p)]
            kb = [p for p in pb if keep(p)]
            pr = pair(ka, kb)
            for i, j, dd in pr:
                r = math.hypot(ka[i][0] - cx, ka[i][1] - cy)
                bnd = band_of(r)
                n1[(direction, d, bnd)].append(
                    abs(ka[i][axis] - kb[j][axis]))
                n1e[(direction, d, bnd)].append(dd)
            mA = set(i for i, _, _ in pr)
            mB = set(j for _, j, _ in pr)
            for i, p in enumerate(ka):
                bnd = band_of(math.hypot(p[0] - cx, p[1] - cy))
                n2[(direction, d, bnd)][0] += 1
                n2[(direction, d, bnd)][1] += 0 if i in mA else 1
            for j, p in enumerate(kb):
                bnd = band_of(math.hypot(p[0] - cx, p[1] - cy))
                n2[(direction, d, bnd)][2] += 1
                n2[(direction, d, bnd)][3] += 0 if j in mB else 1
            prr = pair(pa, pb)
            mAr = set(i for i, _, _ in prr)
            mBr = set(j for _, j, _ in prr)
            for i, p in enumerate(pa):
                bnd = band_of(math.hypot(p[0] - cx, p[1] - cy))
                n2raw[(direction, d, bnd)][0] += 1
                n2raw[(direction, d, bnd)][1] += 0 if i in mAr else 1
            for j, p in enumerate(pb):
                bnd = band_of(math.hypot(p[0] - cx, p[1] - cy))
                n2raw[(direction, d, bnd)][2] += 1
                n2raw[(direction, d, bnd)][3] += 0 if j in mBr else 1

            # ---- crop controls, common region only.  S and B share an
            # origin, so S against B changes the extent and not the block
            # grid's phase; S against A changes both.
            ks = [p for p in S if keep(p)]
            for store, other in ((cropA, ka), (cropB, kb)):
                for i, j, dd in pair(ks, other):
                    bnd = band_of(math.hypot(ks[i][0] - cx, ks[i][1] - cy))
                    store[(direction, d, bnd)].append(dd)

    # ---- N-3: d = 0, photometric noise only
    arr = np.asarray(img, dtype=np.float64)
    for sg in SIGMAS:
        r2 = np.random.default_rng(SEED + int(sg) * 1000 + k)
        noisy = np.clip(np.rint(arr + r2.normal(0.0, sg, arr.shape)),
                        0, 255).astype(np.uint8)
        pn = [(p[0], p[1]) for p in run(Image.fromarray(noisy, "L"), "n")]
        pr = pair(S, pn)
        for i, j, dd in pr:
            bnd = band_of(math.hypot(S[i][0] - cx, S[i][1] - cy))
            n3[(sg, bnd)].append(dd)
            n3a[(sg, bnd)].append(abs(S[i][0] - pn[j][0]))
        mA = set(i for i, _, _ in pr)
        mB = set(j for _, j, _ in pr)
        for i, p in enumerate(S):
            bnd = band_of(math.hypot(p[0] - cx, p[1] - cy))
            n3n[(sg, bnd)][0] += 1
            n3n[(sg, bnd)][1] += 0 if i in mA else 1
        for j, p in enumerate(pn):
            bnd = band_of(math.hypot(p[0] - cx, p[1] - cy))
            n3n[(sg, bnd)][2] += 1
            n3n[(sg, bnd)][3] += 0 if j in mB else 1

    for e in os.listdir(wk):
        os.remove(os.path.join(wk, e))
    return {"count": len(xs), "excluded": False, "det": det,
            "null_dev": null_dev, "null_un": null_un,
            "n1": dict(n1), "n1e": dict(n1e), "n2": dict(n2),
            "n2raw": dict(n2raw), "n3": dict(n3), "n3a": dict(n3a),
            "n3n": dict(n3n), "cropA": dict(cropA), "cropB": dict(cropB)}


def measure(src_dir, tag):
    """Run the whole measurement over one subset directory."""
    os.makedirs(WORK, exist_ok=True)
    # ------------------------------------------------------------ accumulators
    n1 = defaultdict(lambda: array('f'))        # (dir, d, band) -> along deviation
    n1e = defaultdict(lambda: array('f'))       # (dir, d, band) -> 2-D deviation
    n2 = defaultdict(lambda: [0, 0, 0, 0])      # (dir, d, band) -> nA, unA, nB, unB
    n2raw = defaultdict(lambda: [0, 0, 0, 0])   # the same without the margin
    n3 = defaultdict(lambda: array('f'))        # (sigma, band) -> 2-D deviation
    n3a = defaultdict(lambda: array('f'))       # (sigma, band) -> along-x deviation
    n3n = defaultdict(lambda: [0, 0, 0, 0])
    cropA = defaultdict(lambda: array('f'))     # (dir, d, band) -> S against A
    cropB = defaultdict(lambda: array('f'))     # (dir, d, band) -> S against B
    null_dev = array('f')
    null_un = [0, 0]
    det = {"checked": 0, "identical": 0, "files": Counter()}
    counts = []
    excluded = 0
    names = sorted(f for f in os.listdir(src_dir) if f.lower().endswith(".tif"))
    print("%s: %d images" % (tag, len(names)), flush=True)


    for k, res in enumerate(pool.run([(i, os.path.join(src_dir, f))
                                      for i, f in enumerate(names)],
                                     _image_work, "INV016_SERIAL")):
        counts.append(res["count"])
        if res["excluded"]:
            excluded += 1
        else:
            det["checked"] += res["det"]["checked"]
            det["identical"] += res["det"]["identical"]
            for e, c in res["det"]["files"].items():
                det["files"][e] += c
            null_dev.extend(res["null_dev"])
            null_un[0] += res["null_un"][0]
            null_un[1] += res["null_un"][1]
            for store, part in ((n1, res["n1"]), (n1e, res["n1e"]),
                                (n3, res["n3"]), (n3a, res["n3a"]),
                                (cropA, res["cropA"]), (cropB, res["cropB"])):
                for kk, v in part.items():
                    store[kk].extend(v)
            for store, part in ((n2, res["n2"]), (n2raw, res["n2raw"]),
                                (n3n, res["n3n"])):
                for kk, v in part.items():
                    t = store[kk]
                    for q in range(4):
                        t[q] += v[q]
        if (k + 1) % 10 == 0:
            print("  %d/%d" % (k + 1, len(names)), flush=True)


    out = {
        "tag": tag, "images": len(names), "excluded_lt_%d" % NMIN: excluded,
        "params": {"ds": DS, "sigmas": SIGMAS, "pair_radius": PAIR_R,
                   "margin": MARGIN, "n_min": NMIN, "qm_threshold": QM_T,
                   "block": BLOCK, "bands": BANDNAMES, "seed": SEED},
        "counts": {"min": int(min(counts)), "max": int(max(counts)),
                   "median": float(np.median(counts))},
        "N0": {"checked": det["checked"], "identical": det["identical"],
               "files_differing": dict(det["files"])},
        "null_control": {"n": len(null_dev),
                         "max": float(np.max(null_dev)) if len(null_dev) else None,
                         "unmatched": null_un[0], "of": null_un[1]},
        "N1": summ(n1, k3), "N1_2d": summ(n1e, k3),
        "crop_A": summ(cropA, k3),
        "crop_B": summ(cropB, k3),
        "N3": summ(n3, k2), "N3_along": summ(n3a, k2),
        "N2": {"%s|%d|%s" % (kk[0], kk[1], BANDNAMES[kk[2]]): v
               for kk, v in n2.items()},
        "N2_raw": {"%s|%d|%s" % (kk[0], kk[1], BANDNAMES[kk[2]]): v
                   for kk, v in n2raw.items()},
        "N3_sets": {"%g|%s" % (kk[0], BANDNAMES[kk[1]]): v
                    for kk, v in n3n.items()},
        "pooled_by_d": pooled(n1, lambda kk: kk[1]),
        "pooled_by_d_2d": pooled(n1e, lambda kk: kk[1]),
        "pooled_by_dmod8": pooled(n1, lambda kk: kk[1] % 8),
        "pooled_by_dmod8_2d": pooled(n1e, lambda kk: kk[1] % 8),
        "zero_by_d": {str(dd): float(np.mean([x == 0 for kk, v in n1.items()
                      if kk[1] == dd for x in v])) for dd in DS},
        "pooled_by_dir": pooled(n1, lambda kk: kk[0]),
        "pooled_by_band": pooled(n1, lambda kk: BANDNAMES[kk[2]]),
        "pooled_by_band_2d": pooled(n1e, lambda kk: BANDNAMES[kk[2]]),
        "cropA_by_d": pooled(cropA, lambda kk: kk[1]),
        "cropB_by_d": pooled(cropB, lambda kk: kk[1]),
        "F": pooled(n1, lambda kk: "all")["all"],
        "F_2d": pooled(n1e, lambda kk: "all")["all"],
    }
    return out
