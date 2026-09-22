"""The instrument of `quality/INV-015`: which warp family predicts a held-out
correspondence.

mindtct only, positions only, entirely in mindtct's own .xyt frame. Nine model
families are fitted with a Huber loss to correspondences frozen before any
model is seen, and compared by five-fold cross-validation stratified by radius
over six pairing radii. No model re-pairs: a model allowed to choose its own
correspondences chooses the ones that flatter it.

Imported, never invoked as a command, as `REF-013` decision 3 requires; the
command form is `scripts/measure_warp_families.py`, which imports and calls.

`measure(src_dir, tag)` returns the aggregate the record is written from. Every
minutia stays inside this run: positions are read, forked into the worker
processes of a pool and passed back between them over a pipe, and they reach
no file and no return value. What comes back is counts, residual summaries and
fitted coefficients, never a position.

The pool is there because a corpus is eight hundred fingers, not ten. It moves
no number, and the argument for that is one claim: every draw from the module
generator below is made in this process, in the order a sequential run makes
it. `ransac()` is split into `ransac_sample`, which draws, and `ransac_score`,
which does not, so the claim can be checked by reading. `INV015_SERIAL=1`
takes the sequential path, which returns the same bytes.
"""
import math
import os
import subprocess
from array import array
from collections import Counter, defaultdict

import numpy as np
from PIL import Image

from implementation.library import pool

WORK = os.environ.get("INV015_WORK", "/tmp/inv015")

RS = 269.0                     # image half-diagonal, fixed by the brief
QM_T = 1                       # foreground = quality map >= QM_T
BLOCK = 8                      # mindtct map block, pixels
TAUS = [3, 5, 8, 12, 15, 20]
BANDS = [0, 30, 60, 90, 120, 150, 10 ** 9]
BANDNAMES = ["0-30", "30-60", "60-90", "90-120", "120-150", "150+"]
HUBER = 3.0
SEED = 20260908
RANSAC_N = 4000
RANSAC_INLIER = 12.0
RANSAC_DTOL = 3.0
RANSAC_MINSEP = 25.0
NMIN = 8                       # pairs with fewer correspondences are excluded
LAMBDAS = [0.0, 10.0, 100.0, 1000.0, 10000.0]
RHOS = [40, 60, 80, 100, 120]

rng = np.random.default_rng(SEED)


# ------------------------------------------------------------- extraction
def extract(path):
    wk = pool.scratch(WORK)
    img = Image.open(path).convert("L")
    w, h = img.size
    img.save("%s/a.png" % wk)
    subprocess.run(["mindtct", "%s/a.png" % wk, "%s/a" % wk], check=True,
                   capture_output=True)
    xyt = np.array([[float(v) for v in l.split()]
                    for l in open("%s/a.xyt" % wk)])
    q = np.array([[int(v) for v in l.split()]
                  for l in open("%s/a.qm" % wk)])
    lcm = np.array([[int(v) for v in l.split()]
                    for l in open("%s/a.lcm" % wk)])
    for e in os.listdir(wk):
        os.remove(os.path.join(wk, e))
    mask = q >= QM_T
    ys, xs = np.nonzero(mask)
    area = float(len(xs)) * BLOCK * BLOCK
    cx = float(xs.mean() + 0.5) * BLOCK
    cy = h - float(ys.mean() + 0.5) * BLOCK          # into the .xyt frame
    # block centres in the .xyt frame
    bx = (xs + 0.5) * BLOCK
    by = h - (ys + 0.5) * BLOCK
    return {"w": w, "h": h, "p": xyt[:, 0:2] if len(xyt) else np.zeros((0, 2)),
            "area": area, "area_lcm": float((lcm == 0).sum()) * BLOCK * BLOCK,
            "c": np.array([cx, cy]), "a": math.sqrt(area / math.pi),
            "blocks": np.stack([bx, by], axis=1)}


# --------------------------------------------------------------- geometry
# Bound once: wprocrustes and huber_w are the inner loop of every fit, and on
# arrays of ten to sixty rows the attribute lookups are a measurable share of a
# call.
_CONCATENATE = np.concatenate
_REDUCE = np.add.reduce
_ARRAY = np.array
_HYPOT = np.hypot
_FMAX = np.fmax


def rot(th):
    c, s = math.cos(th), math.sin(th)
    return np.array([[c, -s], [s, c]])


def wprocrustes(S, T, w, scale=False):
    ST = _CONCATENATE((S, T), axis=1)
    m = (ST * w[:, None]).sum(0)
    m /= _REDUCE(w)
    d = ST - m
    dx = d[:, 0]
    dy = d[:, 1]
    ex = d[:, 2]
    ey = d[:, 3]
    num = float(_REDUCE(w * (dx * ey - dy * ex)))
    den = float(_REDUCE(w * (dx * ex + dy * ey)))
    th = math.atan2(num, den)
    sc = (math.hypot(num, den) / float(_REDUCE(w * (dx * dx + dy * dy)))
          if scale else 1.0)
    c = math.cos(th)
    s = math.sin(th)
    R = _ARRAY(((c, -s), (s, c)))
    v = R.dot(m[:2])
    if sc != 1.0:
        v = sc * v
    return sc, R, m[2:] - v, th


