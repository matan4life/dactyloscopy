# INV-017 — What a run record must carry, found by making a run

Date: 2026-09-21

## Numbering

This record takes 017, the next free investigation number after `INV-016`. The
reservation at 001 is explained in `REF-002`.

## Question

`M-1`, the composition of a run record, is open: issue #1, `blocks:kernel`.
`REF-002` says the trailer set of a `run:` commit is a projection of that
composition and is therefore open too, and `runs/README.md` names six things a
record must name — the dataset, the manifests, the protocol, the metric
definition, the seed and the code revision — without saying what form any of
them takes or whether six is enough.

**This record asks what a run record must carry for its headline number to be
re-derived from the record alone, and answers by making a run.** One matching
run of the baseline pair, `mindtct` templates and `bozorth3` scores, is made on
each of two subsets, written down as a candidate record with its observation
beside it, and then read back three ways: the numbers re-derived from the
observation and the definitions alone; the run made again from what the
record names and every score compared; and the definitions handed as text, with
the observation and nothing else, to three readers who had not seen the code.
What each reading needed that the record did not carry, and what the record
carried that no reading needed, are the facts.

It is also the first time two fingerprints have been compared under a comparison
list inside this system; the six-pair fixture `MAN-tools.v2` freezes compared
three images to check the tool is the tool, and F-6 meets two of those pairs.
The numbers are stated as measured. **Nothing here is a protocol, a metric
registration or a `runs/` entry**: the pairs are the organisers' own lists, the
metric definitions are stated in full by the instrument because no tracked file
defines them, and the records are derived data under `$LABDATA/derived`, because
what a `runs/` entry is composed of is what this record investigates.

## Method

### The dataset, addressed by manifest and verified before use

The subset is named by its manifest id, `fvc2002/DB1_B` or `fvc2002/DB1_A`,
and the instrument carries no dataset path: `MAN-fvc2002.v1`'s
`distribution.root` names `$LABDATA/raw/fvc2002` and the subset's `path` field
names its directory. The one literal it does carry is `Dbs`, the distribution
directory the index files sit in, which the manifest's `layout` names but does
not tie to them. The subset's `checksums` field names its per-file list and
carries that list's sha256, which the instrument verifies before reading the
list, and then every image an index file names is digested and compared with
the list before it is read. A run on a directory that merely has the subset's
name is not a run on the subset.

### The pairs, which are the organisers' and not this record's

`MAN-fvc2002.v1` records the four comparison indices the distribution ships,
`index_a.MFA`, `index_a.MFR`, `index_B.MFA` and `index_B.MFR`, by sha256 and
line count, and says in its own note that the protocol they define has no
manifest and is not the manifest's subject (`INV-005` F-7). The instrument
picks the two whose letter matches the subset's, verifies each against the
manifest's digest, and uses every line in file order: `.MFR` is the genuine
list and `.MFA` the impostor list, each line a probe and a gallery, nothing
added, removed or reordered. So the genuine list of `DB1_A` keeps the one
comparison `INV-005` F-8 deduced would be a self-comparison, between the two
byte-identical files `81_5.tif` and `81_7.tif`, and this record reports what
it scored.

### The tools, at the invocations the manifest freezes

`mindtct <image.png> <output_root>` and `bozorth3 <probe.xyt> <gallery.xyt>`, no
flags on either, as `MAN-tools.v2` records them. `-m1` is passed to neither:
`REF-005` decided the extractor's flags, and the manifest records that the
matcher is called without it so that it reads the representation the extractor
wrote, with `D-1` open on whether the other representation scores differently.
Each binary's sha256 is measured in the image and compared with the manifest's
before a template is written, and the run stops on a mismatch. Each `.tif` is
decoded to 8-bit greyscale and written as PNG for `mindtct`, which is the input
format the manifest records.

