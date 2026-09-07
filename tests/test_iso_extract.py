"""What ``iso-extract`` reads, and what it does when the input is malformed.

``REF-005`` requires that what reaches a tool be verified identical to what the
dataset holds. Until now this repository has asserted that and never checked
it. These tests check it, on the one tool whose reader this repository owns.

**What can be observed from here, and what cannot.** The reader is
``pgm_parse`` in ``implementation/tools/iso-extract.c``. It is a function
inside a binary: the runtime image carries no compiler, ``REF-011`` decision 2
lets exactly two files cross into it, and a position-independent executable
cannot be opened with ``dlopen`` on this base, so the buffer that function
builds cannot be read out of the process directly. Three observations pin it
anyway, and between them they leave nothing about the buffer unfixed:

* **Where it starts and how long it is**, from the tool's own exit status. A
  well-formed PGM is exactly ``header + width * height`` bytes. A reader whose
  header parse stopped one byte early — which is precisely the defect
  ``INV-007`` F-6 measured in the program upstream ships — would find one byte
  more than it needs and exit 9 here. One that stopped one byte late would find
  one too few and exit 8. Both cases are tested against files that really do
  carry one byte too many and one too few, so neither code is a code the tool
  cannot produce. The offset is therefore exact to the byte.
* **What it contains**, by comparing the template ``iso-extract`` writes with
  the template ``libFJFX.so`` produces when this test calls it directly, over
  the exact bytes this test wrote. The library is already one of the two files
  that cross, so nothing new is admitted to the image to do this, and the
  invocation ``REF-012`` froze is not touched.
* **That the comparison above could have failed**, by running the same library
  over the buffer ``INV-007`` F-6 measured the upstream reader to produce — the
  separator byte followed by the pixels less the last one — and requiring that
  it give a different template. Without this the second observation would be
  satisfied by a library that ignored its input.

The bytes themselves are compared byte for byte, not by count and not by
digest, in ``test_the_file_holds_exactly_the_bytes_that_were_written``.

**The image.** Synthetic, generated here, and generated so that a fingerprint
extractor has something to find: a ridge field with a loop and a delta, which
is a shape this file computes and no finger's. No corpus image appears in this
directory and no template byte is written into this file. That is
``REF-013`` section 6's contract for ``tests/`` and the standing rule behind
it.
"""

import ctypes
import math
import os
import subprocess

import pytest

# From libFJFX/include/FJFX.h at the commit the Dockerfile pins, blob
# 3845cc43a9a0328408d36b199a1b0d1759336734. Repeated here because the runtime
# image carries the library and not its header.
ISO_19794_2_2005 = 0x01010001
FJFX_FMD_BUFFER_SIZE = 34 + 256 * 6

# REF-012 A. The tool takes no resolution argument; this is the value it
# compiles in, and the value this test must pass to reach the same template.
DECLARED_DPI = 500

ISO_EXTRACT = "/usr/local/bin/iso-extract"
LIBFJFX = "libFJFX.so"

# The exit codes iso-extract.c defines. A test that asserted "non-zero" would
# pass on the wrong failure.
EX_OK = 0
EX_USAGE = 2
EX_OPEN = 3
EX_MAGIC = 4
EX_HEADER = 5
EX_MAXVAL = 6
EX_DIMENSION = 7
EX_SHORT = 8
EX_TRAILING = 9

WIDTH = HEIGHT = 384


