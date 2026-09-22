"""The fixture part of `quality/INV-011`: the paired example, F-4, F-5, F-6.

One synthetic image gives the worked example of F-1 and F-2; the three fixture
images `MAN-tools.v2` names give the declared image size of F-4 and the ranges
of F-5; and F-6 varies the declared resolution by calling the library directly,
which is an instrument of the investigation and not the invocation `REF-012`
adopted.

Imported, never invoked as a command; the command form is
`scripts/measure_coordinate_frames.py`. Only ranges and counts leave this
process: no coordinate of any corpus minutia is returned.
"""
import ctypes
import json
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


def ridge_field(width, height, core, delta, keep=lambda x, y: True):
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
            ph = 2.0 * math.pi * (r + 2.0 * a1 - 2.0 * a2) / PERIOD
            px[y * width + x] = max(0, min(255, int(round(
                128.0 + 110.0 * math.cos(ph)))))
    return bytes(px)


def be16(b, o):
    return (b[o] << 8) | b[o + 1]


def decode(t):
    n = t[27]
    mins = []
    for i in range(n):
        o = 28 + 6 * i
        xw = be16(t, o)
        mins.append((xw & 0x3FFF, be16(t, o + 2) & 0x3FFF, xw >> 14))
    return {"magic": bytes(t[0:4]), "version": bytes(t[4:8]),
            "length": int.from_bytes(t[8:12], "big"),
            "image_x": be16(t, 14), "image_y": be16(t, 16),
            "res_x": be16(t, 18), "res_y": be16(t, 20),
            "views": t[22], "reserved": t[23], "count": n,
            "minutiae": mins, "bytes": len(t)}


def iso_raw(px, dpi, width=W, height=H):
    out = ctypes.create_string_buffer(BUF)
    size = ctypes.c_uint(BUF)
    rc = lib.fjfx_create_fmd_from_raw(px, dpi, height, width, ISO, out,
                                      ctypes.byref(size))
    return (rc, None) if rc else (0, out.raw[:size.value])


def span(v):
    return (min(v), max(v)) if v else (None, None)