def huber_w(res):
    return HUBER / _FMAX(_HYPOT(res[:, 0], res[:, 1]), HUBER)


def hull(P):
    if len(P) < 3:
        return P
    idx = np.lexsort((P[:, 1], P[:, 0]))
    Q = P[idx]

    def half(pts):
        out = []
        for p in pts:
            while len(out) >= 2:
                a, b = out[-2], out[-1]
                if (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) <= 0:
                    out.pop()
                else:
                    break
            out.append(p)
        return out
    lo = half(Q)
    hi = half(Q[::-1])
    return np.array(lo[:-1] + hi[:-1]) if len(lo) + len(hi) > 3 else Q


def in_hull(H, pts):
    if len(H) < 3:
        return np.zeros(len(pts), dtype=bool)
    ok = np.ones(len(pts), dtype=bool)
    for k in range(len(H)):
        a, b = H[k], H[(k + 1) % len(H)]
        cross = ((b[0] - a[0]) * (pts[:, 1] - a[1])
                 - (b[1] - a[1]) * (pts[:, 0] - a[0]))
        ok &= cross >= -1e-9
    return ok


# ---------------------------------------------------------------- models
def _recurred(seen, outs, key, it, iters):
    """Short-circuit an IRLS loop that has started to repeat itself.

    Every fitter below is a deterministic map from its weight vector to the
    next one, so once a weight vector recurs the iteration is in a cycle and
    the remaining iterations are already known.  `key` identifies the state
    at the top of iteration `it`; if it was first seen at iteration `first`,
    the cycle has length `it - first` and the state the full `iters` loop
    would have ended on is `outs[first + (iters - 1 - first) % (it - first)]`.
    Returning that is the same value the loop returns, not an approximation
    of it: the loop is cut short only where its remaining output is already
    in hand."""
    first = seen.get(key)
    if first is None:
        seen[key] = it
        return None
    return outs[first + (iters - 1 - first) % (it - first)]


def fit_radial(V, T, powers, iters=60):
    """q = R (V * h(r)) + t,  h = 1 + sum c_k r^(k-1)/RS^k."""
    r = np.hypot(V[:, 0], V[:, 1])
    B = (np.stack([r ** (k - 1) / RS ** k for k in powers], axis=1)
         if powers else None)
    c = np.zeros(len(powers))
    w = np.ones(len(V))
    R, t = np.eye(2), np.zeros(2)
    seen, outs = {}, []
    if not powers:
        S = V * (1.0 + np.zeros(len(V)))[:, None]
        for it in range(iters):
            done = _recurred(seen, outs, w.tobytes(), it, iters)
            if done is not None:
                R, t = done
                break
            _, R, t, _ = wprocrustes(S, T, w)
            w = huber_w(T - (S @ R.T + t))
            outs.append((R, t))
        return {"kind": "radial", "powers": powers, "c": c, "R": R, "t": t}
    A = np.concatenate([V[:, 0:1] * B, V[:, 1:2] * B], axis=0)
    h = 1.0 + B @ c
    S = V * h[:, None]
    for it in range(iters):
        done = _recurred(seen, outs, (c.tobytes(), w.tobytes()), it, iters)
        if done is not None:
            c, R, t = done
            break
        _, R, t, _ = wprocrustes(S, T, w)
        D = (T - t) @ R - V
        sw = np.sqrt(np.concatenate([w, w]))
        c = np.linalg.lstsq(A * sw[:, None],
                            np.concatenate([D[:, 0], D[:, 1]]) * sw,
                            rcond=None)[0]
        h = 1.0 + B @ c
        S = V * h[:, None]
        _, R, t, _ = wprocrustes(S, T, w)
        w = huber_w(T - (S @ R.T + t))
        outs.append((c, R, t))
    return {"kind": "radial", "powers": powers, "c": c, "R": R, "t": t}


def apply_radial(m, V):
    r = np.hypot(V[:, 0], V[:, 1])
    h = np.ones(len(V))
    if m["powers"]:
        B = np.stack([r ** (k - 1) / RS ** k for k in m["powers"]], axis=1)
        h = 1.0 + B @ m["c"]
    return (V * h[:, None]) @ m["R"].T + m["t"]


def fit_trans(V, T, iters=60):
    w = np.ones(len(V))
    t = np.zeros(2)
    seen, outs = {}, []
    for it in range(iters):
        done = _recurred(seen, outs, w.tobytes(), it, iters)
        if done is not None:
            t = done
            break
        t = ((T - V) * w[:, None]).sum(0) / w.sum()
        w = huber_w(T - (V + t))
        outs.append(t)
    return {"kind": "trans", "t": t}


def fit_sim(V, T, iters=60):
    w = np.ones(len(V))
    sc, R, t = 1.0, np.eye(2), np.zeros(2)
    seen, outs = {}, []
    for it in range(iters):
        done = _recurred(seen, outs, w.tobytes(), it, iters)
        if done is not None:
            sc, R, t = done
            break
        sc, R, t, _ = wprocrustes(V, T, w, scale=True)
        w = huber_w(T - (sc * (V @ R.T) + t))
        outs.append((sc, R, t))
    return {"kind": "sim", "s": sc, "R": R, "t": t}


