# INV-015 — Which warp family predicts a held-out correspondence

Date: 2026-09-08

## Numbering

This record takes 015, the next free investigation number after `INV-014`. The
reservation at 001 is explained in `REF-002`.

## Question

Whether a low-parameter radial warp predicts a **held-out** correspondence
between two impressions of one finger better than the conventional families do,
as a function of distance from the contact centre, and by how much.

Five subordinate questions were fixed in advance as predictions and are scored
at the end, whichever way they came out.

## Two things this record does not rest on

**A document that is not in this repository.** The brief that commissioned this
investigation cites `STATE-2026-09-08 §6.2` twice, for the exclusion of angles
and for treating the pairing radius as a swept parameter. **No such file exists
in this tree**, and a record here may rest only on what is in it, for the same
reason `CLAUDE.local.md` may not be cited: an untracked document cannot be
checked by a later reader. Both constraints are kept, and both are grounded on
records that do exist. Angles are out because `D-3` and `D-4` are open —
`REF-006`, `REF-007` and `REF-008` all track them, and `INV-013` F-3 measured
that the standard's previews leave the sense of the tangent unstated. The
radius is swept rather than chosen because `INV-014`'s Method established that
choosing one radius chooses the answer.

**A simulated number.** The brief predicts, from simulation outside this
repository, that the estimation errors of the two radial coefficients are
correlated at about −0.89, and that the consistency residual of §7 is 2 to 3
times more sensitive than a fit residual. Neither is a fact of this repository.
The first is measured here and reported beside the prediction; the second is
not tested here and is left in "what was left unchecked".

## Method

### Frame and units

**One extractor, `mindtct`, and no frame conversion.** This investigation is
not about the difference between extractors — `INV-014` is — and using two
would confound the two questions. Every coordinate below is a `mindtct` `.xyt`
coordinate exactly as the tool wrote it. `INV-011` F-1 and F-2 describe what
must be done when two tools' frames are compared; no comparison of that kind
happens here.

One consequence has to be stated because it is the only place two of
`mindtct`'s own outputs meet. The `.xyt` file counts y from the bottom and the
block maps are written in image raster order, from the top. The **maps are
flipped into the `.xyt` frame**, not the minutiae into the maps' frame, so that
no point coordinate is ever altered. That is one tool's two outputs put into
one of that tool's own frames, and it is not the frame crossing `INV-011` is
about.

Every length is in **pixels at 500 dpi**, where **1 px = 0.0508 mm**.

### Step 1 — what is measured per image

- **M-1** the minutia positions from `mindtct`'s `.xyt`, positions only.
- **M-2** the foreground mask: `mindtct`'s own quality map `.qm`, thresholded
  at **q ≥ 1**, which is the one parameter of the mask and is not tuned per
  image. The map is one value per 8 by 8 pixel block, so the mask area is the
  count of foreground blocks times 64 px², and the mask's resolution is 8 px.
- **M-3** the mask centroid, in the `.xyt` frame, and the equivalent radius
  `a = sqrt(area/pi)`.
- **M-4** the count of minutiae inside the mask.

The mask is the contact patch throughout, and `r` is always measured from its
centroid. `r_s`, the scale that makes coefficients comparable across pairs, is
the image half-diagonal fixed at **269 px**; the images are 388 by 374, whose
half-diagonal is 269.4.

### Step 2 — the correspondence, frozen before any model is fitted

1. **Coarse alignment**: translation and rotation only, by RANSAC over minutia
   positions. A sample is two source points and two target points whose
   separations agree to within 3 px, with the source separation above 25 px;
   200 000 random quadruples are drawn and the first 4000 that pass the
   separation test are scored by the number of source points landing within
   12 px of some target point. The best is refined three times by Procrustes on
   its inliers. The seed is 20260908.
2. **Pairing**: mutual nearest neighbour within τ, positions only.
3. **τ is swept** over {3, 5, 8, 12, 15, 20} px and all six pairings are
   carried forward.
4. **The pairing is frozen.** No model re-pairs. A model allowed to choose its
   own correspondences chooses the ones that flatter it.

### Step 3 — the models, frozen before looking

All are written as `q = R · D(p − c) + t` with `c` the mask centroid of the
source image, so that every model is anchored at the same point and the radial
family is exactly nested in the same parameterisation.

| id | `D(v)`, with `r = |v|` | params |
| --- | --- | --- |
| M0 | `v`, and `R` fixed to the identity | 2 |
| M1 | `v` | 3 |
| M2 | `s·v`, free scale | 4 |
| M3 | `v + c1(r/r_s)·v̂` | 4 |
| M4 | `v + c1(r/r_s)·v̂ + c3(r/r_s)³·v̂` | 5 |
| M5 | `v + c1(r/r_s)·v̂ + c2(r/r_s)²·v̂` | 5 |
| M6 | M4 plus `c5(r/r_s)⁵·v̂` | 6 |
| M7 | affine, `A·v` with `A` free | 6 |
| M8 | thin-plate spline, λ ∈ {0, 10, 10², 10³, 10⁴} | 2N+6 |

**M2 and M3 are one model written twice.** `c1(r/r_s)·v̂ = c1·v/r_s`, so
`D(v) = v(1 + c1/r_s)`, which is a similarity of scale `s = 1 + c1/r_s`. They
are both in the list as the implementation check, and they are never fitted
together.

### Step 4 — fitting and evaluation

Every model is fitted with a **Huber loss, δ = 3 px, on positions only**, by
iteratively reweighted least squares: the rigid and radial families by
alternating a weighted Procrustes with a linear solve for the coefficients, the
affine by a weighted linear solve, and the spline by the weighted smoothing
system with `λ/w_i` on the diagonal.

**The iteration count is 60, and it was raised from 15 because the
implementation check failed at 15.** At 15 iterations the two parameterisations
of the same model, M2 and M3, disagreed by 1.4·10⁻³ in the scale and 1.6·10⁻²
px in the residual, which is convergence and not algebra but is not "numerical
precision" either. A separate test on synthetic data — 40 problems with
outliers, at 15, 40, 120 and 400 iterations — gave worst disagreements of
2.1·10⁻⁵, 2.3·10⁻¹⁴, 6.7·10⁻¹⁶ and 4.4·10⁻¹⁶ in the scale, so the routines
converge to the same optimum and the iteration count was the whole of it. The
number reported below is the one at 60.

Evaluation is **5-fold cross-validation over the frozen correspondences**,
folds stratified by radius: the points are sorted by `r` and dealt round-robin
into five folds, so every fold holds peripheral points. Every correspondence is
held out exactly once, which is what makes the model-to-model comparison a
paired one.

