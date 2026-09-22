# INV-018 — The second extractor through the matcher

Date: 2026-09-22

## Numbering

This record takes 018, the next free investigation number after `INV-017`. The
reservation at 001 is explained in `REF-002`.

## Question

`INV-011` measured the frame each extractor reports in, `INV-012` the angle
each reports, `INV-014` how the two differ on the same images. Between them
they measured everything a handing of one tool's minutiae to the other's
matcher would need, and nothing did the handing: `INV-017`'s runs scored
`mindtct`'s templates with `bozorth3`, and `iso-extract`'s were never scored
by anything.

**This record hands `iso-extract`'s templates to `bozorth3` under the same
comparison lists, and reports what each choice in the handing costs.** The
conversion has three named parameters — the half turn of the angle, the
angle's sense, and whether it is snapped to `mindtct`'s grid — plus the
quality byte; each is run every way it can be read, so that the reading the
comparison rests on is a measured choice. The comparison itself is then two
runs beside `INV-017`'s two: same subsets, same lists, same matcher, same
metrics, different extractor.

`D-4`, how the ISO angle and the native `NBIS` angle are related, is open.
The conversion applies the relation `INV-012` measured as a parameter of this
investigation, and F-2 reports what the matcher does under every other. That
is a fact about the matcher and the relation; deciding `D-4` is a
refinement's.

## Method

### The conversion, and what each parameter is

`implementation/library/iso_xyt.py` reads an ISO/IEC 19794-2:2005 template by
the layout `INV-011` F-2 derived — the count at offset 27, six bytes per
minutia from 28 — and writes the four-column `.xyt` file `bozorth3` reads, as
`mindtct` writes it. Each difference between the two conventions is a
parameter with a measured default:

| parameter | default | the fact it applies |
| --- | --- | --- |
| frame | `y_xyt = H − y_image`, x unchanged | `INV-011` F-1, from `xytreps.c`: `mindtct`'s `.xyt` origin is bottom left; `INV-011` F-2, F-3, F-5: `iso-extract`'s template is in the image's own frame |
| `turn_deg` | 180 | `INV-012` F-2: `mindtct` reports a known orientation turned by 178.624° over 648 points; F-3: `iso-extract` by 0.117°; `INV-014`: the same turn on the corpus, 3.20° and 3.52° from exact |
| `sense` | +1 | `INV-012` F-2, F-3: both tools' angles increase the same way |
| `quantise` | none: the ISO byte times 360/256, rounded to a degree | `INV-012` F-7: `mindtct` writes 32 values 11.25° apart, `iso-extract` 256 values 1.40625° apart; F-1 below: `bozorth3` uses an integer degree off the grid |
| `quality` | kept | the ISO quality byte, 0..100, as the fourth column |

The 32 values the `mindtct32` snap uses are computed from `xytreps.c`'s formula
over the 32 direction indices and are the set `INV-002` F-8 lists; a test
holds that.

### The run

`implementation/library/matching.py`, the instrument of `INV-017`, now names
its extractor. For `iso-extract` it writes each image as a binary PGM, runs the
caller at the invocation `MAN-tools.v2` freezes — two arguments, no flags —
after verifying the caller and the library it drives by sha256 against the
manifest, converts the template under the run's parameters, and records the
parameters beside the tool identities. Everything else is `INV-017`'s - the
subset by manifest id with every image verified against its checksum list,
the organisers' index files by digest, both of `bozorth3`'s streams kept, the
per-image minutia count carried - plus what commit `fee8c2f` added after it,
applying `REF-014` decision 5: the three manifests verified before an image
is read. A refusal by the library is carried by image name with its return
code, because an empty template scores 0. The `mindtct` path is unchanged:
run again on `DB1_B` from a clean tree at the revision this record's
`iso-extract` runs were made at, it gives the committed record
`runs/20260922-fvc2002_DB1_B-a6fd834` back score for score and count for
count; that record is listed below with the others.

### The readings