Two things the manifest says about `bozorth3` shape what the observation
keeps. Its `default_minminutiae` note: below ten minutiae the score is 0
rather than an error, so a zero from a rejected template is indistinguishable
in a score vector from a genuine non-match unless the counts travel with the
scores — so the number of lines `mindtct` wrote to each `.xyt` is kept per
image. Its `overflow_sentinel` note, from `INV-004` B-3: on internal overflow
the tool prints 4000, inside the range a real score occupies, and says so only
on its error stream — so both streams are captured, whatever was written to
stderr is kept by row, and rows scoring exactly 4000 are listed.

Templates are written to a scratch directory per process and deleted after
use. What the run returns is file names, list labels, integer scores and
counts, and nothing from which a minutia could be reconstructed.

### The metrics, defined in full because nothing in the tree defines them

Before the instrument, the names `eer@1` and `auc@1` occurred in the tree
only in the illustrations of a `run:` commit in `docs/commits.md` and
`REF-002`, and `runs/README.md` says a record names its metric definition;
**no tracked file defines either metric.** The
instrument therefore states each definition in full, and that text — carried
in `matching.py` and copied into every record beside the value — is the
definition this run's numbers are computed under. An equal-error rate can be
read more than one way: whether a pair scoring exactly the threshold is
accepted, whether the sweep includes a threshold that rejects everything,
over which values the sweep runs, and how a tie is broken. Each choice is
made in the text rather than in the code alone:

> Threshold sweep over the distinct scores observed, and one threshold above
> the largest, with a pair accepted when its score is at least the threshold.
> FMR(t) is the fraction of impostor pairs accepted and FNMR(t) the fraction of
> genuine pairs rejected. The operating threshold is the one that minimises
> |FMR(t) - FNMR(t)|; on a tie the smallest threshold is taken.
> EER = (FMR(t) + FNMR(t)) / 2 at that threshold, stored as a fraction.

> Exact Mann-Whitney U with average ranks for ties: every genuine and impostor
> score is ranked together, tied scores sharing the mean of the ranks they
> span, U = R_genuine - n_genuine (n_genuine + 1) / 2, and
> AUC = U / (n_genuine n_impostor). Equal to the probability that a genuine
> score exceeds an impostor score, counting a tie as one half. Stored as a
> fraction.

Every other reading those choices admit — accepted at or strictly above the
threshold, with or without the reject-all threshold, a tie broken to the
smallest or the largest — is computed alongside and stored in the record, so
that whether the choices move the number is a fact and not an assurance. The
rank form of `auc@1` is compared with a direct pairwise count when the record
is read back.

### The record, its provenance, and the three readings

The record is two documents: `results.json`, which names the dataset, the set
digest, the index digests, the tool identities as invocation plus measured
sha256, the metric values with their definition texts, the counts, and the
provenance; and `observation.json`, one row per index line with its score, the
per-image counts, the stderr by row and the sentinel rows, whose sha256 and
byte count `results.json` carries.

The image carries no `git`. The code revision, whether the tree was dirty, the
branch and the image id are read on the host by the `Makefile` target
`run-matching` and passed into the container in the environment; the record
marks any of them the caller did not supply
`UNVERIFIED`, digests the two modules that ran regardless, and marks itself
provisional when the revision or the dirty flag is unverified or the tree was
dirty. A provisional record cannot support a claim.

The three readings:

- **Re-derive.** From the record directory, by the instrument's own metric
  code, recompute both metrics from `observation.json` and compare; and
  compare the rank form of `auc@1` with a direct pairwise count. This checks
  that the observation is the record's; whether the definition texts suffice
  on their own is the third reading's question.
- **Reproduce.** From what the record names — the dataset id, the index
  digests, the tool identities — and the corpus and the image, make the run
  again and compare every score, every count and every digest.
- **Blind readers.** Three readers were each given the two definition texts
  and the two observation files and nothing else, told not to open anything
  under the repository, and asked to implement the definitions from the text
  and report both numbers to full double precision, together with every point
  at which the text left them a choice.

No prediction was registered in advance; there was no brief. What was fixed
before any number existed is the composition of the candidate record, which
was written before the first run and not changed after it.

## F-1 — The run, and its numbers

