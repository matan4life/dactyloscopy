# INV-014 — How the two extractors differ on the same images

Date: 2026-09-08

## Numbering

This record takes 014, the next free investigation number after `INV-013`. The
reservation at 001 is explained in `REF-002`.

## Question

`INV-011` measured the two coordinate frames and `INV-012` the two angle
conventions. Before those two records a comparison of the two extractors would
have found a systematic vertical structure and a 180-degree disagreement, and
both would have been artefacts of notation rather than facts about the tools.
With the frames known the outputs can be put side by side, so: **do the two
extractors find the same minutiae, and where they do not, does the
disagreement have a structure?**

Neither tool is a reference for the other. `REF-007` decision 5 adopts both as
reproducible baselines and not as correct ones, so a disagreement measured here
is a fact about the two tools and nothing else.

## Method

### The frame, and which way the mapping runs

Both outputs are put into **the image's own frame**: origin at the top left, y
increasing downward, x in pixels of the input image; and the angle in degrees
counter-clockwise from the +x axis as the image is displayed, pointing along
the ridge the minutia belongs to.

`iso-extract` is already in that frame — `INV-011` F-2 and F-3 for the origin,
`INV-012` F-3 for the angle — so nothing is done to it. `mindtct` is brought to
it by the two transforms those records measured:

    x  = x_xyt
    y  = H - y_xyt                     INV-011 F-1
    th = (theta_xyt + 180) mod 360     INV-012 F-2 and F-5

**Why in that direction.** The frame is the one both earlier records measured
against, so neither transform is invented here. Converting only the tool that
needs converting leaves the other untouched, so an error in the conversion
cannot be hidden by a compensating error on the other side; had both been
mapped into some third frame, it could be.

**The transforms are taken as those records state them and are not re-derived.**
They were measured there on synthetic images, so this record checks — once, in
the plain numbers below — that the angle relation still holds on corpus images,
and reports the number.

### The converter, and `REF-006`

`REF-006`'s Open section forbids writing a reader or a writer before an
investigation reads the standard's text. That prohibition is about **the
canon's** reader, which would have to declare `angle_direction: iso-19794-2`
and so make a claim about a document; the three lines above declare their
conventions as **measured**, by `INV-011` and `INV-012`, and claim nothing
about any standard. They are an instrument of this investigation, they are not
the canon, no canon record is produced here, and nothing in this record is a
step toward writing one.

### Correspondence is a swept parameter

"The same minutia" means "within r pixels", and choosing one r chooses the
answer, so every count below is given across r = 1, 2, 3, 4, 5, 6, 8, 10, 12
and 15.

Three assignment rules are reported, because they differ and the difference is
largest where minutiae are dense:

- **greedy** — all pairs within r sorted by distance, taken in order while both
  ends are free;
- **optimal** — a maximum-cardinality matching on the graph whose edges are the
  pairs within r, by augmenting paths. This is the largest number of
  correspondences the radius admits, and it is never smaller than greedy;
- **mutual** — each is the other's nearest neighbour, and within r. This is the
  strictest, it needs no assignment rule at all, and it is what the fits below
  use, because a pair chosen by an assignment rule is a pair the rule was free
  to choose wrongly.

### The corpus

**Explored on `fvc2002/DB1_B`, confirmed on `fvc2002/DB1_A`.**
`MAN-fvc2002.v1`'s `roles` block records the organisers' own definition —
fingers 1 to 100 distributed as the benchmark evaluation set and 101 to 110 to
participants for parameter tuning — and `INV-005` F-10 measured that `DB1_B`
holds fingers 101 to 110 and `DB1_A` holds 1 to 100, eight impressions each.
So `DB1_B` is where a structure may be looked for, and **no number from it is a
benchmark**; every candidate is then run again, unchanged, on the 800 images of
`DB1_A`, and the two results are given side by side throughout.

**`fvc2002/DB2` is excluded**, by `REF-007` decision 4, untouched by this
record.

### The biometric rule