def fit_affine(V, T, iters=60):
    w = np.ones(len(V))
    A = np.eye(2)
    t = np.zeros(2)
    X = np.concatenate([V, np.ones((len(V), 1))], axis=1)
    seen, outs = {}, []
    for it in range(iters):
        done = _recurred(seen, outs, w.tobytes(), it, iters)
        if done is not None:
            A, t = done
            break
        sw = np.sqrt(w)[:, None]
        sol = np.linalg.lstsq(X * sw, T * sw, rcond=None)[0]
        A, t = sol[0:2].T, sol[2]
        w = huber_w(T - (V @ A.T + t))
        outs.append((A, t))
    return {"kind": "affine", "A": A, "t": t}


def _U(d2):
    out = np.zeros_like(d2)
    nz = d2 > 0
    out[nz] = d2[nz] * np.log(d2[nz])
    return out


_TPS_BASIS = {}
_TPS_BASIS_ORDER = []
_TPS_BASIS_MAX = 8


def _tps_basis(V):
    """The TPS kernel and affine block, which depend on V and nothing else.

    `fit_tps` is called once per lambda in LAMBDAS and once more for the
    full fit, all on the same V, so the same pair of matrices is rebuilt
    five or six times over.  Keying on the bytes of V returns the identical
    arrays rather than an equal-looking rebuild.  The cache is bounded at
    _TPS_BASIS_MAX entries and evicted oldest first, so it cannot grow with
    the corpus."""
    key = (V.shape, V.dtype.str, V.tobytes())
    hit = _TPS_BASIS.get(key)
    if hit is not None:
        return hit
    n = len(V)
    d2 = ((V[:, None, :] - V[None, :, :]) ** 2).sum(-1)
    basis = (_U(d2), np.concatenate([np.ones((n, 1)), V], axis=1))
    _TPS_BASIS[key] = basis
    _TPS_BASIS_ORDER.append(key)
    if len(_TPS_BASIS_ORDER) > _TPS_BASIS_MAX:
        del _TPS_BASIS[_TPS_BASIS_ORDER.pop(0)]
    return basis


def fit_tps(V, T, lam, iters=20):
    n = len(V)
    K, P = _tps_basis(V)
    M = np.zeros((n + 3, n + 3))
    M[:n, :n] = K
    M[:n, n:] = P
    M[n:, :n] = P.T
    rhs = np.zeros((n + 3, 2))
    rhs[:n] = T
    di = (np.arange(n), np.arange(n))
    Kd = K[di]
    w = np.ones(n)
    seen = {}
    sols = []
    for i in range(iters):
        dvec = lam * (1.0 / np.maximum(w, 1e-6))
        key = dvec.tobytes()
        j = seen.get(key)
        if j is not None:
            return {"kind": "tps", "V": V,
                    "sol": sols[j + (iters - 1 - j) % (i - j)]}
        seen[key] = i
        M[di] = Kd + dvec
        sol = np.linalg.lstsq(M, rhs, rcond=None)[0]
        sols.append(sol)
        w = huber_w(T - (K @ sol[:n] + P @ sol[n:]))
    return {"kind": "tps", "V": V, "sol": sols[-1]}


def apply_model(m, V):
    if m["kind"] == "trans":
        return V + m["t"]
    if m["kind"] == "sim":
        return m["s"] * (V @ m["R"].T) + m["t"]
    if m["kind"] == "affine":
        return V @ m["A"].T + m["t"]
    if m["kind"] == "radial":
        return apply_radial(m, V)
    n = len(m["V"])
    d2 = ((V[:, None, :] - m["V"][None, :, :]) ** 2).sum(-1)
    P = np.concatenate([np.ones((len(V), 1)), V], axis=1)
    return _U(d2) @ m["sol"][:n] + P @ m["sol"][n:]


MODELS = [("M0", lambda V, T: fit_trans(V, T)),
          ("M1", lambda V, T: fit_radial(V, T, ())),
          ("M2", lambda V, T: fit_sim(V, T)),
          ("M3", lambda V, T: fit_radial(V, T, (1,))),
          ("M4", lambda V, T: fit_radial(V, T, (1, 3))),
          ("M5", lambda V, T: fit_radial(V, T, (1, 2))),
          ("M6", lambda V, T: fit_radial(V, T, (1, 3, 5))),
          ("M7", lambda V, T: fit_affine(V, T))]
MODELS += [("M8l%g" % l, (lambda ll: (lambda V, T: fit_tps(V, T, ll)))(l))
           for l in LAMBDAS]
MINPTS = {"M0": 1, "M1": 2, "M2": 2, "M3": 2, "M4": 3, "M5": 3, "M6": 4,
          "M7": 3}
for l in LAMBDAS:
    MINPTS["M8l%g" % l] = 4