| | `fvc2002/DB1_B` | `fvc2002/DB1_A` |
| --- | --- | --- |
| images used, every one verified against the checksum list | 80 | 800 |
| genuine pairs, `index_B.MFR` / `index_a.MFR` | 280 | 2800 |
| impostor pairs, `index_B.MFA` / `index_a.MFA` | 45 | 4950 |
| `mindtct` minutiae per image | 19 to 76 | 11 to 96 |
| images below `bozorth3`'s floor of 10 | 0 | 0 |
| images above `bozorth3`'s cap of 150 | 0 | 0 |
| genuine scores, min / median / max | 0 / 88 / 289 | 0 / 98 / 488 |
| impostor scores, min / median / max | 3 / 8 / 18 | 0 / 8 / 36 |
| rows with anything on stderr | 0 | 0 |
| rows scoring the overflow sentinel 4000 | 0 | 0 |
| **`eer@1`** | **0.056548** = 19/336 | **0.032264** = 17887/554400 |
| at threshold | 17 | 18 |
| FMR, FNMR there | 1/15, 13/280 | 31/990, 93/2800 |
| **`auc@1`** | **0.970714** = 1359/1400 | **0.987210** = 5473093/5544000 |

To full precision: `eer@1` 0.05654761904761905 and 0.032263708513708515,
`auc@1` 0.9707142857142858 and 0.987210137085137. Every metric is a fraction,
and the exact rationals are what the doubles are the nearest doubles to.

Both records are non-provisional: made from a clean tree at `3bec618`, two
commits after the one that put the instrument in the tree, in the image
`sha256:e0ded5a5dcc8f594df58ab904be76605ad26492da834130592091b1348f7c3fc`.
Neither draws a random number, and the seed field says so rather than carrying
a value.

## F-2 — The record, read back by the instrument

From `observation.json`, through the instrument's own metric code: both
numbers come back equal to the last bit on both subsets, at the same
threshold; the direct pairwise count of `auc@1` equals its rank form on both;
the observation's sha256 matches what the record carries; the genuine and
impostor counts match `n_genuine` and `n_impostor`. This is the check that the
observation is the record's. That the definition texts suffice without the
code is F-4.

## F-3 — The record, used to make the run again

From the dataset id and the digests the record names, with the corpus and the
image: on both subsets the pair list is identical row for row, every one of
the 325 and 7750 scores is identical, every per-image count is identical, both
binaries digest to what the record carries, the set's checksum list digests to
what the record carries, both index files digest to what the record carries,
and both metrics are equal.

## F-4 — Three readers, from the text alone

All three, working from the two definition texts and the observation files
and nothing else, returned the same four numbers as the instrument, to the last
double, at the same thresholds:

| reader | `DB1_B` `eer@1` | at | `auc@1` | `DB1_A` `eer@1` | at | `auc@1` |
| --- | --- | --- | --- | --- | --- | --- |
| a | 0.05654761904761905 | 17 | 0.9707142857142858 | 0.032263708513708515 | 18 | 0.987210137085137 |
| b | 0.05654761904761905 | 17 | 0.9707142857142858 | 0.032263708513708515 | 18 | 0.987210137085137 |
| c | 0.05654761904761905 | 17 | 0.9707142857142858 | 0.032263708513708515 | 18 | 0.987210137085137 |

Reader a and reader c computed in exact rationals and converted once, reader c
also running a float path that agreed; reader b in floats, every step in pure
Python without a library routine. Reader c also computed readings the text
does not name, to report whether each changes the number on this data: three
that replace the average with another combination of FMR and FNMR differ, as
they must, and one that keeps the formula differs, which the last row below
shows.

**What the definition text leaves open, and whether it matters on this data.**
The first three rows are the instrument's eight readings, and reader c varied
each of the three choices on its own; the last two are reader c's alone:

