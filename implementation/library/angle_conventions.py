"""The instrument of `quality/INV-012`: the angle each extractor reports.

Every image is synthetic. A minutia is a phase dislocation in an analytic ridge
field, so the orientation is a stated property of the generator rather than an
interpretation of a picture, and the direction is computed exactly from the
gradient of the phase with that dislocation's own singular term removed.

Imported, never invoked as a command, as `REF-013` decision 3 requires; the
command form is `scripts/measure_angle_conventions.sh`, which imports and
calls.

`measure()` returns the rows the record is written from. No corpus image is
read: this instrument needs none.
"""
import math
import os
import subprocess

import numpy as np
from PIL import Image

W = H = 384
PERIOD = 9.0
CX = CY = 192.0
WORK = os.environ.get("INV012_WORK", "/tmp/inv012")

# nine dislocations on a square lattice in the (along-ridge, across-ridge)
# frame of the field
LATTICE = [(a, b) for b in (-110.0, 0.0, 110.0) for a in (-110.0, 0.0, 110.0)]
SWEEP = list(range(0, 360, 10))
TARGETS = {"ending": 0.0, "bifurcation": math.pi}


def frame(phi_deg):
    phi = math.radians(phi_deg)
    return ((math.cos(phi), -math.sin(phi)), (-math.sin(phi), -math.cos(phi)))


def wrap(a):
    return (a + math.pi) % (2.0 * math.pi) - math.pi


def background_phase(j, ab):
    """Phase at dislocation j from the base field and the other eight."""
    a, b = ab[j]
    ph = 2.0 * math.pi * b / PERIOD
    for i, (ai, bi) in enumerate(ab):
        if i == j:
            continue
        ph += math.atan2(b - bi, a - ai)
    return ph


def place(target):
    """Shift each dislocation across the ridges until its background phase
    is `target`, so that the line terminating at it is dark (target 0, a
    ridge ending) or light (target pi, a ridge bifurcation)."""
    ab = [list(p) for p in LATTICE]
    for _ in range(60):
        worst = 0.0
        for j in range(len(ab)):
            r = wrap(background_phase(j, ab) - target)
            ab[j][1] -= r * PERIOD / (2.0 * math.pi)
            worst = max(worst, abs(r))
    return [tuple(p) for p in ab], math.degrees(worst)


def true_direction(j, ab, phi_deg):
    """Exact ridge direction at dislocation j, in degrees counterclockwise
    from +x as the image is displayed."""
    a, b = ab[j]
    gu, gn = 0.0, 2.0 * math.pi / PERIOD
    for i, (ai, bi) in enumerate(ab):
        if i == j:
            continue
        da, db = a - ai, b - bi
        r2 = da * da + db * db
        gu += -db / r2
        gn += da / r2
    # perpendicular to the gradient, taken in the sense of +u
    du, dn = (gn, -gu) if gn > 0 else (-gn, gu)
    (ux, uy), (nx, ny) = frame(phi_deg)
    vx = du * ux + dn * nx
    vy = du * uy + dn * ny
    return math.degrees(math.atan2(-vy, vx)) % 360.0


def render(phi_deg, ab):
    (ux, uy), (nx, ny) = frame(phi_deg)
    xs = np.arange(W, dtype=np.float64) - CX
    ys = np.arange(H, dtype=np.float64) - CY
    dx = xs[None, :]
    dy = ys[:, None]
    s = dx * ux + dy * uy
    t = dx * nx + dy * ny
    ph = 2.0 * np.pi * t / PERIOD
    for (a, b) in ab:
        ph = ph + np.arctan2(t - b, s - a)
    v = 128.0 - 110.0 * np.cos(ph)
    return np.clip(np.rint(v), 0, 255).astype(np.uint8)


def points(phi_deg, ab):
    (ux, uy), (nx, ny) = frame(phi_deg)
    return [(CX + a * ux + b * nx, CY + a * uy + b * ny) for a, b in ab]


def axis_from_pixels(img, p, phi_deg, ab, j):
    """Ridge axis by the structure tensor of an annulus around p, in degrees
    modulo 180. Arithmetic on the pixels only; no tool is involved."""
    x0, y0 = int(round(p[0])), int(round(p[1]))
    r = 22
    sub = img[max(0, y0 - r):y0 + r + 1, max(0, x0 - r):x0 + r + 1]
    sub = sub.astype(np.float64)
    gy, gx = np.gradient(sub)
    yy, xx = np.mgrid[0:sub.shape[0], 0:sub.shape[1]]
    m = ((yy - (y0 - max(0, y0 - r))) ** 2
         + (xx - (x0 - max(0, x0 - r))) ** 2) > 81
    gx, gy = gx[m], gy[m]
    jxx = float(np.sum(gx * gx))
    jyy = float(np.sum(gy * gy))
    jxy = float(np.sum(gx * gy))
    # the gradient axis; the ridge axis is perpendicular to it
    ang = 0.5 * math.atan2(2.0 * jxy, jxx - jyy)
    gxa, gya = math.cos(ang), math.sin(ang)
    return math.degrees(math.atan2(-gxa, -gya)) % 180.0


