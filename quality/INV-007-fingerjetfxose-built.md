# INV-007 — FingerJetFXOSE, built here and run on an image

Date: 2026-09-07

## Numbering

This record takes 007, the next free investigation number after `INV-006`. The
reservation at 001 is explained in `REF-002`.

## Question

`INV-003` read this project's source and could measure nothing: it had no
build. Every behavioural fact in its `R` section is `UNVERIFIED` and `X-1` is
in `CONFLICT`.

So: **what does the tool do when this repository builds it and gives it an
image?**

## Method

**The pin, and how it differs from the one `MAN-tools.v1.json` carries.** The
source is the project's own repository at commit
`1726ba08bf7f2137d2f861ac1ae124d5cd355eee`, tree
`e523e7b7ad5ab6d6e8b0a6fd163696f13e4a8b48`, both verified with `git rev-parse`
before anything was built:

    git rev-parse HEAD          -> 1726ba08bf7f2137d2f861ac1ae124d5cd355eee   match: yes
    git rev-parse HEAD^{tree}   -> e523e7b7ad5ab6d6e8b0a6fd163696f13e4a8b48   match: yes
    commit date                 -> Thu Jan 15 09:16:59 2026 -0500
    tags pointing here          -> []
    tags in the repository      -> 0

**There is no publisher-served archive**, and the repository carries no tag at
all. So there is no checksum of the kind `MAN-tools.v1.json` records for NBIS,
where a named release is a file with a digest. The pin here is a commit id: it
fixes a tree, and `git rev-parse HEAD^{tree}` above is what makes that a
statement about content rather than about a label. It does not fix an artefact
anyone published. GitHub's generated tarballs were not used, because their
bytes are not stable across time.

**The submodule, a fourth party.** A plain clone leaves it uninitialised.
Before:

    [submodule "cxxtest"]
    	path = cxxtest
    	url = https://github.com/CxxTest/cxxtest.git

    -a19f85fdf90f97e16d6e3e7e3d2d68c31cd89e3c cxxtest

After `git submodule update --init --recursive`:

     a19f85fdf90f97e16d6e3e7e3d2d68c31cd89e3c cxxtest (4.4-61-ga19f85f)
    files brought in by the submodule: 471

CxxTest is a fourth party: it is not FingerJetFXOSE and it is not NIST, and it
is pinned by a commit id in the same way.

**Where.** A temporary image derived from the base digest this repository's
`Dockerfile` pins,

    python:3.12-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254

plus `build-essential ca-certificates cmake git`, plus `numpy==2.5.2` and
`pillow==12.3.0` at the versions the runtime image uses. It was deleted when
this record was finished. Nothing but this record is committed.

The toolchain inside it: `cmake 3.25.1`, `gcc (Debian 12.2.0-14+deb12u1)
12.2.0`, `g++` the same, `git 2.39.5`, `GNU Make 4.3`.

**Images.** `fvc2002/DB1_B`, the three `MAN-tools.v1.json` uses as a fixture,
each verified against `manifests/checksums/fvc2002/DB1_B.sha256` before use:

    101_1  746707dbf23a59eff97d80b66ca8ee2a010bc179e69ebe41336e3740307bbf04  MATCHES
    101_2  7419a15bddf0d67cfa04364b69a7f8f21396c4ac5a75ee0603ad337fe882a06e  MATCHES
    102_1  59cbe6a35067cc34ef8ab3fd82c24d6c44816cf77db46b72353ffc493c82c551  MATCHES

**What does not appear below.** No coordinate, angle, type or quality of an
FVC2002 minutia, and no template byte. Counts, file digests, sizes, exit codes
and byte comparisons do. Where a worked example needed actual pixel values it
uses a synthetic image, and F-7 states how that image was generated.

## F-1 — The build

The commands, in order, from the clone:

    git clone https://github.com/FingerJetFXOSE/FingerJetFXOSE.git /w/src
    cd /w/src && git checkout 1726ba08bf7f2137d2f861ac1ae124d5cd355eee
    git submodule update --init --recursive
    cd FingerJetFXOSE && ./runCMake.sh x64
    cd build/Linux-x86_64/x64 && make -j1

`runCMake.sh` detects the platform, creates `build/Linux-x86_64/x64`, and runs
`cmake -G "Unix Makefiles" -D32BITS=OFF -D64BITS=ON "" ../../../`. It does not
run `make`; the build is the second step above.