`implementation/library/conversion_checks.py` runs `fvc2002/DB1_B` under the
run's conversion and under five others: no turn; the sense mirrored; the sense
mirrored and no turn, which changes two parameters at once; the angle snapped to
`mindtct`'s 32 values; the quality byte zeroed. It also measures, on a synthetic
pair of templates with no fingerprint in them, three properties of `bozorth3`
the conversion leans on. The command form is `scripts/measure_conversion.sh`;
the aggregate is derived data under `$LABDATA/derived/inv018/`, as `REF-015`
decides.

No prediction was registered in advance; there was no brief. The conversion's
defaults were fixed before the first run and not changed after it.

## F-1 — Three properties of `bozorth3`

On a synthetic pair — forty points on a lattice with angles on and off
`mindtct`'s grid, and the same forty shifted by (3, 2) px — and the same forty
followed by a hundred and twenty points far away that match nothing:

| | score |
| --- | --- |
| the pair as constructed | 499 |
| every probe angle plus one degree | 497 |
| every quality zeroed, both templates | 499 |
| the first 150 of 160, the forty matching ones first | 267 |
| all 160, the forty matching at quality 50, the far ones at 90 | 174 first, 182 last |
| all 160, the forty matching at quality 90, the far ones at 50 | 267 first, 267 last |

So: an integer angle off the 32-value grid is accepted and enters the score;
the quality column does not enter the score below the cap; and above the cap
of 150 that `MAN-tools.v2` records, the minutiae kept are the 150 of highest
quality, whatever their order in the file — when the forty that match are the
low-quality ones, the hundred and twenty far ones all survive and only thirty
of the forty do, and the score falls to 174 or 182 by which thirty the tie
leaves in; when the forty are the high-quality ones, all survive and the score
is the first-150 score. The `mindtct` fixture in
`MAN-tools.v2` never reached the cap; one image below does.

## F-2 — What each reading of the conversion costs, on `DB1_B`

280 genuine and 45 impostor pairs, `iso-extract` templates, `bozorth3`:

| reading | `eer@1` | at | `auc@1` | genuine min / median / max | impostor max |
| --- | --- | --- | --- | --- | --- |
| **as run**: turn 180, sense +1, ISO grid, quality kept | **0.021825** = 11/504 | 16 | **0.990913** | 0 / 98 / 300 | 19 |
| no turn | 0.023611 = 17/720 | 17 | 0.989683 | 0 / 97 / 287 | 20 |
| mirrored | 0.299206 = 377/1260 | 7 | 0.811984 | 0 / 30 / 255 | 17 |
| mirrored, no turn | 0.209921 = 529/2520 | 8 | 0.807976 | 0 / 30 / 256 | 16 |
| snapped to `mindtct`'s 32 values | 0.025397 = 8/315 | 14 | 0.986746 | 0 / 83 / 253 | 18 |
| quality zeroed | 0.021825 = 11/504 | 16 | 0.990913 | 0 / 98 / 300 | 19 |

Three things the table measures.

**The half turn barely reaches the number.** Turning every angle by 180° or
not moves `eer@1` from 0.021825 to 0.023611 and the median genuine score from
98 to 97. That is what a matcher that scores the angles between minutiae,
rather than their absolute directions, would do with a turn applied to every
angle in both templates; `bozorth3`'s source was not read here, and the
0.0018 that remains is not explained. What is measured is the consequence:
whatever `D-4` decides about the relation between the two conventions, this
matcher's answer moves by 0.0018 on this subset, and the comparison in F-3
does not rest on it.

**The sense reaches it entirely.** Mirroring the angle takes `eer@1` to 0.30
and the median genuine score from 98 to 30. `INV-012` measured both tools'
angles increasing the same way, on synthetic ridges; here the corpus says the
same, by the only test that matters for matching.

**The grid costs something, and the quality byte nothing.** Snapping the ISO
angle to `mindtct`'s 32 values raises `eer@1` from 0.021825 to 0.025397 and
lowers the median genuine score from 98 to 83; zeroing the quality byte
changes none of the recorded statistics - both metrics, the threshold, every
minimum, median, maximum and zero count - which is what F-1's synthetic pair
shows score for score, no template here reaching the cap.