def measure(fixture_dir, repo_dir):
    """Run the three parts; return every line the record was written from."""
    os.makedirs(WORK, exist_ok=True)
    out = []

    def emit(line=""):
        print(line)
        out.append(line)

    # ------------------------------------------------------------------ paired
    emit("== F-1/F-2 worked example: one synthetic image, three files")
    px = ridge_field(W, H, (192, 60), (192, 132), lambda x, y: y < H // 2)
    Image.frombytes("L", (W, H), px).save(WORK + "/t.png")
    Image.frombytes("L", (W, H), px).save(WORK + "/t.pgm")
    subprocess.run(["mindtct", WORK + "/t.png", WORK + "/t"], check=True,
                   capture_output=True)
    mn = []
    with open(WORK + "/t.min") as fp:
        head = fp.readline().strip()
        for line in fp:
            f = line.split(":")
            if len(f) < 3 or not f[0].strip().isdigit():
                continue
            a, b = f[1].split(",")
            mn.append((int(a), int(b)))
    xyt = [tuple(int(v) for v in l.split()) for l in open(WORK + "/t.xyt")]
    subprocess.run(["iso-extract", WORK + "/t.pgm", WORK + "/t.ist"], check=True,
                   capture_output=True)
    tmpl = open(WORK + "/t.ist", "rb").read()
    d = decode(tmpl)
    emit("   %s" % head)
    emit("   i   .min (x,y)      .xyt (x,y)      384 - .min y")
    for i in range(min(4, len(mn))):
        emit("   %-3d %-15s %-15s %d" % (i, mn[i], xyt[i][:2], H - mn[i][1]))
    emit("   every row: .xyt x == .min x : %s"
          % all(mn[i][0] == xyt[i][0] for i in range(len(mn))))
    emit("   every row: .xyt y == %d - .min y : %s"
          % (H, all(H - mn[i][1] == xyt[i][1] for i in range(len(mn)))))
    emit("   iso-extract on the same image: %d minutiae, y %s"
          % (d["count"], span([m[1] for m in d["minutiae"]])))
    emit("   the template's first 24 bytes: %s" % tmpl[:24].hex(" "))
    emit("   magic %r version %r length %d (file is %d bytes)"
          % (d["magic"], d["version"], d["length"], d["bytes"]))
    emit("   header image_x %d image_y %d res_x %d res_y %d views %d reserved %d"
          % (d["image_x"], d["image_y"], d["res_x"], d["res_y"], d["views"],
             d["reserved"]))

    # ------------------------------------------------------- F-3, right retried
    emit()
    emit("== F-3, the right-half case retried")
    for tag, core, delta in (("as first tried", (252, 192), (324, 192)),
                             ("core and delta swapped", (324, 192), (252, 192)),
                             ("both moved inward", (240, 192), (300, 192)),
                             ("both moved down", (252, 252), (324, 324))):
        p = ridge_field(W, H, core, delta, lambda x, y: x >= W // 2)
        rc, t = iso_raw(p, 500)
        if rc:
            emit("   %-24s core %s delta %s -> library returned %d"
                  % (tag, core, delta, rc))
        else:
            dd = decode(t)
            emit("   %-24s core %s delta %s -> %d minutiae, x %s, y %s"
                  % (tag, core, delta, dd["count"],
                     span([m[0] for m in dd["minutiae"]]),
                     span([m[1] for m in dd["minutiae"]])))

    # ------------------------------------------------------------- F-4 and F-5
    emit()
    emit("== F-4 and F-5, on the fixture")
    man = json.load(open(os.path.join(repo_dir,
                                         "manifests/MAN-fvc2002.v1.json"),
                                    encoding="utf-8"))
    sub = man["subsets"]["fvc2002/DB1_B"]
    mw, mh = sub["width"]["value"], sub["height"]["value"]
    emit("   MAN-fvc2002.v1.json fvc2002/DB1_B: width %d, height %d" % (mw, mh))
    names = ["101_1", "101_2", "102_1"]
    allx_m, ally_m, allx_i, ally_i = [], [], [], []
    for n in names:
        tif = Image.open("%s/%s.tif" % (fixture_dir, n))
        w, h = tif.size
        tif.convert("L").save("%s/%s.png" % (WORK, n))
        tif.convert("L").save("%s/%s.pgm" % (WORK, n))
        subprocess.run(["mindtct", "%s/%s.png" % (WORK, n), "%s/%s" % (WORK, n)],
                       check=True, capture_output=True)
        rows = [tuple(int(v) for v in l.split())
                for l in open("%s/%s.xyt" % (WORK, n))]
        subprocess.run(["iso-extract", "%s/%s.pgm" % (WORK, n),
                        "%s/%s.ist" % (WORK, n)], check=True, capture_output=True)
        dd = decode(open("%s/%s.ist" % (WORK, n), "rb").read())
        xs, ys = [r[0] for r in rows], [r[1] for r in rows]
        ixs = [m[0] for m in dd["minutiae"]]
        iys = [m[1] for m in dd["minutiae"]]
        allx_m += xs; ally_m += ys; allx_i += ixs; ally_i += iys
        emit("   %s  PIL size (w,h) %s" % (n, (w, h)))
        emit("      template header: image_x %d image_y %d res_x %d res_y %d"
              % (dd["image_x"], dd["image_y"], dd["res_x"], dd["res_y"]))
        emit("      mindtct .xyt %2d minutiae, x %s, y %s"
              % (len(rows), span(xs), span(ys)))
        emit("      iso-extract  %2d minutiae, x %s, y %s"
              % (dd["count"], span(ixs), span(iys)))
    emit("   over the three: mindtct x %s y %s | iso-extract x %s y %s"
          % (span(allx_m), span(ally_m), span(allx_i), span(ally_i)))

    # --------------------------------------------------------------------- F-6
    emit()
    emit("== F-6, the declared resolution varied. An instrument, not the")
    emit("   invocation REF-012 adopted.")
    base = ridge_field(W, H, (192, 132), (192, 252))
    emit("   the image: the same field over the whole 384 x 384, core (192,132),")
    emit("   delta (192,252), nothing blanked")
    emit("   dpi   rc  count  header res_x/res_y  x range        y range")
    for dpi in (250, 300, 400, 450, 499, 500, 501, 550, 600, 800, 1000, 1008,
                1024, 1025):
        rc, t = iso_raw(base, dpi)
        if rc:
            emit("   %-5d %-3d -" % (dpi, rc))
            continue
        dd = decode(t)
        emit("   %-5d %-3d %-6d %d/%-14d %-14s %s"
              % (dpi, rc, dd["count"], dd["res_x"], dd["res_y"],
                 span([m[0] for m in dd["minutiae"]]),
                 span([m[1] for m in dd["minutiae"]])))
    return out
