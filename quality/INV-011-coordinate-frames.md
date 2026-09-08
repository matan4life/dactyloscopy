# INV-011 — The coordinate frame each extractor reports in

Date: 2026-09-08

## Numbering

This record takes 011, the next free investigation number after `INV-010`. The
reservation at 001 is explained in `REF-002`.

## Question

The next study asks how two extractors differ on the same image. That question
is not well posed until both outputs are known to be in the same frame, and
nothing here establishes either: `INV-002` measured `mindtct`'s formats without
asking where its origin is, and `INV-007` decoded an ISO template only far
enough to read one count byte.

So: **where does each extractor put a minutia, in the image, at the invocation
this repository uses?**

## Method

**What was measured against.** The tree at commit `7cbe80b` and the image built
from its `Dockerfile`, image id
`sha256:e0ded5a5dcc8f594df58ab904be76605ad26492da834130592091b1348f7c3fc`. The
tools are the ones `MAN-tools.v2` records, at the invocations it freezes:
`mindtct <image.png> <root>` with no flags, and `iso-extract <image.pgm>
<template.ist>`, whose declared resolution of 500 and ISO output format are
`REF-012` A and B. Corpus images are the three `fvc2002/DB1_B` cases
`MAN-tools.v2` fixtures against, read read-only.

**The biometric rule.** Ranges, counts and distributions from corpus images
travel. A coordinate belonging to an FVC2002 minutia does not. Every worked
example below is a synthetic image whose construction is stated, and every
individual coordinate printed is a synthetic one.

**The angle is out of scope and stays out.** `INV-003` F-1 measures three
different angular grids, no record here has read either standard's text, and
`D-3` and `D-4` are open. Nothing below reads, converts or compares an angle.
The `.xyt` and template rows quoted are truncated to their coordinates for
that reason.

**Source, and measurement, of the same thing.** Each frame is established twice:
from the lines that determine it, and by running the tool on an image where the
answer is known by construction. Where the two agree the record says so; where
they do not, F-6, it reports the measurement.

**Where the source is.** The FingerJetFXOSE files are quoted from the commit
the `Dockerfile` pins, `1726ba08bf7f2137d2f861ac1ae124d5cd355eee`, tree
`e523e7b7ad5ab6d6e8b0a6fd163696f13e4a8b48`, each with its blob id, and are read
with `git show`. The NBIS files are quoted from the builder stage, which
unpacks the archive `MAN-tools.v2` pins by digest, and each is given with its
own sha256 so that a reader who unpacks the same archive can confirm the file
before the line.

## F-1 — `mindtct`'s frame

### From the source

`/src/mindtct/src/lib/mindtct/results.c`, sha256
`f496195f70105b1d72807c56e975c730e47550b848136a9cf656c7e916546ac6`, says which
representation each output file is in. Lines 123 to 129, above the `.min`
writer:

    /* 1. Write Minutiae results to text file "<oroot>.min". */
    /*    XYT's written in LFS native representation:        */
    /*       1. pixel coordinates with origin top-left       */

and lines 145 to 170, above the `.xyt` writer, which describes two
representations and the flag that chooses between them:

    /*    A. If M1 flag set:                                 */
    /*       XYTQ's written according to M1 (ANSI INCITS     */
    /*          378-2004) representation:                    */
    /*       1. pixel coordinates with origin top-left       */
    /*                                                       */
    /*    B. If M1 flag NOT set:                             */
    /*       XYTQ's written according to NIST internal rep.  */
    /*       1. pixel coordinates with origin bottom-left    */

Lines 171 to 182 choose: `m1flag` selects `M1_XYT_REP`, otherwise
`NIST_INTERNAL_XYT_REP`. `MAN-tools.v2` records
`tools.mindtct.invocation.flags` as `[]`, with the note "Called with no flags.
-m1 is deliberately not passed", so the branch this repository takes is the
second.

The arithmetic is in
`/src/mindtct/src/lib/mindtct/xytreps.c`, sha256
`93a79128b210b9838660f45cdcf3da0fb82c91ae2875da7847d2e9854854de50`. Lines 80 to
108, `lfs2nist_minutia_XYT`, the branch this repository uses:

    x = minutia->x;
    y = ih - minutia->y;