# --------------------------------------------------------------- ransac
def ransac_sample(A, B):
    """Draw the candidate correspondences, and keep the consistent ones.

    This is the only part of the alignment that touches the module
    generator.  It is separated so that it can be run in one process, in
    pair order, while the scoring below - which draws nothing - runs in a
    pool: the stream of draws is then the stream a sequential run makes,
    and the alignments are the same alignments."""
    n, m = len(A), len(B)
    if n < 2 or m < 2:
        return None
    dA = np.hypot(*(A[:, None, :] - A[None, :, :]).T).T
    dB = np.hypot(*(B[:, None, :] - B[None, :, :]).T).T
    K = 200000
    i1 = rng.integers(0, n, K)
    i2 = rng.integers(0, n, K)
    j1 = rng.integers(0, m, K)
    j2 = rng.integers(0, m, K)
    da, db = dA[i1, i2], dB[j1, j2]
    ok = (da > RANSAC_MINSEP) & (np.abs(da - db) <= RANSAC_DTOL)
    i1, i2, j1, j2 = i1[ok][:RANSAC_N], i2[ok][:RANSAC_N], j1[ok][:RANSAC_N], j2[ok][:RANSAC_N]
    if not len(i1):
        return None
    return i1, i2, j1, j2


def ransac_score(A, B, sample):
    """Score every candidate, keep the best, refine it.  Draws nothing."""
    n, m = len(A), len(B)
    i1, i2, j1, j2 = sample
    va, vb = A[i2] - A[i1], B[j2] - B[j1]
    th = np.arctan2(vb[:, 1], vb[:, 0]) - np.arctan2(va[:, 1], va[:, 0])
    c, sn = np.cos(th), np.sin(th)
    ax = c[:, None] * A[None, :, 0] - sn[:, None] * A[None, :, 1]
    ay = sn[:, None] * A[None, :, 0] + c[:, None] * A[None, :, 1]
    tx = B[j1, 0] - (c * A[i1, 0] - sn * A[i1, 1])
    ty = B[j1, 1] - (sn * A[i1, 0] + c * A[i1, 1])
    ax = ax + tx[:, None]
    ay = ay + ty[:, None]
    best, bestn = None, -1
    step = max(1, 4000000 // max(1, n * m))
    for s0 in range(0, len(i1), step):
        s1 = min(len(i1), s0 + step)
        dd = np.hypot(ax[s0:s1, :, None] - B[None, None, :, 0],
                      ay[s0:s1, :, None] - B[None, None, :, 1])
        cnt = (dd.min(2) <= RANSAC_INLIER).sum(1)
        k = int(cnt.argmax())
        if cnt[k] > bestn:
            bestn = int(cnt[k])
            best = (rot(float(th[s0 + k])),
                    np.array([tx[s0 + k], ty[s0 + k]]))
    R, t = best
    for _ in range(3):
        dd = np.hypot(*((A @ R.T + t)[:, None, :] - B[None, :, :]).T).T
        j = dd.argmin(1)
        keep = dd.min(1) <= RANSAC_INLIER
        if int(keep.sum()) < 2:
            break
        _, R, t, _ = wprocrustes(A[keep], B[j[keep]], np.ones(int(keep.sum())))
    dd = np.hypot(*((A @ R.T + t)[:, None, :] - B[None, :, :]).T).T
    return (R, t), int((dd.min(1) <= RANSAC_INLIER).sum())


def mutual_pairs(A2, B, tau):
    if not len(A2) or not len(B):
        return np.zeros((0, 2), dtype=int)
    d = np.hypot(*(A2[:, None, :] - B[None, :, :]).T).T
    na, nb = d.argmin(1), d.argmin(0)
    out = [(i, na[i]) for i in range(len(A2))
           if nb[na[i]] == i and d[i, na[i]] <= tau]
    return np.array(out, dtype=int) if out else np.zeros((0, 2), dtype=int)


def band_of(r):
    for k in range(len(BANDS) - 1):
        if BANDS[k] <= r < BANDS[k + 1]:
            return k
    return len(BANDS) - 2


# --------------------------------------------------------------- parallel
# The per-pair work below is pure: it consumes an alignment and produces
# accumulator contributions, and it touches no random state.  That is what
# lets it run in a pool without moving a number - every draw from the module
# generator is made in the parent, in the order it was made when this file
# was sequential, and the contributions are merged back in pair order.
CONTRASTS = [("M4", "M5"), ("M6", "M4"), ("M4", "M1"), ("M3", "M1"),
             ("M5", "M1"), ("M7", "M1"), ("M8l10000", "M1"), ("M8l0", "M1"),
             ("M2", "M3"), ("M7", "M4"), ("M8l10000", "M7")]

_IM = {}


def _evaluate(V, T, r, tau, res_ho, res_fre, paired):
    """5-fold CV over the frozen correspondences, stratified by radius."""
    n = len(V)
    order = np.argsort(r)
    fold = np.empty(n, dtype=int)
    fold[order] = np.arange(n) % 5
    out = {}
    resmat = {}
    for name, fitter in MODELS:
        need = MINPTS[name]
        col = np.full(n, np.nan)
        ins_all = np.zeros(n, dtype=bool)
        for k in range(5):
            tr = fold != k
            te = ~tr
            if int(tr.sum()) < need or int(te.sum()) == 0:
                continue
            m = fitter(V[tr], T[tr])
            col[te] = np.hypot(*(T[te] - apply_model(m, V[te])).T)
            ins_all[te] = in_hull(hull(V[tr]), V[te])
        resmat[name] = (col, ins_all)
        for i in range(n):
            if not math.isnan(col[i]):
                res_ho.setdefault((tau, name, band_of(r[i]),
                                   bool(ins_all[i])), []).append(float(col[i]))
        m = fitter(V, T)
        fre = np.hypot(*(T - apply_model(m, V)).T)
        for dd, rr in zip(fre, r):
            res_fre.setdefault((tau, name, band_of(rr)), []).append(float(dd))
        out[name] = (m, None, fre)
    for a, b in CONTRASTS:
        ca, cb = resmat[a][0], resmat[b][0]
        for i in range(n):
            if not (math.isnan(ca[i]) or math.isnan(cb[i])):
                paired.setdefault((tau, band_of(r[i]), a, b), []).append(
                    float(ca[i] - cb[i]))
    return out


def _extract_work(path):
    """extract(), as a pool task.  It draws no random number and its result
    depends on the image alone, so a pool moves no number."""
    return extract(path)


def _pair_work(task):
    """Everything one genuine pair contributes, given its alignment."""
    g, fa, fb, ai, bi, sample = task
    A, B = _IM[fa]["p"], _IM[fb]["p"]
    (R0, t0), nin = ransac_score(A, B, sample)
    A2 = A @ R0.T + t0
    ca = _IM[fa]["c"]
    ransac_rot = math.degrees(math.atan2(R0[1, 0], R0[0, 0]))
    out = {"g": g, "fa": fa, "fb": fb, "ai": ai, "bi": bi, "ca": ca,
           "pair_rows": [], "radial_hist": {}, "hull_cov": {},
           "excluded": [], "res_ho": {}, "res_fre": {}, "paired": {},
           "core_res": {}, "m4_row": None, "r5_row": None,
           "finger_coef_row": None, "keep_pr": {}}
    for tau in TAUS:
        pr = mutual_pairs(A2, B, tau)
        if tau in (8, 15):
            out["keep_pr"][tau] = pr
        N = len(pr)
        V = A[pr[:, 0]] - ca if N else np.zeros((0, 2))
        T = B[pr[:, 1]] if N else np.zeros((0, 2))
        rr = np.hypot(V[:, 0], V[:, 1]) if N else np.zeros(0)
        out["pair_rows"].append([g, fa, fb, tau, N])
        h = np.zeros(len(BANDNAMES))
        for x in rr:
            h[band_of(x)] += 1
        out["radial_hist"][tau] = h
        blocks = _IM[fa]["blocks"] - ca
        rb = np.hypot(blocks[:, 0], blocks[:, 1])
        Hh = hull(V) if N >= 3 else np.zeros((0, 2))
        ins = (in_hull(Hh, blocks) if len(Hh) >= 3
               else np.zeros(len(blocks), dtype=bool))
        hc = np.zeros((len(BANDNAMES), 2))
        for x, i2 in zip(rb, ins):
            hc[band_of(x)] += [1.0, 1.0 if i2 else 0.0]
        out["hull_cov"][tau] = hc
        if N < NMIN:
            out["excluded"].append(tau)
            continue
        ev = _evaluate(V, T, rr, tau, out["res_ho"], out["res_fre"],
                       out["paired"])
        if tau == 15:
            m4, m2, m3 = ev["M4"][0], ev["M2"][0], ev["M3"][0]
            jc, jr = [], []
            for k in range(N):
                sel = np.ones(N, dtype=bool)
                sel[k] = False
                mk = fit_radial(V[sel], T[sel], (1, 3))
                jc.append(mk["c"])
                jr.append(math.degrees(math.atan2(mk["R"][1, 0],
                                                  mk["R"][0, 0])))
            jc = np.array(jc)
            jr = np.array(jr)
            sd_rot = float(math.sqrt((N - 1.0) / N
                                     * ((jr - jr.mean()) ** 2).sum()))
            cov = (N - 1.0) / N * ((jc - jc.mean(0)).T @ (jc - jc.mean(0)))
            out["m4_row"] = {
                "finger": g, "N": N,
                "c1": float(m4["c"][0]), "c3": float(m4["c"][1]),
                "cov": [[float(cov[0, 0]), float(cov[0, 1])],
                        [float(cov[1, 0]), float(cov[1, 1])]]}
            out["r5_row"] = {
                "s": float(m2["s"]),
                "s_from_c1": float(1.0 + m3["c"][0] / RS),
                "rms_m2": float(np.sqrt((np.hypot(
                    *(T - apply_model(m2, V)).T) ** 2).mean())),
                "rms_m3": float(np.sqrt((np.hypot(
                    *(T - apply_model(m3, V)).T) ** 2).mean())),
                "sqrt_area_ratio": float(math.sqrt(
                    _IM[fb]["area"] / _IM[fa]["area"]))}
            th = math.atan2(m4["R"][1, 0], m4["R"][0, 0])
            out["finger_coef_row"] = [
                ai, bi, float(m4["c"][0]), float(m4["c"][1]),
                math.degrees(th), N, float(math.sqrt(cov[0, 0])),
                float(math.sqrt(cov[1, 1])), sd_rot, nin, ransac_rot]
            for rho in RHOS:
                sel = rr <= rho
                if int(sel.sum()) < 4 or int((~sel).sum()) == 0:
                    continue
                m1 = fit_radial(V[sel], T[sel], ())
                d = np.hypot(*(T[~sel] - apply_model(m1, V[~sel])).T)
                for dd, x in zip(d, rr[~sel]):
                    out["core_res"].setdefault(
                        (rho, band_of(x)), []).append(float(dd))
    return out


def _consistent_work(task):
    """The post-hoc pass on one pair of the consistent subset."""
    fa, fb, ca, prs = task
    A, B = _IM[fa]["p"], _IM[fb]["p"]
    res, paired = {}, {}
    for tau in (8, 15):
        pr = prs.get(tau)
        if pr is None or len(pr) < NMIN:
            continue
        V = A[pr[:, 0]] - ca
        T = B[pr[:, 1]]
        rr = np.hypot(V[:, 0], V[:, 1])
        n = len(V)
        order = np.argsort(rr)
        fold = np.empty(n, dtype=int)
        fold[order] = np.arange(n) % 5
        resmat = {}
        for name, fitter in MODELS:
            col = np.full(n, np.nan)
            for k in range(5):
                tr, te = fold != k, fold == k
                if int(tr.sum()) < MINPTS[name] or int(te.sum()) == 0:
                    continue
                m = fitter(V[tr], T[tr])
                col[te] = np.hypot(*(T[te] - apply_model(m, V[te])).T)
            resmat[name] = col
            for i in range(n):
                if not math.isnan(col[i]):
                    res.setdefault((tau, name, band_of(rr[i])), []).append(
                        float(col[i]))
        for a, b in CONTRASTS:
            ca_, cb_ = resmat[a], resmat[b]
            for i in range(n):
                if not (math.isnan(ca_[i]) or math.isnan(cb_[i])):
                    paired.setdefault((tau, band_of(rr[i]), a, b), []).append(
                        float(ca_[i] - cb_[i]))
    return res, paired


def _impostor_work(task):
    """One impostor pair: the alignment scored, then the same 5-fold CV."""
    fa, fb, sample = task
    A, B = _IM[fa]["p"], _IM[fb]["p"]
    (R0, t0), _ = ransac_score(A, B, sample)
    pr = mutual_pairs(A @ R0.T + t0, B, 15)
    out = {"n": len(pr), "res": {}}
    if len(pr) < NMIN:
        return out
    ca = _IM[fa]["c"]
    V = A[pr[:, 0]] - ca
    T = B[pr[:, 1]]
    rr = np.hypot(V[:, 0], V[:, 1])
    n = len(V)
    order = np.argsort(rr)
    fold = np.empty(n, dtype=int)
    fold[order] = np.arange(n) % 5
    for name, fitter in MODELS:
        for k in range(5):
            tr, te = fold != k, fold == k
            if int(tr.sum()) < MINPTS[name] or int(te.sum()) == 0:
                continue
            m = fitter(V[tr], T[tr])
            d = np.hypot(*(T[te] - apply_model(m, V[te])).T)
            for dd, x in zip(d, rr[te]):
                out["res"].setdefault((name, band_of(x)), []).append(float(dd))
    return out


def measure(src_dir, tag):
    """Run the whole comparison over one subset directory."""
    os.makedirs(WORK, exist_ok=True)
    # ------------------------------------------------------------------ main
    names = sorted(f for f in os.listdir(src_dir) if f.lower().endswith(".tif"))
    by_finger = defaultdict(list)
    for f in names:
        by_finger[f.split("_")[0]].append(f)
    print("%s: %d images, %d fingers" % (tag, len(names), len(by_finger)),
          flush=True)

    IM = dict(zip(names, pool.run([os.path.join(src_dir, f) for f in names],
                                  _extract_work, "INV015_SERIAL")))
    print("  extracted %d images" % len(IM), flush=True)

    W = IM[names[0]]["w"]
    H = IM[names[0]]["h"]

    mask_stats = {
        "threshold": QM_T, "block": BLOCK,
        "area_px2": [IM[f]["area"] for f in names],
        "area_lcm_px2": [IM[f]["area_lcm"] for f in names],
        "equiv_radius_px": [IM[f]["a"] for f in names],
        "n_minutiae": [len(IM[f]["p"]) for f in names],
        "within_finger_area_spread": [
            float(np.std([IM[f]["area"] for f in by_finger[g]]))
            for g in sorted(by_finger)],
        "within_finger_area_range": [
            [float(min(IM[f]["area"] for f in by_finger[g])),
             float(max(IM[f]["area"] for f in by_finger[g]))]
            for g in sorted(by_finger)],
    }

    # ---------------------------------------------------------- accumulators
    res_ho = defaultdict(lambda: array('f'))      # (tau, model, band, inhull) -> residuals
    res_fre = defaultdict(lambda: array('f'))     # (tau, model, band) -> fit residuals
    pair_rows = []
    radial_hist = defaultdict(lambda: np.zeros(len(BANDNAMES)))
    hull_cov = defaultdict(lambda: np.zeros((len(BANDNAMES), 2)))
    core_res = defaultdict(lambda: array('f'))    # (rho, band) -> held-out residual
    paired = defaultdict(lambda: array('f'))      # (tau, band, a, b) -> d_a - d_b, same point
    res_ho_c = defaultdict(lambda: array('f'))    # the same, on the consistent subset only
    paired_c = defaultdict(lambda: array('f'))
    pairdata = []
    m4_rows = []
    r5_rows = []
    finger_coef = defaultdict(list)
    excluded = Counter()
    ransac_fail = 0


    # Pass one, sequential: every draw from the module generator is made
    # here, in the order it was made when this was one pass, so the
    # alignments are the alignments the record was written from.
    global _IM
    _IM = IM
    tasks = []
    for g in sorted(by_finger):
        fs = sorted(by_finger[g])
        if len(fs) > 8:
            # robust_incidence and incidence below allocate eight columns and
            # index them with the impression number, and incidence fixes its
            # degrees of freedom at len(rows) - 7.  Nine impressions raise
            # IndexError inside a solver; refuse here, by name, instead.
            # Generalising the two solvers is a decision, not a repair.
            raise ValueError(
                "finger %s has %d impressions; the incidence solvers are "
                "written for eight" % (g, len(fs)))
        for ai in range(len(fs)):
            for bi in range(ai + 1, len(fs)):
                fa, fb = fs[ai], fs[bi]
                sample = ransac_sample(IM[fa]["p"], IM[fb]["p"])
                if sample is None:
                    ransac_fail += 1
                    continue
                tasks.append((g, fa, fb, ai, bi, sample))
    print("  aligned %d pairs, %d refusals" % (len(tasks), ransac_fail),
          flush=True)

    # Pass two: the pure part, merged back in pair order.
    for out in pool.run(tasks, _pair_work, "INV015_SERIAL"):
        pair_rows.extend(out["pair_rows"])
        for tau, h in out["radial_hist"].items():
            radial_hist[tau] += h
        for tau, hc in out["hull_cov"].items():
            hull_cov[tau] += hc
        for tau in out["excluded"]:
            excluded[tau] += 1
        for k, v in out["res_ho"].items():
            res_ho[k].extend(v)
        for k, v in out["res_fre"].items():
            res_fre[k].extend(v)
        for k, v in out["paired"].items():
            paired[k].extend(v)
        for k, v in out["core_res"].items():
            core_res[k].extend(v)
        if out["m4_row"] is not None:
            m4_rows.append(out["m4_row"])
            r5_rows.append(out["r5_row"])
            finger_coef[out["g"]].append(out["finger_coef_row"])
        pairdata.append({"g": out["g"], "ai": out["ai"], "bi": out["bi"],
                         "fa": out["fa"], "fb": out["fb"],
                         "ca": out["ca"], "pr": out["keep_pr"]})
    print("  %d pairs measured" % len(pairdata), flush=True)


    # -------------------------------- a post-hoc filter: consistent rotations
    def robust_incidence(rows, col):
        X = np.zeros((len(rows), 8))
        y = np.array([r[col] for r in rows])
        for k, r in enumerate(rows):
            X[k, int(r[0])] = -1.0
            X[k, int(r[1])] = 1.0
        w = np.ones(len(rows))
        for _ in range(30):
            sw = np.sqrt(w)[:, None]
            sol = np.linalg.lstsq(X * sw, y * np.sqrt(w), rcond=None)[0]
            res = y - X @ sol
            a = np.abs(res)
            w = np.where(a <= 3.0, 1.0, 3.0 / np.maximum(a, 1e-9))
        return y - X @ sol


    consistent = set()
    rot_resid = {}
    for g in sorted(finger_coef):
        rows = finger_coef[g]
        res = robust_incidence(rows, 4)
        for r, e in zip(rows, res):
            rot_resid[(g, int(r[0]), int(r[1]))] = float(e)
            if abs(e) <= 5.0:
                consistent.add((g, int(r[0]), int(r[1])))

    ctasks = [(pd["fa"], pd["fb"], pd["ca"], pd["pr"]) for pd in pairdata
              if (pd["g"], pd["ai"], pd["bi"]) in consistent]
    for res, pr in pool.run(ctasks, _consistent_work, "INV015_SERIAL"):
        for kk, v in res.items():
            res_ho_c[kk].extend(v)
        for kk, v in pr.items():
            paired_c[kk].extend(v)

    # ------------------------------------------ step 5, the eight impressions
    def incidence(rows, col, sdcol):
        """c(i->j) = c_j - c_i over the 28 pairs of one finger."""
        if len(rows) < 8:
            return None
        Xr = np.zeros((len(rows), 8))
        y = np.zeros(len(rows))
        sd = np.zeros(len(rows))
        for k, rw in enumerate(rows):
            Xr[k, int(rw[0])] = -1.0
            Xr[k, int(rw[1])] = 1.0
            y[k] = rw[col]
            sd[k] = rw[sdcol]
        sol = np.linalg.lstsq(Xr, y, rcond=None)[0]
        resid = y - Xr @ sol
        dof = len(rows) - 7
        obs = float(math.sqrt((resid ** 2).sum() / dof))
        null = []
        for _ in range(400):
            ys = Xr @ sol + rng.normal(0.0, np.maximum(sd, 1e-12))
            rs = ys - Xr @ np.linalg.lstsq(Xr, ys, rcond=None)[0]
            null.append(math.sqrt((rs ** 2).sum() / dof))
        null = np.array(null)
        return {"observed": obs, "null_mean": float(null.mean()),
                "null_p95": float(np.percentile(null, 95)),
                "ratio": float(obs / null.mean()) if null.mean() > 0 else None,
                "n_pairs": len(rows), "dof": dof,
                "mean_sd": float(sd.mean())}


    step5 = {}
    for g in sorted(finger_coef):
        rows = finger_coef[g]
        step5[g] = {"c1": incidence(rows, 2, 6), "c3": incidence(rows, 3, 7),
                    "rot": incidence(rows, 4, 8)}

    # ------------------------------------------------- step 10, the impostors
    fingers = sorted(by_finger)
    imp_pairs = [(a, b) for ai, a in enumerate(fingers) for b in fingers[ai + 1:]]
    if len(imp_pairs) > 300:
        sel = rng.choice(len(imp_pairs), 300, replace=False)
        imp_pairs = [imp_pairs[int(i)] for i in sel]
    imp_res = defaultdict(lambda: array('f'))
    imp_n = []
    itasks = []
    for a, b in imp_pairs:
        fa, fb = sorted(by_finger[a])[0], sorted(by_finger[b])[0]
        sample = ransac_sample(IM[fa]["p"], IM[fb]["p"])
        if sample is None:
            continue
        itasks.append((fa, fb, sample))
    for out in pool.run(itasks, _impostor_work, "INV015_SERIAL"):
        imp_n.append(out["n"])
        for k, v in out["res"].items():
            imp_res[k].extend(v)


    def summarise(store, keyf):
        out = {}
        for k, v in store.items():
            a = np.asarray(v)
            out[keyf(k)] = {"n": int(len(a)), "rms": float(np.sqrt((a ** 2).mean())),
                            "p90": float(np.percentile(a, 90)),
                            "median": float(np.median(a))}
        return out


    out = {
        "tag": tag, "images": len(names), "fingers": len(by_finger),
        "params": {"rs": RS, "qm_threshold": QM_T, "block": BLOCK,
                   "huber_delta": HUBER, "taus": TAUS, "bands": BANDNAMES,
                   "seed": SEED, "ransac": {"samples": RANSAC_N,
                                            "inlier_px": RANSAC_INLIER,
                                            "dist_tol_px": RANSAC_DTOL,
                                            "min_sep_px": RANSAC_MINSEP},
                   "n_min": NMIN, "lambdas": LAMBDAS, "rhos": RHOS,
                   "px_mm": 25.4 / 500.0},
        "mask": mask_stats,
        "ransac_failures": ransac_fail,
        "genuine_pairs": len(pair_rows) // len(TAUS),
        "N_by_tau": {str(t): [r[4] for r in pair_rows if r[3] == t]
                     for t in TAUS},
        "excluded_by_tau": {str(t): excluded[t] for t in TAUS},
        "radial_hist": {str(t): radial_hist[t].tolist() for t in TAUS},
        "hull_coverage": {str(t): (hull_cov[t][:, 1]
                                   / np.maximum(hull_cov[t][:, 0], 1)).tolist()
                          for t in TAUS},
        "R1": summarise(res_ho, lambda k: "%d|%s|%s|%s" % (k[0], k[1],
                                                           BANDNAMES[k[2]], k[3])),
        "R3": summarise(res_fre, lambda k: "%d|%s|%s" % (k[0], k[1],
                                                         BANDNAMES[k[2]])),
        "R4": m4_rows,
        "R5": r5_rows,
        "step5": step5,
        "core": summarise(core_res, lambda k: "%d|%s" % (k[0], BANDNAMES[k[1]])),
        "impostor": summarise(imp_res, lambda k: "%s|%s" % (k[0], BANDNAMES[k[1]])),
        "impostor_pairs": len(imp_pairs), "impostor_N": imp_n,
        "finger_coef": {g: finger_coef[g] for g in sorted(finger_coef)},
        "rot_resid": {"%s|%d|%d" % k: v for k, v in rot_resid.items()},
        "consistent_n": len(consistent), "consistent_of": len(pairdata),
        "R1c": summarise(res_ho_c, lambda k: "%d|%s|%s" % (k[0], k[1],
                                                           BANDNAMES[k[2]])),
        "paired_c": {"%d|%s|%s|%s" % (k[0], BANDNAMES[k[1]], k[2], k[3]): {
            "n": len(v), "mean": float(np.mean(v)),
            "se": float(np.std(v, ddof=1) / math.sqrt(len(v))) if len(v) > 1 else None,
            "frac_a_better": float(np.mean(np.asarray(v) < 0))}
            for k, v in paired_c.items()},
        "paired": {"%d|%s|%s|%s" % (k[0], BANDNAMES[k[1]], k[2], k[3]): {
            "n": len(v), "mean": float(np.mean(v)),
            "se": float(np.std(v, ddof=1) / math.sqrt(len(v))) if len(v) > 1 else None,
            "frac_a_better": float(np.mean(np.asarray(v) < 0))}
            for k, v in paired.items()},
    }
    return out