| choice | readings | `DB1_B` | `DB1_A` |
| --- | --- | --- | --- |
| accepted at the threshold, or strictly above | `≥` / `>` | same EER; the threshold reported as 17 or 16 | same EER; 18 or 17 |
| a reject-all threshold in the sweep, or not | with / without | same | same |
| a tie in \|FMR − FNMR\| broken low or high | smallest / largest | same; no tie occurs | same; no tie occurs |
| thresholds from all scores, or one list only | pooled / genuine / impostor | same | same |
| the minimum over sweep points, or the interpolated crossing | discrete / interpolated | 0.056548 / **0.047934** | 0.032264 / **0.033110** |

The scores are integers, so `>` at `t` is `≥` at the next score and the
operating point is the same point under a different label. On both subsets
exactly one threshold attains the minimum gap, so the tie rule is never
exercised. The one reading that keeps the formula and moves the number,
interpolating the crossing between adjacent sweep points, is not in the
sentence, which says "the one that minimises", a sweep point; reader c
computed it because it is the most common other convention, and on this data
it is a different number.

In computing the numbers all three used the score and the list label of each
row and nothing else, because the definitions name nothing else; readers a and
b said so, and reader c additionally checked the file names for duplicate,
reversed and self pairs and found none. All three read the stderr and
sentinel fields and reported them empty. Two of the three noted the
observation's remark that a `bozorth3` zero may be a floor, and none acted on
it, because the definition gives no rule. The observation carried those fields
for the reader who asks a different question, not for these.

## F-5 — What the run needed, against what the tree names

`runs/README.md` names six things a record must name. Against what this run
actually had to carry for F-2, F-3 and F-4 to succeed:

| the six | what this run carried for it |
| --- | --- |
| the dataset | the manifest id, the manifest's sha256, the checksum list's path and sha256, the count of entries, and that every image used was verified against it |
| the manifests | `MAN-fvc2002.v1` and `MAN-tools.v2`, each by path and sha256 |
| the protocol | none exists to name; the record carries the two index files by name, sha256 and status, and says in a note that no protocol manifest exists |
| the metric definition | the full text of each, beside its value — text the instrument had to write, because no tracked file defines `eer@1` or `auc@1` |
| the seed | none; the field carries `null` and a sentence saying no random number is drawn |
| the code revision | the revision, from the host |

And what the run carried that the six do not name, each with the reading that
needed it:

| carried | needed by |
| --- | --- |
| each tool's invocation, flags and binary path, with the sha256 the manifest records **and** the sha256 measured in the image | F-3: a re-run has to know it ran the same binary, and `MAN-tools.v2` says the digest is the identity because neither tool reports a version |
| the per-image minutia count | the reader who asks whether a zero is a floor; `MAN-tools.v2` `default_minminutiae` says why (F-7) |
| stderr by row, and the rows scoring 4000 | the reader who asks whether a high score is an overflow; `MAN-tools.v2` `overflow_sentinel` says why |
| the observation's sha256 and byte count | F-2: the record has to say which observation it is the record of |
| whether the tree was dirty, and the branch | the provisional flag, without which a run from an uncommitted tree looks like any other |
| the image id | F-3 on another machine: the binaries live in the image |
| the sha256 of each module that ran | pins the code when the revision is missing or the tree was dirty |
| every open reading of `eer@1`, computed | F-4's last table; without it, "the choices do not matter here" would be an assurance |

Three of those the image cannot supply. There is no `git` in it, so the
revision, the dirty flag and the branch have to be read on the host and
crossed into the container; `make run-matching` does that, and a run started
any other way forms a record with those fields `UNVERIFIED` and marked
provisional. The first two runs of this instrument were provisional for a
smaller reason: an untracked directory in the working tree, which
`git status --porcelain` counts. The records this record is written from were
made after it was excluded, from a clean tree, and their numbers are the same.

## F-6 — Two protocol pairs are fixture pairs, and agree with the manifest

`MAN-tools.v2` freezes six `bozorth3` scores over three `DB1_B` images as its
fixture. Two of the six are comparisons the organisers' lists also make:

| pair | list | `MAN-tools.v2` fixture | this run |
| --- | --- | --- | --- |
| `101_1` `101_2` | genuine | 60 | 60 |
| `101_1` `102_1` | impostor | 9 | 9 |