## F-3 — The comparison

The same lists, the same matcher, the same metrics, the two extractors:

| | `fvc2002/DB1_B` | | `fvc2002/DB1_A` | |
| --- | --- | --- | --- | --- |
| | `mindtct` | `iso-extract` | `mindtct` | `iso-extract` |
| genuine / impostor pairs | 280 / 45 | 280 / 45 | 2800 / 4950 | 2800 / 4950 |
| minutiae, total | 3946 | 3749 | 41 044 | 37 081 |
| minutiae per image | 19 to 76 | 16 to 96 | 11 to 96 | 10 to 155 |
| images at or below the floor of 10 | 0 | 0 | 0 | 1 at 10 |
| images above the cap of 150 | 0 | 0 | 0 | 1 at 155 |
| genuine scores, min / median / max | 0 / 88 / 289 | 0 / 98 / 300 | 0 / 98 / 488 | 0 / 113 / 520 |
| impostor scores, min / median / max | 3 / 8 / 18 | 3 / 6 / 19 | 0 / 8 / 36 | 0 / 7 / 27 |
| genuine pairs scoring 0 | 2 | 1 | 2 | 3 |
| **`eer@1`** | **0.056548** = 19/336 | **0.021825** = 11/504 | **0.032264** = 17887/554400 | **0.025848** = 1433/55440 |
| at threshold | 17 | 16 | 18 | 17 |
| FMR, FNMR there | 1/15, 13/280 | 1/45, 3/140 | 31/990, 93/2800 | 59/2475, 39/1400 |
| **`auc@1`** | **0.970714** = 1359/1400 | **0.990913** = 24971/25200 | **0.987210** = 5473093/5544000 | **0.989112** = 1370909/1386000 |

To full precision, `iso-extract`: `eer@1` 0.021825396825396824 and
0.02584776334776335, `auc@1` 0.9909126984126985 and 0.9891118326118327. The
`mindtct` column is `INV-017` F-1 and the two committed run records. Every
open reading of `eer@1` gives the same value on both `iso-extract` runs, with
no tie at the minimum.

**`iso-extract`'s templates score lower error than `mindtct`'s with
`mindtct`'s own matcher, on both subsets**: `eer@1` 0.0218 against 0.0565 on
the tune set and 0.0258 against 0.0323 on the benchmark set, `auc@1` higher
on both. That is with 5 and 10 per cent fewer minutiae in total, with every
position on the 1.498 px lattice `INV-014` C-1 measured, and with a
conversion this repository wrote. What the number is not: a statement about
either extractor alone. `bozorth3` was written for `mindtct`'s output, and the
conversion is one way of presenting the other tool's minutiae to it; F-2
prices its choices on `DB1_B`: the turn 0.0018 of `eer@1`, the grid 0.0036,
the quality byte nothing, and the sense 0.28 - the one choice the corpus
leaves no room on. The gap between the extractors is 0.035.

## F-4 — The zeros, the floor and the cap

`bozorth3` returns 0 below ten minutiae and truncates to the 150 of highest
quality above 150 (F-1).

| subset, extractor | genuine rows scoring 0, with the two counts |
| --- | --- |
| `DB1_B`, `iso-extract` | row 77, `103_4` `103_8`, 16 and 18 |
| `DB1_A`, `iso-extract` | row 1252, `45_4` `45_7`, 10 and 38; row 2095, `75_5` `75_7`, 11 and 29; row 2096, `75_5` `75_8`, 11 and 37 |

Row 77 of `DB1_B` is a zero for both extractors: `INV-017` F-7 lists the same
pair, `103_4` `103_8`, at 22 and 30 minutiae under `mindtct`. On `DB1_A`
`45_4.tif` has exactly ten minutiae under `iso-extract`, the floor itself, and
one of its two `mindtct` zeros is a zero here too; the other, `45_2` `45_4`,
scores 7. Both zeros of `75_5` are at eleven minutiae. `87_6.tif` has 155
minutiae under `iso-extract`, the one template above the cap on either
subset, so `bozorth3` scored it on its 150 of highest quality; nothing here
measures what the five it dropped would have done. The library refused no
image on either subset, as `INV-014` also found.