Counts, distributions, histograms and aggregates travel out of the container.
No coordinate, angle, type, quality or template byte of any FVC2002 minutia
does. The whole measurement runs in one process inside the image: the corpus is
mounted read-only, every intermediate file is written to `/tmp` and deleted
after the image that produced it, and the only thing written to the mounted
output directory is the aggregate JSON this record is made from.

## The plain numbers, before any structure is looked for

| | `DB1_B` | `DB1_A` |
| --- | --- | --- |
| images | 80 | 800 |
| all 388 by 374 | 80 | 800 |
| template header agrees with the image size | 80 | 800 |
| images the library refused | 0 | 0 |
| minutiae, `mindtct` | **3946** | **41 044** |
| minutiae, `iso-extract` | **3749** | **37 081** |
| per image, `mindtct` | 19 to 76 | 11 to 96 |
| per image, `iso-extract` | 16 to 96 | 10 to 155 |
| images where `iso-extract` found more | 24 of 80 | 187 of 800 |

`mindtct` finds about 5 per cent more minutiae in total on `DB1_B` and about 11
per cent more on `DB1_A`, but not image by image: on nearly a quarter of the
images the library finds more, and its per-image maximum is far higher.

### How many correspond

Every entry is a count of corresponding pairs, over the whole subset.

| r | `DB1_B` greedy | optimal | mutual | `DB1_A` greedy | optimal | mutual |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 516 | 516 | 516 | 5387 | 5387 | 5387 |
| 2 | 1116 | 1116 | 1116 | 11 669 | 11 669 | 11 669 |
| 3 | 1821 | 1821 | 1821 | 19 110 | 19 111 | 19 110 |
| 4 | 2206 | 2206 | 2205 | 23 033 | 23 034 | 23 032 |
| 5 | 2441 | 2441 | 2439 | 25 491 | 25 494 | 25 483 |
| 6 | 2571 | 2572 | 2568 | 26 611 | 26 620 | 26 586 |
| 8 | 2701 | 2708 | 2693 | 27 778 | 27 815 | 27 672 |
| 10 | 2790 | 2798 | 2762 | 28 430 | 28 508 | 28 198 |
| 12 | 2832 | 2849 | 2793 | 28 785 | 28 921 | 28 431 |
| 15 | 2885 | 2904 | 2819 | 29 229 | 29 415 | 28 664 |

As a fraction of the smaller of the two totals, which is `iso-extract`'s in both
subsets: at r = 3, **48.6** per cent on `DB1_B` and **51.5** per cent on
`DB1_A`; at r = 15, **77.5** and **79.3** per cent. Against `mindtct`'s total
the same optimal counts are 46.1 and 73.6 per cent on `DB1_B`, 46.6 and 71.7 on
`DB1_A`.

**The assignment rule matters less than the radius.** Greedy and optimal are
identical up to r = 5 and differ by at most 0.6 per cent at r = 15; mutual is
below both by up to 2.6 per cent at r = 15. The choice of r moves the answer by
30 percentage points and the choice of rule by under one.

### The frame, checked on corpus images

`INV-012` measured the 180-degree turn on synthetic images only. Over the
mutual pairs at r = 4, the difference between `iso-extract`'s angle and
`mindtct`'s turned angle:

| | `DB1_B` | `DB1_A` |
| --- | --- | --- |
| pairs | 2205 | 23 032 |
| circular mean of the difference | **3.20 degrees** | **3.52 degrees** |
| concentration R | **0.9366** | **0.9329** |
| pairs within 15 degrees | 1664 (75.5%) | 17 266 (75.0%) |

**The relation `INV-012` measured on constructed ridges holds on fingerprints.**
It is not exact — a few degrees of bias and a quarter of the pairs outside 15
degrees — but nothing here suggests the turn is other than 180 degrees, and
without it the difference would be centred near 183 rather than near 3.

## The candidates, fixed before looking

Five, each with a mechanism already in the records, written down before any of
them was tested. Anything found outside the five is labelled in a section of
its own and does not carry the same standing.

## C-1 — a lattice in `iso-extract`'s positions

### The lattice, derived rather than assumed