def ray_means(img, p, phi_deg):
    """Mean pixel value along the +u and -u rays from p, over one to three
    ridge periods. Dark on +u is a ridge terminating there."""
    (ux, uy), _ = frame(phi_deg)
    out = []
    for sgn in (1.0, -1.0):
        vals = []
        for d in np.arange(PERIOD, 3.0 * PERIOD + 0.01, 0.5):
            x = int(round(p[0] + sgn * d * ux))
            y = int(round(p[1] + sgn * d * uy))
            if 0 <= x < W and 0 <= y < H:
                vals.append(float(img[y, x]))
        out.append(sum(vals) / len(vals) if vals else float("nan"))
    return out


def read_min(path):
    rows = []
    with open(path) as fp:
        fp.readline()
        for line in fp:
            f = line.split(":")
            if len(f) < 6 or not f[0].strip().isdigit():
                continue
            x, y = f[1].split(",")
            rows.append((int(x), int(y), int(f[2]), f[4].strip()))
    return rows


def be16(b, o):
    return (b[o] << 8) | b[o + 1]


def read_ist(path):
    t = open(path, "rb").read()
    n = t[27]
    return [(be16(t, 28 + 6 * i) & 0x3FFF, be16(t, 30 + 6 * i) & 0x3FFF,
             be16(t, 28 + 6 * i) >> 14, t[32 + 6 * i]) for i in range(n)]


def measure():
    """Run the sweep; return the per-point rows and the two checks."""
    os.makedirs(WORK, exist_ok=True)
    placed = {}
    for name, target in TARGETS.items():
        ab, worst = place(target)
        placed[name] = ab
        print("placement %-12s residual background phase at worst %.4f deg"
              % (name, worst))
    print()

    rows = []
    axis_err = []
    ray_rows = []
    for name, ab in placed.items():
        for phi in SWEEP:
            img = render(phi, ab)
            pil = Image.fromarray(img, "L")
            tag = "%s_%03d" % (name[:3], phi)
            pil.save("%s/%s.png" % (WORK, tag))
            pil.save("%s/%s.pgm" % (WORK, tag))
            pts = points(phi, ab)
            truth = [true_direction(j, ab, phi) for j in range(len(ab))]
            if phi in (0, 90, 180, 270) or phi == 30:
                for j, p in enumerate(pts):
                    ax = axis_from_pixels(img, p, phi, ab, j)
                    d = min((truth[j] - ax) % 180.0, (ax - truth[j]) % 180.0)
                    axis_err.append(d)
                    ray_rows.append((name, phi, j) + tuple(ray_means(img, p, phi)))
            subprocess.run(["mindtct", "%s/%s.png" % (WORK, tag),
                            "%s/%s" % (WORK, tag)], check=True,
                           capture_output=True)
            xyt = [tuple(int(v) for v in l.split())
                   for l in open("%s/%s.xyt" % (WORK, tag))]
            mn = read_min("%s/%s.min" % (WORK, tag))
            r = subprocess.run(["iso-extract", "%s/%s.pgm" % (WORK, tag),
                                "%s/%s.ist" % (WORK, tag)], capture_output=True)
            ist = read_ist("%s/%s.ist" % (WORK, tag)) if r.returncode == 0 else []
            for j, p in enumerate(pts):
                row = {"family": name, "phi": phi, "j": j, "truth": truth[j],
                       "n_xyt": len(xyt), "n_ist": len(ist),
                       "iso_rc": r.returncode}
                cand = sorted((math.hypot(m[0] - p[0], (H - m[1]) - p[1]), k)
                              for k, m in enumerate(xyt))
                if cand and cand[0][0] <= 6.0:
                    k = cand[0][1]
                    row["m_dist"] = cand[0][0]
                    row["m_theta"] = xyt[k][2]
                    row["m_qual"] = xyt[k][3]
                    if k < len(mn):
                        row["m_dir"] = mn[k][2]
                        row["m_type"] = mn[k][3]
                cand = sorted((math.hypot(m[0] - p[0], m[1] - p[1]), k)
                              for k, m in enumerate(ist))
                if cand and cand[0][0] <= 6.0:
                    k = cand[0][1]
                    row["i_dist"] = cand[0][0]
                    row["i_theta"] = ist[k][3]
                    row["i_type"] = ist[k][2]
                rows.append(row)

    print("%d rows; structure-tensor axis error max %.3f deg over %d"
          % (len(rows), max(axis_err), len(axis_err)))
    return {"rows": rows, "axis_err_max": max(axis_err),
            "axis_err_n": len(axis_err), "rays": ray_rows,
            "placed": {k: list(v) for k, v in placed.items()}}