def _ridge_field(width, height):
    """Return width * height bytes of a synthetic ridge field.

    The phase is ``(radius + 2 * angle_to_the_core - 2 * angle_to_the_delta)``
    over a ridge period of 9 pixels, which at the 500 dpi this image declares
    is a ridge spacing of about 0.46 mm. The two singular points are 120 pixels
    apart on the vertical centre line. Every pixel is a function of its own
    coordinates and of the five constants above, so the buffer this returns is
    known by construction and is recomputed, not stored.
    """
    period = 9.0
    core_x, core_y = width / 2.0, height / 2.0 - 60.0
    delta_x, delta_y = width / 2.0, height / 2.0 + 60.0

    pixels = bytearray(width * height)
    for y in range(height):
        for x in range(width):
            radius = math.hypot(x - core_x, y - core_y)
            to_core = math.atan2(y - core_y, x - core_x)
            to_delta = math.atan2(y - delta_y, x - delta_x)
            phase = 2.0 * math.pi * (radius + 2.0 * to_core
                                     - 2.0 * to_delta) / period
            value = 128.0 + 110.0 * math.cos(phase)
            pixels[y * width + x] = max(0, min(255, int(round(value))))
    return bytes(pixels)


@pytest.fixture(scope="module")
def image():
    """The synthetic image, as (width, height, pixels)."""
    return WIDTH, HEIGHT, _ridge_field(WIDTH, HEIGHT)


@pytest.fixture(scope="module")
def library():
    """libFJFX.so, opened by name.

    By name and not by path: that is what the runtime's ldconfig makes
    possible, and it is the same resolution the caller's NEEDED entry uses, so
    a broken install fails here rather than somewhere subtler.
    """
    lib = ctypes.CDLL(LIBFJFX)
    lib.fjfx_create_fmd_from_raw.restype = ctypes.c_int
    lib.fjfx_create_fmd_from_raw.argtypes = [
        ctypes.c_char_p,            # raw_image
        ctypes.c_ushort,            # pixel_resolution_dpi
        ctypes.c_ushort,            # height
        ctypes.c_ushort,            # width
        ctypes.c_uint,              # output_fmd_data_format
        ctypes.c_char_p,            # fmd
        ctypes.POINTER(ctypes.c_uint),   # size_of_fmd_ptr
    ]
    return lib


def extract_in_process(library, width, height, pixels):
    """Call the library over exactly these bytes. Returns (rc, template)."""
    out = ctypes.create_string_buffer(FJFX_FMD_BUFFER_SIZE)
    size = ctypes.c_uint(FJFX_FMD_BUFFER_SIZE)
    rc = library.fjfx_create_fmd_from_raw(
        pixels, DECLARED_DPI, height, width,
        ISO_19794_2_2005, out, ctypes.byref(size))
    if rc != 0:
        return rc, None
    return 0, out.raw[:size.value]


def pgm_header(width, height, comment=None):
    """The 'P5' header this test writes, as bytes.

    One newline after the magic, the two dimensions, the maximum value, and
    exactly one newline before the raster. A comment, when asked for, goes
    between the magic and the width, where the format allows one and where it
    does not disturb the single separator the raster depends on.
    """
    parts = [b"P5\n"]
    if comment is not None:
        parts.append(b"#" + comment + b"\n")
    parts.append(b"%d %d\n255\n" % (width, height))
    return b"".join(parts)


def write_pgm(path, width, height, pixels, comment=None, extra=b"", trim=0):
    """Write a PGM. ``extra`` and ``trim`` deliberately malform the raster."""
    body = pixels[:len(pixels) - trim] if trim else pixels
    path.write_bytes(pgm_header(width, height, comment) + body + extra)
    return path


def run_extract(source, target):
    return subprocess.run([ISO_EXTRACT, str(source), str(target)],
                          capture_output=True)


def test_the_runtime_carries_the_extractor_and_the_library():
    """Fail here, with this message, rather than four tests later.

    These tests are defined against the image the Dockerfile builds, which is
    what ``make test`` runs them in. Outside it there is no tool to test.
    """
    assert os.path.exists(ISO_EXTRACT), (
        "%s is missing: these tests run inside the image, through "
        "'make test'" % ISO_EXTRACT)
    ctypes.CDLL(LIBFJFX)


