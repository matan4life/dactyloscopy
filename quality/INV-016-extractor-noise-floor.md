# INV-016 — The localization noise floor of mindtct under exact geometry

Date: 2026-09-08

## Numbering

This record takes 016, the next free investigation number after `INV-015`. The
reservation at 001 is explained in `REF-002`.

## Question

`INV-015` measured a held-out residual of 4.5 to 7 px between two impressions of
one finger, and a spread of 0.6 px between the best and the worst warp family
in a list of nine. Two readings of that fit the same numbers and point opposite
ways: the residual is mostly the extractor's own localization noise, in which
case no deformation model can reach it; or it is real inter-impression
difference that none of the nine families represents, in which case the model
search is not over.

**This record measures the first quantity directly**, on images that differ by
an exact integer translation and by nothing else, so that the ground-truth
displacement is known everywhere and there is no deformation to confound it.

## What this bounds, and what it does not

**It is a lower bound.** Two real impressions differ by more than framing:
different ridge contact, different moisture, different pressure. Each of those
raises the floor. So a large number here settles the reading; a small number
here would not license the opposite conclusion, because the real floor is
higher than this one by an unmeasured amount.

The brief fixes the threshold in advance, before any of the numbers below
existed, and this record applies it and reports which band the result lands in.
**Taking the decision is not this record's business** — an investigation states
facts — so the decision is stated as the brief's, and the number is stated as
the measurement.

## Method

### The construction, and why no pixel is invented

For a source image `S` of width `W` and height `H` and an integer shift `d`:

- horizontally, `A` is columns `[d, W)` of `S` and `B` is columns `[0, W−d)`;
- vertically, `A` is rows `[d, H)` and `B` is rows `[0, H−d)`.

`A` and `B` are two crops of the same pixels. Nothing is resampled, no border is
invented, and a feature that lies at source column `c` appears at column `c−d`
in `A` and at column `c` in `B`. `mindtct` is then run **independently** on
each, so the two runs see different image extents and a differently aligned
block grid, which is the sensitivity being measured.

**Both outputs are mapped back into the source's own `.xyt` frame**, where the
true displacement between paired minutiae is exactly zero, and the deviation is
read there. The maps are:

| | from `A` | from `B` |
| --- | --- | --- |
| horizontal | `x_S = x_A + d`, `y_S = y_A` | `x_S = x_B`, `y_S = y_B` |
| vertical | `x_S = x_A`, `y_S = y_A` | `x_S = x_B`, `y_S = y_B + d` |

The vertical row is asymmetric and the asymmetry is not a slip. `mindtct`'s
`.xyt` counts y from the **bottom** of the image it was given; `A` is the crop
that drops the top rows, so its bottom edge is the source's bottom edge and its
`.xyt` y needs no correction, while `B` drops the bottom rows and its y is short
by `d`. The brief's `|x_B − (x_A + d)|` is the horizontal case of the same
quantity, and it is what is reported as `N-1`.

### The block size, read from the source and not assumed