**Pairs with fewer than 8 correspondences are excluded from model comparison**
and the exclusions are counted, per τ, rather than dropped in silence.

### The corpus, and the order in which it was used

Explored on `fvc2002/DB1_B`, the ten fingers the organisers gave for parameter
tuning (`MAN-fvc2002.v1`'s `roles`, `INV-005` F-10), 80 images and 280 genuine
pairs. **`DB1_A` was not run until the `DB1_B` sections below were written**,
and its results are in a section of their own. `fvc2002/DB2` is excluded by
`REF-007` decision 4, untouched.

### The biometric rule

Every measurement runs in one process inside the container: the corpus is
mounted read-only, every intermediate file is deleted after the image that
produced it, and what leaves the container is counts, histograms, residual
summaries and fitted coefficients. No minutia position, and no per-minutia
value of any kind, is written out.

## Step 1 on `DB1_B` — the images and the mask

Ten fingers, eight impressions each, all 388 by 374. Every length below is in
pixels; **1 px = 0.0508 mm**.

| | value |
| --- | --- |
| minutiae per image | 19 to 76 |
| mask area | 39 552 to 97 152 px², mean 74 621 |
| equivalent radius `a` | 112.2 to 175.9 px, mean 153.4 |
| within-finger spread of the area, standard deviation | 5267 to 15 026 px² |
| the same mask from `.lcm == 0` instead of `.qm >= 1` | mean ratio 0.9673, largest difference 4608 px² |

**The mask check of §10 passes.** The area varies between impressions of one
finger by a standard deviation of 5000 to 15 000 px², which is 7 to 20 per cent
of the mean area, so the threshold is not saturating and `R-5` can be
interpreted. The two candidate definitions of foreground — the quality map at
`q >= 1` and the low-contrast map at 0 — agree to within 3 per cent of area,
so the choice between them is not what any number here rests on.

## Step 2 on `DB1_B` — the frozen correspondences

RANSAC found an alignment for all 280 genuine pairs.

| τ | median N | min | max | pairs with N < 8, excluded | pairs used |
| --- | --- | --- | --- | --- | --- |
| 3 | 10 | 1 | 39 | 100 | 180 |
| 5 | 18 | 3 | 51 | 37 | 243 |
| 8 | 24 | 4 | 56 | 6 | 274 |
| 12 | 25 | 9 | 57 | 0 | 280 |
| 15 | 26 | 9 | 58 | 0 | 280 |
| 20 | 27 | 10 | 59 | 0 | 280 |

Where the correspondences are, in 30 px bins from the mask centroid:

| τ | 0-30 | 30-60 | 60-90 | 90-120 | 120-150 | 150+ |
| --- | --- | --- | --- | --- | --- | --- |
| 3 | 209 | 516 | 801 | 853 | 556 | 233 |
| 5 | 369 | 856 | 1266 | 1434 | 964 | 382 |
| 8 | 472 | 1078 | 1593 | 1859 | 1241 | 562 |
| 12 | 499 | 1152 | 1742 | 2066 | 1447 | 660 |
| 15 | 509 | 1178 | 1765 | 2128 | 1525 | 700 |
| 20 | 520 | 1191 | 1801 | 2212 | 1633 | 761 |

and the fraction of the mask's area, band by band, that falls inside the convex
hull of the correspondences:

| τ | 0-30 | 30-60 | 60-90 | 90-120 | 120-150 | 150+ |
| --- | --- | --- | --- | --- | --- | --- |
| 3 | 0.633 | 0.535 | 0.359 | 0.187 | 0.080 | 0.020 |
| 5 | 0.836 | 0.754 | 0.574 | 0.331 | 0.148 | 0.037 |
| 8 | 0.915 | 0.856 | 0.690 | 0.434 | 0.218 | 0.065 |
| 12 | 0.952 | 0.906 | 0.761 | 0.502 | 0.267 | 0.081 |
| 15 | 0.959 | 0.914 | 0.776 | 0.528 | 0.284 | 0.090 |
| 20 | 0.964 | 0.924 | 0.803 | 0.568 | 0.313 | 0.099 |

**Most of the periphery is extrapolated at every τ.** Beyond 120 px the hull
never covers a third of the mask, and beyond 150 px it never covers a tenth. At
τ ≥ 12 the coverage crosses 50 per cent inside the 90-to-150 band, which is
what `P-5` predicted; at τ ≤ 8 it crosses earlier still, in 60-to-90.

## Step 4 on `DB1_B` — `R-1`, the held-out residual

Root mean square of the held-out residual, in pixels, pooled over all pairs.
The row `n` is the number of held-out points in each band.

**τ = 8**

| model | 0-30 | 30-60 | 60-90 | 90-120 | 120-150 | 150+ |
| --- | --- | --- | --- | --- | --- | --- |
| M0 translation | 20.45 | 25.45 | 34.29 | 45.62 | 55.46 | 64.55 |
| M1 rigid | 4.03 | 3.95 | 4.04 | 4.23 | 4.33 | 4.78 |
| M2 similarity | 4.00 | 3.95 | 4.05 | 4.20 | 4.33 | 4.72 |
| M3 rigid + c1 | 4.00 | 3.95 | 4.05 | 4.20 | 4.33 | 4.72 |
| M4 + c3 | 4.01 | 3.98 | 4.09 | 4.20 | 4.40 | 5.23 |
| M5 + c2 | 4.02 | 4.01 | 4.10 | 4.20 | 4.36 | 5.00 |
| M6 + c5 | 4.04 | 4.04 | 4.13 | 4.38 | 5.09 | 14.81 |
| M7 affine | **3.90** | **3.68** | **3.77** | **3.96** | 4.49 | 4.72 |
| M8 λ=0 | 4.56 | 4.33 | 4.27 | 4.54 | 4.79 | 5.31 |
| M8 λ=10³ | 4.08 | 3.76 | 3.85 | 4.05 | 4.38 | 4.89 |
| M8 λ=10⁴ | **3.70** | **3.42** | **3.54** | **3.72** | **4.15** | **4.46** |
| n | 468 | 1074 | 1584 | 1846 | 1236 | 560 |

**τ = 15**

| model | 0-30 | 30-60 | 60-90 | 90-120 | 120-150 | 150+ |
| --- | --- | --- | --- | --- | --- | --- |
| M0 | 19.68 | 29.09 | 40.61 | 53.28 | 63.70 | 70.49 |
| M1 | 4.90 | 5.02 | 5.11 | 5.67 | 6.31 | 6.72 |
| M2 | 4.83 | 5.01 | 5.16 | 5.70 | 6.26 | 6.57 |
| M3 | 4.83 | 5.01 | 5.16 | 5.70 | 6.26 | 6.57 |
| M4 | 4.84 | 5.06 | 5.17 | 5.71 | 6.27 | 6.99 |
| M5 | 4.85 | 5.09 | 5.17 | 5.70 | 6.25 | 6.81 |
| M6 | 4.90 | 5.11 | 5.20 | 5.75 | 7.13 | 10.37 |
| M7 | 4.72 | 4.76 | 4.88 | 5.50 | 6.32 | 6.54 |
| M8 λ=0 | 5.67 | 5.66 | 5.71 | 6.59 | 7.02 | 8.16 |
| M8 λ=10⁴ | **4.59** | **4.53** | **4.71** | **5.52** | **6.10** | **6.53** |
| n | 509 | 1178 | 1765 | 2128 | 1525 | 700 |

The full six-τ table is in the run's own output; the ordering is what matters
and it is stable, so the two above are given in full and the rest is reported
through the paired differences below. At τ = 3 the residuals are near 2 px and
at τ = 20 near 8; the pairing radius moves the absolute level by a factor of
four.

### The paired differences, which are what the comparison rests on

Every correspondence is held out exactly once under every model, so the models
can be compared point by point rather than through two pooled root-mean-squares.
Each entry is the mean of `d_a − d_b` in pixels with its standard error; a
negative entry means the first model is closer.

**τ = 15**

| contrast | 0-30 | 30-60 | 60-90 | 90-120 | 120-150 | 150+ |
| --- | --- | --- | --- | --- | --- | --- |
| M2 − M3 | +0.000 ±0.000 | +0.000 ±0.000 | +0.000 ±0.000 | −0.000 ±0.000 | −0.000 ±0.000 | +0.000 ±0.000 |
| M3 − M1 | −0.061 ±0.026 | −0.018 ±0.020 | +0.006 ±0.021 | −0.037 ±0.022 | −0.113 ±0.030 | −0.202 ±0.049 |
| M4 − M1 | −0.065 ±0.029 | +0.017 ±0.027 | +0.009 ±0.026 | −0.023 ±0.023 | −0.109 ±0.036 | +0.065 ±0.088 |
| **M4 − M5** | −0.014 ±0.007 | −0.033 ±0.006 | −0.000 ±0.004 | +0.003 ±0.003 | **+0.017 ±0.006** | **+0.115 ±0.021** |
| M5 − M1 | −0.051 ±0.031 | +0.050 ±0.029 | +0.009 ±0.026 | −0.026 ±0.023 | −0.126 ±0.035 | −0.050 ±0.077 |
| **M6 − M4** | **+0.057 ±0.021** | +0.049 ±0.021 | +0.027 ±0.013 | +0.043 ±0.013 | +0.175 ±0.072 | **+1.014 ±0.250** |
| M7 − M1 | −0.181 ±0.049 | −0.294 ±0.044 | −0.301 ±0.040 | −0.355 ±0.043 | −0.241 ±0.060 | −0.360 ±0.092 |
| **M7 − M4** | −0.116 ±0.043 | −0.312 ±0.042 | −0.310 ±0.040 | −0.332 ±0.040 | −0.132 ±0.057 | −0.425 ±0.097 |
| M8 λ=0 − M1 | +0.496 ±0.126 | +0.289 ±0.084 | +0.254 ±0.073 | +0.293 ±0.076 | +0.131 ±0.098 | +0.515 ±0.168 |
| **M8 λ=10⁴ − M1** | −0.489 ±0.084 | −0.650 ±0.057 | −0.587 ±0.048 | −0.490 ±0.053 | −0.598 ±0.072 | −0.642 ±0.123 |
| M8 λ=10⁴ − M7 | −0.308 ±0.070 | −0.355 ±0.038 | −0.286 ±0.034 | −0.135 ±0.036 | −0.357 ±0.052 | −0.283 ±0.090 |

**τ = 8**, the same contrasts, abbreviated to the three that decide the
question:

| contrast | 0-30 | 30-60 | 60-90 | 90-120 | 120-150 | 150+ |
| --- | --- | --- | --- | --- | --- | --- |
| M4 − M5 | −0.008 ±0.006 | −0.017 ±0.005 | +0.000 ±0.003 | +0.009 ±0.003 | +0.023 ±0.007 | +0.120 ±0.024 |
| M7 − M4 | −0.115 ±0.043 | −0.291 ±0.037 | −0.324 ±0.036 | −0.328 ±0.034 | −0.085 ±0.055 | −0.413 ±0.102 |
| M8 λ=10⁴ − M1 | −0.429 ±0.071 | −0.581 ±0.048 | −0.597 ±0.044 | −0.655 ±0.043 | −0.497 ±0.063 | −0.587 ±0.110 |

**τ = 3**, where the correspondences are tightest:

| contrast | 0-30 | 30-60 | 60-90 | 90-120 | 120-150 | 150+ |
| --- | --- | --- | --- | --- | --- | --- |
| M4 − M5 | −0.011 ±0.006 | −0.013 ±0.004 | −0.003 ±0.002 | +0.007 ±0.004 | +0.033 ±0.011 | +0.115 ±0.028 |
| M4 − M1 | −0.039 ±0.022 | +0.050 ±0.021 | −0.002 ±0.019 | +0.012 ±0.020 | +0.079 ±0.039 | +0.266 ±0.091 |
| M7 − M1 | −0.043 ±0.036 | +0.050 ±0.027 | −0.044 ±0.026 | −0.070 ±0.028 | −0.037 ±0.040 | −0.049 ±0.058 |
| M8 λ=10⁴ − M1 | −0.112 ±0.052 | +0.006 ±0.035 | −0.101 ±0.031 | −0.099 ±0.033 | −0.127 ±0.047 | −0.086 ±0.066 |

### What the answer to the question is, on `DB1_B`

**A low-parameter radial warp does not predict a held-out correspondence better
than the conventional families, at any radius, at any τ.**

- Against rigid, the whole radial family is worth **at most 0.2 px** and in the
  outermost band M4 is not better than rigid at all. What little the family
  buys is the term `c1`, which is a similarity scale and is therefore not a
  radial deformation but a change of scale under another name.
- **Affine beats the radial cubic in every band**, by 0.09 to 0.43 px, and by
  more than five standard errors in four of the six bands at τ = 15.
- **A heavily smoothed spline beats everything**, by 0.49 to 0.65 px against
  rigid at τ = 15, including in the outermost band where by construction it is
  extrapolating from a hull that covers under a tenth of the area.
- At **τ = 3** the picture changes in one way that matters: the extra
  parameters stop paying. Affine is within two standard errors of rigid in five
  of the six bands, the spline's advantage shrinks to about 0.1 px, and M4 is
  **worse** than rigid in the outermost band by 0.27 ± 0.09. The tighter the
  correspondence, the less any model beyond rigid is worth.

The size of all of this is worth stating in the units of the thing: the largest
model-to-model difference in the tables above is **0.65 px, which is
0.033 mm**, against residuals of 4 to 7 px. No model in the list explains the
residual; they differ in the third significant figure of it.

## `R-2` — inside and outside the fitting fold's hull

Held-out RMS at τ = 15, given as inside/outside the convex hull of the fold the
model was fitted on.

| model | 0-30 | 30-60 | 60-90 | 90-120 | 120-150 | 150+ |
| --- | --- | --- | --- | --- | --- | --- |
| M1 | 4.88/5.64 | 4.84/7.14 | 4.81/6.29 | 4.81/6.88 | 4.90/7.06 | 4.46/7.15 |
| M4 | 4.82/5.53 | 4.87/7.25 | 4.83/6.48 | 4.80/6.97 | 4.78/7.05 | 4.40/7.48 |
| M5 | 4.83/5.61 | 4.90/7.28 | 4.83/6.49 | 4.79/6.96 | 4.77/7.03 | 4.38/7.27 |
| M7 | 4.72/4.82 | 4.64/6.26 | 4.56/6.16 | 4.43/6.94 | 4.48/7.25 | 4.02/7.01 |
| M8 λ=10⁴ | 4.59/4.66 | 4.37/6.38 | 4.34/6.09 | 4.36/7.05 | 4.22/7.04 | 4.04/7.00 |
| n inside/outside | 497/12 | 1101/77 | 1448/317 | 1332/796 | 591/934 | 135/565 |

**The band is not the variable that matters; the hull is.** Inside the hull the
residual is 4.2 to 4.9 px and **it does not grow with radius at all** — for
every model the outermost band's inside-hull residual is the smallest in the
row. Outside the hull it is 5.5 to 7.5 px everywhere. The apparent growth of
`R-1` with radius in the earlier table is the changing mixture: at 0-30 nearly
every held-out point is interpolated and at 150+ four in five are extrapolated.

## `R-3` — the fit residual, for contrast

RMS of the fit residual at τ = 15, on the points the model was fitted to:

| model | 0-30 | 30-60 | 60-90 | 90-120 | 120-150 | 150+ |
| --- | --- | --- | --- | --- | --- | --- |
| M1 | 4.71 | 4.75 | 4.77 | 5.29 | 5.93 | 6.30 |
| M4 | 4.60 | 4.65 | 4.62 | 5.15 | 5.64 | 5.76 |
| M6 | 4.60 | 4.58 | 4.59 | 5.12 | 5.57 | **5.49** |
| M7 | 4.45 | 4.35 | 4.27 | 4.72 | 5.45 | 5.67 |
| M8 λ=0 | **0.00** | **0.00** | **0.00** | **0.00** | **0.00** | **0.00** |
| M8 λ=10⁴ | 3.52 | 3.26 | 3.18 | 3.36 | 3.56 | 3.43 |

**The two orderings are different, and one of them is a mirage.** By fit
residual M6 is the best of the parametric family in the outermost band, 5.49
against M4's 5.76; by held-out residual in the same band it is the worst by a
wide margin, 10.37 against 6.99. The spline at λ = 0 has a fit residual of
exactly zero in every band and the largest held-out residual of the whole
spline family.

## `R-4` — the two radial coefficients, and their error

M4 fitted per pair at τ = 15, 280 pairs. The estimation error covariance is
estimated per pair by jackknife over that pair's own correspondences, and the
two covariances are reported apart, as the brief requires, because they are the
same size.

| | c1 | c3 |
| --- | --- | --- |
| mean over the 280 pairs | −0.415 | −2.427 |
| standard deviation over the 280 pairs | 7.415 | 41.330 |

| covariance | var c1 | cov | var c3 | correlation |
| --- | --- | --- | --- | --- |
| observed, between pairs | 55.0 | −255.8 | 1708.1 | **−0.835** |
| estimation error, mean of the jackknives | 55.9 | −265.0 | 1650.8 | **−0.873** |
| observed / error, variance ratio | **0.984** | | **1.035** | |

**The cloud is the error.** The observed spread of `(ĉ1, ĉ3)` across 280 pairs
is 98 per cent of the estimation error variance in `c1` and 104 per cent in
`c3`; there is no room left for a between-pair signal. The anti-correlation the
brief warned would look like a law is present at −0.835 observed and −0.873 in
the error, against the −0.89 the brief's own simulation predicted, and it is a
property of the fit, not of the finger.

This is the answer to the brief's instruction about plotting: an error ellipse
drawn on these axes covers the cloud.

## `R-5` — the similarity scale against the contact area

`ŝ` from M2 at τ = 15, against `sqrt(A_j/A_i)` from the two masks.

| | value |
| --- | --- |
| pairs | 280 |
| `ŝ` | 0.96096 to 1.05122 |
| `sqrt(A_j/A_i)` | 0.719 to 1.507 |
| regression slope | **0.0224 ± 0.0069** |
| intercept | 0.9746 |
| correlation | **0.191** |
| residual scatter of `ŝ` about the line | 0.0142 |

**The slope is positive and three standard errors from zero, and it is 45 times
smaller than one.** If the fitted scale were the linear size ratio of the two
contact patches, the slope would be 1 and the correlation near it; measured, the
contact-area ratio accounts for 3.6 per cent of the variance of `ŝ`, and the
mask area ranges over a factor of 2.3 while `ŝ` ranges over 9 per cent.

So the prediction as worded is confirmed and the reading behind it is not: `ŝ`
is not the contact-area ratio. What the other 96 per cent of its variance is,
this record does not say.

## Step 5 — consistency across the eight impressions

For each finger the 28 pairwise coefficient sets were fitted to the incidence
model `c(i→j) = c_j − c_i`, 8 unknowns of rank 7, 21 degrees of freedom, and
the null was calibrated per finger by parametric bootstrap from that finger's
own jackknife standard errors — 400 draws each.

| finger | c1 observed | null | ratio | c3 observed | null | ratio | rotation observed | null | ratio |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 101 | 8.58 | 8.46 | 1.01 | 54.1 | 51.9 | 1.04 | 19.09 | 0.88 | 21.8 |
| 102 | 6.44 | 8.66 | 0.74 | 38.1 | 42.3 | 0.90 | 10.18 | 0.56 | 18.1 |
| 103 | 9.23 | 10.93 | 0.85 | 45.5 | 62.6 | 0.73 | 53.61 | 1.13 | 47.6 |
| 104 | 4.95 | 6.09 | 0.81 | 24.9 | 30.5 | 0.82 | 37.12 | 0.59 | 63.0 |
| 105 | 6.96 | 3.89 | **1.79** | 52.2 | 15.1 | **3.46** | 34.38 | 0.45 | 77.2 |
| 106 | 6.40 | 6.01 | 1.06 | 26.0 | 23.6 | 1.11 | 39.93 | 0.48 | 83.0 |
| 107 | 3.91 | 4.77 | 0.82 | 23.0 | 23.1 | 0.99 | **0.99** | 0.57 | 1.7 |
| 108 | 3.67 | 3.58 | 1.03 | 23.5 | 16.3 | 1.45 | **0.89** | 0.44 | 2.1 |
| 109 | 7.99 | 8.22 | 0.97 | 60.0 | 53.0 | 1.13 | 45.80 | 0.89 | 51.7 |
| 110 | 5.37 | 8.32 | 0.65 | 25.4 | 41.8 | 0.61 | 43.67 | 0.67 | 63.7 |

**For the radial coefficients the test finds nothing.** Nine of the ten fingers
have `c1` and `c3` residuals at or below the noise the correspondences
themselves imply; only finger 105 stands out, at 1.8 and 3.5 times. Whatever
per-impression radial deformation exists, this test cannot see it above the
estimation error, which `R-4` has already shown to be the whole of the observed
spread.

**For the rotation the test finds something, and it is not deformation.** Eight
of the ten fingers have a rotation residual 18 to 83 times the noise, while two
— 107 and 108 — are at 1.7 and 2.1, meaning their 28 alignments are mutually
consistent to about a degree. A rotation composes additively, so a residual of
this size is a statement that some of the 28 pairwise alignments disagree with
the rest. Refitting the same incidence model robustly, per pair, gives a median
absolute residual of **0.67 degrees**, with **248 of the 280 pairs within 5
degrees and 32 outside it**. So about **11 per cent of the RANSAC alignments
are wrong**, and the eight fingers' large residuals are three or four bad pairs
each rather than a deformation.

This is what §7 was put in the brief to catch, and it caught something larger
than what it was aimed at.

## Step 6 — the distortion-free core

M1 fitted only on correspondences inside ρ, then evaluated on the
correspondences outside it, at τ = 15:

| ρ | 30-60 | 60-90 | 90-120 | 120-150 | 150+ |
| --- | --- | --- | --- | --- | --- |
| 40 | 5.45 | 7.37 | 9.18 | 12.13 | 14.02 |
| 60 | — | 5.76 | 7.34 | 8.65 | 10.65 |
| 80 | — | 5.89 | 6.75 | 8.04 | 9.33 |
| 100 | — | — | 6.19 | 7.16 | 7.90 |
| 120 | — | — | — | 6.66 | 7.42 |

**The residual rises from the smallest radius tested, and there is no ρ\* where
it is flat.** At ρ = 40 it more than doubles between the first band available
and the last; at ρ = 120 it still rises, 6.66 to 7.42, over the last 30 px of
reach. Read down a column instead of across a row and the same thing appears
from the other side: in the 120-150 band the residual falls monotonically from
12.13 to 6.66 as the fitting radius grows, so every extra pixel of fitting reach
still buys accuracy at 120 px.

Of the brief's two outcomes this is the second: **no distortion-free core is
visible in this measurement.** The brief attributes a remark to Bazen and
Gerez; that paper has not been read here and this record therefore states only
its own measurement, with two qualifications of its own. `R-2` has already
shown that most of this curve is a hull effect rather than a radius effect. And
the test cannot separate a deformation that grows with radius from an
extrapolation error that grows with distance from the fitted points, because
here the two grow together by construction.

## The checks that could have failed

**`P-3`, the implementation check.** After the iteration count was raised to 60
for the reason given in the Method, the two parameterisations of one model agree
to `max |ŝ − (1 + ĉ1/r_s)| = 1.3·10⁻⁶` over 280 pairs and
`max |RMS_{M2} − RMS_{M3}| = 1.6·10⁻⁵ px`, and their paired held-out difference
is 0.000 ± 0.000 px in every band. **It passes.**

**The shuffle control.** The whole pipeline run on 45 impostor pairs —
impression 1 of each finger against impression 1 of each other finger — at
τ = 15:

| | 0-30 | 30-60 | 60-90 | 90-120 | 120-150 | 150+ |
| --- | --- | --- | --- | --- | --- | --- |
| impostor, M1 | 8.37 | 8.82 | 8.55 | 8.73 | 8.71 | 8.19 |
| genuine, M1 | 4.90 | 5.02 | 5.11 | 5.67 | 6.31 | 6.72 |
| impostor, M8 λ=10⁴ | 9.07 | 9.67 | 9.39 | 9.78 | 9.99 | 9.51 |
| genuine, M8 λ=10⁴ | 4.59 | 4.53 | 4.71 | 5.52 | 6.10 | 6.53 |

**It passes, and it passes by less than the brief expected.** The impostor
residual is worse at every radius and for every model, but by a factor of 1.2
to 1.8, not by an order. Two further numbers say why that matters. All 45
impostor pairs produced at least 8 mutual correspondences within 15 px, with a
median of **21 against the genuine median of 26** — so at τ = 15 **the number
of correspondences barely distinguishes a genuine pair from an impostor one**,
and only the residual does. And the impostor residual is flat in radius, 8.2 to
8.8 across every band, which is what a chance pairing over a bounded image
should give.

The consequence for everything above is that at large τ a genuine pairing is a
mixture, and the models are being asked to fit that mixture. It is the reason
the τ sweep is in the brief, and the reason the τ = 3 column of the paired
differences is reported beside τ = 15 rather than instead of it.

**The mask check.** Reported in Step 1: it passes.

**`N` per pair.** Reported in Step 2, with the exclusions: 100 pairs excluded at
τ = 3, 37 at τ = 5, 6 at τ = 8, none above.

## The predictions, scored on `DB1_B`

| | prediction | outcome |
| --- | --- | --- |
| `P-1` | M4 beats M5 in 120-150 and 150+ | **FAILS.** M4 − M5 is +0.017 ± 0.006 and **+0.115 ± 0.021** at τ = 15, and +0.023 ± 0.007 and +0.120 ± 0.024 at τ = 8. M5, the model with the even power the prediction's grounds called unphysical, is the better predictor in both outer bands at every τ tested. |
| `P-2` | M6 worse than M4 in the outermost band, better in 0-30 | **HALF.** Worse in the outermost band, +1.014 ± 0.250, decisively. But **not better in 0-30**: +0.057 ± 0.021, worse by nearly three standard errors. |
| `P-3` | M2 and M3 identical, `ŝ = 1 + ĉ1/r_s` pair by pair | **PASSES**, at 60 iterations, to 1.3·10⁻⁶. It did not pass at 15, and the Method records what was changed and why. |
| `P-4` | `ŝ` correlates with `sqrt(A_j/A_i)`, slope distinguishable from zero | **PASSES as worded, and refutes the reading behind it.** Slope 0.0224 ± 0.0069, three standard errors from zero and forty-five from one. |
| `P-5` | hull coverage below 50% somewhere in 90-150 px | **PASSES**, at τ ≥ 12; at τ ≤ 8 the crossing is earlier still. |
| `P-6` | FRE ordering ≠ `R-1` ordering; λ=0 has the smallest FRE and a large outer `R-1` | **PASSES.** λ=0's FRE is exactly 0 in every band and its held-out residual is +0.50 ± 0.13 px worse than rigid in 0-30; M6 is best by FRE and worst by `R-1` in the outermost band. |

Nothing in the model list was changed after these were scored, and the same
six are scored again on `DB1_A` below.

## One thing generated by looking

**A post-hoc filter, and it is labelled as such because it was not
pre-registered.** Step 5 found that about 11 per cent of the pairwise
alignments are mutually inconsistent. Removing them — keeping the 248 pairs
whose rotation is within 5 degrees of the robust incidence fit — and repeating
the whole model comparison changes the residual level but not one conclusion:

| contrast, τ = 15, consistent subset | 0-30 | 60-90 | 120-150 | 150+ |
| --- | --- | --- | --- | --- |
| M4 − M5 | −0.015 ±0.007 | +0.001 ±0.003 | +0.016 ±0.005 | +0.090 ±0.019 |
| M4 − M1 | −0.061 ±0.028 | −0.002 ±0.025 | −0.136 ±0.036 | −0.016 ±0.082 |
| M7 − M4 | −0.130 ±0.045 | −0.349 ±0.040 | −0.153 ±0.057 | −0.456 ±0.093 |
| M8 λ=10⁴ − M1 | −0.572 ±0.085 | −0.662 ±0.049 | −0.691 ±0.072 | −0.837 ±0.123 |

`P-1` still fails, `P-2` still half-fails, affine still beats the radial cubic
everywhere and the smoothed spline still beats everything. What the filter does
change is the translation-only model, whose residual falls from 19.7 to 14.5 px
in the innermost band, which is the signature of the bad alignments it removed.

## `DB1_A` — the confirmation

Run after the sections above were written, with the same script, the same
parameters and the same seed: 800 images, 100 fingers, **2800 genuine pairs**,
ten times the exploratory set. RANSAC found an alignment for every pair.

### Step 1 and step 2 repeat

| | `DB1_B` | `DB1_A` |
| --- | --- | --- |
| minutiae per image | 19 to 76 | 11 to 96 |
| mask area | 39 552 to 97 152 px² | 28 224 to 106 496 px² |
| equivalent radius | 112.2 to 175.9, mean 153.4 | 94.8 to 184.1, mean 150.8 |
| within-finger area spread | 5267 to 15 026 px² | 4766 to 23 153 px² |
| `.qm >= 1` against `.lcm == 0` | ratio 0.9673 | ratio 0.9683 |

| τ | median N | excluded, `DB1_B` | excluded, `DB1_A` |
| --- | --- | --- | --- |
| 3 | 11 | 100 of 280 | 935 of 2800 |
| 5 | 19 | 37 | 346 |
| 8 | 25 | 6 | 50 |
| 12 | 28 | 0 | 7 |
| 15 | 29 | 0 | 6 |
| 20 | 30 | 0 | 2 |

Hull coverage by band at τ = 15: 0.967, 0.922, 0.784, 0.532, 0.286, 0.081 —
the same curve as `DB1_B` to within 0.01 in every band, and the same crossing
of 50 per cent inside 90-to-150 px.

### `R-1` on `DB1_A`

**τ = 15**, held-out RMS in pixels:

| model | 0-30 | 30-60 | 60-90 | 90-120 | 120-150 | 150+ |
| --- | --- | --- | --- | --- | --- | --- |
| M0 | 20.77 | 27.71 | 38.42 | 52.84 | 58.65 | 63.97 |
| M1 | 4.88 | 4.81 | 5.12 | 5.88 | 6.66 | 7.08 |
| M2 = M3 | 4.88 | 4.81 | 5.15 | 5.87 | 6.60 | 7.04 |
| M4 | 4.92 | 4.87 | 5.20 | 5.90 | 6.69 | 7.44 |
| M5 | 4.94 | 4.90 | 5.20 | 5.89 | 6.65 | 7.28 |
| M6 | 4.95 | 4.95 | 5.23 | 6.00 | 7.76 | 10.25 |
| M7 | 4.80 | 4.71 | 4.97 | 5.72 | 6.61 | 7.18 |
| M8 λ=0 | 5.75 | 5.59 | 5.90 | 6.77 | 7.62 | 8.38 |
| M8 λ=10⁴ | **4.64** | **4.53** | **4.86** | **5.63** | **6.49** | **7.06** |
| n | 5315 | 14 630 | 19 450 | 20 628 | 16 364 | 6586 |

The paired differences, τ = 15, with ten times the sample and therefore about a
third of the standard error:

| contrast | 0-30 | 30-60 | 60-90 | 90-120 | 120-150 | 150+ |
| --- | --- | --- | --- | --- | --- | --- |
| M2 − M3 | +0.000 ±0.000 | −0.000 ±0.000 | +0.000 ±0.000 | +0.000 ±0.000 | +0.000 ±0.000 | −0.000 ±0.000 |
| M3 − M1 | +0.001 ±0.007 | +0.001 ±0.005 | +0.002 ±0.006 | −0.051 ±0.007 | −0.120 ±0.010 | −0.129 ±0.019 |
| **M4 − M1** | **+0.017 ±0.009** | **+0.037 ±0.007** | **+0.026 ±0.008** | −0.030 ±0.008 | −0.064 ±0.013 | **+0.085 ±0.031** |
| **M4 − M5** | −0.019 ±0.002 | −0.021 ±0.002 | −0.001 ±0.001 | +0.005 ±0.001 | **+0.018 ±0.002** | **+0.088 ±0.007** |
| M6 − M4 | +0.031 ±0.008 | +0.053 ±0.006 | +0.024 ±0.004 | +0.062 ±0.005 | +0.178 ±0.027 | +0.826 ±0.072 |
| M7 − M4 | −0.118 ±0.012 | −0.184 ±0.010 | −0.280 ±0.011 | −0.323 ±0.013 | −0.258 ±0.017 | −0.318 ±0.033 |
| M8 λ=10⁴ − M1 | −0.424 ±0.023 | −0.436 ±0.015 | −0.462 ±0.015 | −0.548 ±0.018 | −0.580 ±0.023 | −0.595 ±0.042 |

and at **τ = 3**, where the correspondences are tightest:

| contrast | 0-30 | 30-60 | 60-90 | 90-120 | 120-150 | 150+ |
| --- | --- | --- | --- | --- | --- | --- |
| M4 − M1 | +0.004 ±0.007 | +0.028 ±0.005 | +0.021 ±0.005 | +0.019 ±0.006 | **+0.105 ±0.016** | **+0.399 ±0.045** |
| M4 − M5 | −0.008 ±0.002 | −0.011 ±0.001 | +0.001 ±0.001 | +0.008 ±0.001 | +0.044 ±0.006 | +0.169 ±0.019 |
| M7 − M1 | −0.031 ±0.010 | −0.046 ±0.007 | −0.051 ±0.008 | −0.041 ±0.010 | +0.020 ±0.015 | +0.062 ±0.032 |
| M8 λ=10⁴ − M1 | −0.098 ±0.015 | −0.098 ±0.009 | −0.100 ±0.009 | −0.107 ±0.011 | −0.040 ±0.017 | +0.022 ±0.035 |

**Every conclusion of the `DB1_B` sections survives, and one of them sharpens.**
Affine beats the radial cubic in all six bands, the smoothed spline beats
everything, and the spline at λ = 0 is worse than rigid. What sharpens is the
radial family itself: with 2800 pairs, **M4 is now worse than rigid in the three
inner bands** by two to five standard errors, and at τ = 3 it is worse than
rigid in five of six bands and by 0.40 ± 0.05 px in the outermost. On the
tuning set that was a null result; on the evaluation set the cubic term is a
cost, not a gain.

### The rest of the outputs on `DB1_A`

| | `DB1_B` | `DB1_A` |
| --- | --- | --- |
| `P-3`, max &#124;ŝ − (1+ĉ1/r_s)&#124; | 1.3·10⁻⁶ | **2.4·10⁻⁷** |
| `R-5` slope | 0.0224 ± 0.0069 | **0.0072 ± 0.0021** |
| `R-5` correlation | 0.191 | 0.065 |
| `R-4` observed/error variance, c1 | 0.984 | 0.911 |
| `R-4` observed/error variance, c3 | 1.035 | 0.668 |
| `R-4` correlation, observed / error | −0.835 / −0.873 | −0.806 / −0.868 |
| step 5, c1 ratio | median 1.01, one finger above 1.5 | **median 0.82, none above 1.5** |
| step 5, c3 ratio | median 1.04, one finger above 1.5 | **median 0.81, none above 1.5** |
| step 5, rotation ratio | median 43, 8 of 10 above 2 | **median 46, 75 of 100 above 2** |
| rotation incidence, median &#124;residual&#124; | 0.67° | 0.59° |
| alignments outside 5° | 32 of 280, 11.4% | **340 of 2794, 12.2%** |
| impostor pairs, median N | 21 against genuine 26 | **21 against genuine 29** |
| impostor M1 residual | 8.2 to 8.8 px | 7.9 to 8.8 px |

Step 6 repeats without a flat region: at ρ = 40 the held-out residual runs
5.18 → 12.17 px from the 30-60 band to 150+, and at ρ = 120 it still rises,
7.07 → 7.82. `R-2` repeats too — inside the fitting fold's hull the residual is
4.4 to 5.7 px at every radius and outside it 5.6 to 7.8.

Three of these deserve a sentence.

- **`R-5` shrinks with the larger sample.** The slope falls from 0.0224 to
  0.0072 while staying 3.4 standard errors from zero, and the correlation falls
  from 0.19 to 0.065. So `P-4` is confirmed twice over as worded, and what it
  was worded to test is refuted more firmly than on the tuning set: the fitted
  similarity scale is not the contact-area ratio, and on 2800 pairs the area
  ratio accounts for 0.4 per cent of its variance.
- **`R-4` goes past "no signal" into "the error estimate is too large".** On
  `DB1_A` the observed variance of `ĉ3` is 0.67 of the jackknife's estimate of
  the error variance, which cannot happen if the jackknife is unbiased and a
  real between-pair spread exists on top of it. Either the jackknife
  over-estimates the error of this estimator — which is what a jackknife tends
  to do for a nonlinear one — or the estimator is shrunk toward zero. Either
  way there is no between-pair signal to find, which is the same conclusion as
  on `DB1_B` and arrived at from the other side.
- **Step 5 finds nothing in the radial coefficients on any of 100 fingers**,
  and the same rotation inconsistency on three quarters of them. The proportion
  of mis-aligned pairs is the same to within a point: 11.4 per cent on the
  tuning set, 12.2 per cent on the evaluation set.

The post-hoc consistent-rotation subset on `DB1_A` is 2454 of 2800 pairs, and,
as on `DB1_B`, removing the inconsistent pairs changes no conclusion: M7 − M4
runs −0.125 to −0.382 px, M8 λ=10⁴ − M1 runs −0.481 to −0.727, and M4 − M5
stays positive in the two outer bands.

### The predictions, scored again on `DB1_A`

| | outcome on `DB1_A` |
| --- | --- |
| `P-1` | **FAILS**, more sharply. M4 − M5 is +0.018 ± 0.002 in 120-150 and +0.088 ± 0.007 in 150+ at τ = 15, nine and twelve standard errors the wrong way, and +0.044 ± 0.006 and +0.169 ± 0.019 at τ = 3. |
| `P-2` | **HALF**, as before. M6 − M4 is +0.826 ± 0.072 in the outermost band, and +0.031 ± 0.008 in 0-30 — worse, not better, by four standard errors. |
| `P-3` | **PASSES**, to 2.4·10⁻⁷ over 2794 pairs. |
| `P-4` | **PASSES as worded** at 3.4 standard errors, with the slope now 0.0072, a hundred and thirty-nine times smaller than one. |
| `P-5` | **PASSES**: coverage 0.532 in 90-120 and 0.286 in 120-150 at τ = 15. |
| `P-6` | **PASSES**: λ=0 has an exactly zero fit residual and is +0.06 to +0.47 px worse than rigid held out; M6 is best by fit residual in the outermost band and worst by held-out residual there. |

## The answer, on both subsets

**No.** A low-parameter radial warp does not predict a held-out correspondence
better than the conventional families at any radius on either subset. Ranked by
held-out residual, on `DB1_A` at τ = 15:

1. a thin-plate spline smoothed at λ = 10⁴, better than rigid by 0.42 to
   0.60 px;
2. affine, better than rigid by 0.10 to 0.44 px;
3. rigid, similarity and the radial family, indistinguishable from each other to
   within about 0.15 px, with the cubic term costing 0.02 to 0.09 px near the
   centre and in the far periphery;
4. a thin-plate spline unsmoothed, worse than rigid by 0.06 to 0.47 px;
5. translation, worse by an order.

The **by how much** the question asks for is the headline: at τ = 15 the whole
spread from the best model to the worst of the sensible ones is **0.6 px, which
is 0.03 mm**, on residuals of 4.5 to 7 px. Whatever separates two impressions of
one finger at this pairing radius, none of these nine families explains more
than a tenth of it.

Two facts bound how much of that residual is deformation at all. Inside the
fitting fold's convex hull the residual is flat in radius, 4.4 to 5.7 px, and
outside it 5.6 to 7.8 — so most of the apparent growth with radius is
extrapolation, not deformation. And an impostor pairing at the same τ yields a
median of 21 correspondences against a genuine 29, with a residual of 8 px
against 5 — so a genuine correspondence set at τ = 15 is a mixture, and part of
the 4.5 px floor is chance pairs rather than finger.

## Reproducing this

Every command was run on 2026-09-08 against the tree at `b0a35f7` and the image
built from its `Dockerfile`, image id
`sha256:e0ded5a5dcc8f594df58ab904be76605ad26492da834130592091b1348f7c3fc`.
`mindtct` is the tool `MAN-tools.v2` records, at the invocation it freezes:
`mindtct <image.png> <root>`, no flags.

**One process, three mounts, nothing per-minutia leaving it.** `$SP` is a
scratch directory outside the tree, `$SP/out` the only writable one:

    docker run --rm -v "$SP:/sp:ro" -v "$SP/out:/out" \
      -v "$LABDATA/raw:/data/raw:ro" dactyloscopy:dev \
      python /sp/warp.py /data/raw/fvc2002/Dbs/Db1_b DB1_B
    docker run --rm ... python /sp/warp.py /data/raw/fvc2002/Dbs/Db1_a DB1_A

`$LABDATA` resolves as `.env.example` specifies and `MAN-fvc2002.v1`'s
`distribution` block records.

**The parameters, all of them, in one place.**

| what | value |
| --- | --- |
| `r_s` | 269 px |
| mask | `.qm >= 1`, 8 px blocks |
| Huber δ | 3 px |
| IRLS iterations | 60, and 20 for the spline |
| τ | 3, 5, 8, 12, 15, 20 px |
| radial bands | 0-30, 30-60, 60-90, 90-120, 120-150, 150+ px |
| RANSAC | 200 000 quadruples drawn, first 4000 with separations agreeing to 3 px and a source separation above 25 px scored, inlier radius 12 px, 3 Procrustes refinements |
| folds | 5, stratified by radius |
| `N` minimum | 8 |
| spline λ | 0, 10, 10², 10³, 10⁴ |
| core ρ | 40, 60, 80, 100, 120 px |
| jackknife | leave-one-correspondence-out, at τ = 15 |
| step 5 bootstrap | 400 draws per finger |
| impostor pairs | impression 1 of each finger against impression 1 of each other, capped at 300 and sampled with the seed |
| seed | 20260908 |

**The reachable arithmetic, stated so a reader need not read the script.** A
model is `q = R·D(p − c) + t` with `c` the source mask centroid; the radial
`D(v) = v·(1 + Σ c_k r^{k−1}/r_s^k)`, which is why `c1` alone is a similarity;
the fit alternates a weighted Procrustes for `(R, t)` with a linear solve for
the coefficients, under Huber weights recomputed each round.

**The implementation check on synthetic data** — 40 problems with planted
outliers, at 15, 40, 120 and 400 iterations — is a separate script that imports
the same fitters and is what established that the M2-against-M3 disagreement
was iteration count and not algebra.

## What was left unchecked

- **Anything about angles.** `D-3` and `D-4` are open, no angle was read,
  converted or compared, and the correspondence is a distance in pixels and
  nothing else.
- **Which extractor is right.** One extractor was used, by design. Nothing here
  is evidence about `iso-extract`, and `INV-014`'s findings are not carried in.
- **Anything about the anatomical finger.** `r` is measured from the mask
  centroid, which is a property of the press, not of the finger. A finger
  pressed off-centre has a different `r` for the same tissue.
- **The sensor's own optical distortion.** It is common to all impressions of
  one sensor and cancels in every pairwise quantity here. It does not cancel in
  any absolute frame, and no absolute frame is built.
- **Whether any of this matters for matching.** That needs a matcher, a
  protocol and a metric, and none of the three is in scope. No score was
  computed and no `results.json` written.
- **Generalisation beyond `DB1`.** `DB3` and `DB4` exist and were not used;
  `DB2` is excluded by `REF-007` decision 4. One sensor, one image size.
- **The brief's second simulated claim** — that the consistency residual of
  step 5 is 2 to 3 times more sensitive to out-of-class deformation than a fit
  residual. Testing it needs a known out-of-class deformation to inject, and
  none was injected here. What step 5 did detect was mis-alignment, which is
  not what that claim is about.
- **The mis-aligned pairs were detected and not repaired.** The pre-registered
  analysis includes all of them; the post-hoc section removes them and reports
  what changes. No attempt was made to align them correctly.
- **The τ = 3 sample is a different sample.** 100 of the 280 pairs fall below
  `N = 8` there and are excluded, so the τ = 3 column is computed on the 180
  easiest pairs. The selection is reported and not corrected for.
- **The mask is quantised at 8 px**, so the centroid, the area and therefore
  every `r` and every band edge carry that quantisation. Nothing here estimates
  what it costs.
- **Everything outside the model list.** No anisotropic radial term, no
  per-quadrant or per-sector model, no model with a centre fitted rather than
  taken from the mask, and no elastic model other than the spline. The list was
  frozen before looking and was not extended afterwards.
- **The tuning constants of the evaluation were not swept.** Huber δ fixed at
  3 px, five folds, and a coarse λ grid of powers of ten.