def test_the_file_holds_exactly_the_bytes_that_were_written(tmp_path, image):
    """The raster on disk is the buffer this test built, byte for byte.

    This is the comparison ``REF-005`` asks for, made on the file rather than
    inferred from a count. It fixes one end of the chain: from here on, "the
    bytes the file holds" and "the values written" are the same object.
    """
    width, height, pixels = image
    path = write_pgm(tmp_path / "ridges.pgm", width, height, pixels)

    data = path.read_bytes()
    header = pgm_header(width, height)
    assert data[:len(header)] == header
    raster = data[len(header):]

    assert len(raster) == width * height
    assert raster == pixels
    # Not just equal in bulk: equal at the ends, where an off-by-one lives.
    assert raster[0] == pixels[0]
    assert raster[-1] == pixels[-1]


def test_the_extractor_reads_the_pixels_the_file_holds(tmp_path, image,
                                                       library):
    """iso-extract's template equals the library's over the same bytes.

    The tool is run through the two-argument invocation ``REF-012`` C froze,
    with no other argument and no environment of its own.
    """
    width, height, pixels = image
    source = write_pgm(tmp_path / "ridges.pgm", width, height, pixels)
    target = tmp_path / "ridges.ist"

    result = run_extract(source, target)
    assert result.returncode == EX_OK, result.stderr.decode()
    assert result.stdout == b""
    assert result.stderr == b""

    rc, expected = extract_in_process(library, width, height, pixels)
    assert rc == 0
    assert target.read_bytes() == expected

    # The template is not empty, and its length agrees with the minutia count
    # at offset 27 by the relation INV-007 F-8 measured, so the two ends of
    # the record agree independently of each other.
    count = expected[27]
    assert count > 0
    assert len(expected) == 24 + 6 + 6 * count


def test_a_shifted_buffer_gives_a_different_template(image, library):
    """The comparison above could have failed.

    The buffer here is the one ``INV-007`` F-6 measured the upstream sample's
    read to produce: the byte that separates the header from the raster,
    followed by the pixels less the last one. ``INV-007`` F-8 measured that
    this changes the template on every image it tried. If it did not change it
    on this one, the test above would be satisfied by a library that ignored
    its input, so this is a condition on the fixture as much as on the tool.
    """
    width, height, pixels = image

    rc, correct = extract_in_process(library, width, height, pixels)
    assert rc == 0
    rc, shifted = extract_in_process(library, width, height,
                                     b"\x0a" + pixels[:-1])
    assert rc == 0

    assert shifted != correct


def test_a_trailing_byte_is_refused(tmp_path, image):
    """One byte too many, and the tool says which failure it is.

    A reader that stopped its header parse one byte early would reach this
    code on a well-formed file, because a well-formed file carries exactly one
    byte more than such a read starts short by — ``INV-007`` F-6's arithmetic.
    That the well-formed file above exits 0 and this one exits 9 is what fixes
    the start of the raster to the byte.
    """
    width, height, pixels = image
    source = write_pgm(tmp_path / "long.pgm", width, height, pixels,
                       extra=b"\x00")
    target = tmp_path / "long.ist"

    result = run_extract(source, target)
    assert result.returncode == EX_TRAILING
    assert not target.exists()


def test_a_missing_byte_is_refused(tmp_path, image):
    """One byte too few. The check the upstream reader has cannot fire; this
    one does, because the whole file is in memory and the comparison is
    between two lengths."""
    width, height, pixels = image
    source = write_pgm(tmp_path / "short.pgm", width, height, pixels, trim=1)
    target = tmp_path / "short.ist"

    result = run_extract(source, target)
    assert result.returncode == EX_SHORT
    assert not target.exists()