**Packages beyond what the NBIS stage already installs.** The NBIS builder
stage installs `build-essential ca-certificates cmake curl unzip`. This build
needs `build-essential ca-certificates cmake` and additionally **`git`**, for
the clone and for the submodule. It needs neither `curl` nor `unzip`.

**Whether the build is clean.** It exits 0. Of 125 log lines, **0** contain
`error` and **7** contain `warning`. Not one is a compiler diagnostic: the log
contains no `[-W...]` option marker at all. The seven, by kind:

| kind | count | what it is |
| --- | --- | --- |
| CMake | 1 | `Ignoring empty string ("") provided on the command line.` — `runCMake.sh` passes `"$xtraflags"` unquoted-empty on this platform |
| Python `SyntaxWarning` | 4 | `invalid escape sequence '\s'` in `cxxtest/python/python3/cxxtest/cxxtest_parser.py` at lines 43, 130, 131 and 134 — the fourth party's code, under this image's Python |
| `make` | 2 | `File 'CMakeFiles/Makefile2' has modification time 0.19 s in the future` and `Clock skew detected.  Your build may be incomplete.` — an artefact of building on a bind-mounted host filesystem; it does not occur when the build runs on the container's own filesystem |

So: no compiler warning, no error, and every warning attributable to the build
script, the fourth party, or the mount.

## F-2 — The artefacts

Twelve files in `dist/Linux-x86_64/x64`, which is everything the build put
there.

| artefact | size | sha256 | shared libraries it needs |
| --- | --- | --- | --- |
| `fjfxSample` | 16432 | `4abb1a0a1422fd113d817e59812825db3b9eaab220148b86e558f6c9566c2837` | `libFJFX.so` by absolute path in the build tree, `libc.so.6`, the loader |
| `fjfxSample_static` | 326008 | `ccc77ba2cd065747c2624432ca77fc2bd437f3090f8eda951b3f4cf5fdf46406` | `libc.so.6`, the loader |
| `frfxllSample` | 402512 | `fac6470c5463f3dac8f9515994767d3e7fa9237a7cc1f94c854719a6f3b6afdd` | `libFRFXLL.so` by absolute path, `libc.so.6`, the loader |
| `frfxllSample_static` | 746320 | `3e315299d1720e2ae6f6a4d7d89e240af9020428c81affb6f54fc4f10ccdd95b` | `libc.so.6`, the loader |
| `libFJFX.so` | 395944 | `ba453c674a82f4e9dd74985a4840285a07e5681defcde790d32473a7f4de1bf1` | `libc.so.6`, the loader |
| `libFJFX_MINEX.so` | 395976 | `2b14d9e0eaf3fd939f29a84c987dd4022a71f6cddc58bf992134cb380f5635af` | `libc.so.6`, the loader |
| `libFJFX_static.a` | 3634 | `9737e66dcefc26d40a7bfbf6d02c4748cbcaecb9b81452339e1aa5332b248bff` | archive, not linked |
| `libFRFXLL.so` | 423184 | `624cd2e0176c45bf668846758dbb72ddcbfe9194b0385cf0ececd2b2b170b8ab` | `libc.so.6`, the loader |
| `libFRFXLL_static.a` | 467170 | `e636ad67f8dc6b329861b85fcec9ca4d770305a1abb65a92db63dd1942964539` | archive, not linked |
| `libTestVectors.a` | 3335162 | `afa9668f783362da8f942622c907f9f7617d34c7eb508c78754f54b707ea8cd6` | archive, not linked |
| `testFRFXLL` | 4220280 | `ec876419b354a918e6f5aad9aa7739bf30ebf91754667490c4b28296e5474f38` | `libc.so.6`, the loader |
| `testFRFXLLInternals` | 2387200 | `71e445ba0287c48e9dc1b477eee392bc0f5ef7f32c67a1b712f0ec0674e098ea` | `libc.so.6`, the loader |

`fjfxSample` and `fjfxSample_static` are two builds of one source file. The
first resolves `libFJFX.so` through an absolute path recorded at link time in
the build tree; the second needs only the C library. This record chooses
neither.

Every "static" artefact here is static with respect to the project's own
libraries and dynamic with respect to `libc`.

## F-3 — Upstream's own tests, run

