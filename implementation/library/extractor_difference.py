"""The instrument of `quality/INV-014`: how the two extractors differ.

Both tools are run on the same images and both outputs are put into the
image's own frame by the transforms `INV-011` and `INV-012` measured, so that
what is left is a difference between the tools rather than between notations.
Correspondence is swept over a range of radii and computed three ways, because
choosing one radius or one assignment rule chooses the answer.

Imported, never invoked as a command, as `REF-013` decision 3 requires; the
command form is `scripts/measure_extractor_difference.py`, which imports and
calls.

`measure(src_dir, tag)` returns the aggregate the record is written from. Every
minutia stays inside this process: what comes back is counts, histograms and
summaries, never a position.
"""
import math
import os
import subprocess
from collections import Counter

import numpy as np
from PIL import Image

WORK = os.environ.get("INV014_WORK", "/tmp/inv014")
RADII = [1, 2, 3, 4, 5, 6, 8, 10, 12, 15]

# ---------------------------------------------------------------- the frame
# INV-011 F-1: mindtct's .xyt has its origin at the bottom left, so
# y_image = H - y_xyt and x is unchanged.  INV-011 F-2 and F-3: iso-extract's
# template is already in the image's own frame.  INV-012 F-2 and F-3:
# mindtct's angle points away from the ridge, iso-extract's along it, so
# mindtct's is turned by 180.  The common frame is the image's own.


def read_xyt(path, h):
    rows = []
    for line in open(path):
        x, y, t, q = (int(v) for v in line.split())
        rows.append((x, h - y, (t + 180) % 360, q))
    return rows


def read_min_types(path):
    out = []
    with open(path) as fp:
        fp.readline()
        for line in fp:
            f = line.split(":")
            if len(f) < 6 or not f[0].strip().isdigit():
                continue
            out.append(f[4].strip())
    return out


def be16(b, o):
    return (b[o] << 8) | b[o + 1]


def read_ist(path):
    t = open(path, "rb").read()
    n = t[27]
    out = []
    for i in range(n):
        o = 28 + 6 * i
        xw = be16(t, o)
        out.append((xw & 0x3FFF, be16(t, o + 2) & 0x3FFF,
                    t[o + 4] * 360.0 / 256.0, t[o + 5], xw >> 14))
    return out, be16(t, 14), be16(t, 16)


# ------------------------------------------------------- the correspondence
def greedy(a, b, r):
    cand = []
    for i, p in enumerate(a):
        for j, q in enumerate(b):
            d = math.hypot(p[0] - q[0], p[1] - q[1])
            if d <= r:
                cand.append((d, i, j))
    cand.sort()
    ua, ub, pairs = set(), set(), []
    for d, i, j in cand:
        if i not in ua and j not in ub:
            ua.add(i)
            ub.add(j)
            pairs.append((i, j, d))
    return pairs


def optimal(a, b, r):
    """Maximum-cardinality matching on the graph of pairs within r."""
    adj = [[j for j, q in enumerate(b)
            if math.hypot(p[0] - q[0], p[1] - q[1]) <= r] for p in a]
    matchb = [-1] * len(b)

    def try_k(i, seen):
        for j in adj[i]:
            if seen[j]:
                continue
            seen[j] = True
            if matchb[j] == -1 or try_k(matchb[j], seen):
                matchb[j] = i
                return True
        return False

    n = 0
    for i in range(len(a)):
        if try_k(i, [False] * len(b)):
            n += 1
    return n


def mutual(a, b, r):
    if not a or not b:
        return []
    na = [min(range(len(b)), key=lambda j: math.hypot(p[0] - b[j][0],
                                                      p[1] - b[j][1]))
          for p in a]
    nb = [min(range(len(a)), key=lambda i: math.hypot(q[0] - a[i][0],
                                                      q[1] - a[i][1]))
          for q in b]
    out = []
    for i, j in enumerate(na):
        if nb[j] == i:
            d = math.hypot(a[i][0] - b[j][0], a[i][1] - b[j][1])
            if d <= r:
                out.append((i, j, d))
    return out


# ------------------------------------------------------------- the lattice
def muldiv(x, y, z):
    return (x * y + (z >> 1)) // z