`INV-003` S-11 has the mechanism: inside the declared-resolution window this
repository is in, the library resamples the image before extracting, to a
target of `in_width / 6 * 4` by a routine named `imresize23`, and neither the
target nor the routine mentions the declared resolution. Two thirds.

The return path is three steps, all in
`FingerJetFXOSE/libFRFXLL/src/algorithm/FeatureExtraction.h`, blob
`5a775d0ccdceb776211f8ab296f87e401a8fe981`. Line 54 sets the constant:

    static const int32 imageScale = 127 * 5;

`RescaleMinutia`, lines 116 to 121, is applied at line 153:

        md.minutia[i].position.x = int16(md.minutia[i].position.x * imageScale / imageResolution);

which for the declared 500 is a multiplication by 635/500 = 1.27 in C integer
division, truncating. Lines 157 and 158 then add a constant per axis:

          m.position.x += int16(xOffs * imageScale / imageResolution);

and lines 168 to 174 rescale again by a constant the file's own comment calls
broken:

      #define StdFmdDeserializer_Resolution 167
          m.position.x = muldiv(m.position.x, 197, StdFmdDeserializer_Resolution);

`muldiv` rounds half up (`INV-003` S-2). Nothing after that touches the
position: `md.minutia_resolution_ppi` is set to 500 at line 177, so the
serializer's `mr_ppcm` is 197, equal to its default `resolutionX`, and the
conditional rescale of `INV-011` F-2 does not fire.

**So the composed factor is (635/500) x (197/167) = 1.4981437…**, and the set
of output coordinates the arithmetic can produce is

    R(k) = { muldiv( (635 p) div 500 + k, 197, 167 ) : p = 0, 1, 2, ... }

with `k` the one free constant, the padding term. **It is not all the
integers.** At k = 1, over 0 to 400, `R` has 267 members of 401; its gaps are 1
(160 times), 2 (80 times) and 3 (26 times), and the mean gap is 1.498. Its
density is **0.6675** at k = 1 and 0.6550 at k = 7.

### The test, and the trap

For each image and each axis, the `k` in 0 to 80 is chosen that puts the most
of that image's coordinates inside `R(k)`, and the fraction inside is reported.
**The identical procedure, with the identical freedom to choose the best of 81
offsets, is applied to `mindtct`'s coordinates on the same images**, and to a
uniform random set of the same size per image.

**The trap is that ridges are periodic too.** Minutiae sit on ridges, ridge
spacing on these images is about 9 pixels, and 9 is a multiple of 1.5, so a
ridge-scale periodicity could appear at the lattice scale. Finding periodicity
is therefore not the finding. Three things separate them here.

- **The test is membership in a set, not an amplitude.** `R(k)` comes out of
  integer arithmetic and excludes a third of the integers outright. A smooth
  modulation of density at any period cannot put every coordinate inside it.
- **`mindtct` is the control.** It reads the same images, sees the same ridges,
  and is given the same best-of-81 freedom. Whatever the ridges contribute, it
  contributes to both.
- **The ridge scale is measured beside the lattice scale.** The relative
  amplitude of the period-9 component of the pooled 1-pixel marginal histogram
  is reported next to the period-3 one, for both tools.

### What it found

| | `DB1_B` | `DB1_A` |
| --- | --- | --- |
| `iso-extract` x, mean fraction inside `R` | **1.0000** | **1.0000** |
| `iso-extract` y, mean fraction inside `R` | **1.0000** | **1.0000** |
| images where `iso-extract` is at 1.0 on x | **80 of 80** | **800 of 800** |
| images where `iso-extract` is at 1.0 on y | **80 of 80** | **800 of 800** |
| `mindtct` x, mean fraction | 0.7706 | 0.7631 |
| `mindtct` y, mean fraction | 0.7638 | 0.7608 |
| images where `mindtct` is at 1.0 | 0 | 0 |
| uniform random, mean fraction | 0.7462 | 0.7519 |

**Every one of the 40 830 minutiae `iso-extract` produced over 880 images has
both of its coordinates in the set the library's own integer arithmetic can
reach**, at one offset per image per axis. `mindtct`, on the same images and
with the same freedom, sits within a point or two of the random baseline.