Two of the artefacts are test suites, built from the CxxTest submodule. Run
from the distribution directory:

| suite | tests it reports | output | exit status |
| --- | --- | --- | --- |
| `testFRFXLL` | 91 | one line, `Running testFRFXLL tests (91 tests)`, a run of dots, then `OK!` | 0 |
| `testFRFXLLInternals` | 137 | one line of the same shape, ending `OK!` | 0 |

Each suite writes exactly one line. **91** tests and **137** tests, both
reporting `OK!` and exiting 0. Neither suite failed, so there is no failure to
report as a finding.

## F-4 — Reproducibility

**A confound found and removed.** The first attempt built the two trees at two
different paths, `/tmp/a` and `/tmp/b`, and reported 5 of 12 artefacts
differing. That measured the build path, not the build. Both parts below were
re-run with **every build at the identical path `/tmp/x`**, one after another,
so the directory is not a variable. The numbers in this section are from the
second attempt.

**Two builds of the same source, same flags.** The define reaching the compiler
was `DFRFXLL_BUILD=71` in both, which is `git rev-list --all | wc -l` on this
clone, as `cmake/version.cmake` line 2 computes it.

    identical: 12   differing: 0

**All twelve artefacts are byte-identical.** The build is reproducible with
respect to repetition; it is not reproducible with respect to the directory it
runs in.

**Two builds differing only in `-DFRFXLL_BUILD`.** The define is confirmed to
have differed, read from the generated `flags.make` of the `FRFXLL` target and
not from the command line:

    /tmp/c  ->  DFRFXLL_BUILD=1
    /tmp/d  ->  DFRFXLL_BUILD=2

Four of twelve artefacts differ, eight do not:

| differs | identical |
| --- | --- |
| `frfxllSample_static` | `fjfxSample` |
| `libFRFXLL.so` | `fjfxSample_static` |
| `libFRFXLL_static.a` | `libFJFX.so` |
| `testFRFXLL` | `libFJFX_MINEX.so` |
| | `libFJFX_static.a` |
| | `libTestVectors.a` |
| | `testFRFXLLInternals` |
| | `frfxllSample` |

This is what the comparison shows. The record does not say what the source
suggests it should show, and it does not explain the split.

## F-5 — The sample program's own account of itself

`fjfxSample_static` run with no arguments prints, and exits 255:

    Fingerprint Minutia Extraction
    Usage: <path> <image.pgm> <fmd.ist>
    where <image.pgm> is the binary PGM (P5) file that containing 500DPI 8-bpp grayscale figerprint image
          <fmd.ist> is the file where to write fingerprint minutia data in ISO/IEC 19794-2 2005 format

