# INV-002 — Minutia formats: what mindtct writes and how it transforms

Date: 2026-09-06

## Numbering

This is the first investigation record in the repository, and it takes the
number 002 rather than 001. `REF-002` states the author's account that
`INV-001` exists in earlier work and is pending import and translation; 001 is
reserved to it. That account is not verified here and nothing below rests on
it.

## Question

Two questions, both about files this repository already produces:

1. What does `mindtct` put in `.min` and in `.xyt`, how are the two related,
   and what does the `-m1` flag change?
2. On what grid are the angles of `.xyt` and of the ISO template a second
   extractor would produce, and do those grids meet?

The second question is answered here only as far as arithmetic and one
reported observation reach. No ISO template was produced inside this
repository.

## Method

The tool is `mindtct` as it sits in the runtime image, sha256
`4d587263e242781e97afe236f5c8c46f275eb617c42e47f34d969c536c122c53`, which is
the digest `manifests/MAN-tools.v1.json` froze and which
`scripts/check_tools.sh` re-checks on every run. Python 3.12, Pillow 12.3.0
and numpy 2.5.2, all pinned in the image.

The data is every image of FVC2002 `Db1_b`: 80 files, the same directory the
three-case fixture in `MAN-tools.v1.json` was recorded against. No dataset
manifest exists yet, so the set is identified by the name of the directory it
was read from and not by a checksummed set; that identification carries status
`UNVERIFIED` and is stated here for the same reason it is stated in the
manifest.

Each image was converted with Pillow `.convert("L")` to PNG and to PGM, and
`mindtct` was run twice on each PNG, once with no flags and once with `-m1`.
The directory holding the images was mounted read-only. Every derived file —
`.min`, `.xyt`, `.png`, `.pgm` — was written to a path inside the container and
destroyed with it. Nothing derived from an image reached the repository, and
no coordinate of any minutia appears below: the facts are counts, ranges and
rules.

Minutiae of `.min` and of `.xyt` were paired by position in the file. That
pairing is not assumed: fact F-5 measures it.

## Measured facts

Every fact in this section was measured here, over all 80 images, by the
commands in "Reproducing this". Where a fact reported to this investigation
did not reproduce, that is stated in the fact rather than in a footnote.

### F-1 — The set — VERIFIED

80 `*.tif` files, from `101_1` to `110_8`. Every one decodes to Pillow mode
`L`, and every one is 388 x 374. The height also appears in the first line of
each `.min` file, `Image (w,h) 388 374`, so the height used below was read
from the tool's own output and not assumed.

### F-2 — TIFF to PNG and to P5 PGM preserves the pixels — VERIFIED

Pillow `.convert("L")` followed by `save`:

- PNG, decoded pixels equal to the TIFF's: **80/80**
- PGM, decoded pixels equal to the TIFF's: **80/80**
- PGM written with the binary magic `P5`: **80/80**

The comparison is on decoded arrays, never on the encoded bytes.

### F-3 — What mindtct accepts and what it refuses — VERIFIED

- `.tif` refused: **80/80**
- `.pgm` refused: **80/80**
- `.png` accepted, exit status 0: **80/80**

All 160 refusals print one message, which differs only in the path:

    ERROR : read_and_decode_grayscale_image : <file> : image type UNKNOWN : not supported

The refusal exits with status **253**.

### F-4 — How many minutiae — VERIFIED

**3946** minutiae over the 80 images, from **19** to **76** per image. The
`.min` file, the native `.xyt` and the `-m1` `.xyt` agree on the count on
**80/80** images. The three images of the manifest's fixture contribute 33, 24
and 62, which is the 119 the reconnaissance worked over.

### F-5 — The native .xyt coordinates, against .min — VERIFIED

Pairing by position in the file, and with `H` the image height from the `.min`
header:

- native `.xyt` x equals `.min` x, and native `.xyt` y equals `H - .min y`:
  **3946/3946**

The `.min` file therefore counts y from the top and the native `.xyt` counts it
from the bottom, and the by-position pairing that the rest of this record uses
holds on every minutia measured.

### F-6 — The direction index — VERIFIED

The fourth field of a `.min` line takes **32** distinct values over the 3946
minutiae, spanning **[0, 31]**. 360 / 32 = 11.25.

### F-7 — The angle rule, and a reported rule that does not reproduce — VERIFIED