The other four are self-comparisons or a pairing the lists do not contain.

## F-7 — The zeros, and the floor

`bozorth3` returns 0 below ten minutiae. No image in either subset is below
ten; the smallest count is 19 on `DB1_B` and 11 on `DB1_A`. So every zero is
the tool's own verdict on two templates it accepted:

| subset | genuine rows scoring 0 | the two counts | impostor rows scoring 0 |
| --- | --- | --- | --- |
| `DB1_B` | row 74, `103_4` `103_5`; row 77, `103_4` `103_8` | 22 and 40; 22 and 30 | 0 |
| `DB1_A` | row 1240, `45_2` `45_4`; row 1252, `45_4` `45_7` | 50 and 11; 11 and 23 | 5 |

On `DB1_A` both genuine zeros involve `45_4.tif`, the image with 11 minutiae,
one above the floor. The record can say that only because the counts travel
with the scores; without them the two rows are two non-matches.

## F-8 — The self-comparison the organisers' list contains

`INV-005` F-6 measured `81_5.tif` and `81_7.tif` in `DB1_A` byte-identical, and
F-8 deduced that a deterministic extractor and matcher would therefore score
that line of `index_a.MFR` as a self-comparison. It scored **488**, the
largest genuine score in the subset; the next largest is 318. The pair
is one of the 2800 and was kept, because the list is the organisers' and this
record does not edit it.

## F-9 — Four digits that were already in the tree

`docs/commits.md` has carried, since the root commit of 2026-09-03, the lines
`run: eer@1 0.0323 on fvc2002/DB1_A, mindtct + bozorth3`,
`Result: eer@1 0.032264` and `Result: auc@1 0.987210`, under a note that every
number on the page is there to show the form and that no run has produced
them; `REF-002` has carried the same lines as its illustration since the same
commit. This run's `DB1_A` values are 0.032263708513708515 and
0.987210137085137, which round to the six digits the page carries, and to
the four of the subject line.

This record states the coincidence and no more. The page's note was true when
it was written: no run in this repository had produced those digits, and
`README.md` says nothing is carried over from an earlier codebase. Where the
digits on the page came from is not a fact of this repository.

## Reproducing this

**The instrument is in the tree.** The run is
`implementation/library/matching.py` and the record, with its two readings, is
`implementation/library/run_record.py`; the command forms are
`scripts/run_matching.sh` and `scripts/reproduce_matching.sh`, reached through
the `Makefile` targets, of which `run-matching` carries the host's provenance
across:

    make run-matching LABDATA=/path/to/labdata SUBSET=fvc2002/DB1_B
    make run-matching LABDATA=/path/to/labdata SUBSET=fvc2002/DB1_A
    make reproduce-matching LABDATA=/path/to/labdata RECORD=inv017/fvc2002_DB1_B
    make reproduce-matching LABDATA=/path/to/labdata RECORD=inv017/fvc2002_DB1_A

Each `run-matching` writes `results.json` and `observation.json` under
`$LABDATA/derived/inv017/<subset>/` and prints the re-derivation. The records
this record is written from:

| | `results.json` sha256 | `observation.json` sha256, bytes |
| --- | --- | --- |
| `DB1_B` | `8088c06301bb5b6b534552fb6da187be6fa60e69d63a34cdc1ae5c85f67c85af` | `532628ae6aac9a6a7e2a8e2e76b6233b077e76b41c51311b13ed0716b0a4e407`, 22 083 |
| `DB1_A` | `41cb4226e6e6358527f9121ea1a70b6a9b097ac7f0c0778edee66a1dec917320` | `c815708f51139ff79e06372d2b85eeeff9c5c0129f6d0d4d96cc8b19b28de7cf`, 473 796 |