(The `<path>` above is `argv[0]`; the two typos are the program's.)

**The input format it names:** binary PGM, P5, 8 bits per pixel, greyscale.
**The resolution it names:** 500 DPI, in the usage text, and as a literal in
the call it makes — `fjfxSample.c` line 85 passes `500` to
`fjfx_create_fmd_from_raw`. `INV-003` S-14 read that line; it is now also the
line that ran.

One adjacent fact about the entry point the sample calls, from
`libFJFX/include/FJFX.h` lines 99 to 101, where the declaration is preceded by

    // we are deprecating this entire library - no need for it
    DEPRECATED

## F-6 — How the sample reads a PGM

### Measured

On a synthetic image, generated as F-7 states: 64 x 64, pixel `i` set to
`(i % 251) + 1`, so the first eight pixels are 1 to 8 and the last is 80. The
file is 4109 bytes: a 13-byte header and 4096 pixels.

A program compiled from the sample's own two calls, `fscanf(fp, "P5%d%d%d",
&width, &height, &gray)` and `fread(image, 1, size, fp)`, reports:

    fscanf("P5%d%d%d") returned 3; width=64 height=64 gray=255
    stream position after the header parse: 12
    fread asked for 4096 bytes and returned 4096
    the short-read check (n != size) fires: no
    first eight bytes the sample's read yields: 10 1 2 3 4 5 6 7
    last byte it yields: 79

The header is 13 bytes, so the pixels begin at index 13. The parse leaves the
stream at **12**, one byte earlier: on the `0x0A` that separates the maxval
from the pixel data. The first byte the read yields is therefore **10**, the
separator, and the values that follow are the true pixels shifted one place.
The last byte it yields is 79, while the true last pixel is 80: the final pixel
is never read.

`fscanf` with `%d` stops after the last digit it converts and does not consume
the byte that terminated the field. That is why the position is 12 and not 13.

### Arithmetic

Why the short-read check cannot fire, from the file layout alone and not from
any observation. Let `H` be the header length in bytes and `w*h` the pixel
count. A well-formed P5 file is exactly `H + w*h` bytes. The parse leaves the
stream at `H - 1`. The bytes remaining from there are

    (H + w*h) - (H - 1) = w*h + 1

which is one more than `fread` asks for. So `fread` returns exactly `size`, the
test `n != size` at line 78 is false, and the program continues. The check is
not merely unhelpful here; **it cannot fire on any well-formed PGM**, whatever
its dimensions, because the file always carries exactly one byte more than the
read starts short by.

This is what makes the behaviour silent. The program reports success, writes a
template, and exits 0.

## F-7 — What the PGM writer in this image emits

The writer is Pillow 12.3.0, the version the runtime image pins, saving a mode
`L` image to a `.pgm` path. For the synthetic 64 x 64 image:

    header bytes, as text:  'P5\n64 64\n255\n'
    header bytes, as ints:  [80, 53, 10, 54, 52, 32, 54, 52, 10, 50, 53, 53, 10]
    header length 13 bytes; separator after the maxval is byte 10 at index 12
    header contains a '#' comment: False
    13 + 64*64 = 4109, and the file is 4109 bytes

For the three fixture images the header is `'P5\n388 374\n255\n'`, 15 bytes,
also with no comment, and each file is 145127 bytes = 15 + 388 * 374.

**It writes no comment, so F-6 is the silent case.** `fscanf(fp,
"P5%d%d%d", ...)` cannot convert a `#`, so a comment anywhere in the header
would make the conversion count come back below 3, the test at line 58 would be
true, and the program would print `Image file ... is in unsupported format` and
exit 10 — loudly, before reading a pixel. Because this writer emits no comment,
that branch is never reached and the shift of F-6 happens instead.

## F-8 — The cost, and the closed loop

The minutia count is one byte at **offset 27** of an ISO template. The offset
is derived from the source, not from any template's length:
`serializeFpData.h` line 292 sets `viewDataOffset = recordHeaderLength`, line
372 sets `recordHeaderLength = 24` for the ISO serializer, and `WriteViewData`
from line 269 writes, from `viewDataOffset`, one byte of finger position, one
of view number and impression type, one of finger quality, and then at line 278

    wr << uint8(num);                                                 // Number of Minutiae

which is offset 24 + 3 = **27**.

On the three fixture images, converted to PGM by the writer of F-7:

| image | producer | minutiae | template sha256 |
| --- | --- | --- | --- |
| `101_1` | the sample | 26 | `15970676a4f2168aa9ffb94e64616b5de5328a08b176151caa221e43ec2cf4bf` |
| `101_1` | the reference reader | 25 | `eb34422b99203d9d2cac3ce65756401927e5f2033bf252abce102429c7d7d07b` |
| `101_1` | the reference reader, shifted buffer | 26 | `15970676a4f2168aa9ffb94e64616b5de5328a08b176151caa221e43ec2cf4bf` |
| `101_2` | the sample | 16 | `2c94d91b5bb001ea81aafb34717147149293d8a875663edc7335365da821b494` |
| `101_2` | the reference reader | 17 | `2ad547355939d68693c7206ec1147f44c5f115bf874c25d1e4b1db40b172acc3` |
| `101_2` | the reference reader, shifted buffer | 16 | `2c94d91b5bb001ea81aafb34717147149293d8a875663edc7335365da821b494` |
| `102_1` | the sample | 60 | `a374b05e53a29cc370192ee71b6b408f5546e4c41f072cd713612a2e4b226566` |
| `102_1` | the reference reader | 60 | `5cdd58272e100e6441f6c3385080151919c473b90392c24e0fed4ba60a065072` |
| `102_1` | the reference reader, shifted buffer | 60 | `a374b05e53a29cc370192ee71b6b408f5546e4c41f072cd713612a2e4b226566` |