Three candidate rules from the direction index `d` to the integer angle in the
native `.xyt`, each counted over all 3946 minutiae:

| rule | agrees | fails on |
| --- | --- | --- |
| `floor((270 - 11.25 d) mod 360)` | **2994/3946** | 80 of 80 images |
| `round((270 - 11.25 d) mod 360)`, Python `round` | **3445/3946** | 78 of 80 images |
| `(270 - round_half_up(11.25 d)) mod 360` | **3946/3946** | 0 of 80 images |

The first of these is the rule reported to this investigation, together with a
count of 33/33 on image `101_1`. It does not reproduce. Measured on `101_1`
alone it agrees on **28/33**, so the disagreement is not an effect of widening
the sample from 3 images to 80; the third rule agrees on **33/33** there.

Where the first rule fails is exact. Grouping the 3946 minutiae by the
fractional part of `(270 - 11.25 d) mod 360`:

| fractional part | minutiae | `floor` wrong on |
| --- | --- | --- |
| .0 | 1030 | 0 |
| .25 | 1023 | 0 |
| .5 | 941 | 0 |
| .75 | 952 | **952** |

`floor` is wrong on every minutia of the .75 class and on no other.

The third rule rounds before subtracting: `11.25 d` is rounded to the nearest
integer, halves away from zero, and that integer is subtracted from 270 modulo
360. An equivalent statement on the subtracted form is rounding half **down**,
which is why both `floor` (wrong on .75) and `round` (wrong on .5) miss.
Whether this is what the tool's source does was not established: see "What was
left unchecked".

### F-8 — The angle projection is injective — VERIFIED

The 32 direction indices produce **32** distinct native angles, so no two
directions collide in the `.xyt` file and the index is recoverable from the
angle. The 32 values are

    0 11 22 34 45 56 67 79 90 101 112 124 135 146 157 169
    180 191 202 214 225 236 247 259 270 281 292 304 315 326 337 349

and the set produced by the rule of F-7 over `d` in 0..31 is exactly this set.

### F-9 — How reliability and quality are written — VERIFIED

**3946/3946** printed reliabilities match `^[0-9]\.[0-9]{3}$`. There are **802**
distinct printed values, from `0.010` to `0.990`. The three-decimal form was
`APPROX` on the strength of one image; the count above is what raises it.

The `.xyt` quality column is an integer. Over the same 3946 minutiae it takes
**90** distinct values, from **1** to **99**, and **no** value falls outside
0..100. The `-m1` output gives the same range and the same number of distinct
values. That 0 and 100 do not appear is a fact about these 80 images and not
about the column's range, which was not established.

### F-10 — Quality is not a function of printed reliability — VERIFIED

Of the 802 distinct printed reliabilities, **60** occur with two different
`.xyt` qualities. None occurs with more than two. **391** of the 3946 minutiae
carry one of those 60 values.

The reported counterexample reproduces: printed reliability `0.125` occurs
with quality **12** and with quality **13**.

All **60** ambiguous values have **5** as their third decimal. The first ten,
in order, are `0.055 0.085 0.105 0.115 0.125 0.135 0.145 0.155 0.165 0.175`,
each mapping to a pair of consecutive integers.

Two files that print the same reliability and carry a different quality are a
proof that no function of the printed reliability yields the quality. It is
not a search that failed.

### F-11 — Closed forms from printed reliability to quality — VERIFIED

`r` is the printed value read as a float; the target is the `.xyt` quality.

| closed form | agrees | share |
| --- | --- | --- |
| `round(r*100)` | 3732/3946 | **94.58%** |
| `int(r*100+0.5)` | 3724/3946 | 94.37% |
| `floor(r*100)` | 2160/3946 | 54.74% |
| `ceil(r*100)` | 2135/3946 | 54.11% |

The best of them disagrees on **214** of 3946 minutiae, one in eighteen, and
every disagreement is by exactly **1**: the set of absolute differences over
all 3946 is `{0, 1}`.

The same four forms were reported to this investigation over the 119 minutiae
of three images, as 110, 109, 71 and 56 respectively — a best share of about
**92%**, roughly one minutia in twelve wrong. Those counts were not
re-derived; the widened counts above are what this record establishes. Both
figures are recorded, and they differ: the share of a closed form is a property
of the sample it was counted on, and the two samples give 92% and 94.58%.

### F-12 — The band a three-decimal print leaves open — VERIFIED