## F-5 — The self-comparison

The genuine list of `DB1_A` keeps the comparison between the two
byte-identical files `INV-005` F-6 found, `81_5.tif` and `81_7.tif`. Under
`iso-extract` it scored **520**, the largest genuine score in the subset,
with the next largest at 385; under `mindtct` it was 488 with the next at 318
(`INV-017` F-8).

## F-6 — Two totals `INV-014` measured, met again

`INV-014` counted the minutiae `iso-extract` produced over each subset from
the templates directly: 3749 on `DB1_B`, 37 081 on `DB1_A`. This record's
per-image counts, read from the same templates by the converter, sum to the
same two numbers; and `mindtct`'s 3946 and 41 044 there are the sums of
`INV-017`'s counts. Two instruments written apart, one number.

## Reproducing this

**The instrument is in the tree.** The conversion is
`implementation/library/iso_xyt.py`; the run is `matching.py` with
`run_record.py`, as `INV-017` names them, called with the extractor; the
readings and the matcher properties are
`implementation/library/conversion_checks.py`. The command forms:

    make run-matching LABDATA=/path/to/labdata SUBSET=fvc2002/DB1_B EXTRACTOR=iso-extract
    make run-matching LABDATA=/path/to/labdata SUBSET=fvc2002/DB1_A EXTRACTOR=iso-extract
    docker run --rm -v "<repo>:/work" -v "$LABDATA/raw:/data/raw:ro" \
      -v "$LABDATA/derived:/data/derived" -w /work -e LABDATA=/data \
      dactyloscopy:dev bash scripts/measure_conversion.sh fvc2002/DB1_B

The first two write `results.json` and `observation.json` under
`$LABDATA/derived/matching/<subset>_iso-extract/`; the third writes
`$LABDATA/derived/inv018/fvc2002_DB1_B/conversion.json`. The artefacts this
record is written from - the three run records carrying the revision
`a90b13f`, a clean tree and the module digests; the aggregate carrying no
provenance of its own, which is listed below as unchecked, its "as run"
reading equal value for value to the `DB1_B` `iso-extract` record's:

| | sha256 | bytes |
| --- | --- | --- |
| `DB1_B` `iso-extract` `results.json` | `c8cbc61da4c493bf7a0d6982bfc4c3b16c2a0d90dd31c3d950bca12dc1d1addf` | |
| `DB1_B` `iso-extract` `observation.json` | `cd04e215ea12ca57657dec6fe3be01483443b489cb934720a2c20fbd0165ba6a` | 22 264 |
| `DB1_A` `iso-extract` `results.json` | `5761a4be69e497a18eaf013437c512b33b558f0fb520df8fef6e51c527099e91` | |
| `DB1_A` `iso-extract` `observation.json` | `7e7d84f02efabecfc4b27bab8918dfb05cc87a30c3a5e56189c30ba2e1ab2136` | 473 747 |
| `DB1_B` `mindtct` `results.json` | `ec8267576b04e68b36e80e07966739a16c9cbf1de9fa8673677aa542d0b9db02` | |
| `DB1_B` `mindtct` `observation.json` | `8f71d35d5811696f8ba12e799ef0ee1c13de6071e4ce78198a94b2cdb8d3e203` | 22 252 |
| `conversion.json` | `dea04119193d1609a73be39e1ff843d44550f2d3010b237e838e649baf30b677` | 4 244 |

All three run records are non-provisional; the two `iso-extract` ones name
the conversion they used: `turn_deg` 180, `sense` 1, `quantise` none,
`quality` kept, module `implementation/library/iso_xyt.py`. The `DB1_B`
`mindtct` record's pairs and counts are the committed record
`runs/20260922-fvc2002_DB1_B-a6fd834`'s, row for row; its observation
differs from the committed one only by the `extractor_refusals` field the
observation gained at `8578ce6`, empty here. The `mindtct` figures in F-3
are the committed records, that one and
`runs/20260922-fvc2002_DB1_A-3030b18`.