**The comparison that attributes the difference.** The shifted buffer is
`0x0A` followed by the pixels less the last one, which is exactly what F-6
measured the sample's read to produce:

    101_1   sample == reference-on-shifted-buffer: yes   sample == reference: NO
    101_2   sample == reference-on-shifted-buffer: yes   sample == reference: NO
    102_1   sample == reference-on-shifted-buffer: yes   sample == reference: NO

On all three images the reference reader, given the shifted buffer, reproduces
the sample's template **byte for byte**. Nothing else differs between the two
paths: the difference in the rows above is the one-byte shift and nothing
else.

Three further things the table shows. `102_1` gives the same count from both
buffers and a different template, so the shift can change which minutiae are
found without changing how many. The counts move in both directions: one image
loses a minutia, one gains one. And the sizes obey `24 + 6 + 6 * count` in
every row, which is the layout `INV-003` F-2 gives, so the byte at offset 27
and the file length agree independently.

**What this settles elsewhere.** `INV-003` R-6 reported, as `UNVERIFIED`, that
this tool produces 26 minutiae in 186 bytes for `101_1`, 16 in 126 for `101_2`
and 60 in 390 for `102_1`. Those are the sample's figures in the table above,
and the sizes are 186, 126 and 390. R-6 is reproduced here exactly. It is also
now known what those numbers are figures *of*: a buffer beginning with a
separator byte.

## F-9 — The reference reader, in full

An instrument of this investigation. It parses a file and hands the pixels to
the library; the only place a minutia is computed is the library call.

```python
"""Read a binary PGM correctly and hand the pixels to libFJFX.

An instrument of INV-007. It parses a file and calls the library; it computes
no minutia of its own.

  refread.py <libFJFX.so> <in.pgm> <out.ist> [--shift]

--shift replaces the pixel buffer with 0x0A followed by the pixels less the
last one, which is what the sample program's read sequence produces.
"""
import ctypes
import sys

ISO_19794_2_2005 = 0x01010001
BUFFER_SIZE = 34 + 256 * 6


def read_pgm(path):
    """Return (width, height, pixels) from a binary PGM, or raise."""
    data = open(path, "rb").read()
    if data[:2] != b"P5":
        raise ValueError("not a binary PGM")
    pos, fields = 2, []
    while len(fields) < 3:
        while data[pos:pos + 1].isspace():
            pos += 1
        if data[pos:pos + 1] == b"#":          # a comment runs to end of line
            pos = data.index(b"\n", pos) + 1
            continue
        start = pos
        while not data[pos:pos + 1].isspace():
            pos += 1
        fields.append(int(data[start:pos]))
    pos += 1                                   # exactly one separator byte
    width, height, _maxval = fields
    pixels = data[pos:pos + width * height]
    if len(pixels) != width * height:
        raise ValueError("file is short of width * height pixel bytes")
    if len(data) != pos + width * height:
        raise ValueError("file has bytes after the pixel data")
    return width, height, pixels


def extract(lib, width, height, pixels):
    """Call the library. Nothing here decides what a minutia is."""
    out = ctypes.create_string_buffer(BUFFER_SIZE)
    size = ctypes.c_uint(BUFFER_SIZE)
    rc = lib.fjfx_create_fmd_from_raw(
        ctypes.c_char_p(pixels), ctypes.c_ushort(500),
        ctypes.c_ushort(height), ctypes.c_ushort(width),
        ctypes.c_uint(ISO_19794_2_2005), out, ctypes.byref(size))
    if rc != 0:
        raise RuntimeError("fjfx_create_fmd_from_raw returned %d" % rc)
    return out.raw[:size.value]


if __name__ == "__main__":
    lib = ctypes.CDLL(sys.argv[1])
    width, height, pixels = read_pgm(sys.argv[2])
    if "--shift" in sys.argv[4:]:
        pixels = b"\x0a" + pixels[:-1]
    open(sys.argv[3], "wb").write(extract(lib, width, height, pixels))
```

It calls the same entry point with the same arguments the sample uses,
including the same 500. The only difference between it and the sample is where
the pixel buffer starts.

It is not proposed for adoption, and this record takes no position on whether
anything like it should be.

## Reproducing this