Under the hypothesis that the printed reliability is an internal value rounded
to three places, the true value lies in `[p - 0.0005, p + 0.0005]`, and each
rule can produce a set of qualities from that band. Counting minutiae whose
observed quality lies outside that reachable set:

- rounding: **0/3946** outside the band
- flooring: **1774/3946** outside the band

This is a statement about the observed data under a stated hypothesis, not a
statement about the tool's source. It is consistent with the two files being
independent projections of one internal value that neither of them exposes;
it does not establish that.

### F-13 — What -m1 changes — VERIFIED

Pairing native and `-m1` output by position, over all 3946 minutiae:

- x unchanged: **3946/3946**
- `y_m1 == H - y_native`, which is the same as `y_m1 == .min y`:
  **3946/3946** for both statements
- `theta_m1 == ((theta_native + 180) mod 360) // 2`: **3946/3946**
- quality unchanged: **3946/3946**

The division is integer division, and that is not a formality: `(theta_native +
180) mod 360` is **odd** on **1959** of the 3946 minutiae, so on nearly half of
them an exact division would not be an integer at all. 16 of the 32 native
angles are odd.

### F-14 — Angle units and ranges — VERIFIED

- native: **32** distinct values, range **[0, 349]**, none above 359
- `-m1`: **32** distinct values, range **[0, 174]**, none above 179

**16** of the 32 `-m1` values are odd, which is what a unit of 2 degrees
implies: the stored integer counts units, not degrees, so it is not restricted
to even numbers.

### F-15 — Determinism of this extraction — VERIFIED

Ten images were re-extracted in the same container and their `.xyt` output was
byte-identical to the first extraction: **10/10**. The three-case fixture in
`MAN-tools.v1.json` is checked on every `make check-tools` run and is not
repeated here.

### F-16 to F-18 — The lattice, as arithmetic — VERIFIED as arithmetic

These three facts are exact arithmetic, checkable by anyone, and they are
marked `VERIFIED` as arithmetic only. Two of the three steps they operate on
are reported to this investigation and are not verified here (R-1, R-6); the
conclusions inherit that.

- **F-16.** Taking the three nominal angular steps as 45/4 degrees (native, from
  F-6), 2 degrees (ANSI INCITS 378-2004, reported) and 45/32 degrees (ISO
  19794-2:2005, reported), the smallest `m` for which all three are a whole
  number of 1/`m` degrees is **32**. In units of 1/32 degree the steps are
  **360**, **64** and **45**, and a full circle is **11520**.
- **F-17.** 45/4 divided by 45/32 is **8** exactly, so every one of the 32
  native directions falls on a point of the reported ISO grid with no
  rounding.
- **F-18.** The least common multiple of 360, 64 and 45 is **2880** units,
  which is **90** degrees, so the three grids share exactly **4** directions in
  a full circle: 0, 90, 180 and 270 degrees.

## Facts reported to this investigation and not re-checked here

Everything in this section was established outside this repository, by the
author, before this record existed. None of it was reproduced here, because
none of it can be: it needs a second extractor that is not in the image. Each
carries status `UNVERIFIED` and the method by which it was obtained. Nothing
in this record rests on any of them.

- **R-1 — UNVERIFIED.** The ISO 19794-2:2005 angle unit is 360/256 = 1.40625
  degrees, with values in 0..255; a value as high as 253 was observed in a real
  template. Method: decoding a template produced by FingerJetFXOSE. This
  differs from ANSI INCITS 378-2004, whose step is reported as 2 degrees; the
  two standards are routinely conflated.
- **R-2 — UNVERIFIED.** ISO angles point about 180 degrees away from native
  NBIS angles. Method: circular mean of the difference over 22 minutiae that
  the two extractors placed within 6 px of each other on one image, giving
  **183.0** degrees with concentration **R = 0.97**. One image, one pairing
  radius, 22 minutiae.
- **R-3 — UNVERIFIED.** FingerJetFXOSE builds with `./runCMake.sh x64` followed
  by `make`, with zero errors, at commit
  `1726ba08bf7f2137d2f861ac1ae124d5cd355eee`, dated 2026-01-15. Method: a build
  performed outside this repository. It is the project's own repository rather
  than a mirror, and it publishes no tagged releases.
- **R-4 — UNVERIFIED.** That build produces `bin/fjfxSample`, which requires
  binary P5 PGM input and writes ISO/IEC 19794-2:2005.