**The command forms are Python files since 2026-09-22.** The commit `code:
write every command form in Python` replaced `scripts/measure_conversion.sh`
with `scripts/measure_conversion.py`, same argument, so the third command
above is now

    docker run --rm -v "<repo>:/work" -v "$LABDATA/raw:/data/raw:ro" \
      -v "$LABDATA/derived:/data/derived" -w /work -e LABDATA=/data \
      dactyloscopy:dev python3 scripts/measure_conversion.py fvc2002/DB1_B

and the two `make` commands are unchanged. Run from the tree at `d8404f6`
on 2026-09-22, the `DB1_B` `iso-extract` run returns the pairs, counts,
refusals, error-stream rows and sentinel rows of the committed record
`runs/20260922-fvc2002_DB1_B-iso-extract-bozorth3-434035a` unchanged and
reproduces with every score identical, and `conversion.json` is byte for
byte the aggregate in the table above.

**The record digests every module that ran since 2026-09-22.** The three run
records above pin two modules by digest, `matching.py` and `run_record.py`,
and not `iso_xyt.py`, which ran in the two `iso-extract` ones; since the
commit `code: address a subset by its manifest id in every command form` a
record's `code.modules` digests every module under `implementation/library`
loaded when it was composed. A `DB1_B` `iso-extract` run from the tree at
`f96b1eb` on 2026-09-22 lists six, `iso_xyt` among them, and returns the
pairs, counts, refusals, error-stream rows, sentinel rows and both metrics of
the committed record
`runs/20260922-fvc2002_DB1_B-iso-extract-bozorth3-434035a` unchanged.

Every command was run on 2026-09-22 against the tree at `a90b13f` and the
image built from its `Dockerfile`, image id
`sha256:e0ded5a5dcc8f594df58ab904be76605ad26492da834130592091b1348f7c3fc`, on
a 13th Gen Intel Core i9-13900HX, twenty-four cores and thirty-two threads.
`iso-extract` is the caller `MAN-tools.v2` records, at its invocation, with
the library it drives verified by sha256 beside it; `bozorth3` as `INV-017`.

## What was left unchecked

- **The five minutiae the cap dropped from `87_6.tif`.** F-1 establishes
  which are kept; what the dropped ones would have scored was not run.
- **The lattice.** Every `iso-extract` position sits on the 1.498 px lattice
  `INV-014` C-1 measured; whether snapping `mindtct`'s positions to the same
  lattice, or lifting `iso-extract`'s off it, moves a score was not measured.
- **The other direction.** `mindtct`'s `.xyt` was not converted to an ISO
  template and no matcher that reads ISO exists in the image; the comparison
  runs through `bozorth3` alone, which was written for `mindtct`.
- **`-m1`.** `D-1` stays open; both tools were called without it.
- **Why the residual of the turn is 0.0018 and not 0.** F-2 measures that
  `bozorth3` is nearly, not exactly, invariant to a half turn of every angle;
  which part of its scoring keeps the absolute direction was not read from
  its source.
- **The readings on `DB1_A`.** F-2 is `DB1_B` only; the two `DB1_A` runs use
  the conversion as run.
- **Type.** The ISO template carries a minutia type in the top two bits of
  the X word; `.xyt` carries none, and the conversion drops it. `INV-014` C-5
  measured the two tools' type agreement; nothing here uses it.
- **The aggregate's own provenance.** `conversion.json` carries its subset,
  the matcher properties and the readings, and no revision, dirty flag or
  module digest; it was made from the tree the two run records name, and
  the reader has this record's word and the equality of its first reading
  with the `DB1_B` record for it. `REF-015` decision 2 names the aggregate
  by digest; what the aggregate names is not decided.
- **Whether the comparison generalises.** One sensor, `DB1` only, one
  matcher.