and lines 122 to 150, `lfs2m1_minutia_XYT`, the branch it does not:

    x = minutia->x;
    y = minutia->y;

**So, from the source: the `.xyt` file this repository produces has its origin
at the bottom left, x increasing to the right and y increasing upward, and the
`.min` file written beside it in the same run has its origin at the top left.**
The two files disagree by a vertical flip, and both are written on every run.

Two further facts follow from that one line and are stated because they are
arithmetic, not observation. The flip is `ih - y` and not `ih - 1 - y`, so a
minutia at internal row 0 reports `y = ih`, one past the last row index; the
`.xyt` y therefore ranges over 1..`ih` where the image rows are 0..`ih-1`. And
`ih` is the image height in pixels, so the unit is a pixel of the input image
and nothing scales it — consistent with `INV-004` M-2, which measured that this
build never reads a resolution from a PNG at all.

### By measurement

On the synthetic image whose construction is given in F-3 under `top`, 384 by
384, `mindtct` wrote both files in one run. Their first four rows, and the
comparison over all 21:

    Image (w,h) 384 384
    i   .min (x,y)      .xyt (x,y)      384 - .min y
    0   (28, 193)       (28, 191)       191
    1   (40, 193)       (40, 191)       191
    2   (52, 193)       (52, 191)       191
    3   (64, 193)       (64, 191)       191
    every row: .xyt x == .min x : True
    every row: .xyt y == 384 - .min y : True

The two files are the same 21 minutiae in the same order, the x agrees on every
one, and the y of one is the image height minus the y of the other on every
one. The source and the measurement agree.

## F-2 — `iso-extract`'s frame

### From the source