- **R-5 — UNVERIFIED.** `fjfxSample` hardcodes 500 dpi: line 85 of
  `fjfxSample.c` passes the literal `500` to `fjfx_create_fmd_from_raw`.
  Method: reading the source. FVC2002 DB1, DB3 and DB4 are reported as 500 dpi
  and DB2 as 569 dpi; those resolutions are not verified here either, and no
  dataset manifest exists to carry them.
- **R-6 — UNVERIFIED.** On three images of `Db1_b` the tool is deterministic and
  produces 26 minutiae in 186 bytes, 16 in 126 bytes and 60 in 390 bytes. A
  decoded header showed image size 388 x 374, resolution 197 px/cm, finger
  quality 49, and minutia types 0, 1 and 2 all present. Method: running the
  tool and decoding its output outside this repository.

R-6's image size agrees with F-1, which is the only point at which a reported
fact and a measured one meet. That agreement is not treated as a verification
of anything else in the list.

## Reproducing this

Every count above comes from a script run inside the image the `Dockerfile`
builds. The scripts ran in the container and were destroyed with it; they read
images and write minutiae, so they are not committed. What they did is stated
below in full.

The container is entered as `make shell` does, with the image directory mounted
read-only:

    MSYS_NO_PATHCONV=1 docker run --rm \
      -v "<Db1_b>:/fixture:ro" dactyloscopy:dev bash

Inside it, for each of the 80 names:

    python3 -c 'from PIL import Image; import sys
    im = Image.open(sys.argv[1]); g = im.convert("L")
    g.save(sys.argv[2]); g.save(sys.argv[3])' /fixture/$n.tif /tmp/w/$n.png /tmp/w/$n.pgm

    mindtct     /tmp/w/$n.png /tmp/w/nat/$n     # .min and native .xyt
    mindtct -m1 /tmp/w/$n.png /tmp/w/m1/$n      # .xyt in the other convention
    mindtct     /fixture/$n.tif /tmp/w/reject   # F-3: refusal, status 253
    mindtct     /tmp/w/$n.pgm  /tmp/w/reject    # F-3: refusal, status 253

F-2 compares `numpy.array(Image.open(...))` of the TIFF against the PNG and the
PGM. F-5 to F-15 parse `.min` with

    ^\s*(\d+)\s*:\s*(\d+),\s*(\d+)\s*:\s*(\d+)\s*:\s*(\S+)\s*:

taking group 4 as the direction index and group 5 as the reliability **as
printed**, never as a float re-formatted; and parse `.xyt` as four
whitespace-separated integers per line. F-16 to F-18 need no image and are
reproduced by exact rational arithmetic on the three steps.

## What was left unchecked

- **The tool's source was not read.** F-7 gives a rule that reproduces every
  one of 3946 angles; it does not establish that this is the arithmetic
  `mindtct` performs. A rule that agrees on all 32 directions agrees
  everywhere, so no further image can separate it from the true one; only the
  source can.
- **One database, one sensor, one resolution.** Every measured fact is from
  FVC2002 `Db1_b`: 80 images, all 388 x 374. Nothing here shows what happens on
  a different image size, and F-13's `H - y` relation is exercised at exactly
  one value of `H`.
- **One build of one tool.** The facts are about the binary whose digest is
  named in "Method". Another build of NBIS 5.0.0 was not compared.
- **The `.min` file's other fields.** The type field (`APP`, `DIS`), the class
  field (`RIG`), the neighbour list and the number of neighbours were parsed
  past and not examined. Minutia type is a field ISO carries and this
  investigation says nothing about how the two agree.
- **The seven other mindtct outputs.** Only `.min` and `.xyt` were read. The
  quality map `.qm`, which is the more likely origin of the `.xyt` quality
  column, was not opened.
- **Whether the ambiguity of F-10 matters to a score.** No score was computed
  under two different quality columns. `bozorth3` reads the quality column, and
  what a difference of 1 does to a score is unmeasured.
- **Everything in R-1 to R-6.** No ISO template was produced or decoded here,
  and no second extractor is in the image.
- **The dataset identity.** The 80 images were read from a directory. Until a
  dataset manifest with a `set_md5` exists, no count above can be tied to a
  checksummed set. One copy of `Db1_b` was read, and no second copy was
  compared against it; F-4's 3946 is the denominator of every ratio above, and
  it is the first number a different copy would change.