`mindtct.c` line 154, sha256
`d23c84e13eb4533a2b20a918d98874bc404a7735395a210e3039d9997ecf912c`, calls the
detector with `&lfsparms_V2`. `globals.c` lines 161 to 169, sha256
`2f62dab2edf6e5ef98719f81c1ed4c561956d4ee2751957819499db14fe46637`, builds that
structure:

    LFSPARMS lfsparms_V2 = {
       ...
       /* Map Controls */
       MAP_BLOCKSIZE_V2,
       MAP_WINDOWSIZE_V2,
       MAP_WINDOWOFFSET_V2,

and `lfs.h` lines 333 to 349, sha256
`1944208fdb9c3a24c7d01e0e20584cb407d9a3b5a710f20c942a0664c86c0a71`, defines
them, with the file's own comment:

    /* Pixel dimension of image blocks. The following three constants work */
    /* together to define a system of 8X8 adjacent and non-overlapping     */
    /* blocks that are assigned results from analyzing a larger 24X24      */
    /* window centered about each of the 8X8 blocks.                       */
    #define MAP_BLOCKSIZE_V2         8
    #define MAP_WINDOWSIZE_V2       24
    #define MAP_WINDOWOFFSET_V2      8

**So `b = 8`**, and the window that produces each block's value is 24 by 24,
three blocks across. `N-4` is computed against `d mod 8` on that ground.

### Pairing, and the common region

Minutiae are paired by **mutual nearest neighbour within 15 px in the source
frame** — 15 px is the radius `N-2` names, and using one radius for both keeps
`N-1` and `N-2` measuring the same set.

**The common region is enforced, and both numbers are given.** For a shift `d`,
`A` has no pixels below source column `d` and `B` none at or above `W−d`, so a
minutia outside `[d, W−d)` cannot have a partner for reasons of geometry rather
than instability. Everything below keeps only minutiae at least **16 px inside
both crops' own borders** — source coordinate in `[d+16, W−d−16)`, and the
analogous range vertically. `N-2` is additionally reported without that
restriction, so the reader can see what the margin removes.

### The mask, the bands and the exclusions

The radius of a minutia is measured from the mask centroid of `S`, with the mask
defined as `INV-015` defines it: `mindtct`'s own quality map at `q >= 1`, one
value per 8 by 8 block. Bands are 0-30, 30-60, 60-90, 90-120, 120-150 and 150+
px. An image yielding fewer than 12 minutiae is excluded and the exclusions are
counted.

### The noise of `N-3`

Zero-mean Gaussian noise of standard deviation σ ∈ {1, 2, 4, 8} grey levels is
added to the 8-bit array, rounded to integers and clipped to 0..255. The
generator is seeded per image and per σ from a fixed seed, so the noisy images
are reproducible. `A` is the untouched image and `B` the noisy one, both at full
size, so the true displacement is exactly zero.

## The two checks that had to pass first

**`N-0`, determinism.** `mindtct` was run twice on each of the 80 images and all
eight output files compared byte for byte — `.brw`, `.dm`, `.hcm`, `.lcm`,
`.lfm`, `.min`, `.qm`, `.xyt`. **80 of 80 images identical on all eight files**,
no file differing on any image. `Q-1` passes and nothing below is undermined by
non-determinism.

**The null-shift control.** With `d = 0` and no noise added, the source's
minutiae were paired against the second identical run's: **3946 pairs, maximum
deviation 0.000 px, zero unmatched of 3946**. The pairing code returns exactly
zero when the answer is exactly zero, so a non-zero number below is the
extractor and not the arithmetic.

**Exclusions.** No image fell below 12 minutiae; the counts run from 19 to 76
with a median of 49, and none of the 80 was excluded.

## `N-1` — the deviation under an exact translation

89 489 paired minutiae over 80 images, 13 shifts and two directions. The
"along" column is the brief's `|x_B − (x_A + d)|` and its vertical counterpart;
the "2-D" column is the full Euclidean deviation, which is the quantity
comparable with `INV-015`'s residual.

| d | pairs | along RMS | 2-D RMS | fraction exactly 0 |
| --- | --- | --- | --- | --- |
| 1 | 7038 | 0.943 | 1.343 | 0.859 |
| 2 | 6819 | 1.075 | 1.645 | 0.807 |
| 3 | 6686 | 1.196 | 1.818 | 0.782 |
| 4 | 6626 | 1.211 | 1.865 | 0.779 |
| 5 | 6691 | 1.237 | 1.835 | 0.791 |
| 6 | 6774 | 1.141 | 1.708 | 0.806 |
| 7 | 7017 | 0.937 | 1.357 | 0.809 |
| **8** | 7586 | **0.402** | **0.532** | **0.875** |
| 9 | 6925 | 0.996 | 1.387 | 0.803 |
| 10 | 6686 | 1.101 | 1.664 | 0.783 |
| 12 | 6530 | 1.186 | 1.826 | 0.811 |
| 14 | 6655 | 1.163 | 1.720 | 0.800 |
| **16** | 7456 | **0.344** | **0.450** | **0.896** |

**Pooled over every `d` from 1 to 16: `F` = 1.024 px along the shift, 1.526 px
in two dimensions.**

Two things about the shape of that number. It is **not a broad scatter**: four
out of five paired minutiae do not move by a single pixel, and the RMS is
carried by the fifth that does. And its tail is **cut off by the pairing rule**:
a minutia that moves more than 15 px is not a large deviation in this table, it
is an unmatched minutia in `N-2`, so every RMS here is a deviation conditional
on the minutia surviving as a pair, and the largest value seen is 15.0 px by
construction.

By direction the floor is the same, 1.015 px horizontally and 1.033 vertically,
so nothing here is an artefact of one axis.

By radius band, at the shifts that are not multiples of 8:

| band | pairs | along RMS | 2-D RMS | fraction exactly 0 |
| --- | --- | --- | --- | --- |
| 0-30 | 3847 | **1.583** | **2.248** | 0.698 |
| 30-60 | 9387 | 1.256 | 1.759 | 0.775 |
| 60-90 | 14 485 | 1.182 | 1.687 | 0.788 |
| 90-120 | 19 141 | 0.956 | 1.378 | 0.822 |
| 120-150 | 17 239 | 0.956 | 1.625 | 0.825 |
| 150+ | 10 348 | 1.157 | 1.792 | 0.818 |

**The floor is largest at the centre**, not at the periphery: 2.25 px in the
innermost band against 1.38 in the 90-120 one. That is the opposite of the
shape a deformation growing with radius would have, and it is worth putting
beside `INV-015`'s finding that its own residual, taken inside the fitting
fold's convex hull, was flat in radius.

## `N-4` — against `d`, and against `d mod 8`

The block size read from the source in the Method is **8**. Pooling the same
89 489 deviations by `d mod 8`:

| `d mod 8` | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| along RMS, px | **0.374** | 0.970 | 1.088 | 1.196 | 1.199 | 1.237 | 1.152 | 0.937 |

**The deviation collapses by a factor of three when the shift is a whole number
of blocks**, and is otherwise flat in `d` at about 1.1 px with a shallow maximum
near half a block. Pooled: 1.110 px at `d mod 8 ≠ 0` against **0.374 px** at
`d ∈ {8, 16}`.

### The crop controls say why, and they refute the reasoning of `Q-2`

`S` and `B` share a left edge — or a bottom edge, vertically — so `B` differs
from `S` in **extent only**, with the block grid in the same phase. `A` differs
from `S` in extent **and** in the grid's phase, by `d`. Both were compared with
`S` over the same common region:

| control | what changes | pairs | RMS | fraction exactly 0 |
| --- | --- | --- | --- | --- |
| `S` against `B` | the extent | 84 505 | **0.099 px** | **0.998** |
| `S` against `A` | the extent and the grid phase | 74 506 | 1.659 px | 0.692 |
| `S` against `A`, at `d` = 8, 16 | the extent, phase back in step | — | 0.483 px | 0.820 |

**Changing how much image `mindtct` is given moves essentially nothing: 998 of
every 1000 minutiae do not move at all, and the RMS is a tenth of a pixel.**
Changing where the 8-pixel block grid falls moves 1.66 px RMS, which is the
whole of the `A`-against-`B` effect. `Q-2` predicted the deviation would not
drop at multiples of the block size **because the image extent changed as
well**; the extent change contributes 0.1 px and the phase change 1.66, so the
reason given is measured to be wrong even though the prediction's letter — that
`N-1` never reaches zero — holds.

## `N-2` — set instability

The fraction of minutiae with no partner within 15 px, inside the common region.
Both sides are given because they need not agree.

| d | `A`-side unmatched | `B`-side unmatched | without the margin, `A` / `B` |
| --- | --- | --- | --- |
| 1 | 8.76% | 9.58% | 8.99% / 9.74% |
| 2 | 11.66% | 12.31% | 12.09% / 12.62% |
| 3 | 13.11% | 13.93% | 13.69% / 14.30% |
| 4 | **13.65%** | **14.37%** | 14.40% / 14.63% |
| 5 | 12.46% | 13.42% | 13.31% / 13.75% |
| 6 | 11.53% | 12.09% | 12.28% / 12.38% |
| 7 | 8.48% | 8.81% | 9.47% / 9.29% |
| **8** | **1.10%** | **1.15%** | 2.47% / 1.87% |
| 9 | 8.76% | 9.52% | 10.12% / 10.28% |
| 10 | 11.58% | 12.56% | 13.01% / 13.38% |
| 12 | 13.60% | 14.18% | 15.20% / 15.12% |
| 14 | 11.54% | 11.98% | 13.31% / 12.88% |
| **16** | **0.97%** | **0.96%** | 3.47% / 2.37% |

**A one-pixel shift of the frame costs about 9 per cent of the minutia set, and
a four-pixel shift about 14 per cent.** The margin removes between 0.2 and 2.5
points of that, so the effect is not the crop boundary. And the same period-8
collapse appears: at a whole number of blocks the set is stable to about one per
cent.

By band, at `d` = 1, the `A`-side unmatched fraction is 8.8, 7.6, 7.1, 6.8, 10.0
and 12.9 per cent from the innermost band outward — worst at the periphery,
where `INV-015` found the hull coverage collapsing.

**This number feeds `INV-014` directly.** `INV-014` measured that at a 15 px
radius, 71.7 to 79.3 per cent of minutiae correspond between two impressions of
one finger by two different extractors. Here, one extractor against itself, on
the same pixels, differing only by where the frame starts, loses **9 to 14 per
cent** of the set.

## `N-3` — photometric noise alone

`d = 0`, so the true displacement is exactly zero; `B` is the source image plus
zero-mean Gaussian noise.

| σ, grey levels | pairs | 2-D RMS | fraction exactly 0 | largest | unmatched, source side / noisy side |
| --- | --- | --- | --- | --- | --- |
| 1 | 3850 | **0.725 px** | 0.930 | 14.3 | 2.43% / 2.28% |
| 2 | 3603 | 1.175 | 0.869 | 15.0 | 8.69% / 4.10% |
| 4 | 3504 | 1.379 | 0.795 | 14.6 | 11.20% / 5.96% |
| 8 | 3400 | 2.087 | 0.682 | 14.9 | 13.84% / 11.20% |

**`Q-5` passes.** At σ = 1 grey level — noise no one would see in the image —
seven per cent of minutiae move, 2.4 per cent of the set disappears, and the
deviation of those that remain has an RMS of 0.73 px with a largest value of
14.3. At σ = 8 the RMS is 2.09 px and one minutia in seven is gone.

Note that the number of pairs falls as σ rises, from 3850 to 3400, because the
unmatched are excluded from the deviation; the two columns have to be read
together.

## `F`, and the band it lands in

The brief defines `F` as the pooled RMS of `N-1` over `d ∈ {1..16}`, and `N-1`
as the deviation along the shift. Measured over 89 489 pairs:

| | value | the brief's bands |
| --- | --- | --- |
| **`F`, along the shift, as defined** | **1.024 px** | `F ≤ 1.5` |
| `F`, two-dimensional | 1.526 px | `1.5 < F < 3.0`, by 0.026 px |

**By the definition the brief gives, `F = 1.024 px` and the result is in the
second band: the 4.5 to 7 px residual of `INV-015` is not extractor noise.**
`F` is not near the 3.0 px boundary on any reading — the noise-limited reading
is excluded by a factor of two to three, and that much is unambiguous.

**The one ambiguity is definitional and this record does not resolve it.** The
quantity comparable with `INV-015`'s residual is the two-dimensional one,
because that residual is a Euclidean distance; it is 1.526 px, which is 0.026 px
inside the middle band where the brief says to report and decide separately. The
distinction is not statistical: with 89 489 pairs the standard error of either
RMS is under 0.01 px. So the two readings differ by which quantity the threshold
was meant for, and **choosing between them is a decision, which an investigation
does not take.**

**`DB1_A` was not run.** The brief scopes this to `DB1_B` and adds `DB1_A` only
if §6 lands in the ambiguous band; on `F` as defined it does not. Running it
would return the same two numbers on a different set of fingers with the same
precision, and could not resolve a definitional question — though whether the
ten tuning fingers' floor is the hundred evaluation fingers' floor is untested
and is listed below.

**What the number implies for `INV-015`'s residual, as arithmetic.** If the
extractor floor is independent of whatever else separates two impressions, the
two add in quadrature, and a residual of 4.5 px decomposes as
`sqrt(1.526² + 4.233²)`. On that assumption the floor is **11.5 per cent of the
variance** at the low end of `INV-015`'s range and **4.8 per cent** at 7 px. The
independence is an assumption, not a measurement, and it is stated as one.

## The predictions, scored

| | prediction | outcome |
| --- | --- | --- |
| `Q-1` | `N-0` byte-identical | **PASSES.** 80 of 80 images, all eight output files. |
| `Q-2` | `N-1` non-zero for every `d ≥ 1`, and not dropping to zero at multiples of the block size | **PASSES as worded, and its reasoning is refuted.** The smallest value is 0.344 px at `d = 16`, never zero. But it does drop, by a factor of three, and the stated reason — that the extent changed as well — is measured: the extent change alone contributes 0.099 px and the grid phase 1.659. |
| `Q-3` | `N-1` RMS at least 2 px pooled | **FAILS.** 1.024 px along the shift, 1.526 px in two dimensions. Both below 2 on 89 489 pairs. |
| `Q-4` | `N-2` non-zero at `d = 1` and growing with `d` | **HALF.** Non-zero at `d = 1`, 8.76 per cent. It does not grow with `d`: it peaks at `d = 4` at 13.65 per cent, falls back, and collapses to about 1 per cent at 8 and 16. The dependence is periodic in `d`, not monotone. |
| `Q-5` | `N-3` at σ = 1 already moves minutiae | **PASSES.** 7.0 per cent of minutiae move, 2.4 per cent of the set is lost, RMS 0.725 px, largest 14.3 px. |

Nothing was changed after these were scored.

## What this record does not decide

The brief fixes a decision on `F` and this record supplies `F`. **The decision
is not taken here**, in either of its two readings, and no refinement is
written. What the record states is the number, the band it falls in by the
brief's own definition, and the one place where the definition is ambiguous.

## Reproducing this

Every command was run on 2026-09-08 against the tree at `f844aae` and the image
built from its `Dockerfile`, image id
`sha256:e0ded5a5dcc8f594df58ab904be76605ad26492da834130592091b1348f7c3fc`.
`mindtct` is the tool `MAN-tools.v2` records, at the invocation it freezes:
`mindtct <image.png> <root>`, no flags.

    docker run --rm -v "$SP:/sp:ro" -v "$SP/out:/out" \
      -v "$LABDATA/raw:/data/raw:ro" dactyloscopy:dev \
      python /sp/floor.py /data/raw/fvc2002/Dbs/Db1_b DB1_B

`$LABDATA` resolves as `.env.example` specifies and `MAN-fvc2002.v1`'s
`distribution` block records. The run took about twelve minutes and made 4640
`mindtct` invocations.

| parameter | value |
| --- | --- |
| shifts `d` | 1 to 10, 12, 14, 16 |
| directions | horizontal and vertical |
| σ for `N-3` | 1, 2, 4, 8 grey levels |
| pairing | mutual nearest neighbour, 15 px, in the source frame |
| common-region margin | 16 px inside both crops' own borders |
| minimum minutiae per image | 12 |
| mask | `.qm >= 1`, 8 px blocks, as `INV-015` |
| bands | 0-30, 30-60, 60-90, 90-120, 120-150, 150+ px from the mask centroid of `S` |
| seed | 20260908 |

The crops are `PIL.Image.crop`, which copies pixels and resamples nothing; each
crop is written as PNG and passed to `mindtct` exactly as a corpus image is.
The determinism check compares the eight output files with `filecmp.cmp` at
`shallow=False`.

The block size and the parameter set were read from the NBIS sources in the
builder stage:

    docker build --target nbis-builder -t dactyloscopy:nbis-audit .
    docker run --rm dactyloscopy:nbis-audit sha256sum \
      /src/mindtct/include/lfs.h \
      /src/mindtct/src/lib/mindtct/globals.c \
      /src/mindtct/src/bin/mindtct/mindtct.c

with the ranges quoted in the Method: `lfs.h` 333-349, `globals.c` 161-169,
`mindtct.c` 154.

## What was left unchecked

- **Nothing about `iso-extract`.** One extractor, by design; the comparison
  between extractors is `INV-014`.
- **Nothing about angles.** No angle was read or compared. Positions only.
- **The true inter-impression floor, which is higher.** Two real impressions
  differ by ridge contact, moisture and pressure as well as by framing, and
  none of those is present here. This is a lower bound and cannot be used to
  argue the floor is small.
- **Only translation.** A relative rotation between two impressions changes the
  block grid's relationship to the ridges in a way an integer translation
  cannot, and no rotation was tested — it cannot be tested by this
  construction, because rotating an image requires resampling and the whole
  point here is that no pixel is invented.
- **Deviations beyond 15 px.** They are counted as unmatched in `N-2` rather
  than measured in `N-1`, so every RMS above is conditional on the minutia
  surviving as a pair, and the floor's tail is unmeasured.
- **Shift and noise together.** `N-1` and `N-3` were run separately; whether
  their effects add, and how, was not measured.
- **Whether aligning to the block grid would remove the effect.** The period-8
  structure says the grid phase is what moves the minutiae; nothing here tests
  a protocol that keeps the phase fixed, and doing so would be an intervention
  rather than a measurement.
- **Generalisation.** Eighty images, ten fingers, one sensor, one image size,
  `DB1_B` only. Whether the floor on `DB1_A`'s hundred fingers is the same is
  untested; the brief's trigger for running it was not met.
- **Why `INV-015` found about 12 per cent of its RANSAC alignments mutually
  inconsistent.** That is a separate defect in the correspondence stage and
  needs its own investigation. Nothing here touches it.