`FingerJetFXOSE/libFRFXLL/src/algorithm/serializeFpData.h`, blob
`cfba519962b3c3b6c65f1dc5a8d0b66f53e889e0`. `WriteMinutiae`, lines 226 to 255,
is the whole of what happens to a position on its way out:

    unsigned int mr_ppcm = muldiv(md.minutia_resolution_ppi,197,500);

    for ( size_t i = 0; i < num; i++ ) {
      Point pos = md.minutia[i].position;

      if (resolutionX != mr_ppcm) {
        pos.x = muldiv(pos.x,resolutionX,mr_ppcm);
      }
      if (resolutionY != mr_ppcm) {
        pos.y = muldiv(pos.y,resolutionY,mr_ppcm);
      }
      ...
      wr << uint16((pos.x & 0x3FFF) | (md.minutia[i].type << 14));    // X
      wr << uint16(pos.y & 0x3FFF);                                   // Y

**There is no flip.** The serializer writes the position it is given, with one
conditional rescale of both axes by the same factor, and masks each to fourteen
bits; the top two bits of the X word carry the minutia type. Whatever frame the
library's internal position is in is the frame the template is in, and the
serializer neither knows nor changes it. What the internal frame is was
established by measurement below, not traced through the extractor.

### The record layout, derived rather than assumed

`WriteRecordHeaders`, lines 256 to 268, writes from offset 0; the ISO subclass
at lines 367 to 389 supplies the three virtual writers and sets
`recordHeaderLength = 24`. `WriteTotalLength` sets the cursor to 8 and writes
four bytes; `WriteDeviceInfo` writes two bytes; `WriteImageSize` sets the cursor
to 14 and writes two `uint16`s. So:

| offset | bytes | field |
| --- | --- | --- |
| 0 | 4 | format identifier, `0x464D5200` |
| 4 | 4 | version, `0x20323000` |
| 8 | 4 | total record length |
| 12 | 2 | capture device information |
| 14 | 2 | image size in X |
| 16 | 2 | image size in Y |
| 18 | 2 | X resolution |
| 20 | 2 | Y resolution |
| 22 | 1 | number of finger views |
| 23 | 1 | reserved |

and `WriteViewData`, lines 269 to 285, continues at 24: finger position, then
view number and impression type packed in one byte, then finger quality, then
the minutia count at **27**, which is the offset `INV-007` F-8 derived the same
way. Each minutia is six bytes from 28: `uint16` X with the type in the top two
bits, `uint16` Y, one byte of angle, one byte of quality.

### By measurement

The same synthetic image, through `iso-extract` at its frozen invocation. Its
first 24 bytes:

    46 4d 52 00 20 32 30 00 00 00 00 8a 00 00 01 80 01 80 00 c5 00 c5 01 00

Read by the table above: magic `b'FMR\x00'`, version `b' 20\x00'`, length
`0x0000008a` = 138, which is the size of the file; image size in X `0x0180` =
384 and in Y 384, which is the image; X and Y resolution `0x00c5` = 197; one
finger view; reserved 0. Every multi-byte field is big-endian, and every field
lands where the derivation puts it.

## F-3 — the origin test

### The construction

One 384 by 384 greyscale image per case. A loop-and-delta ridge field is
computed over the whole plane and then blanked outside a named half:

    phase = 2*pi*(r + 2*a_core - 2*a_delta) / period
    pixel = 128 + 110*cos(phase), clamped to 0..255
    outside the kept half: pixel = 255

with `r` the distance to the core, `a_core` and `a_delta` the angles to the core
and to the delta, and **period 9 pixels**, which at the 500 dpi the caller
declares is a ridge spacing of about 0.46 mm. The period is stated because the
library's acceptance of a synthetic field depends on it, and 9 is the value
that this record's construction was accepted at. `INV-012`'s last section
measures that dependence and finds the library refusing half its images at
period 13; no record in this repository measured it before that one.
The blanked half is a uniform 255, in which there is no ridge and therefore no
minutia: **a minutia can only occur in the half that carries the field.**

Both singular points are placed inside the kept half, so that the structure the
extractor needs is there and not in the part that was blanked. Each image is
written once as PNG for `mindtct` and once as PGM for `iso-extract`, and the two
were confirmed to decode to identical pixels in every case.

### What each extractor reported

`mindtct` was run at its frozen invocation and both its files read;
`iso-extract` at its frozen invocation, and the template decoded by the table of
F-2.

| case | the field occupies | core, delta | `mindtct` .min y | `mindtct` .xyt y | `iso-extract` y |
| --- | --- | --- | --- | --- | --- |
| top | rows 0..191 | (192,60), (192,132) | 57..193 | 191..327 | 59..197 |
| bottom | rows 192..383 | (192,252), (192,324) | 189..326 | 58..195 | 192..327 |

| case | the field occupies | core, delta | `mindtct` .min x | `mindtct` .xyt x | `iso-extract` x |
| --- | --- | --- | --- | --- | --- |
| left | columns 0..191 | (60,192), (132,192) | 68..193 | 68..193 | 66..196 |
| right | columns 192..383 | (252,192), (324,192) | 189..326 | 189..326 | the library returned 3 |

Counts, for completeness: top 21 `mindtct` and 18 `iso-extract`; bottom 29 and
19; left 24 and 6; right 30 and none.

**Where each extractor placed them.**

- With the field in rows 0..191, `mindtct`'s `.xyt` reports y in 191..327 —
  the far half of the coordinate range from the half the ridges are in. With
  the field in rows 192..383 it reports 58..195. The `.xyt` y runs opposite to
  the image rows.
- The `.min` file from the same runs reports 57..193 and 189..326: the same
  half the ridges are in, in both cases.
- `iso-extract` reports 59..197 and 192..327: the same half the ridges are in,
  in both cases.
- On the horizontal axis all three agree with the image columns: field in
  columns 0..191 gives 66..196, field in columns 192..383 gives 189..326.

### The right-half case the library refused

The `right` construction returned 3, `FJFX_FAIL_EXTRACTION_BAD_IMP`, so that
cell of the table is a refusal and not a placement. Three further placements of
the two singular points inside the same right half were tried, and the record
gives all four rather than only the one that worked:

| the two singular points | result |
| --- | --- |
| core (252,192), delta (324,192) | the library returned 3 |
| core (324,192), delta (252,192) | 7 minutiae, x 188..319, y 190..316 |
| core (240,192), delta (300,192) | 8 minutiae, x 188..301, y 133..254 |
| core (252,252), delta (324,324) | 8 minutiae, x 188..323, y 206..327 |

Every one that produced a template put its x in 188..323, the half the field
occupies. The horizontal answer does not depend on which of the four was used.

## F-4 — the image size each template declares, against the manifest

`MAN-fvc2002.v1.json` gives `fvc2002/DB1_B` a width of 388 and a height of 374.
On each of the three fixture images, the template's header, read at offsets 14
and 16:

| image | Pillow reports (w,h) | header image X | header image Y |
| --- | --- | --- | --- |
| 101_1 | (388, 374) | 388 | 374 |
| 101_2 | (388, 374) | 388 | 374 |
| 102_1 | (388, 374) | 388 | 374 |

**They agree, on all three, on both axes.** `REF-007` decision 2 makes a tool's
claim about an image that the manifest contradicts a failure of the run; this
one does not contradict it, and until now nothing had looked.

The check is discriminating because 388 and 374 are different numbers, and it
is worth making because the transposition it rules out is live. The library's
entry point takes its arguments in the order `(raw_image,
pixel_resolution_dpi, height, width, ...)` — height before width — while
`FJFX.cpp` line 91 passes them on to the extractor as `width, height` and line
103 builds the export parameters with `imageSizeX` from `width` and `imageSizeY`
from `height`. The two orders are three lines apart in one file.

Swapping the two arguments was measured rather than imagined, on a synthetic
field 320 wide and 256 high built by the construction of F-3 with nothing
blanked:

    called as the header declares, (height=256, width=320): rc=0  image_x=320 image_y=256 count=6
    called with the two swapped,    (height=320, width=256): rc=0  image_x=256 image_y=320 count=255

**The swap produces no error.** It returns success, writes a header that
transposes the image, and finds 255 minutiae where the correct call finds 6.
Nothing in the library detects it; the only thing that would is the comparison
in the table above.

## F-5 — are the coordinates in the image's pixel grid at 500 dpi

The three fixture images are 388 by 374 by `MAN-fvc2002.v1.json`. Over all
three, the ranges each extractor produced — ranges and counts, no coordinate
belonging to any one of them:

| image | `mindtct` .xyt | | `iso-extract` | |
| --- | --- | --- | --- | --- |
| | x | y | x | y |
| 101_1 | 100..327 | 21..351 | 116..298 | 45..353 |
| 101_2 | 58..282 | 109..337 | 79..247 | 44..256 |
| 102_1 | 58..307 | 23..363 | 58..302 | 18..354 |
| **all three** | **58..327** | **21..363** | **58..302** | **18..354** |

Both extractors put every coordinate inside 0..388 horizontally and 0..374
vertically, which are the image's own dimensions. The largest value either
produced is 327 against a width of 388 and 363 against a height of 374, and
nothing exceeded either. **At the one declared resolution this repository uses,
both are in the image's pixel grid**, and neither is in a grid scaled by a
resolution: at the export resolution of 197 per centimetre the same image is
153 by 147 units across, which the ranges above overrun on both axes, and any
grid rescaled from 500 dpi by the ratio the header carries would be out by the
same factor.

The counts, for the record, are the ones `MAN-tools.v2` already fixtures: 33,
24 and 62 for `mindtct`, 25, 17 and 60 for `iso-extract`.

## F-6 — `INV-003` X-1, now that the tool is in the image

### Two things about this finding, before its numbers

**A declared resolution other than 500 is an instrument of this investigation.**
`REF-012` A fixes the value this repository passes at 500, and `iso-extract`
compiles it in rather than taking it as an argument. Every other value below was
reached by calling `libFJFX.so` directly through `ctypes`, exactly as
`INV-007` F-9's reference reader did, and **no number in this finding describes
the tool as this repository runs it.** The 500 row does.

**Settling X-1 does not lift `REF-007` decision 4's exclusion of
`fvc2002/DB2`.** What that decision rests on is `INV-003` S-8, that the library
pins its internal resolution whatever it is told, together with `INV-002` R-5,
that DB2's reported resolution differs. X-1 appears in it once, as the third of
three grounds for rejecting a different course — declaring each image's true
resolution — and the first two of those grounds do not mention it. So settling
X-1 removes one ground against an alternative that decision rejected; it does
not touch what the exclusion itself stands on. Nothing here lifts it, and
lifting it would need its own refinement.

### What X-1 says

`INV-003` X-1 is in `CONFLICT` between a report and a reading of the source. The
report: *"The header records whichever resolution was declared, while the
coordinates stay in the image's pixel grid regardless."* The reading, from
`INV-003` S-13 and S-8: `resolutionX` is both written into the header and the
numerator of the coordinate rescale, over a denominator fixed at 197, so the two
cannot move independently — and where the caller sets it, as
`fjfx_create_fmd_from_raw` does, *"the header reads the declared value and the
coordinates are rescaled, by `dpcm/197`. At 450 and 550 that is 177/197 and
216/197, which moves a coordinate near 200 by about 20 and 19 pixels."*

Both halves are measurable here. The image is the F-3 construction at 384 by
384 with nothing blanked, core (192,132) and delta (192,252).

### The header field and the coordinate range, at each declared value

| declared dpi | return | minutiae | header X/Y resolution | x range | y range |
| --- | --- | --- | --- | --- | --- |
| 250 | 1 | — | — | — | — |
| 300 | 0 | 255 | 118 | 77..299 | 19..365 |
| 400 | 0 | 8 | 157 | 40..192 | 131..252 |
| 450 | 0 | 31 | 177 | 6..196 | 130..254 |
| 499 | 0 | 31 | 196 | 7..196 | 130..254 |
| **500** | 0 | 31 | **197** | 7..197 | 131..255 |
| 501 | 0 | 31 | 197 | 7..197 | 130..255 |
| 550 | 0 | 31 | 216 | 7..196 | 129..253 |
| 600 | 3 | — | — | — | — |
| 800 | 3 | — | — | — | — |
| 1000 | 2 | — | — | — | — |
| 1008 | 2 | — | — | — | — |
| 1024 | 2 | — | — | — | — |
| 1025 | 1 | — | — | — | — |

The return codes are the library's own: 1 is `FJFX_FAIL_IMAGE_SIZE_NOT_SUP`, 2
`FJFX_FAIL_EXTRACTION_UNSPEC`, 3 `FJFX_FAIL_EXTRACTION_BAD_IMP`. On this image
the library accepted 300 to 550 and refused everything above it.

### The same question asked sharply

A range over a set of minutiae can move because the coordinates moved or because
a different set was found. Inside the window where `INV-003` S-11 measured the
resampling not to reference the declared value, the count is 31 at every value
tried, so the sets can be compared directly. Sorted, the first four of each:

| declared dpi | header resolution | first four (x, y) | identical to the 500 set |
| --- | --- | --- | --- |
| 450 | 177 | (6,252) (17,252) (18,132) (22,252) | no |
| 475 | 187 | (7,252) (17,252) (19,132) (21,252) | no |
| 499 | 196 | (7,251) (17,251) (19,131) (21,251) | no |
| **500** | **197** | (7,252) (17,252) (19,132) (21,252) | — |
| 501 | 197 | (7,251) (17,251) (19,132) (21,251) | no |
| 525 | 206 | (6,252) (18,252) (19,132) (21,252) | no |
| 550 | 216 | (7,251) (16,251) (19,130) (22,251) | no |

**The header field moves and the coordinates do not.** From 450 to 550 the
header resolution goes from 177 to 216, a change of 22 per cent. Over the same
span the largest x moves from 196 to 196 and the smallest from 6 to 7; the
coordinates differ between adjacent settings, but by ones, never by a factor.
Under the rescale `INV-003` derives, a coordinate of 197 at 500 dpi would read
177 at 450 and 216 at 550. It reads 196 and 196.

### What that settles, and what it leaves

**The report reproduces.** The conjunction X-1 records as reported — a header
that varies with the declared value and coordinates that do not — is what this
repository's own tool produces, measured on a template made and decoded here,
which is one of the two things `INV-003` named as able to settle it.

**The reading of the source does not reproduce, and the mechanism is not
established here.** `serializeFpData.h` lines 236 to 241 rescale both axes
when `resolutionX != mr_ppcm`, and `mr_ppcm` is
`muldiv(md.minutia_resolution_ppi,197,500)`.
`FeatureExtraction.h` blob `5a775d0ccdceb776211f8ab296f87e401a8fe981` line
177 sets `md.minutia_resolution_ppi = 500` unconditionally, under the comment
`its currently broken!`, with the line that would carry the declared value
commented out above it. On that reading `mr_ppcm` is 197 at every declared
value, the condition holds at 450 and at 550, and the coordinates should have
moved by about a fifth. They did not.

This record does not explain why. It reports that the predicted rescale does not
appear in the output, names the lines that predict it, and stops: constructing a
reconciliation would be exactly the kind of account this repository asks a
measurement to replace. What would establish the mechanism is the internal
minutia list, which `FRFXLLGetMinutiae` exposes and which is not reachable from
this image — `REF-011` decision 2 sends only `libFJFX.so` across, and
`libFRFXLL.so` stays in the builder stage.

**Two further things the table shows and this record does not explain.** Outside
the 450-to-550 window the extraction itself differs: 255 minutiae at 300 dpi,
which is the cap the format allows, and 8 at 400, against 31 inside the window.
And inside the window the coordinate sets are not identical from one setting to
the next — 499, 500 and 501 give three different sets of 31 — so the declared
value reaches the extraction somewhere, in a way that moves coordinates by ones
rather than by a factor.

**X-1's own status is not changed by this record.** `REF-002` keeps history
rather than rewriting it, so `INV-003` is not edited; what to do with a
`CONFLICT` finding that a later measurement settles is a decision, and no
refinement takes it.

## Reproducing this

Every command was run on 2026-09-08 against the tree at `7cbe80b`. `$SP` is a
scratch directory outside the tree and `$FIX` is the read-only mount of the
FVC2002 `Db1_b` images. No corpus image, minutia or template leaves a
container: every container is `--rm`, the fixture mount is `:ro`, and the
repository is mounted `:ro` where it is mounted at all.

**S — the source, from the pin.** The FingerJetFXOSE files, from a clone at the
commit and tree the `Dockerfile` verifies:

    git rev-parse HEAD HEAD^{tree}
      1726ba08bf7f2137d2f861ac1ae124d5cd355eee
      e523e7b7ad5ab6d6e8b0a6fd163696f13e4a8b48
    git rev-parse HEAD:FingerJetFXOSE/libFRFXLL/src/algorithm/serializeFpData.h
      cfba519962b3c3b6c65f1dc5a8d0b66f53e889e0
    git rev-parse HEAD:FingerJetFXOSE/libFRFXLL/src/algorithm/FeatureExtraction.h
      5a775d0ccdceb776211f8ab296f87e401a8fe981
    git rev-parse HEAD:FingerJetFXOSE/libFJFX/src/FJFX.cpp
      bc3cf90dd14ba0c4ee6f85c4f74710f7c01d147e
    git show HEAD:<path> | sed -n '<first>,<last>p'

and the NBIS files, from the builder stage that unpacks the archive
`MAN-tools.v2` pins:

    docker build --target nbis-builder -t dactyloscopy:nbis-audit .
    docker run --rm dactyloscopy:nbis-audit sha256sum \
      /src/mindtct/src/lib/mindtct/results.c /src/mindtct/src/lib/mindtct/xytreps.c
      f496195f70105b1d72807c56e975c730e47550b848136a9cf656c7e916546ac6  results.c
      93a79128b210b9838660f45cdcf3da0fb82c91ae2875da7847d2e9854854de50  xytreps.c

The ranges quoted are `results.c` 123-129 and 145-182, and `xytreps.c` 80-108
and 122-150; `serializeFpData.h` 158-161, 226-255, 256-268, 269-285 and
367-389; `FeatureExtraction.h` 176-177; `FJFX.cpp` 88-106.

**G — the ridge field.** Every synthetic image in this record comes from this
function, and each finding says what it passed for `core`, `delta` and `keep`.

    def ridge_field(width, height, core, delta, keep):
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
                phase = 2.0 * math.pi * (r + 2.0 * a1 - 2.0 * a2) / 9.0
                px[y * width + x] = max(0, min(255, int(round(
                    128.0 + 110.0 * math.cos(phase)))))
        return bytes(px)

    Image.frombytes("L", (width, height), px).save(name + ".png")
    Image.frombytes("L", (width, height), px).save(name + ".pgm")

The four cases of F-3 pass `keep` = `y < 192`, `y >= 192`, `x < 192`,
`x >= 192`; F-6 passes `lambda x, y: True`.

**R — the two extractors, at their frozen invocations.**

    docker run --rm -v "$SP:/sp:ro" -v "<repo>:/work:ro" -v "$FIX:/fixture:ro" \
      dactyloscopy:dev python /sp/frames.py

    mindtct <image>.png <root>          # then read <root>.xyt and <root>.min
    iso-extract <image>.pgm <out>.ist   # then decode by the table of F-2

The `.min` line format is `index : x, y : direction : reliability : type : …`;
the `.xyt` line format is `x y theta quality`, one minutia per line, in the same
order as the `.min`. Only the coordinates were read from either.

**D — the template decoder**, which is the table of F-2 and nothing else:

    def be16(b, o):
        return (b[o] << 8) | b[o + 1]

    count = t[27]
    minutiae = [((be16(t, 28 + 6*i) & 0x3FFF), (be16(t, 30 + 6*i) & 0x3FFF))
                for i in range(count)]
    image_x, image_y = be16(t, 14), be16(t, 16)
    res_x,   res_y   = be16(t, 18), be16(t, 20)

**X — the declared resolution varied**, by calling the library directly rather
than through `iso-extract`, which compiles 500 in:

    lib = ctypes.CDLL("libFJFX.so")
    lib.fjfx_create_fmd_from_raw.argtypes = [
        ctypes.c_char_p, ctypes.c_ushort, ctypes.c_ushort, ctypes.c_ushort,
        ctypes.c_uint, ctypes.c_char_p, ctypes.POINTER(ctypes.c_uint)]
    rc = lib.fjfx_create_fmd_from_raw(pixels, dpi, height, width,
                                      0x01010001, out, ctypes.byref(size))

**T — the transposition**, the same call with the third and fourth arguments
exchanged, on a 320 by 256 field.

## What was left unchecked

- **The angle, in every form.** No angle was read, converted or compared. The
  `.xyt` third column and the template's fifth byte per minutia were skipped.
  `INV-003` F-1's three grids stand as it left them, and `D-3` and `D-4` are
  open.
- **`D-1`, which coordinate convention the matcher requires.** That is about
  `mindtct` and `bozorth3` and about `.xyt` files reaching a matcher. Nothing
  here touches it, and nothing here should be read as an answer to it.
- **Whether either extractor is correct.** Neither is a reference for the other.
  This record says where each one puts a minutia and takes no position on which
  frame is right.
- **How the two differ.** That is the next study. No coordinate produced by one
  extractor is compared with a coordinate produced by the other anywhere above,
  and the F-3 tables are read one row at a time by construction.
- **The internal frame of the FingerJetFXOSE extractor.** F-2 establishes that
  the serializer applies no flip, and F-3 measures what comes out. Where in the
  extractor the frame is fixed was not traced.
- **Why the rescale of `serializeFpData.h` 236-241 does not appear.** F-6 states
  the measurement and the lines that predict otherwise, and stops there.
- **Whether the coordinates would still be in the image grid at a declared
  resolution other than 500.** F-5 asks the question `REF-012` A's value poses
  and no other; F-6's ranges are from a synthetic image and are not a second
  answer to F-5.
- **Anything about `fvc2002/DB2`.** `REF-007` decision 4's exclusion is
  untouched, and F-6 says so in terms.
- **The `-m1` branch of `mindtct`**, beyond quoting the lines that show it
  exists and that this repository does not take it. No `.xyt` was produced
  with it.
- **Whether a minutia ever lands on the row that would make the `.xyt` y equal
  the image height.** The arithmetic of `ih - y` is quoted from the source; no
  measurement here produced such a minutia, and none looked for one.