The offset is nearly the same everywhere: on x it is `k = 1` on all 880 images;
on y it is `k = 7` on 843 of them, 2 on 35 and 3 on 2.

Beside it, the two scales:

| relative amplitude of the pooled marginal histogram | `DB1_B` | `DB1_A` |
| --- | --- | --- |
| `iso-extract`, period 3, x / y | 0.205 / 0.251 | 0.197 / 0.216 |
| `mindtct`, period 3, x / y | 0.060 / 0.007 | 0.008 / 0.021 |
| `iso-extract`, period 9, x / y | 0.026 / 0.021 | 0.026 / 0.016 |
| `mindtct`, period 9, x / y | 0.032 / 0.050 | 0.012 / 0.006 |

and the residues modulo 3, pooled over `DB1_A`:

| | 0 | 1 | 2 |
| --- | --- | --- | --- |
| `iso-extract` x | 11 789 | 10 601 | 14 691 |
| `iso-extract` y | 15 031 | 11 029 | 11 021 |
| `mindtct` x | 13 665 | 13 592 | 13 787 |
| `mindtct` y | 13 623 | 13 472 | 13 949 |

**At the lattice scale one tool has a large periodic component and the other
has none. At the ridge scale both are small and of the same order, and neither
tool is the larger one consistently.** The periodicity is at the resampling
scale, in the tool that resamples, and it is not the ridges.

### What this is, and what it is not

`INV-013` F-4 records NIST determining, in a report card last updated in 2015,
that template generator 3F "produces minutia exhibiting a periodic structure",
departing from the minutia placement requirements of INCITS 378 clause 5. The
lattice measured here is a periodic structure in minutia positions produced by
the open source code descended from that submission, and its period is derived
from that code's own arithmetic.

**It is not a reproduction of NIST's measurement**, and `INV-013` F-6 lists why
in four numbered gaps: NIST tested a 2009 Windows library, in the ANSI INCITS
378 format, against a PIV profile, over a sequestered US-VISIT set. This record
tested a Linux build of a 2026 commit, in the ISO format, over FVC2002 DB1,
with a different statistic. What the two have in common is the phenomenon and
the tool lineage, and that is all this record claims.

**Nothing here says the lattice is wrong**, either. `REF-007` decision 5
adopted these tools as reproducible baselines, and what a coordinate on a
1.5-pixel lattice does to a comparison score is not measured anywhere in this
repository.

## C-2 — a residual global transform

### What the arithmetic predicts

The three steps of C-1 compose to 1.4981437, and `INV-003` S-11's resample is
two thirds, so the round trip from input pixel to output coordinate is

    (2/3) x (635/500) x (197/167) = 250190/250500 = 0.9987625

**a shrink of 0.124 per cent**, not unity. If instead the resample were a fit
to the target width — 388 to 256, and 374 to 248 — the round trip would be
0.98847 in x and 0.99342 in y. The two readings of S-11 differ by an order of
magnitude and the measurement below separates them.

### The fit

Over the mutual pairs at r = 12, `iso-extract`'s coordinate is regressed on
`mindtct`'s, per axis, and a similarity is fitted to the pairs as points.
Because both coordinates carry error, the forward slope is biased low and the
inverse of the reverse slope biased high, so the two are given as a bracket
around the true one.

| | `DB1_B` | `DB1_A` |
| --- | --- | --- |
| pairs | 2793 | 28 431 |
| x scale, forward | 0.998579 ± 0.000655 | **0.998618 ± 0.000199** |
| x scale, from the reverse | 0.999779 | 0.999751 |
| y scale, forward | 0.999944 ± 0.000526 | **0.998438 ± 0.000155** |
| y scale, from the reverse | 1.000717 | 0.999119 |
| x offset, pixels | +0.309 | +0.322 |
| y offset, pixels | +1.068 | +1.464 |
| similarity scale | 0.999464 | 0.998499 |
| similarity rotation | −0.0536 degrees | −0.0438 degrees |
| residual RMS, x / y, pixels | 2.274 / 2.481 | 2.121 / 2.297 |