def reachable(off, hi):
    """The output coordinates the library's own arithmetic can produce.

    FeatureExtraction.h: RescaleMinutia multiplies the internal coordinate by
    imageScale/imageResolution = 635/500 in C integer division, a constant
    from the padding correction is added, and the result is scaled by
    muldiv(., 197, 167).  The composed factor is 1.27 * 197/167.
    """
    s = set()
    p = 0
    while True:
        c = muldiv((p * 635) // 500 + off, 197, 167)
        if c > hi:
            break
        s.add(c)
        p += 1
    return s


REACH = {off: reachable(off, 800) for off in range(0, 81)}
DENSITY = len(REACH[0] & set(range(0, 400))) / 400.0
DENSITIES = [len(REACH[o] & set(range(0, 400))) / 400.0 for o in range(0, 81)]


def lattice_fit(vals):
    best = (0.0, None)
    if not vals:
        return best
    for off, s in REACH.items():
        f = sum(1 for v in vals if v in s) / float(len(vals))
        if f > best[0]:
            best = (f, off)
    return best


def spectrum(vals, n, period):
    if not vals:
        return 0.0
    h = np.bincount(np.asarray(vals, dtype=int), minlength=n)[:n].astype(float)
    if h.sum() == 0:
        return 0.0
    k = n / float(period)
    t = np.arange(n)
    c = (h * np.exp(-2j * np.pi * k * t / n)).sum()
    return float(abs(c)) / h.sum() * 2.0


def hist(v, lo, hi, step):
    b = list(range(lo, hi + step, step))
    c = Counter()
    for x in v:
        c[min(max(int((x - lo) // step), 0), len(b) - 2)] += 1
    return [[b[i], c.get(i, 0)] for i in range(len(b) - 1)]


def measure(src_dir, tag):
    """Run the whole measurement over one subset directory."""
    os.makedirs(WORK, exist_ok=True)
    # ------------------------------------------------------------- extraction
    names = sorted(f for f in os.listdir(src_dir) if f.lower().endswith(".tif"))
    print("%s: %d images" % (tag, len(names)), flush=True)

    data = []
    refused = 0
    hdr_ok = 0
    sizes = Counter()
    for k, name in enumerate(names):
        stem = os.path.splitext(name)[0]
        img = Image.open(os.path.join(src_dir, name)).convert("L")
        w, h = img.size
        sizes[(w, h)] += 1
        png = "%s/%s.png" % (WORK, stem)
        pgm = "%s/%s.pgm" % (WORK, stem)
        img.save(png)
        img.save(pgm)
        subprocess.run(["mindtct", png, "%s/%s" % (WORK, stem)], check=True,
                       capture_output=True)
        m = read_xyt("%s/%s.xyt" % (WORK, stem), h)
        mt = read_min_types("%s/%s.min" % (WORK, stem))
        r = subprocess.run(["iso-extract", pgm, "%s/%s.ist" % (WORK, stem)],
                           capture_output=True)
        if r.returncode:
            refused += 1
            data.append({"w": w, "h": h, "m": m, "mt": mt, "i": None})
        else:
            i_, hx, hy = read_ist("%s/%s.ist" % (WORK, stem))
            hdr_ok += (hx == w and hy == h)
            data.append({"w": w, "h": h, "m": m, "mt": mt, "i": i_})
        for e in os.listdir(WORK):
            os.remove(os.path.join(WORK, e))
        if (k + 1) % 100 == 0:
            print("  extracted %d/%d" % (k + 1, len(names)), flush=True)

    good = [d for d in data if d["i"] is not None]
    W = max(d["w"] for d in data)
    H = max(d["h"] for d in data)
    allm = [(p[0], p[1]) for d in good for p in d["m"]]
    alli = [(p[0], p[1]) for d in good for p in d["i"]]

    out = {
        "tag": tag, "images": len(names), "iso_refused": refused,
        "sizes": {"%dx%d" % k: v for k, v in sizes.items()},
        "header_matches_pil": hdr_ok,
        "n_mindtct": sum(len(d["m"]) for d in good),
        "n_iso": sum(len(d["i"]) for d in good),
        "n_mindtct_all": sum(len(d["m"]) for d in data),
        "counts_mindtct": hist([len(d["m"]) for d in good], 0, 100, 10),
        "counts_iso": hist([len(d["i"]) for d in good], 0, 100, 10),
        "count_range_mindtct": [min(len(d["m"]) for d in good),
                                max(len(d["m"]) for d in good)],
        "count_range_iso": [min(len(d["i"]) for d in good),
                            max(len(d["i"]) for d in good)],
        "more_iso_than_mindtct": sum(1 for d in good if len(d["i"]) > len(d["m"])),
    }

    # ------------------------------------------------ raw correspondence vs r
    corr = {}
    for rr in RADII:
        g = o = u = 0
        for d in good:
            g += len(greedy(d["m"], d["i"], rr))
            o += optimal(d["m"], d["i"], rr)
            u += len(mutual(d["m"], d["i"], rr))
        corr[str(rr)] = [g, o, u]
    out["correspondence"] = corr

    # --------------------------------------------- candidate 2, the transform
    fit = []
    for d in good:
        for i, j, _ in mutual(d["m"], d["i"], 12):
            fit.append((d["m"][i][0], d["m"][i][1], d["i"][j][0], d["i"][j][1]))
    a = np.array(fit, dtype=float)
    out["fit_n"] = len(fit)
    out["fit"] = {}
    for axis, (c0, c1) in (("x", (0, 2)), ("y", (1, 3))):
        A = np.stack([a[:, c0], np.ones(len(a))], axis=1)
        sol, *_ = np.linalg.lstsq(A, a[:, c1], rcond=None)
        res = a[:, c1] - A @ sol
        out["fit"][axis] = {"scale": float(sol[0]), "offset": float(sol[1]),
                            "rms": float(np.sqrt((res ** 2).mean())),
                            "mean_abs": float(np.abs(res).mean())}
    src, dst = a[:, 0:2], a[:, 2:4]
    mu_s, mu_d = src.mean(0), dst.mean(0)
    s0, d0 = src - mu_s, dst - mu_d
    num = (s0[:, 0] * d0[:, 1] - s0[:, 1] * d0[:, 0]).sum()
    den = (s0 * d0).sum()
    out["fit"]["similarity"] = {
        "scale": float(math.hypot(num, den) / (s0 ** 2).sum()),
        "rotation_deg": float(math.degrees(math.atan2(num, den))),
    }
    out["fit"]["predicted"] = {
        "internal_w": W // 6 * 4, "internal_h": H // 6 * 4,
        "composed_factor": 635.0 / 500.0 * 197.0 / 167.0,
        "scale_if_resample_is_two_thirds": 635.0 * 197.0 * 2.0 / (500.0 * 167.0 * 3.0),
        "scale_if_resample_is_width_ratio_x": 635.0 / 500.0 * 197.0 / 167.0
                                              * (W // 6 * 4) / float(W),
        "scale_if_resample_is_width_ratio_y": 635.0 / 500.0 * 197.0 / 167.0
                                              * (H // 6 * 4) / float(H),
    }
    for axis, c0 in (("x", 0), ("y", 1)):
        n = len(a)
        sd = float(a[:, c0].std())
        out["fit"][axis]["scale_se"] = out["fit"][axis]["rms"] / (sd * math.sqrt(n))
    # the reverse regression: the true slope is bracketed by the two
    for axis, (c0, c1) in (("x", (2, 0)), ("y", (3, 1))):
        A = np.stack([a[:, c0], np.ones(len(a))], axis=1)
        sol, *_ = np.linalg.lstsq(A, a[:, c1], rcond=None)
        out["fit"][axis]["reverse_slope_inverse"] = float(1.0 / sol[0])

    # correspondence again, with mindtct put through the fitted per-axis affine
    sx, ox = out["fit"]["x"]["scale"], out["fit"]["x"]["offset"]
    sy, oy = out["fit"]["y"]["scale"], out["fit"]["y"]["offset"]
    corr2 = {}
    for rr in RADII:
        g = o = 0
        for d in good:
            mm = [(p[0] * sx + ox, p[1] * sy + oy) for p in d["m"]]
            g += len(greedy(mm, d["i"], rr))
            o += optimal(mm, d["i"], rr)
        corr2[str(rr)] = [g, o]
    out["correspondence_after_fit"] = corr2

    # -------------------------------------------------- candidate 1, lattice
    lat = {"iso_x": [], "iso_y": [], "min_x": [], "min_y": []}
    offs_x, offs_y = Counter(), Counter()
    for d in good:
        fx, ox_ = lattice_fit([p[0] for p in d["i"]])
        fy, oy_ = lattice_fit([p[1] for p in d["i"]])
        lat["iso_x"].append(fx)
        lat["iso_y"].append(fy)
        offs_x[ox_] += 1
        offs_y[oy_] += 1
        lat["min_x"].append(lattice_fit([p[0] for p in d["m"]])[0])
        lat["min_y"].append(lattice_fit([p[1] for p in d["m"]])[0])
    rng = np.random.default_rng(20260908)
    null = []
    for d in good:
        n = len(d["i"])
        null.append(lattice_fit([int(v) for v in rng.integers(0, d["w"], n)])[0])
    out["lattice"] = {
        "density": DENSITY,
        "density_at_offset": {str(o): DENSITIES[o] for o in (0, 1, 2, 3, 7)},
        "density_range_over_offsets": [min(DENSITIES), max(DENSITIES)],
        "uniform_null_mean": float(np.mean(null)),
        "uniform_null_max": float(np.max(null)),
        "mean": {k: float(np.mean(v)) for k, v in lat.items()},
        "min": {k: float(np.min(v)) for k, v in lat.items()},
        "images_at_1.0": {k: int(sum(1 for x in v if x >= 0.9999))
                          for k, v in lat.items()},
        "hist": {k: hist([int(round(x * 100)) for x in v], 0, 100, 5)
                 for k, v in lat.items()},
        "iso_offsets_x": offs_x.most_common(8),
        "iso_offsets_y": offs_y.most_common(8),
    }
    out["spectrum"] = {
        "iso_x_p3": spectrum([p[0] for p in alli], W, 3),
        "iso_y_p3": spectrum([p[1] for p in alli], H, 3),
        "min_x_p3": spectrum([p[0] for p in allm], W, 3),
        "min_y_p3": spectrum([p[1] for p in allm], H, 3),
        "iso_x_p9": spectrum([p[0] for p in alli], W, 9),
        "iso_y_p9": spectrum([p[1] for p in alli], H, 9),
        "min_x_p9": spectrum([p[0] for p in allm], W, 9),
        "min_y_p9": spectrum([p[1] for p in allm], H, 9),
    }
    out["residues"] = {
        "iso_x": [sum(1 for p in alli if p[0] % 3 == mm) for mm in range(3)],
        "iso_y": [sum(1 for p in alli if p[1] % 3 == mm) for mm in range(3)],
        "min_x": [sum(1 for p in allm if p[0] % 3 == mm) for mm in range(3)],
        "min_y": [sum(1 for p in allm if p[1] % 3 == mm) for mm in range(3)],
    }

    # ------------------------------- candidates 3, 4, 5, on the r = 12 pairing
    em_m, em_u, ei_m, ei_u = [], [], [], []
    qm_m, qm_u, qi_m, qi_u = [], [], [], []
    types = Counter()
    for d in good:
        pairs = mutual(d["m"], d["i"], 12)
        mm = set(i for i, _, _ in pairs)
        ii = set(j for _, j, _ in pairs)
        w, h = d["w"], d["h"]
        for idx, p in enumerate(d["m"]):
            e = min(p[0], p[1], w - 1 - p[0], h - 1 - p[1])
            (em_m if idx in mm else em_u).append(e)
            (qm_m if idx in mm else qm_u).append(p[3])
        for idx, p in enumerate(d["i"]):
            e = min(p[0], p[1], w - 1 - p[0], h - 1 - p[1])
            (ei_m if idx in ii else ei_u).append(e)
            (qi_m if idx in ii else qi_u).append(p[3])
        for i, j, _ in pairs:
            types[(d["mt"][i] if i < len(d["mt"]) else "?", d["i"][j][4])] += 1
    out["edge"] = {"mindtct_matched": hist(em_m, 0, 60, 5),
                   "mindtct_unmatched": hist(em_u, 0, 60, 5),
                   "iso_matched": hist(ei_m, 0, 60, 5),
                   "iso_unmatched": hist(ei_u, 0, 60, 5),
                   "means": [float(np.mean(v)) if v else None
                             for v in (em_m, em_u, ei_m, ei_u)]}
    out["quality"] = {"mindtct_matched": hist(qm_m, 0, 100, 10),
                      "mindtct_unmatched": hist(qm_u, 0, 100, 10),
                      "iso_matched": hist(qi_m, 0, 100, 10),
                      "iso_unmatched": hist(qi_u, 0, 100, 10),
                      "means": [float(np.mean(v)) if v else None
                                for v in (qm_m, qm_u, qi_m, qi_u)]}
    out["types"] = {"%s|%d" % k: v for k, v in sorted(types.items())}

    # the frame itself, checked on corpus images: the angle after the turn
    dth, dist = [], []
    for d in good:
        for i, j, dd in mutual(d["m"], d["i"], 4):
            dth.append((d["i"][j][2] - d["m"][i][2]) % 360.0)
            dist.append(dd)
    if dth:
        v = np.radians(np.asarray(dth))
        c, sn = float(np.cos(v).mean()), float(np.sin(v).mean())
        out["angle_check"] = {
            "n": len(dth),
            "circular_mean_deg": float(math.degrees(math.atan2(sn, c)) % 360.0),
            "R": float(math.hypot(c, sn)),
            "within_15_deg": int(sum(1 for x in dth if min(x, 360 - x) <= 15)),
            "hist_30": hist([int(x) for x in dth], 0, 360, 30),
        }
        out["pair_distance_hist"] = hist([int(x) for x in dist], 0, 4, 1)
    return out