**The pool is shared and the command forms are `scripts/run_matching.py` and
`scripts/reproduce_matching.py` since 2026-09-22.** The commit `code: one
process pool for every instrument` moved the pool and the scratch directory
out of `matching.py` into `implementation/library/pool.py`; `INV017_SERIAL=1`
still forces this run's sequential path. The commit `code: write every command
form in Python` put Python files with the same arguments in place of the two
shell scripts, and gave the placer, `scripts/record_run.py`, the target `make
record-run`. The `Makefile` targets above are unchanged in name and arguments.
Run through them on 2026-09-22 from the tree at `d8404f6`, a `DB1_B` run
returns the pairs, the minutia counts, the error-stream rows, the sentinel
rows, both metrics and every reading of the committed record
`runs/20260922-fvc2002_DB1_B-a6fd834` unchanged.

**The record digests every module that ran since 2026-09-22.** The Method
above says the record digests the two modules that ran; it did, by two file
names written in `run_record.py`, and the names had been outgrown:
`iso_xyt.py` ran in the `iso-extract` records of `INV-018` and was not pinned.
In the commit `code: address a subset by its manifest id in every command
form`, `code.modules` digests every module under `implementation/library`
loaded when the record is composed; the subset's resolution also moved out of
`matching.py` into `implementation/library/corpus.py`. A `DB1_B` run from the
tree at `f96b1eb` on 2026-09-22 lists six, `corpus`, `iso_xyt`,
`manifest_verify`, `matching`, `pool` and `run_record`, where the records
under `runs/` list two, and returns the pairs, the minutia counts, the
error-stream rows, the sentinel rows, both metrics and every reading of the
committed record `runs/20260922-fvc2002_DB1_B-a6fd834` unchanged.

Every command was run on 2026-09-21 against the tree at `3bec618` and the
image built from its `Dockerfile`, image id
`sha256:e0ded5a5dcc8f594df58ab904be76605ad26492da834130592091b1348f7c3fc`, on
a 13th Gen Intel Core i9-13900HX, twenty-four cores and thirty-two threads.
The record carries no timing; the shell's `time` on `make run-matching` read
1.8 s for `DB1_B` and 10.1 s for `DB1_A`, container start included.
`$LABDATA` resolves as `.env.example` specifies and `MAN-fvc2002.v1`'s
`distribution` block records. The three blind readers were given copies of the
two observation files and the two definition texts in a directory outside the
tree, on the same day; their implementations are not in the tree and are not
needed to reproduce anything above, since F-4 is a fact about the definition
texts and F-2 reproduces the numbers from the instrument.

## What was left unchecked

- **Whether the organisers' index files are the FVC2002 protocol as
  published.** The files were used by digest; no document describing the
  competition's protocol was fetched or read. Naming them "the protocol" is a
  refinement's step, on an investigation that reads the source.
- **The ANSI representation.** `-m1` was passed to neither tool, as the
  Method describes; whether it changes a score is `D-1` and stays open.
- **`iso-extract`.** `bozorth3` reads `.xyt` and nothing here converts an ISO
  template to it; no run on the second extractor's output was made.
- **Interpolated EER.** One reader computed it to show the size of the
  sentence's choice; the instrument does not, and the number is not a metric
  this repository registers.
- **`DB2` to `DB4`.** They exist and were not run. `REF-007` decision 4
  excludes `DB2` from comparisons involving the FingerJetFXOSE extractor,
  which this run does not use; nothing in the tree excludes it here.
- **Where the digits in `docs/commits.md` came from.** F-9 states the
  coincidence; nothing in the tree says.
- **What of the composition survives `M-2`.** The record computes no
  comparability fingerprint. Which of its fields would enter one is `M-2` and
  stays open.
- **Whether the six things `runs/README.md` names were meant to be a floor or
  a list.** F-5 measures the gap against the sentence as written; reading it
  is a refinement's.
- **Whether the definition texts in `matching.py` are the definitions this
  repository will register.** They are the ones this run used, and no tracked
  file registers any; registering one, with an id and a version, is a
  decision.
- **Two zeros per subset among the genuine pairs.** F-7 records them and their
  counts; why `bozorth3` scores two accepted templates of one finger at zero
  was not investigated.