**The predicted 0.998762 lies inside the bracket on both axes of `DB1_A`** —
0.998618 to 0.999751 in x, 0.998438 to 0.999119 in y — and the fit-to-width
reading, 0.98847 in x and 0.99342 in y, is excluded by 51 and 32 standard
errors respectively.
So the resample is two thirds with the surplus columns dropped, not a fit to
the target width, and the return path undershoots it by about a tenth of a per
cent. On `DB1_B` alone the x axis agrees and the y axis does not; the eighty
images do not have the precision to see an effect of 0.5 pixels across the
image, which is why the candidate is stated on `DB1_A`.

The rotation is −0.04 degrees, about one standard error, and nothing suggests a
rotation exists.

### Whether it matters

The mapping was completed by putting `mindtct` through the fitted per-axis
affine and re-counting correspondences. On `DB1_A`, optimal assignment:

| r | before | after |
| --- | --- | --- |
| 1 | 5387 | 4430 |
| 2 | 11 669 | **13 609** |
| 3 | 19 111 | **20 499** |
| 4 | 23 034 | 23 764 |
| 5 | 25 494 | 25 742 |
| 8 | 27 815 | 27 890 |
| 15 | 29 415 | 29 432 |

**The leftover is sub-pixel and it shows only at sub-pixel radii.** At r = 2 it
is worth 16.6 per cent more correspondences and at r = 3 another 7.3; from
r = 8 upward it is worth nothing; and at r = 1 it costs 18 per cent, because
the fitted offsets are fractional and destroy the exact-integer coincidences
that r = 1 counts. **It is not what leaves a fifth of the minutiae unpaired at
r = 15.**

## C-3 — a boundary effect

Distance to the nearest image border, over the mutual pairing at r = 12.

| | `DB1_B` | `DB1_A` |
| --- | --- | --- |
| `mindtct`, mean distance, corresponding | 95.6 | 97.8 |
| `mindtct`, mean distance, not corresponding | **74.5** | **76.3** |
| `iso-extract`, mean distance, corresponding | 95.4 | 97.7 |
| `iso-extract`, mean distance, not corresponding | 93.1 | 98.4 |
| `mindtct` within 20 px of the border, corresponding | 2.15% | 2.06% |
| `mindtct` within 20 px, not corresponding | **8.15%** | **6.26%** |
| `iso-extract` within 20 px, corresponding | 2.51% | 2.29% |
| `iso-extract` within 20 px, not corresponding | 4.08% | 4.12% |

**The candidate holds for `mindtct` and not for `iso-extract`.** A `mindtct`
minutia with no partner sits about 21 pixels nearer the border than one with a
partner, and is three times as likely to be within 20 pixels of it. For
`iso-extract` the means are the same to within a pixel — on `DB1_A` the
unmatched ones are marginally *further* from the border — and only the
near-border fraction moves, by a factor of 1.8.

So the asymmetry is real and it runs one way: `mindtct` reports minutiae close
to the edge that `iso-extract` does not.

## C-4 — a strictness threshold

The quality each tool writes: `mindtct`'s fourth `.xyt` column and the sixth
byte of each ISO minutia, both on 0 to 100.

| | `DB1_B` | `DB1_A` |
| --- | --- | --- |
| `mindtct` mean quality, corresponding | 57.2 | 60.7 |
| `mindtct` mean quality, not corresponding | **23.3** | **22.9** |
| `iso-extract` mean quality, corresponding | 77.2 | 77.9 |
| `iso-extract` mean quality, not corresponding | **61.3** | **60.9** |
| `mindtct` in the 10-to-20 band, corresponding | 14.1% | 11.8% |
| `mindtct` in the 10-to-20 band, not corresponding | **65.0%** | **72.5%** |
| `iso-extract` in the 40-to-60 band, corresponding | 12.2% | 11.9% |
| `iso-extract` in the 40-to-60 band, not corresponding | **50.4%** | **51.2%** |

