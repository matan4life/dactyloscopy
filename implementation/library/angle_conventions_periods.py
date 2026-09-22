"""The period check of `quality/INV-012`: the same construction at four periods.

The ridge period is a parameter of the construction and not an incidental, so
the sweep is repeated at 7, 9, 11 and 13 pixels. Imported, never invoked as a
command; the command form is `scripts/measure_angle_conventions.py`.
"""
import math
import os
import subprocess
import numpy as np
from PIL import Image

W = H = 384
CX = CY = 192.0
WORK = os.environ.get("INV012_WORK", "/tmp/inv012")
LATTICE = [(a, b) for b in (-110.0, 0.0, 110.0) for a in (-110.0, 0.0, 110.0)]


def frame(phi_deg):
    phi = math.radians(phi_deg)
    return ((math.cos(phi), -math.sin(phi)), (-math.sin(phi), -math.cos(phi)))


def wrap(a):
    return (a + math.pi) % (2.0 * math.pi) - math.pi


def place(target, period):
    ab = [list(p) for p in LATTICE]
    for _ in range(60):
        for j in range(len(ab)):
            a, b = ab[j]
            ph = 2.0 * math.pi * b / period
            for i, (ai, bi) in enumerate(ab):
                if i != j:
                    ph += math.atan2(b - bi, a - ai)
            ab[j][1] -= wrap(ph - target) * period / (2.0 * math.pi)
    return [tuple(p) for p in ab]


def true_direction(j, ab, phi_deg, period):
    a, b = ab[j]
    gu, gn = 0.0, 2.0 * math.pi / period
    for i, (ai, bi) in enumerate(ab):
        if i == j:
            continue
        da, db = a - ai, b - bi
        r2 = da * da + db * db
        gu += -db / r2
        gn += da / r2
    du, dn = (gn, -gu) if gn > 0 else (-gn, gu)
    (ux, uy), (nx, ny) = frame(phi_deg)
    return math.degrees(math.atan2(-(du * uy + dn * ny),
                                   du * ux + dn * nx)) % 360.0


def render(phi_deg, ab, period):
    (ux, uy), (nx, ny) = frame(phi_deg)
    dx = (np.arange(W, dtype=np.float64) - CX)[None, :]
    dy = (np.arange(H, dtype=np.float64) - CY)[:, None]
    s = dx * ux + dy * uy
    t = dx * nx + dy * ny
    ph = 2.0 * np.pi * t / period
    for (a, b) in ab:
        ph = ph + np.arctan2(t - b, s - a)
    return np.clip(np.rint(128.0 - 110.0 * np.cos(ph)), 0, 255).astype(np.uint8)


def be16(b, o):
    return (b[o] << 8) | b[o + 1]


def circ(v):
    c = sum(math.cos(math.radians(x)) for x in v) / len(v)
    s = sum(math.sin(math.radians(x)) for x in v) / len(v)
    return math.degrees(math.atan2(s, c)) % 360.0, math.hypot(c, s)


def measure():
    """Repeat the sweep at four ridge periods; return one row each."""
    os.makedirs(WORK, exist_ok=True)
    rows = []
    for period in (7.0, 9.0, 11.0, 13.0):
        ab = place(0.0, period)
        mv, iv, refused, nm = [], [], 0, 0
        for phi in (0, 45, 90, 135, 180, 225, 270, 315):
            img = render(phi, ab, period)
            pil = Image.fromarray(img, "L")
            tag = "p%d_%03d" % (period, phi)
            pil.save("%s/%s.png" % (WORK, tag))
            pil.save("%s/%s.pgm" % (WORK, tag))
            (ux, uy), (nx, ny) = frame(phi)
            pts = [(CX + a * ux + b * nx, CY + a * uy + b * ny) for a, b in ab]
            truth = [true_direction(j, ab, phi, period) for j in range(len(ab))]
            subprocess.run(["mindtct", "%s/%s.png" % (WORK, tag),
                            "%s/%s" % (WORK, tag)], check=True, capture_output=True)
            xyt = [tuple(int(v) for v in l.split())
                   for l in open("%s/%s.xyt" % (WORK, tag))]
            r = subprocess.run(["iso-extract", "%s/%s.pgm" % (WORK, tag),
                                "%s/%s.ist" % (WORK, tag)], capture_output=True)
            ist = []
            if r.returncode:
                refused += 1
            else:
                t = open("%s/%s.ist" % (WORK, tag), "rb").read()
                ist = [(be16(t, 28 + 6 * i) & 0x3FFF, be16(t, 30 + 6 * i) & 0x3FFF,
                        t[32 + 6 * i]) for i in range(t[27])]
            nm += len(xyt)
            for j, p in enumerate(pts):
                c = sorted((math.hypot(m[0] - p[0], (H - m[1]) - p[1]), m)
                           for m in xyt)
                if c and c[0][0] <= 6.0:
                    mv.append((c[0][1][2] - truth[j]) % 360.0)
                c = sorted((math.hypot(m[0] - p[0], m[1] - p[1]), m) for m in ist)
                if c and c[0][0] <= 6.0:
                    iv.append((c[0][1][2] * 360.0 / 256.0 - truth[j]) % 360.0)
        line = "period %4.1f  mindtct %3d paired" % (period, len(mv))
        if mv:
            m, R = circ(mv)
            line += ", offset %7.3f R %.5f" % (m, R)
        line += " | iso refused %d of 8" % refused
        if iv:
            m, R = circ(iv)
            line += ", %3d paired, offset %7.3f R %.5f" % (len(iv), m, R)
        print(line)
        rows.append(line)
    return rows
