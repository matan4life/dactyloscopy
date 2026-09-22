"""An ISO/IEC 19794-2:2005 template, as `iso-extract` writes it, turned into
the `.xyt` file `bozorth3` reads, as `mindtct` writes it.

This is the instrument of `quality/INV-018`, and it is the canonical minutia
record in its smallest form: one set of minutiae, read from one tool's file
and written into another's, with every difference between the two
conventions applied as an explicit, named parameter rather than assumed.

The three differences, each a measured fact of this repository:

  frame     `mindtct`'s `.xyt` has its origin at the bottom left and its y
            runs 1..H, `y_xyt = H - y_image` (`INV-011` F-1, from the
            source); `iso-extract`'s template is in the image's own frame,
            origin top left (`INV-011` F-2, F-3, F-5).
  angle     `mindtct`'s `.xyt` angle is degrees, 0 east, counterclockwise,
            pointing away from the ridge, and reports a known orientation
            turned by half a circle (`INV-012` F-2: circular mean 178.624
            degrees over 648 points); `iso-extract`'s theta byte, in units
            of 360/256 degrees, reports it unturned (`INV-012` F-3: 0.117
            degrees). `INV-014` measured the same half turn on the corpus,
            3.20 and 3.52 degrees from exact on the two DB1 subsets. The
            turn is the parameter `turn_deg`; `D-4`, how the two angles are
            related, is an open question, and this module applies the
            measured relation as a parameter of an investigation, not as a
            decision.
  grid      `mindtct` writes 32 angle values 11.25 degrees apart;
            `iso-extract` 256 values 1.40625 degrees apart (`INV-012` F-7).
            `bozorth3` reads any integer degree (`INV-018` F-1), so the
            default keeps the finer grid rounded to a degree; `quantise` can
            snap it to `mindtct`'s 32 values so that the effect is a number.

The quality byte is carried through as the fourth column, which `bozorth3`
reads and, below its minutia cap, does not use (`INV-018` F-1); `quality`
can zero it so that too is a number.

Imported, never invoked as a command. Nothing here reads an image or runs
a tool: bytes in, bytes out.
"""

TEMPLATE_HEADER = 28        # the minutia count is the byte before, at 27
MINUTIA_BYTES = 6
XYT_FRACTION = 360.0 / 256.0
MINDTCT_STEP = 11.25


def _sround(x):
    """`lfs.h` line 96: round half away from zero; non-negative here."""
    return int(x + 0.5)


# xytreps.c lines 98-103 over the 32 direction indices, which INV-002 F-8
# lists as 0 11 22 34 ... 337 349 and INV-012 F-7 observed all 32 of
MINDTCT_GRID = tuple(sorted({(270 - _sround(d * MINDTCT_STEP)) % 360
                             for d in range(32)}))


def be16(b, o):
    return (b[o] << 8) | b[o + 1]


def read_ist(template):
    """The minutiae of one template: (x, y, theta_byte, quality, type) each,
    plus the header's image width and height. The layout is `INV-011`
    F-2's, derived from the writer: count at offset 27, six bytes per
    minutia from 28 - a big-endian X word whose top two bits are the type and
    whose low fourteen are x, a Y word masked the same way, one angle byte,
    one quality byte."""
    n = template[27]
    out = []
    for i in range(n):
        o = TEMPLATE_HEADER + MINUTIA_BYTES * i
        xw = be16(template, o)
        out.append((xw & 0x3FFF, be16(template, o + 2) & 0x3FFF,
                    template[o + 4], template[o + 5], xw >> 14))
    return out, be16(template, 14), be16(template, 16)


def snap_to_mindtct_grid(theta):
    """The nearest of `mindtct`'s 32 angle values, ties to the lower."""
    best = min(MINDTCT_GRID, key=lambda g: (min(abs(theta - g), 360 - abs(theta - g)), g))
    return best


def to_xyt(minutiae, height, turn_deg=180, quantise=None, quality="keep",
           sense=1):
    """Rows of (x, y, theta_deg, q) in `mindtct`'s `.xyt` convention.

    turn_deg   the half turn `INV-012` measured, applied to the ISO angle;
               0 applies none, which `INV-018` measures the cost of.
    quantise   None keeps the ISO grid rounded to a degree; "mindtct32"
               snaps to the 32 values `mindtct` writes.
    quality    "keep" carries the ISO quality byte; "zero" writes 0.
    sense      1 keeps the angle's sense; -1 mirrors it, theta -> -theta,
               which is what a frame flip would do to a direction if the
               two tools' angles ran opposite ways. `INV-012` measured
               that they do not; `INV-018` measures what -1 costs."""
    if quantise not in (None, "mindtct32"):
        raise ValueError("quantise must be None or 'mindtct32'")
    if quality not in ("keep", "zero"):
        raise ValueError("quality must be 'keep' or 'zero'")
    if sense not in (1, -1):
        raise ValueError("sense must be 1 or -1")
    rows = []
    for x, y, tb, q, _type in minutiae:
        theta = (sense * tb * XYT_FRACTION + turn_deg) % 360.0
        t = int(round(theta)) % 360
        if quantise == "mindtct32":
            t = snap_to_mindtct_grid(t)
        rows.append((x, height - y, t, q if quality == "keep" else 0))
    return rows


def write_xyt(rows):
    """The bytes of a `.xyt` file: one line per minutia, four integers,
    space-separated, newline-terminated, in the order given."""
    return "".join("%d %d %d %d\n" % r for r in rows).encode("ascii")


def convert(template, height, **params):
    """Template bytes in, `.xyt` bytes and the minutia count out."""
    minutiae, _, _ = read_ist(template)
    rows = to_xyt(minutiae, height, **params)
    return write_xyt(rows), len(rows)