**The candidate holds for both tools, strongly.** Nearly three quarters of the
`mindtct` minutiae with no partner sit in one low band of its quality scale,
against about an eighth of those with a partner; half of `iso-extract`'s
unpaired minutiae sit in its own lowest occupied band, against an eighth again.

Two qualifications belong with it. The direction of the implication is not
established: a minutia may be unpaired because it is weak, or scored weak
because it is where the two tools disagree, and nothing here separates those.
And the two scales are not the same scale — **no `iso-extract` minutia in
either subset carries a quality below 40**, while `mindtct` uses the whole
range — so the two rows of this table are not comparable with each other, only
each with itself.

## C-5 — type disagreement where the positions agree

For every mutual pair at r = 12, `mindtct`'s `.min` type against the two type
bits of the ISO minutia, which `INV-012` F-6 records as 0 other, 1 ridge
ending, 2 bifurcation.

`DB1_A`, 28 431 pairs:

| | ISO 1, ending | ISO 2, bifurcation | ISO 0, other |
| --- | --- | --- | --- |
| `mindtct` `RIG` | **13 234** | 3277 | 1192 |
| `mindtct` `BIF` | 2266 | **7688** | 774 |

`DB1_B`, 2793 pairs:

| | ISO 1, ending | ISO 2, bifurcation | ISO 0, other |
| --- | --- | --- | --- |
| `mindtct` `RIG` | **1347** | 351 | 126 |
| `mindtct` `BIF` | 232 | **665** | 72 |

**The two tools agree on the type of 73.6 per cent of the minutiae they agree
on the position of** — 79.1 per cent if the `other` column, which `mindtct` has
no counterpart for, is set aside. On `DB1_B` the same numbers are 72.0 and 77.5
per cent. So roughly one pair in five that both tools place at the same point
is called an ending by one and a bifurcation by the other, and the disagreement
is not one-sided: 3277 against 2266 on `DB1_A`.

`INV-013` F-1 quotes the 2005 preview saying a ridge ending "may --
alternatively -- be regarded as a valley bifurcation depending on the method to
determine its position". This record does not connect that sentence to these
numbers; it measures the disagreement and stops.

## Found by looking, and not of the same standing

Two things were noticed while the five candidates were being tested. They were
not predicted, no mechanism was named for them in advance, and they are set
apart here for that reason.

- **The lattice offset is nearly constant across the corpus.** The arithmetic
  of C-1 predicts that some offset exists per image; it does not predict that
  it is the same one. On x it is `k = 1` on all 880 images of both subsets; on
  y it is `k = 7` on 843, 2 on 35 and 3 on 2. Whether that follows from
  `xOffs` and `yOffs` being nearly constant on images of one size was not
  traced.
- **`mindtct`'s quality column is strongly bimodal.** 72.5 per cent of its
  unpaired minutiae on `DB1_A` fall in a single band of ten, from 10 to 20,
  and the band holds far fewer of the paired ones. `INV-002` F-9 to F-12
  measured how that column relates to the reliability printed in `.min` and
  found the relation partly ambiguous; nothing here follows that up.

## Reproducing this

Every command was run on 2026-09-08 against the tree at `f45295e` and the image
built from its `Dockerfile`, image id
`sha256:e0ded5a5dcc8f594df58ab904be76605ad26492da834130592091b1348f7c3fc`. The
tools are the ones `MAN-tools.v2` records, at the invocations it freezes:
`mindtct <image.png> <root>` with no flags, and `iso-extract <image.pgm>
<template.ist>`.

**M — one process, two mounts.** `$SP` is a scratch directory outside the tree,
`$SP/out` the only writable one, and the corpus is read-only:

    docker run --rm -v "$SP:/sp:ro" -v "$SP/out:/out" \
      -v "$LABDATA/raw:/data/raw:ro" dactyloscopy:dev \
      python /sp/diff.py /data/raw/fvc2002/Dbs/Db1_b DB1_B
    docker run --rm ... python /sp/diff.py /data/raw/fvc2002/Dbs/Db1_a DB1_A

