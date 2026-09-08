"""The origin test of `quality/INV-011`: where each extractor puts a minutia.

Every image is synthetic. A loop-and-delta ridge field is blanked outside a
named half, so that a minutia can occur only in the half that carries the
field and the answer is known by construction.

Imported, never invoked as a command, as `REF-013` decision 3 requires; the
command form is `scripts/measure_coordinate_frames.sh`, which imports and
calls. `measure()` returns one row per case and prints the same.
"""
import ctypes
import hashlib
import math
import os
import subprocess

from PIL import Image

W = H = 384
PERIOD = 9.0
WORK = os.environ.get("INV011_WORK", "/tmp/inv011")

ISO = 0x01010001
BUF = 34 + 256 * 6
lib = ctypes.CDLL("libFJFX.so")
lib.fjfx_create_fmd_from_raw.restype = ctypes.c_int
lib.fjfx_create_fmd_from_raw.argtypes = [
    ctypes.c_char_p, ctypes.c_ushort, ctypes.c_ushort, ctypes.c_ushort,
    ctypes.c_uint, ctypes.c_char_p, ctypes.POINTER(ctypes.c_uint)]


def ridge_field(width, height, core, delta, keep):
    """A loop-and-delta ridge field, blanked outside `keep`.

    phase = 2*pi*(r + 2*angle_to_core - 2*angle_to_delta)/period, with r the
    distance to the core. Pixel = 128 + 110*cos(phase), clamped to 0..255.
    `keep(x, y)` decides which pixels carry the field; everywhere else the
    pixel is 255, a uniform white in which no ridge and so no minutia exists.
    """
    cx, cy = core
    dx, dy = delta
    px = bytearray(width * height)
    for y in range(height):
        for x in range(width):
            if not keep(x, y):
                px[y * width + x] = 255
                continue
            r = math.hypot(x - cx, y - cy)
            a1 = math.atan2(y - cy, x - cx)
            a2 = math.atan2(y - dy, x - dx)
            phase = 2.0 * math.pi * (r + 2.0 * a1 - 2.0 * a2) / PERIOD
            px[y * width + x] = max(0, min(255, int(round(
                128.0 + 110.0 * math.cos(phase)))))
    return bytes(px)


def save(name, pixels, width=W, height=H):
    img = Image.frombytes("L", (width, height), pixels)
    img.save("%s/%s.pgm" % (WORK, name))
    img.save("%s/%s.png" % (WORK, name))
    same = (Image.open("%s/%s.pgm" % (WORK, name)).tobytes()
            == Image.open("%s/%s.png" % (WORK, name)).tobytes())
    return same


def iso_from_raw(pixels, dpi, width=W, height=H):
    out = ctypes.create_string_buffer(BUF)
    size = ctypes.c_uint(BUF)
    rc = lib.fjfx_create_fmd_from_raw(pixels, dpi, height, width, ISO,
                                      out, ctypes.byref(size))
    if rc != 0:
        return rc, None
    return 0, out.raw[:size.value]


def be16(b, o):
    return (b[o] << 8) | b[o + 1]


def decode(t):
    """The ISO record, by the offsets serializeFpData.h writes."""
    n = t[27]
    minutiae = []
    for i in range(n):
        o = 28 + 6 * i
        xw = be16(t, o)
        minutiae.append((xw & 0x3FFF, be16(t, o + 2) & 0x3FFF, xw >> 14))
    return {
        "magic": t[0:4], "version": t[4:8],
        "length": (t[8] << 24) | (t[9] << 16) | (t[10] << 8) | t[11],
        "image_x": be16(t, 14), "image_y": be16(t, 16),
        "res_x": be16(t, 18), "res_y": be16(t, 20),
        "views": t[22], "reserved": t[23],
        "finger": t[24], "view_impression": t[25], "quality": t[26],
        "count": n, "minutiae": minutiae, "bytes": len(t),
    }


def mindtct_xyt(name):
    subprocess.run(["mindtct", "%s/%s.png" % (WORK, name),
                    "%s/%s" % (WORK, name)], check=True,
                   capture_output=True)
    rows = []
    with open("%s/%s.xyt" % (WORK, name)) as fp:
        for line in fp:
            x, y, t, q = line.split()
            rows.append((int(x), int(y), int(t), int(q)))
    return rows


def mindtct_min(name):
    """The .min file, which results.c says is in LFS native, origin top-left."""
    rows = []
    with open("%s/%s.min" % (WORK, name)) as fp:
        head = fp.readline().strip()
        for line in fp:
            fields = line.split(":")
            if len(fields) < 3 or not fields[0].strip().isdigit():
                continue
            x, y = fields[1].split(",")
            rows.append((int(x), int(y)))
    return head, rows


def span(vals):
    return (min(vals), max(vals)) if vals else (None, None)


def measure():
    """Run the four cases; return every line the record was written from."""
    os.makedirs(WORK, exist_ok=True)
    out = []

    def emit(line=""):
        print(line)
        out.append(line)

    emit("== construction")
    emit("   %d x %d, ridge period %.0f px, pixel = 128 + 110*cos(phase),"
          % (W, H, PERIOD))
    emit("   phase = 2*pi*(r + 2*a_core - 2*a_delta)/period; blank = 255")

    CASES = [
        ("top",    (192, 60),  (192, 132), lambda x, y: y < H // 2,
         "rows 0..191"),
        ("bottom", (192, 252), (192, 324), lambda x, y: y >= H // 2,
         "rows 192..383"),
        ("left",   (60, 192),  (132, 192), lambda x, y: x < W // 2,
         "columns 0..191"),
        ("right",  (252, 192), (324, 192), lambda x, y: x >= W // 2,
         "columns 192..383"),
    ]

    emit()
    emit("== F-3, the origin test")
    for name, core, delta, keep, where in CASES:
        px = ridge_field(W, H, core, delta, keep)
        identical = save(name, px)
        rc, tmpl = iso_from_raw(px, 500)
        xyt = mindtct_xyt(name)
        emit("  -- %s: the ridge field occupies %s; core %s, delta %s"
              % (name, where, core, delta))
        emit("     png and pgm decode to identical pixels: %s" % identical)
        if xyt:
            xs, ys = [r[0] for r in xyt], [r[1] for r in xyt]
            emit("     mindtct .xyt : %d minutiae, x %s, y %s"
                  % (len(xyt), span(xs), span(ys)))
            head, mn = mindtct_min(name)
            if mn:
                emit("     mindtct .min : %d minutiae, x %s, y %s   [%s]"
                      % (len(mn), span([m[0] for m in mn]),
                         span([m[1] for m in mn]), head))
        else:
            emit("     mindtct .xyt : 0 minutiae")
        if rc:
            emit("     iso-extract  : the library returned %d" % rc)
        else:
            d = decode(tmpl)
            xs, ys = [m[0] for m in d["minutiae"]], [m[1] for m in d["minutiae"]]
            emit("     iso-extract  : %d minutiae, x %s, y %s"
                  % (d["count"], span(xs), span(ys)))
    return out