The temporary image, from the base digest the `Dockerfile` pins:

    FROM python:3.12-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254
    RUN apt-get update && apt-get install -y --no-install-recommends \
            build-essential ca-certificates cmake git \
        && rm -rf /var/lib/apt/lists/*
    RUN pip install --no-cache-dir numpy==2.5.2 pillow==12.3.0

The clone, the pin check and the submodule, then F-1's build, are the commands
quoted in Method and F-1.

F-2: `sha256sum`, `stat -c%s` and `ldd` over `dist/Linux-x86_64/x64/*`.

F-3: `./testFRFXLL` and `./testFRFXLLInternals` from that directory, reading
the reported count and `$?`.

F-4, with every build at the same path so the directory is not a variable:

    X=/tmp/x
    run () {                       # $1 label, $2 extra cmake args
      rm -rf "$X"; cp -a /w/src "$X"
      rm -rf "$X/FingerJetFXOSE/build" "$X/FingerJetFXOSE/dist"
      cd "$X/FingerJetFXOSE"; mkdir -p build/Linux-x86_64/x64
      cd build/Linux-x86_64/x64
      cmake -G "Unix Makefiles" -D32BITS=OFF -D64BITS=ON $2 ../../../ >/dev/null 2>&1
      make -j1 >/dev/null 2>&1
      grep -rhoE 'DFRFXLL_BUILD=[0-9]+' \
        libFRFXLL/src/CMakeFiles/FRFXLL.dir/flags.make | sort -u | head -1
      cd "$X/FingerJetFXOSE/dist/Linux-x86_64/x64" && sha256sum * | sort -k2
    }
    run p1 "" ; run p2 ""                              # F-4, first part
    run b1 "-DFRFXLL_BUILD=1" ; run b2 "-DFRFXLL_BUILD=2"   # F-4, second part

comparing the two digest lists of each pair.

F-5: `./fjfxSample_static` with no arguments.

F-6 and F-7, the synthetic image and the probe:

    python3 -c 'import numpy as np; from PIL import Image; \
      a=np.array([(i%251)+1 for i in range(64*64)],dtype=np.uint8).reshape(64,64); \
      Image.fromarray(a,mode="L").save("/tmp/synth.pgm")'

and a C program holding exactly the sample's two calls, printing `ftell(fp)`
after the `fscanf`, the return of the `fread` against the requested size, and
the first eight and last bytes of the buffer. Its source is in "Reproducing"
only as this description because it is four statements long; the two calls it
makes are quoted verbatim in F-6.

F-8, for each of the three images, with the corpus mounted read-only:

    python3 -c 'from PIL import Image; \
      Image.open("/fixture/101_1.tif").convert("L").save("/tmp/101_1.pgm")'
    ./fjfxSample_static /tmp/101_1.pgm /tmp/101_1.sample.ist
    python3 refread.py libFJFX.so /tmp/101_1.pgm /tmp/101_1.ref.ist
    python3 refread.py libFJFX.so /tmp/101_1.pgm /tmp/101_1.shift.ist --shift
    python3 -c 'print(open("/tmp/101_1.sample.ist","rb").read()[27])'
    sha256sum /tmp/101_1.*.ist

The shifted buffer is constructed inside `refread.py` by the one line quoted in
F-9: `pixels = b"\x0a" + pixels[:-1]`.

Every template written by these commands stayed inside the container and was
destroyed with it.

## What was left unchecked

- **Whether any of this justifies adopting the tool, and in what form.**
  Nothing here addresses it. This record measures; the question is a decision.
- **`INV-003` X-1.** A template was decoded exactly far enough to read one byte
  at offset 27. No coordinate and no resolution field was read, and the
  `CONFLICT` stands untouched.
- **What the tool does at a declared resolution other than 500.** The sample
  passes a literal, and the reference reader passes the same literal so that it
  differs from the sample in one thing only. Nothing here varies it.
- **Whether any of this holds at another revision of the project.** One commit
  was built. The repository carries no tag, so there is no released version to
  compare against.
- **Generalisation from three images.** F-8 is three images of one subset of
  one database. Whether the shift changes a count on other images, and in which
  direction, is not established; on these three it went both ways once and
  neither way once.
- **Why four artefacts of twelve change with `FRFXLL_BUILD` and eight do
  not.** F-4 reports the split and does not explain it.
- **The `libFJFX_MINEX.so` and `libMINEX` outputs.** They were built, digested
  and listed. Nothing was run from them.
- **Whether the sample's read defect is present in the other sample.**
  `frfxllSample` was built and digested and was not run.