def test_a_comment_in_the_header_is_read_the_same_way(tmp_path, image):
    """A '#' comment is legal where whitespace is, and changes no pixel.

    ``INV-007`` F-7 measured that the writer in this image emits no comment,
    so nothing on this repository's own path exercises this branch. The test
    does, and it holds the branch to the only outcome that makes sense: the
    same raster, and therefore the same template.
    """
    width, height, pixels = image
    plain = write_pgm(tmp_path / "plain.pgm", width, height, pixels)
    noted = write_pgm(tmp_path / "noted.pgm", width, height, pixels,
                      comment=b" written by a test, not by a scanner")

    assert noted.read_bytes() != plain.read_bytes()

    plain_out = tmp_path / "plain.ist"
    noted_out = tmp_path / "noted.ist"
    assert run_extract(plain, plain_out).returncode == EX_OK
    assert run_extract(noted, noted_out).returncode == EX_OK

    assert noted_out.read_bytes() == plain_out.read_bytes()


@pytest.mark.parametrize("name,content,code", [
    ("magic", b"P2\n8 8\n255\n" + b"\x80" * 64, EX_MAGIC),
    ("truncated-header", b"P5\n8 8\n", EX_HEADER),
    ("no-fields", b"P5\n", EX_HEADER),
    ("field-not-a-number", b"P5\nx 8\n255\n" + b"\x80" * 64, EX_HEADER),
    ("no-separator", b"P5\n8 8\n255" + b"\x80" * 64, EX_HEADER),
    ("maxval-127", b"P5\n8 8\n127\n" + b"\x80" * 64, EX_MAXVAL),
    ("maxval-65535", b"P5\n8 8\n65535\n" + b"\x80" * 128, EX_MAXVAL),
    ("zero-width", b"P5\n0 8\n255\n", EX_DIMENSION),
    ("width-above-65535", b"P5\n70000 8\n255\n", EX_DIMENSION),
    ("empty", b"", EX_MAGIC),
])
def test_a_malformed_file_is_refused_with_its_own_code(tmp_path, name,
                                                       content, code):
    """Each malformation gets its own exit code, and none of them is 0.

    Distinct codes because ``REF-012`` C makes the exit codes part of the
    invocation a run has to read, and a run that could only see "non-zero"
    could not tell a broken file from a broken tool. The ground for refusing
    at all rather than carrying on is ``INV-004`` B-3: a tool whose failure is
    quiet is a tool a run reports a number from.
    """
    source = tmp_path / (name + ".pgm")
    source.write_bytes(content)
    target = tmp_path / (name + ".ist")

    result = run_extract(source, target)
    assert result.returncode == code, result.stderr.decode()
    assert not target.exists()
    assert result.stdout == b""
    assert result.stderr.startswith(b"iso-extract: ")


def test_an_input_that_cannot_be_opened_is_refused(tmp_path):
    target = tmp_path / "absent.ist"
    result = run_extract(tmp_path / "absent.pgm", target)

    assert result.returncode == EX_OPEN
    assert not target.exists()
    assert result.stderr.startswith(b"iso-extract: cannot open ")


@pytest.mark.parametrize("args", [[], ["one"], ["one", "two", "three"]])
def test_the_wrong_number_of_arguments_is_refused(args):
    """The invocation is two arguments. Anything else prints the usage.

    The usage names the declared resolution, so that a reader of the terminal
    learns what ``REF-012`` A decided without opening the manifest.
    """
    result = subprocess.run([ISO_EXTRACT] + args, capture_output=True)

    assert result.returncode == EX_USAGE
    assert result.stdout == b""
    assert b"<image.pgm> <template.ist>" in result.stderr
    assert b"500 dpi" in result.stderr


def test_an_image_the_library_refuses_is_reported_not_written(tmp_path):
    """A well-formed PGM the extractor finds no fingerprint in.

    A uniform grey field is a valid image and not a fingerprint. The tool must
    distinguish "the file is malformed" from "the library declined", and it
    must leave no output file behind either way — a later step that found one
    would report a number from a run that failed.
    """
    width = height = 200
    source = write_pgm(tmp_path / "flat.pgm", width, height,
                       b"\x80" * (width * height))
    target = tmp_path / "flat.ist"

    result = run_extract(source, target)
    assert result.returncode != EX_OK
    assert not target.exists()
    assert b"the library returned" in result.stderr