`$LABDATA` resolves as `.env.example` specifies and
`MAN-fvc2002.v1.json`'s `distribution` block records. The two runs took 5 and
43 seconds.

**E — what the script does per image.** Opens the TIFF with Pillow, converts
to `L`, writes it once as PNG and once as PGM — `INV-002` F-2 measured that
this preserves the pixels — runs both tools, reads `.xyt`, `.min` and the
template, deletes every file it wrote, and keeps only the parsed minutiae in
memory. All the analysis runs in the same process afterwards, and the only
output is one JSON of aggregates per subset.

**F — the frame**, three lines, from `INV-011` F-1 and `INV-012` F-2 and F-5:

    x  = x_xyt ;  y = H - y_xyt ;  theta = (theta_xyt + 180) mod 360

with the template read by the layout `INV-011` F-2 derived: `uint16` X at
`28 + 6i` with the type in its top two bits, `uint16` Y at `30 + 6i`, the angle
byte at `32 + 6i` scaled by 360/256, the quality byte at `33 + 6i`.

**C — the three assignment rules.** Greedy sorts every pair within `r` by
distance and takes them in order; optimal is a maximum-cardinality bipartite
matching by augmenting paths over the same edge set; mutual keeps the pairs
that are each other's nearest neighbour and within `r`.

**L — the lattice test.** `R(k)` is generated directly from the arithmetic,

    def reachable(k):
        return { ((((p * 635) // 500 + k) * 197 + 83) // 167) for p in ... }

where `(x*197 + 83) // 167` is `muldiv(x, 197, 167)` written out by `INV-003`
S-2's definition, and `k` runs over 0 to 80. The random baseline draws, per
image, as many uniform integers on `[0, w)` as the tool produced, and puts them
through the identical best-of-81 procedure. The seed is 20260908.

**S — the spectra.** The pooled 1-pixel marginal histogram of the coordinate
over a whole subset, its discrete Fourier coefficient at the bin nearest the
named period, twice its modulus divided by the total count.

## What was left unchecked

- **Which extractor is right.** Neither is a reference for the other, and this
  record ranks nothing. That `iso-extract`'s coordinates lie on a lattice is a
  fact about its arithmetic; that `mindtct`'s do not is a fact about its.
- **Anything about the angle beyond the relation `INV-012` measured.** The
  angle was used once, to check that the 180-degree turn survives on corpus
  images, and never in the correspondence: "the same minutia" is a distance in
  pixels and nothing else. `D-3` is untouched.
- **Generalisation beyond `DB1`.** `DB3` and `DB4` exist and were not used.
  `DB2` is excluded by `REF-007` decision 4. Every number above is from one
  sensor, one image size and 880 images of 110 fingers.
- **Whether any of this matters for matching.** That needs a matcher, a
  protocol and a metric, and none of the three is in scope. No score was
  computed, no `results.json` was written, and nothing here says a lattice, a
  0.12 per cent scale or a fifth of the minutiae unpaired changes any rate.
- **The resampler itself.** `imresize23` was not read. C-1 and C-2 rest on
  `INV-003` S-11's quotation of the target size and the routine's name, plus
  the return path quoted here; the resampling kernel, and what it does to a
  minutia's position within one internal pixel, were not traced.
- **`xOffs` and `yOffs`.** The offset `k` of C-1 was fitted, not read. Where
  the padding constants come from and why they are nearly the same on every
  image was not traced.
- **Whether the unpaired minutiae are spurious.** C-4 shows the unpaired ones
  are the low-quality ones in both tools; it does not show that either tool is
  finding something that is not there, which would need ground truth this
  corpus does not carry.
- **`mindtct`'s reliability column, and the `.min` fields beyond type.** The
  neighbour lists, the `APP`/`DIS` field and the reliability were parsed past.
- **Per-finger and per-impression structure.** Every aggregate above pools the
  whole subset. Whether the disagreement varies by finger, by impression
  number or by image quality was not looked at.
- **A second implementation of the correspondence.** The three assignment
  rules are three functions in one file written by one author, and they agree
  with each other; they were not checked against an independent one.
