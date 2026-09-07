# INV-009 — Every field of MAN-tools.v1, re-verified against the image

Date: 2026-09-07

## Numbering

This record takes 009, the next free investigation number after `INV-008`. The
reservation at 001 is explained in `REF-002`.

## Question

Two fields of `manifests/MAN-tools.v1.json` have turned out not to say what
the tree says, and both were found while doing something else:
`build.extra_build_packages`, which the `Dockerfile` stopped matching, and
`fixture.dataset`, which a later manifest replaced. Each appears once in each
of the two tool entries, so four rows were already spoken for.

`MAN-tools.v1.json` carries **63 fields with a `value` and a `status`**.

So: **how many of the other 59 still hold, and did `MAN-tools.v2` inherit any
of them without checking?**

## Method

**What was measured against.** The tree at commit `641bfb6`, which is the tree
this record is written on, and the image built from its `Dockerfile`, image id
`sha256:e0ded5a5dcc8f594df58ab904be76605ad26492da834130592091b1348f7c3fc`. For
the fields that describe an artefact outside the image — the archive, the
publisher's page, the mirror — the artefact itself was fetched.

**Not against `docs/tools.md`.** That file is captured output and can be as
stale as the manifest, so nothing below rests on it. Where a figure in this
record and a figure there disagree, this record says so and gives the command
it ran.

**The verdicts, and what they are not.** Each field gets one of four verdicts.
They are **audit verdicts about whether a claim still holds. They are not the
`VERIFIED` / `APPROX` / `UNVERIFIED` / `CONFLICT` vocabulary of
`manifests/README.md`**, which says how well a value was established when it
was written. A field can be `VERIFIED` and `fails`, and two of them are.

- `holds` — re-measured now and agrees.
- `fails` — re-measured now and disagrees.
- `historical` — the field asserts something about a past state or an external
  artefact and is not a claim about the present image. The row says what it is
  a claim about and whether that claim was checkable.
- `superseded` — already corrected in a later manifest. The row names where.

**Where two verdicts could both apply, and how that was resolved.** Both
failing fields are also corrected in `MAN-tools.v2`, so `superseded` could be
argued for them; and the two `superseded` fields could be argued to fail. The
rule applied throughout is this. A field is `fails` when it was re-measured
against the present state and disagreed — regardless of whether a later
manifest has since corrected it. A field is `superseded` when there was no
present-state measurement to take, because the value was never a claim about
the image: both `fixture.dataset` fields carry a directory name under an
`UNVERIFIED` status, with a note saying the field is replaced when a dataset
manifest is issued. A reader who prefers the other assignment can move two
rows; the measurements in them do not change, and F-2 records the history of
the failing pair either way.

**The last column of F-1 is a second question, asked of the same field.** Not
"does it hold" but "would anything in this repository have noticed if it
stopped holding, before this record". The criterion for each value is stated so
that a row can be disputed without disturbing the rest:

- `manifest` — a mechanism read this field's value out of the manifest and
  failed if what it measured disagreed. This is the only category in which a
  **wrong manifest value** is caught.
- `property (script)` — `scripts/check_tools.sh` measured the property the
  field asserts and would have failed had the property been false, but compared
  against its own constant or against what it had just built, not against the
  field.
- `property (build)` — the `Dockerfile` does the same: a step would fail if the
  property stopped holding. The archive is fetched and its digest gated on
  every build, the patch step asserts its own effect, and a `COPY` fails if the
  artefact is not where it says.
- `none` — nothing in the repository measured it.

**Two mechanisms, not one.** `scripts/check_tools.sh` and the `Dockerfile` both
re-measure fields of this manifest, and F-3 maps each of them onto the fields
it touches. For the script, the revision audited is the one that covers both
tools: it stood from `28b467b` until `56f53b7` replaced it, and was read at
`609c46c`, the last commit before that change. For the `Dockerfile`, what makes
a step a check of a *field* rather than of itself is block **D**: seven values
per tool were found as verbatim substrings of the file, so the string the
manifest carries is the string the build runs. The eighth, `source.kind`, is
prose and matches nothing; F-3 says what stands behind it instead.

**Nine command blocks produced the measurements in the table**, labelled
**D**, **H**, **A**, **P**, **R**, **M**, **X**, **I** and **N**. Seven more
produced the findings after it: **G**, the two histories; **S** and **S2**, the
two revisions of the verification script; **S3**, that script run against v1
today; **T**, the field walk; **V**, v1 against v2; and **Q**, what reads the
other manifests. Sixteen labels under fifteen headings, because **S** and
**S2** share one. Each is given in full under "Reproducing this".

**Every field has a method beside it, and for two of them the method is not a
command.** Rows 23 and 54, the `superseded` pair, name the manifest that
carries the corrected value instead. That is not a fifth verdict and not a
field left unaudited: `superseded` is defined as "already corrected in a later
manifest, the row names where", and naming where is the whole of what it asks
for. What those two rows do not carry is a present-state measurement, and they
say so in the cell.


## F-1 — the audit table

All 63 fields, by their path in the JSON. The `how it was re-measured` column
names the command block and what it showed; the last column is the second
question the Method describes.

| # | field | verdict | how it was re-measured | measured before this record |
| --- | --- | --- | --- | --- |
| 1 | `tools.mindtct.source.kind` | holds | **D** the fetch step is `curl` on a publisher URL followed by `sha256sum -c`; **R** ran it | property (build) |
| 2 | `tools.mindtct.source.url` | holds | **H** HTTP 200; **A** the file it serves; **R** fetched it | property (build) |
| 3 | `tools.mindtct.source.archive_sha256` | holds | **A** `sha256sum` on the download; **R** printed `/tmp/nbis.zip: OK` | property (build) |
| 4 | `tools.mindtct.source.archive_size_bytes` | holds | **H** `Content-Length`; **A** `stat -c %s` | none |
| 5 | `tools.mindtct.source.release` | holds | **P** the page still lists 5.0.0 as the newest stable version | none |
| 6 | `tools.mindtct.source.release_date` | holds | **P** the page still gives `(03/04/2015)` | none |
| 7 | `tools.mindtct.source.upstream` | holds | **H**, **A**, **R** the archive comes from nigos.nist.gov and its digest matches | none |
| 8 | `tools.mindtct.source.mirror_previously_used` | historical | **M** the commit is still `master`; **X** the comparison re-run. A claim about how the recipe was developed, against a mirror the recipe no longer uses. Checkable, and checked | none |
| 9 | `tools.mindtct.build.base_image` | holds | **D** all three `FROM` lines carry that digest, verbatim | property (build) |
| 10 | `tools.mindtct.build.setup` | holds | **D** verbatim at line 50; **R** the step ran | property (build) |
| 11 | `tools.mindtct.build.patch` | holds | **D** verbatim at line 59; **R** printed line 142 carrying `-fcommon` | property (build) |
| 12 | `tools.mindtct.build.make` | holds | **D** verbatim at line 66; **R** the step ran | property (build) |
| 13 | `tools.mindtct.build.extra_build_packages` | fails | **D** the stage installs five packages, not four: `git` is absent, `curl` and `unzip` are present | none |
| 14 | `tools.mindtct.build.artifact_copied` | holds | **D** verbatim at line 181; **I** the file is at the destination | property (build) |
| 15 | `tools.mindtct.binary.path` | holds | **I** `command -v` and `sha256sum` on that path | manifest |
| 16 | `tools.mindtct.binary.sha256` | holds | **I** `sha256sum` in the image; **R** the same digest from a rebuild out of the archive | manifest |
| 17 | `tools.mindtct.binary.size_bytes` | holds | **I** `stat -c %s` | none |
| 18 | `tools.mindtct.runtime.shared_libraries` | holds | **I** `ldd` | property (script) |
| 19 | `tools.mindtct.invocation.command` | holds | **I** called as `mindtct <png> <root>`; the fixture reproduces | property (script) |
| 20 | `tools.mindtct.invocation.flags` | holds | **I** called with none; the fixture reproduces | property (script) |
| 21 | `tools.mindtct.invocation.input_format` | holds | **I** PNG exits 0, TIFF and PGM exit 253 with `image type UNKNOWN : not supported`; **N** `rules.mak` line 84 carries `-D__NBIS_PNG__` | property (script) |
| 22 | `tools.mindtct.invocation.outputs` | holds | **I** one run leaves exactly those eight extensions and no ninth | property (script) |
| 23 | `tools.mindtct.fixture.dataset` | superseded | corrected in `MAN-tools.v2`, which carries `fvc2002/DB1_B`, the subset id `MAN-fvc2002.v1.json` issues. No present-state measurement was taken: the value was a placeholder its own note said would be replaced | none |
| 24 | `tools.mindtct.fixture.conversion` | holds | **I** `np.array_equal` on the decoded TIFF and the decoded PNG, all three images | property (script) |
| 25 | `tools.mindtct.fixture.cases.101_1.minutiae` | holds | **I** `wc -l` of the `.xyt` | manifest |
| 26 | `tools.mindtct.fixture.cases.101_1.xyt_sha256` | holds | **I** `sha256sum` of the `.xyt` | manifest |
| 27 | `tools.mindtct.fixture.cases.101_2.minutiae` | holds | **I** as above | manifest |
| 28 | `tools.mindtct.fixture.cases.101_2.xyt_sha256` | holds | **I** as above | manifest |
| 29 | `tools.mindtct.fixture.cases.102_1.minutiae` | holds | **I** as above | manifest |
| 30 | `tools.mindtct.fixture.cases.102_1.xyt_sha256` | holds | **I** as above | manifest |
| 31 | `tools.bozorth3.source.kind` | holds | **D** the fetch step is `curl` on a publisher URL followed by `sha256sum -c`; **R** ran it | property (build) |
| 32 | `tools.bozorth3.source.url` | holds | **H** HTTP 200; **A** the file it serves; **R** fetched it | property (build) |
| 33 | `tools.bozorth3.source.archive_sha256` | holds | **A** `sha256sum` on the download; **R** printed `/tmp/nbis.zip: OK` | property (build) |
| 34 | `tools.bozorth3.source.archive_size_bytes` | holds | **H** `Content-Length`; **A** `stat -c %s` | none |
| 35 | `tools.bozorth3.source.release` | holds | **P** the page still lists 5.0.0 as the newest stable version | none |
| 36 | `tools.bozorth3.source.release_date` | holds | **P** the page still gives `(03/04/2015)` | none |
| 37 | `tools.bozorth3.source.upstream` | holds | **H**, **A**, **R** the archive comes from nigos.nist.gov and its digest matches | none |
| 38 | `tools.bozorth3.source.mirror_previously_used` | historical | **M** the commit is still `master`; **X** the comparison re-run. A claim about how the recipe was developed, against a mirror the recipe no longer uses. Checkable, and checked | none |
| 39 | `tools.bozorth3.build.base_image` | holds | **D** all three `FROM` lines carry that digest, verbatim | property (build) |
| 40 | `tools.bozorth3.build.setup` | holds | **D** verbatim at line 50; **R** the step ran | property (build) |
| 41 | `tools.bozorth3.build.patch` | holds | **D** verbatim at line 59; **R** printed line 142 carrying `-fcommon` | property (build) |
| 42 | `tools.bozorth3.build.make` | holds | **D** verbatim at line 66; **R** the step ran | property (build) |
| 43 | `tools.bozorth3.build.extra_build_packages` | fails | **D** the stage installs five packages, not four: `git` is absent, `curl` and `unzip` are present | none |
| 44 | `tools.bozorth3.build.artifact_copied` | holds | **D** verbatim at line 182; **I** the file is at the destination | property (build) |
| 45 | `tools.bozorth3.binary.path` | holds | **I** `command -v` and `sha256sum` on that path | manifest |
| 46 | `tools.bozorth3.binary.sha256` | holds | **I** `sha256sum` in the image; **R** the same digest from a rebuild out of the archive | manifest |
| 47 | `tools.bozorth3.binary.size_bytes` | holds | **I** `stat -c %s` | none |
| 48 | `tools.bozorth3.runtime.shared_libraries` | holds | **I** `ldd` | property (script) |
| 49 | `tools.bozorth3.invocation.command` | holds | **I** called as `bozorth3 <a.xyt> <b.xyt>`; one integer per pair on stdout | property (script) |
| 50 | `tools.bozorth3.invocation.flags` | holds | **I** called with none; the matrix reproduces | property (script) |
| 51 | `tools.bozorth3.invocation.default_max_minutiae` | holds | **I** the usage still prints `[150]` and `legal range is [0,200]` | none |
| 52 | `tools.bozorth3.invocation.default_minminutiae` | holds | **I** the usage still prints `minminutiae=# ... [10]` | none |
| 53 | `tools.bozorth3.invocation.input` | holds | **I** the `.xyt` mindtct writes without `-m1` has four fields per line and bozorth3 scores it without `-m1` | property (script) |
| 54 | `tools.bozorth3.fixture.dataset` | superseded | corrected in `MAN-tools.v2`, which carries `fvc2002/DB1_B`. No present-state measurement was taken, for the reason given in the `mindtct` row | none |
| 55 | `tools.bozorth3.fixture.source_of_xyt` | holds | **I** the matrix reproduces from `.xyt` made that way, and the three counts are 33, 24 and 62 | property (script) |
| 56 | `tools.bozorth3.fixture.pairs.101_1 101_1` | holds | **I** the full matrix | manifest |
| 57 | `tools.bozorth3.fixture.pairs.101_1 101_2` | holds | **I** the full matrix | manifest |
| 58 | `tools.bozorth3.fixture.pairs.101_1 102_1` | holds | **I** the full matrix | manifest |
| 59 | `tools.bozorth3.fixture.pairs.101_2 101_2` | holds | **I** the full matrix | manifest |
| 60 | `tools.bozorth3.fixture.pairs.101_2 102_1` | holds | **I** the full matrix | manifest |
| 61 | `tools.bozorth3.fixture.pairs.102_1 102_1` | holds | **I** the full matrix | manifest |
| 62 | `tools.bozorth3.fixture.symmetry` | holds | **I** three off-diagonal pairs both ways | property (script) |
| 63 | `tools.bozorth3.fixture.determinism` | holds | **I** one pair five times, one distinct value | property (script) |

### The count

| verdict | fields | | measured before this record | fields |
| --- | --- | --- | --- | --- |
| `holds` | 57 | | `manifest` | 16 |
| `fails` | 2 | | `property (build)` | 16 |
| `historical` | 2 | | `property (script)` | 13 |
| `superseded` | 2 | | `none` | 18 |
| **total** | **63** | | **total** | **63** |

The table was generated from the manifest rather than typed: the script that
emitted it asserts that the set of paths it prints equals the set of paths a
walk of `MAN-tools.v1.json` finds, so no field is missing from it and none is
invented. The command is **T** under "Reproducing this".

### Note-level claims that were checked, and are not part of the 63

The scope of this audit is fields carrying a `value` and a `status`. A `note`
carries neither, so no note has a verdict. Five were read anyway, in the four
items below, because they carry numbers or assertions a reader would take for
measurements. The two `mirror_previously_used` notes are read together in the
fourth item: they carry the same figures in different words, and where the
wording differs the item says so. One of the five, `produced_by.note`, is
attached to no field at all. What they say, and what was measured against them,
is recorded here as fact and nowhere given a verdict.

**`tools.mindtct.build.artifact_copied`, note.** "One file crosses the stage
boundary. No compiler, no source tree and no other NBIS tool reaches the
runtime image." The boundary the note means is the NBIS builder's, and two
files cross it now, at lines 181 and 182 (**D**): the note was written before
`bozorth3` was copied out at `630afae`. Its second sentence still holds. The
field's own `value` is unaffected and holds.

**`tools.bozorth3.build.artifact_copied`, note.** "Produced by the same make it
as mindtct, in the same builder stage, from the same archive. Two files now
cross the stage boundary and nothing else." Scoped by its own first sentence to
the same NBIS boundary, this is still exactly true: two files cross it. Four
files reach the runtime image in all, but the other two cross out of
`fjfx-builder` at lines 196 and 197, a stage this note is not about.

**`produced_by.note`.** "No INV record exists in this repository yet. The
evidence behind every VERIFIED value below is the captured output in
`docs/tools.md`, produced by `scripts/check_tools.sh`." Seven INV records exist
at `641bfb6`: `git ls-tree --name-only 641bfb6 quality/ | grep -c 'INV-'` prints
7, and this record is the eighth file, numbered 009 because 001 is reserved. And
by the last column of F-1, `scripts/check_tools.sh` at `609c46c` produced no
evidence at all for 34 of the 63 fields, and produced evidence that was not
compared against the manifest for a further 13.

**`tools.mindtct.source.mirror_previously_used` and the `bozorth3` twin,
notes.** Both carry the figures of the comparison between the archive and the
mirror, in different words. The `mindtct` note reads "Compared against this
archive: 3879 paths on both sides, none missing from either, 593
byte-identical, 3286 differing only in line endings (the mirror carries CRLF,
the archive LF), and none differing in content", and adds "Built in the same
directory, the mirror produces the byte-identical binary recorded below". The
`bozorth3` note gives the same five figures without the parenthesis about CRLF,
and ends "so no file this tool compiles from differs between them". The figures
are what was checked below. The two closing assertions were not: the first, that
the mirror produces the byte-identical binary, is the subject of a transcript in
`docs/tools.md` and no field carries it; the second follows from the figure that
none differ in content.

Re-run today (**X**), the comparison gives 3879 paths on both sides, none
missing from either, and none differing in content — and **3879 byte-identical
with 0 differing in line endings**, not 593 and 3286.

The difference was then measured rather than guessed. The same comparison was
run twice, differing only in how the mirror is checked out:

| `git clone` | byte-identical | differ only in line endings | mirror has more CR bytes | differ in content |
| --- | --- | --- | --- | --- |
| `-c core.autocrlf=false` | 3879 | 0 | 0 | 0 |
| `-c core.autocrlf=true` | 593 | 3286 | 3286 | 0 |

The second row reproduces the note's figures exactly. So those figures are a
property of a checkout made with `core.autocrlf=true`, and the note's
parenthesis — "the mirror carries CRLF, the archive LF" — is a statement about
that checkout and not about what the mirror repository stores: checked out with
the conversion off, every one of the 3879 files is byte-identical to the
archive. `INV-003`'s Method records the same mechanism for this repository's
own files. The note's conclusion, that no file these tools compile from differs
in content between the two, holds under both checkouts.

## F-2 — when the two failing fields stopped being true

Both failures are the same field in the two tool entries:
`build.extra_build_packages`, `["build-essential", "ca-certificates", "cmake",
"git"]`. The file it describes is the `Dockerfile`, and its history was read
commit by commit (**G**). The package set the NBIS builder stage installs, at
every commit that touched the file:

| commit | date | subject | the set the NBIS stage installs |
| --- | --- | --- | --- |
| `4464e90` | 2026-09-06 | infra: pin a base image and route every docker run through make | none — there is no builder stage yet |
| `7aa439f` | 2026-09-06 | infra: build mindtct from pinned NBIS source in a builder stage | build-essential, ca-certificates, cmake, **git** |
| `2ac93d4` | 2026-09-06 | infra: fetch NBIS from NIST and verify its checksum before unpacking | build-essential, ca-certificates, cmake, **curl, unzip** |
| `630afae` | 2026-09-06 | infra: copy bozorth3 out of the builder into the runtime image | unchanged |
| `40f172d` | 2026-09-07 | infra: build FingerJetFXOSE and copy two files into the runtime | unchanged for this stage |

Against that, the history of the manifest itself (**G**). The file has three
commits and was renamed once:

| commit | date | subject | what it did |
| --- | --- | --- | --- |
| `c68ec2a` | 2026-09-06 | man: freeze the provenance, binary and invocation of mindtct | created `manifests/tools.json` with 26 value-and-status fields for `mindtct`, `extra_build_packages` among them |
| `ed64c9e` | 2026-09-06 | man: name the NIST archive as the source and rename the manifest | renamed the file to `manifests/MAN-tools.v1.json` and replaced the `source` block: `commit`, `commit_date` and `repository` removed, `kind`, `url`, `archive_sha256`, `archive_size_bytes`, `release`, `release_date` and `mirror_previously_used` added; 26 fields became 30 |
| `4eeffa2` | 2026-09-06 | man: freeze bozorth3 and record its two silent defaults | added the `bozorth3` entry, 33 fields; `mindtct`'s 30 unchanged from `ed64c9e` |

Putting the two histories side by side gives the answer, and it is different
for the two entries.

**`tools.mindtct.build.extra_build_packages` expired at `2ac93d4`.** It was
written at `c68ec2a`, when the `Dockerfile` had no builder stage at all. At that
commit the file is byte-identical to the one `4464e90` added — `git rev-parse
4464e90:Dockerfile c68ec2a:Dockerfile` returns one blob id for both — and it
carries no `apt-get` line, only the runtime's `pip install`. So the four
packages the field names were installed nowhere in the tree when the field was
written. It became true at `7aa439f`, which installed exactly those four. It
was still true at `ed64c9e`, the commit that gave the manifest its `v1` name.
`2ac93d4`, the next commit, replaced the git clone with a checksummed archive,
removed `git` and added `curl` and `unzip`.

It has been false from `2ac93d4` onward, that commit included: `git rev-list
--count 2ac93d4^..641bfb6` counts **30** commits over which it has stood, of
which 29 come after `2ac93d4` itself. The span is written against `641bfb6`
rather than `HEAD`, so that it does not grow by one every time this repository
gains a commit.

**`tools.bozorth3.build.extra_build_packages` was never true.** It was written
at `4eeffa2`, and `git rev-list --count 2ac93d4..4eeffa2` counts 3, so the set
it names had left the `Dockerfile` three commits before the field existed. Its
value is byte-identical to the one standing in the `mindtct` entry since
`ed64c9e`, which is consistent with the one having been copied from the other
and does not measure it. How the value was authored is not established here.

The two `superseded` fields have no expiry commit: `fixture.dataset` was
`UNVERIFIED` from the start and its own note said it would be replaced when a
dataset manifest was issued. `MAN-fvc2002.v1.json` was issued at `1be9b7a`,
which is when the replacement became possible; `MAN-tools.v2` made it.

## F-3 — how many were never re-measured between issue and this record

**18 of the 63.** Nothing in this repository measured them at all. That is the
number this finding reports, and the method for arriving at it is the two
mappings below, one per mechanism; the four rows that could be argued out of
the `property (script)` column are named there, and moving all four makes it
22.

A second number falls out of the same mappings and is stated because it does
not move at all: **47 of the 63** were never measured in a way that could have
caught the manifest being wrong, because only the 16 in the `manifest` category
are compared against the value the manifest carries, and 63 minus 16 is 47
whatever the property columns contain.

**Method.** Two mechanisms in this repository re-measure something about these
tools, and both were mapped onto the fields they touch.

### The verification script

`scripts/check_tools.sh`, in the revision that covers both tools: it stood from
`28b467b` until `56f53b7` replaced it, and was read at `609c46c`, the last
commit before that change (**S**). The `Makefile` is the only file that invokes
it; `INV-005` F-11 and `docs/tools.md` each write out a direct invocation as
well, so "only the Makefile calls it" is a statement about the tree and not
about how it has been run.

| section | what it does | fields | category |
| --- | --- | --- | --- |
| 1 | the toolchain is absent; each tool is on `PATH` | none — it uses the tool's name, which is a key and not a field | — |
| 2 | reads `binary.path` and `binary.sha256`, digests the file at that path | 4 | `manifest` |
| 3 | `ldd` on that path, asserts libm and libc and nothing else | 2 | `property (script)` |
| 4 | prints the first three lines of each tool's usage | none — nothing is compared, and the two `bozorth3` defaults are not in the first three lines | — |
| 5 | TIFF to PNG, decoded pixels compared | 1 | `property (script)` |
| 6 | reads the `mindtct` cases and runs `mindtct <png> <root>` with no flags, comparing count and digest | 6 | `manifest` |
| 6 | the same run exercises how the tool is called | 3 — `invocation.command`, `.flags`, `.input_format` | `property (script)` |
| 7 | the same PNG twice, eight named outputs compared | 1 | `property (script)` |
| 8 | reads the `bozorth3` pairs and runs `bozorth3 <a> <b>` with no flags, comparing each score | 6 | `manifest` |
| 8 | the same run exercises how the tool is called and what it is fed | 4 — `invocation.command`, `.flags`, `.input`, `fixture.source_of_xyt` | `property (script)` |
| 9 | symmetry on the three off-diagonal pairs | 1 | `property (script)` |
| 10 | one pair five times | 1 | `property (script)` |

16 `manifest` and 13 `property (script)`, which is what F-1's last column
counts.

**One of those thirteen is covered in one direction only.** Section 7 hardcodes
the eight output names and compares each pair with `cmp -s`, so an output that
disappeared would fail it and a ninth output would not. F-1 row 22 reads
"exactly those eight extensions and no ninth", and the half of that claim about
a ninth was measured here (**I**) and by nothing before.

**Four rows in the `property (script)` column are the arguable ones**, and they
are named so that a reader can move them: the two `invocation.flags`,
`tools.bozorth3.invocation.input` and `tools.bozorth3.fixture.source_of_xyt`.
In each the script realises the arrangement the field describes rather than
testing it, and the argument for counting them is only that the run would have
failed had the arrangement not worked. Moved to `none`, the first number
becomes 22 and the second stays at 47.

**For one commit the coverage was narrower still.** The `bozorth3` entry was
added at `4eeffa2`, and `28b467b`, the next commit, is where the script began
reading both tools; before it the script covered `mindtct` alone. So the 29
counted here is the coverage over all but that one commit, and 18 is the count
of fields nothing covered over any of them.

### The Dockerfile

The `Dockerfile` is the second mechanism, and it re-measures eight fields per
tool on every build. What makes seven of those eight steps a check of a *field*
rather than of itself is block **D**: seven values per tool were found as
verbatim substrings of the file, so the string the manifest carries is the
string the build runs. The eighth, `source.kind`, is prose — "publisher
archive, pinned by checksum" — and appears nowhere in the file; what stands
behind its row is not a string match but the two steps beneath it, a `curl` on
a publisher URL and a `sha256sum -c` gate, which are what that phrase
describes.

| step | what fails if the property stops holding | fields | category |
| --- | --- | --- | --- |
| `FROM ...@sha256:` | the registry cannot supply that digest | `build.base_image` ×2 | `property (build)` |
| `curl -fsSL "${NBIS_URL}"` | the URL stops serving; `-f` fails the build on a 4xx or 5xx | `source.url` ×2 | `property (build)` |
| `... \| sha256sum -c -` | the file at that URL is not that archive | `source.archive_sha256` ×2 | `property (build)` |
| the two together | the source stops being a publisher archive pinned by checksum | `source.kind` ×2 | `property (build)` |
| `RUN ... ./setup.sh ...` | the command fails | `build.setup` ×2 | `property (build)` |
| `RUN sed -i '142s/...' && sed -n '142p' \| grep -q -- '-fcommon'` | the patch does not land on line 142 | `build.patch` ×2 | `property (build)` |
| `RUN make config && make it` | the build fails | `build.make` ×2 | `property (build)` |
| `COPY --from=nbis-builder <src> <dst>` | the artefact is not at `<src>` | `build.artifact_copied` ×2 | `property (build)` |

16 fields. They are not in the `manifest` column: nothing compares the
`Dockerfile`'s constants with the manifest's values, so the two can diverge
silently, which is exactly what `build.extra_build_packages` did. That field is
the one build value with no verbatim match in the file, and the `Dockerfile`
cannot catch it: the build installs whatever the `apt-get` line says, so no
step can fail on account of the list being wrong.

**This mechanism has its own narrow window, and it is the mirror of the
script's.** `source.kind`, `source.url` and `source.archive_sha256` entered the
manifest at `ed64c9e`, and the `curl` and `sha256sum -c` steps that gate them
arrived one commit later, at `2ac93d4`. At `ed64c9e` the builder still ran `git
clone "${NBIS_REPO}"` against the `lessandro` mirror: `git show
ed64c9e:Dockerfile` carries `ARG NBIS_REPO=https://github.com/lessandro/nbis`
at line 31 and that clone at line 33, and no `curl` and no `sha256sum` anywhere
(**G**). So for the first commit of `MAN-tools.v1`'s life those three fields
were gated by nothing, and `source.url`'s own note — "The build fetches this
URL directly" — did not describe the tree it was committed into. That is the
same shape as `extra_build_packages` at `c68ec2a` in F-2: a value written
before the thing it describes was in the file. All three fields `hold` today.

### What is left

18 fields, in no category: per tool, `source.archive_size_bytes`,
`source.release`, `source.release_date`, `source.upstream`,
`source.mirror_previously_used`, `build.extra_build_packages`,
`binary.size_bytes` and `fixture.dataset`; and, for `bozorth3` only,
`invocation.default_max_minutiae` and `invocation.default_minminutiae`.

One of the 18 is coupled to a field that is covered:
`source.archive_size_bytes` cannot change while `source.archive_sha256` still
gates, because a file of a different length has a different digest. Nothing
compares the size, and it is counted here as uncovered, but a build cannot pass
with it wrong.

**What these numbers are not.** They count what the repository's mechanisms
cover, not how often those mechanisms ran.

At least one run of the script did happen in the interval, and it is recorded
inside the record chain rather than in captured output, so the Method's
exclusion of `docs/tools.md` does not touch it. `INV-005` F-11, at `6f58f9e`,
records `scripts/check_tools.sh` "run unchanged against the corpus copy" and
lists what passed: both binary digests against the manifest, the TIFF-to-PNG
conversion pixel-identical on all three images, the three mindtct counts and
`.xyt` digests, all eight mindtct outputs byte-identical on a repeat, all six
bozorth3 scores, symmetry on the three off-diagonal pairs, and five repeated
runs of one pair returning one value.

That list names the checks of sections 2, 3, 5, 6, 7, 8, 9 and 10 and no
others, and those are the eight sections the table above maps onto the 16
`manifest` and 13 `property (script)` fields. The list is of checks, not of
fields, and the correspondence is the table's, not the list's.

The `Dockerfile`'s sixteen ran whenever the image was built, which every
`docs/` transcript and every measurement in this record presupposes; how many
times is not established here.

**The script was run once more for this record, and passes.** `609c46c`'s
revision, taken out of git unchanged and pointed at `MAN-tools.v1.json` in
today's image (**S3**), completes all ten of its sections and exits 0: the two
binary digests match the manifest, the three mindtct counts and `.xyt` digests
match, the six bozorth3 scores match, and the property checks hold. That is the
29 fields it covers, confirmed end to end in one command. It says nothing
about the other 34, sixteen of which the `Dockerfile`
covers and eighteen of which nothing does.

## F-4 — the cross-check against MAN-tools.v2

**Every one of v1's 63 field paths exists in `MAN-tools.v2`** (**V**). Of the
63 values:

| | fields |
| --- | --- |
| carried into v2 with an identical value | 59 |
| changed in v2 | 4 |
| **total** | **63** |

The four that changed are the two `build.extra_build_packages` and the two
`fixture.dataset`, one of each per tool — the two this audit finds `fails` and
the two it finds `superseded`.

**Of the 59 carried unchanged, 14 had never been measured by anything** when v2
was issued: they are the 18 `none` rows of F-1 minus the four that changed, all
four of which are `none` rows. The other 45 are the 16 `manifest`, the 16
`property (build)` and the 13 `property (script)` rows.

**Every one of the 59 agrees with what is measured now.** v2's value for each
of the 59 is byte-identical to v1's, and F-1 re-measured 61 of v1's 63 — every
row except the two `superseded`, which by the Method's own definition had no
present-state measurement to take. Both of those are among the four that
changed, so all 59 are covered. Of the 59, 57 are `holds` and two are the
`historical` pair, whose value — the mirror's URL and commit — was checked with
**M** and still resolves to `master`.

**So no stale value was inherited into v2.** The audit was set up to find one
and there is none. The one field that could have carried a stale value into v2
is `extra_build_packages`, and v2 measured it instead: v2 records
`["build-essential", "ca-certificates", "cmake", "curl", "unzip"]`, which is
what **D** reads out of the `Dockerfile` today.

**One claim v2 makes about itself, measured against these counts.** v2's
`what_changed_from_v1` begins its second entry: "Every measurable value v1
carried was re-measured against the image this version was issued against, by
`scripts/check_tools.sh`", and then enumerates them — the two binary digests,
the linked libraries, the TIFF-to-PNG pixel identity, the mindtct fixture and
its determinism, the whole bozorth3 matrix, its symmetry and its determinism.
That enumeration names the same eight sections of the script that `INV-005`
F-11 names, and the table in F-3 maps those eight onto the 29 fields F-1 places
in the `manifest` and `property (script)` categories. It names the script alone
and no other mechanism. The remaining 34 of the 63 were not among them; this
record measured 32 of those 34 with the blocks named in F-1, so they were
measurable at the time, and the other two are the `superseded` pair.

**What changed about the coverage of those same 63 paths, after v2 was
issued.** Not by v2 itself: v1 and v2 carry the same value for every field
whose coverage moved, and the coverage of the 63 was still 16 in the
`manifest` category on the day v2 was issued. It moved at `56f53b7`, the next
commit, which rewrote the verification script (**S2**). That revision reads two
more of the 63 out of the manifest than `609c46c` did:
`runtime.shared_libraries` for both tools moved from `property (script)` to
`manifest`, because the linked libraries are now compared as a set against the
list the manifest carries rather than against a hardcoded expectation of libm
and libc. So the `manifest` category over these 63 paths goes from 16 to 18.

**The count of fields nothing measures does not move.** It is 18 before and
after, which is a different 18 from the one in the sentence above and shares
nothing with it but the number. Checked both ways against `56f53b7`, because
reading a field out of the manifest is not the only route out of `none`: the
new revision reads none of those 18 out of the manifest, and none of its new
sections measures a property any of them asserts — its additions are a source
blob id, composed identities, a library-resolution check, an exit-code table
and a fixture, all of them for fields v1 does not carry.

## F-5 — the same question of the other two frozen manifests, as a count

Counted the same way, by walking each file for objects carrying both a `value`
and a `status` (**T**):

| manifest | fields with a value and a status | statuses | measured by anything, at `641bfb6` |
| --- | --- | --- | --- |
| `manifests/MAN-minutia.v1.json` | 8 | 8 `VERIFIED` | nothing reads the file |
| `manifests/MAN-fvc2002.v1.json` | 124 | 105 `VERIFIED`, 19 `UNVERIFIED` | nothing reads the file |
| `manifests/MAN-tools.v1.json` | 63 | 61 `VERIFIED`, 2 `UNVERIFIED` | nothing reads the file either; see below |
| `manifests/MAN-tools.v2.json` | 137 | 136 `VERIFIED`, 1 `UNVERIFIED` | not counted here |

**The third row needs its own sentence, because the column is present tense.**
At `641bfb6` nothing in the repository reads `MAN-tools.v1.json`:
`scripts/check_tools.sh` defaults to `MAN-tools.v2.json` and the `Makefile`
passes no override, so the file is reachable only by setting `MANIFEST=` by
hand, which is what block **S3** did. The counts of F-3 — 16 read from the
manifest, 29 more measured as properties, 18 measured by nothing — are about
the interval that ends at this record, not about the state of the tree at its
end.

`MAN-minutia.v1.json`'s eight are all under `x-manifest.asserted_numbers`;
`MAN-fvc2002.v1.json`'s 124 are 11 under `distribution`, 12 under
`index_files`, 97 under `subsets` and 4 under `observations`.

**Nothing executable in this repository reads either file.** A search of every
`.sh`, `.py`, `.c` and the `Makefile` for the two manifest names returns
nothing outside `quality/`, and the same search for `checksums` over the same
four file types returns nothing either (**Q**).

So of the 132 fields those two manifests carry between them, **the number that
any mechanism in this repository re-measures is 0**. Their contents are not
audited here.

## Reproducing this

Every block below was run on 2026-09-07 against the tree at `641bfb6`. The
paths outside the repository are the author's; `$SP` is a scratch directory
outside the tree and `$FIX` is the read-only mount of the FVC2002 Db1_b
images, which never enter the repository.

**D — the `Dockerfile`, read at this commit.**

    grep -n '^FROM' Dockerfile
    sed -n '/AS nbis-builder/,/^WORKDIR \/src/p' Dockerfile | grep -A9 'apt-get install'
    grep -n 'setup.sh\|sed -i .142s\|make config && make it\|^COPY --from=' Dockerfile
    grep -n 'NBIS_URL\|NBIS_SHA256\|sha256sum -c' Dockerfile

Five values per tool were then compared as strings rather than read by eye:
`build.base_image`, `build.setup`, `build.patch`, `build.make` and
`build.artifact_copied`, each searched for as a verbatim substring of the
`Dockerfile`, the line it was found on being the line the table cites.
`binary.path` is not among them; it is checked in the image by block **I**.

    python - <<'PY'
    import json
    d = json.load(open("manifests/MAN-tools.v1.json", encoding="utf-8"))
    lines = open("Dockerfile", encoding="utf-8").read().splitlines()
    def find(sub):
        return next((i for i, l in enumerate(lines, 1) if sub in l), None)
    for tool in ("mindtct", "bozorth3"):
        t = d["tools"][tool]
        for k in ("url", "archive_sha256"):
            print(tool, k, find(t["source"][k]["value"]))
        b = t["build"]
        for k in ("base_image", "setup", "patch", "make"):
            print(tool, k, find(b[k]["value"]))
        src, dst = [x.strip() for x in b["artifact_copied"]["value"].split("->")]
        print(tool, "artifact_copied",
              find("COPY --from=nbis-builder %s %s" % (src, dst)))
        print(tool, "extra_build_packages",
              [find(x) for x in b["extra_build_packages"]["value"]])
    PY

It prints, for both tools, `url` 38, `archive_sha256` 39, `base_image` 15,
`setup` 50, `patch` 59, `make` 66, and `artifact_copied` 181 for `mindtct` and
182 for `bozorth3`: every one of those seven values present verbatim, at the
line the table cites. For `extra_build_packages` it prints
`[19, 20, 21, 79]` for both tools, and that line is why a substring search is
not enough for a list of package names: 19, 20 and 21 are `build-essential`,
`ca-certificates` and `cmake` in the NBIS builder stage, but 79 is a comment
line inside the FingerJetFXOSE builder stage that names `git` — that stage,
added at `40f172d`, does install `git`, at line 87, and it is not the stage
this field describes. The finding of rows 13 and 43 therefore rests on the
second command of this block, which prints the NBIS stage's own `apt-get` list:
`build-essential`, `ca-certificates`, `cmake`, `curl`, `unzip`. `git` is not in
it, and `curl` and `unzip` are not in the field.

`binary.path` is not in the loop; it is checked in the image by block **I**.

**H — the archive URL, headers only.**

    curl -sSI --max-time 60 https://nigos.nist.gov/nist/nbis/nbis_v5_0_0.zip

It answered `HTTP/1.1 200 OK`, `Content-Length: 52595795`, `last-modified: Tue,
03 Mar 2015 20:57:05 GMT`, `etag: "3228c53-5106893bf8a40"`.

**A — the archive itself.**

    curl -sS --max-time 600 -o "$SP/nbis.zip" https://nigos.nist.gov/nist/nbis/nbis_v5_0_0.zip
    stat -c '%s' "$SP/nbis.zip"          # 52595795
    sha256sum "$SP/nbis.zip"             # 0adf8ab0f6b0e4208de50ca00ba21d3d77112ecd66288757ddfed21f6bee92c3
    head -c4 "$SP/nbis.zip" | xxd        # 504b 0304

**P — the publisher's page.** Two commands: one to fetch it and report the
status and the URL it ended at, one to strip the tags and print the paragraph.

    curl -sS -L --max-time 120 -o "$SP/nigos.html" \
      -w 'http=%{http_code} final=%{url_effective} bytes=%{size_download}\n' \
      https://www.nist.gov/itl/iad/image-group/products-and-services/image-group-open-source-server-nigos

    python - "$SP/nigos.html" <<'PY'
    import re, sys
    h = open(sys.argv[1], encoding="utf-8", errors="replace").read()
    t = re.sub(r"\s+", " ", re.sub(r"&nbsp;", " ", re.sub(r"<[^>]+>", " ", h)))
    i = t.find("NBIS Software")
    print(t[i:i + 320])
    PY

The first printed `http=200`, `bytes=105548` and a `final=` of
`https://www.nist.gov/itl/iad/btg/products-and-services/image-group-open-source-server-nigos`,
so the URL in the command redirects; that is a fact about the page and about no
field. The second printed:

    NBIS Software See the NBIS home page for more information. Release 5.0.0 -
    Test 5.0.0 - stable version - (03/04/2015) - changelog Release 4.2.0 - Test
    4.2.0 - stable version - (10/30/2013) Release 4.1.0 - ...

5.0.0 is the newest release listed and it still carries `(03/04/2015)`.

**R — the NBIS builder stage rebuilt from scratch.** It re-runs the fetch, the
checksum gate, `setup.sh`, the patch and `make it`, and produces the two
binaries from the archive rather than reading them out of a cached layer.

    MSYS_NO_PATHCONV=1 docker build --progress=plain --no-cache-filter nbis-builder \
      -t dactyloscopy:audit .
    MSYS_NO_PATHCONV=1 docker run --rm dactyloscopy:audit \
      sha256sum /usr/local/bin/mindtct /usr/local/bin/bozorth3
    docker image inspect dactyloscopy:audit --format '{{.Id}}'
    docker image inspect dactyloscopy:dev   --format '{{.Id}}'

It printed `/tmp/nbis.zip: OK` at the fetch step, and at the patch step

    CFLAGS	:= -O2 -w -ansi -fcommon -D_POSIX_SOURCE $(ENDIAN_FLAG) $(NBIS_JASPER_FLAG) $(NBIS_OPENJP2_FLAG) $(NBIS_PNG_FLAG) $(ARCH_FLAG)

and the two binaries came out at
`4d587263e242781e97afe236f5c8c46f275eb617c42e47f34d969c536c122c53` and
`24fb809830f6a940dc27290b700b1d8e581a1f5c2c6bb9a97a856f96e8cdb287`, the digests
the manifest records. The two `image inspect` calls printed the same id,
`sha256:e0ded5a5dcc8f594df58ab904be76605ad26492da834130592091b1348f7c3fc`. The
sizes 960024 and 57784 are not R's: nothing here runs `stat`, and they come
from block **I**, which is what F-1 rows 17 and 47 cite.

**M — the mirror, without cloning it.**

    git ls-remote https://github.com/lessandro/nbis

`3d3b05f0144b706bed56407957bc00779baf2fa5` is still both `HEAD` and
`refs/heads/master`.

**X — the archive against the mirror, re-run.** In a throwaway image from the
same pinned base plus `git` and `unzip`, with the archive of **A** mounted
read-only. The script unzips the archive, clones the mirror at the pinned
commit, removes `.git`, and compares every path present in both.

    printf 'FROM python:3.12-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254\nRUN apt-get update && apt-get install -y --no-install-recommends git unzip ca-certificates && rm -rf /var/lib/apt/lists/*\n' > "$SP/cmp.Dockerfile"
    docker build -q -f "$SP/cmp.Dockerfile" -t dactyloscopy:cmp "$SP"
    docker run --rm -v "$SP:/sp:ro" dactyloscopy:cmp bash /sp/mirror_cmp.sh

with `mirror_cmp.sh`. The archive unpacks into a top-level `Rel_5.0.0/` and the
clone is flat, so the walk starts one directory lower on the archive side; that
alignment is what makes the two path sets comparable at all.

    unzip -q /sp/nbis.zip -d /tmp/w/official
    git -c core.autocrlf=false clone -q https://github.com/lessandro/nbis /tmp/w/mirror
    git -C /tmp/w/mirror -c core.autocrlf=false checkout -q 3d3b05f0144b706bed56407957bc00779baf2fa5
    rm -rf /tmp/w/mirror/.git
    python3 - <<'PY'
    import os

    def files(root):
        out = {}
        for dirpath, _d, filenames in os.walk(root):
            for f in filenames:
                p = os.path.join(dirpath, f)
                out[os.path.relpath(p, root).replace(os.sep, "/")] = p
        return out

    official = files("/tmp/w/official/Rel_5.0.0")   # the alignment
    mirror = files("/tmp/w/mirror")
    common = sorted(set(official) & set(mirror))
    print(len(official), len(mirror), len(common),
          len(set(official) - set(mirror)), len(set(mirror) - set(official)))

    identical = endings = different = cr_mirror = 0
    code_total = code_diff = 0
    for rel in common:
        a = open(official[rel], "rb").read()
        b = open(mirror[rel], "rb").read()
        is_code = rel.endswith((".c", ".h", ".mak")) or \
            os.path.basename(rel) in ("Makefile", "makefile")
        code_total += is_code
        if a == b:
            identical += 1
        elif a.replace(b"\r\n", b"\n") == b.replace(b"\r\n", b"\n"):
            endings += 1
            cr_mirror += b.count(b"\r") > a.count(b"\r")
        else:
            different += 1
            code_diff += is_code
    print(identical, endings, different, cr_mirror, code_total, code_diff)
    PY

and again with `core.autocrlf=true` in both `git` invocations and nothing else
changed. The first line printed `3879 3879 3879 0 0` in both runs. The second
printed `3879 0 0 0 2302 0` with the conversion off and `593 3286 0 3286 2302 0`
with it on, which is the table in F-1. The 2302 is the count of files whose
name ends `.c`, `.h` or `.mak` or is `Makefile`; `docs/tools.md` records 2179
for an earlier run whose file set this record cannot read.

**I — the image, measured from the inside.** One shell script, run against the
image with the fixture mounted read-only, writing only into a `mktemp -d` of
its own inside the container. No image, minutia or template leaves it: the
container is `--rm`, the fixture mount is `:ro`, and the only mount that could
be written to is the repository's, which is not mounted at all here.

    docker run --rm -v "$SP:/sp:ro" -v "$FIX:/fixture:ro" dactyloscopy:dev \
      bash /sp/audit_image.sh

The script is a sequence of one-liners over `W="$(mktemp -d)"`, `FIX=/fixture`.
Each is given below with what it printed, so the block is reproducible without
the file.

    for t in mindtct bozorth3; do command -v $t; sha256sum /usr/local/bin/$t; \
      stat -c '%s' /usr/local/bin/$t; done
      /usr/local/bin/mindtct
      4d587263e242781e97afe236f5c8c46f275eb617c42e47f34d969c536c122c53  /usr/local/bin/mindtct
      960024
      /usr/local/bin/bozorth3
      24fb809830f6a940dc27290b700b1d8e581a1f5c2c6bb9a97a856f96e8cdb287  /usr/local/bin/bozorth3
      57784

    for t in mindtct bozorth3; do ldd /usr/local/bin/$t; done
      both print four lines: linux-vdso.so.1, libm.so.6, libc.so.6 and
      /lib64/ld-linux-x86-64.so.2, and no other "=>" entry

`ldd` prints four names and the field lists three, so the comparison needs a
rule and it is this: a line beginning `linux-vdso` is dropped, a line with a
`=>` contributes the name before it, and a line beginning `/` contributes its
basename. That maps the four onto exactly `libm.so.6`, `libc.so.6` and
`ld-linux-x86-64.so.2`, which is the field's value. The rule is not invented
here for the comparison: it is the one `scripts/check_tools.sh` at `56f53b7`
applies in its own section 6, where the same list is read out of the manifest
(**S2**).

    mindtct 2>&1 | head -4
      Invalid number of arguments on command line
      Usage : mindtct [-b] [-m1] <finger_img_in> <oroot>
              -b  = contrast boost image
              -m1 = output "*.xyt" according to ANSI INCITS 378-2004
    bozorth3 2>&1 | grep -E '^\s+-m1|max-minutiae|minminutiae'
      -m1                    all xyt files use representation according to ANSI INCITS 378-2004
      -n <max-minutiae>      set maximum number of munitiae to use from any file [150]; legal range is [0,200]
             minminutiae=#   set minimum number of munitiae for match score to be more than 0 [10]

    python3 -c 'from PIL import Image; im=Image.open("'$FIX'/101_1.tif").convert("L"); \
      im.save("'$W'/probe.png"); im.save("'$W'/probe.pgm")'
    cp "$FIX/101_1.tif" "$W/probe.tif"
    for e in png tif pgm; do mindtct "$W/probe.$e" "$W/probe_$e"; echo "$e $?"; done
      png 0
      ERROR : read_and_decode_grayscale_image : <tmp>/probe.tif : image type UNKNOWN : not supported
      tif 253
      ERROR : read_and_decode_grayscale_image : <tmp>/probe.pgm : image type UNKNOWN : not supported
      pgm 253

    ls "$W" | grep '^probe_png\.' | sed 's/.*\.//' | sort | tr '\n' ' '; \
      ls "$W" | grep -c '^probe_png\.'
      brw dm hcm lcm lfm min qm xyt 8

    python3 -c 'import numpy as np
    from PIL import Image as I
    for n in ("101_1","101_2","102_1"):
        t = I.open(f"'$FIX'/{n}.tif"); t.convert("L").save(f"'$W'/{n}.png")
        print(n, np.array_equal(np.array(t), np.array(I.open(f"'$W'/{n}.png"))))'
      101_1 True
      101_2 True
      102_1 True

    for n in 101_1 101_2 102_1; do mindtct "$W/$n.png" "$W/$n"; \
      echo "$n $(wc -l < "$W/$n.xyt") $(sha256sum "$W/$n.xyt" | cut -d' ' -f1)"; done
      101_1 33 4aebdeeeab9fe3dd21f0bf2815df09f92da00c2c6ed6d906c0e2a61955b46437
      101_2 24 a9baeb93db9fe96b4a686032e5bb94fc044945081140b147471ee13015e611bc
      102_1 62 ac7a7d3e878848d491e82ca488f7c1dd4fe99742d8ecac46b150ab60ead2c16e
      (33, 24 and 62 are all above the floor of 10 and below the cap of 150)

    for p in "101_1 101_1" "101_1 101_2" "101_1 102_1" "101_2 101_2" \
             "101_2 102_1" "102_1 102_1"; do set -- $p; \
      echo "$1 $2 $(bozorth3 "$W/$1.xyt" "$W/$2.xyt")"; done
      216, 60, 9, 163, 4, 499 in that order
    for p in "101_1 101_2" "101_1 102_1" "101_2 102_1"; do set -- $p; \
      echo "$(bozorth3 "$W/$1.xyt" "$W/$2.xyt") $(bozorth3 "$W/$2.xyt" "$W/$1.xyt")"; done
      60 60 / 9 9 / 4 4
    for i in 1 2 3 4 5; do bozorth3 "$W/101_1.xyt" "$W/101_1.xyt"; done
      216 216 216 216 216

    awk 'NR==1{print NF}' "$W/101_1.xyt"
      4

**N — the generated `rules.mak`, in the builder stage.** The `grep` matches
three lines and the `sed` prints a fourth; all four are given.

    docker build --target nbis-builder -t dactyloscopy:nbis-audit .
    docker run --rm dactyloscopy:nbis-audit bash -c \
      "grep -n 'NBIS_PNG_FLAG' /src/rules.mak; sed -n '142p' /src/rules.mak"
    84:NBIS_PNG_FLAG			:= -D__NBIS_PNG__
    142:CFLAGS	:= -O2 -w -ansi -fcommon -D_POSIX_SOURCE $(ENDIAN_FLAG) $(NBIS_JASPER_FLAG) $(NBIS_OPENJP2_FLAG) $(NBIS_PNG_FLAG) $(ARCH_FLAG)
    143:#CFLAGS	:= -g $(ENDIAN_FLAG) $(NBIS_JASPER_FLAG) $(NBIS_PNG_FLAG) $(ARCH_FLAG)
    CFLAGS	:= -O2 -w -ansi -fcommon -D_POSIX_SOURCE $(ENDIAN_FLAG) $(NBIS_JASPER_FLAG) $(NBIS_OPENJP2_FLAG) $(NBIS_PNG_FLAG) $(ARCH_FLAG)

The commented-out line 143 is the project's own, untouched by the patch.

**G — the two histories of F-2.**

The dates in both tables come from the `--date=short` format of the first and
third commands; the package sets from the second; the field counts from the
fourth, which runs the walk of block **T** over the file as it stood at each
commit; and the two spans from the sixth.

Two of these commands need a word about their shape. The second scopes its
`awk` to the stage that begins `AS nbis-builder` and stops at the next `FROM`,
because from `40f172d` onward the file has a second builder stage whose own
`apt-get` list is `build-essential ca-certificates cmake git` — the very set
F-2 concludes left the NBIS stage at `2ac93d4`. An unscoped `awk` prints both
lists with nothing to say which is which. The third omits `--reverse`, because
`--follow` and `--reverse` together lose the rename and print only `ed64c9e`;
without `--reverse` it prints all three commits, newest first.

    git log --reverse --format='%h %ad %s' --date=short -- Dockerfile
    for c in $(git log --reverse --format='%h' -- Dockerfile); do echo "== $c"; \
      git show $c:Dockerfile \
        | awk '/AS nbis-builder|^FROM/{s=($0 ~ /AS nbis-builder/)} \
               s&&/apt-get install/{f=1;next} f&&/rm -rf/{f=0} f'; done
    git log --format='%h %ad %s' --date=short --follow \
      -- manifests/MAN-tools.v1.json
    for r in c68ec2a:manifests/tools.json \
             ed64c9e:manifests/MAN-tools.v1.json \
             4eeffa2:manifests/MAN-tools.v1.json; do \
      git show "$r" | python -c '
    import json, sys
    d = json.load(sys.stdin)["tools"]
    def count(o):
        if isinstance(o, dict):
            if "value" in o and "status" in o: return 1
            return sum(count(v) for v in o.values())
        return 0
    print("mindtct", count(d["mindtct"]),
          "bozorth3", count(d.get("bozorth3", {})),
          "total", count(d))'; done
    git rev-parse 4464e90:Dockerfile c68ec2a:Dockerfile
    git rev-list --count 2ac93d4^..641bfb6; git rev-list --count 2ac93d4..4eeffa2
    git show ed64c9e:Dockerfile | grep -nE 'curl|sha256sum|git clone|NBIS_REPO'

The fourth prints, for the three commits in order:

    mindtct 26 bozorth3 0 total 26
    mindtct 30 bozorth3 0 total 30
    mindtct 30 bozorth3 33 total 63

The fifth prints one blob id twice. The sixth prints 30 and 3. The seventh
prints two lines and no others, the `ARG` naming the mirror at line 31 and the
`git clone` of it at line 33:

    31:ARG NBIS_REPO=https://github.com/lessandro/nbis
    33:RUN git clone "${NBIS_REPO}" . \

**S and S2 — the two revisions of the verification script.**

    git show 609c46c:scripts/check_tools.sh
    git show 56f53b7:scripts/check_tools.sh

**S3 — the v1-era script, run against v1 today.** Taken out of git unchanged,
into a scratch directory outside the tree, and pointed at the manifest it was
written for. The repository is mounted read-only so that the run cannot write
into it.

    git show 609c46c:scripts/check_tools.sh > "$SP/check_tools_609c46c.sh"
    docker run --rm -v "<repo>:/work:ro" -v "$SP:/sp:ro" -v "$FIX:/fixture:ro"       -w /work -e MANIFEST=/work/manifests/MAN-tools.v1.json       dactyloscopy:dev bash /sp/check_tools_609c46c.sh /fixture

It printed its ten section headers, ended `all checks passed`, and exited 0.

**T — the field walk, and the table of F-1.** A field is an object carrying
both a `value` and a `status`; the walk descends into every other object and
into lists, and does not descend into a field once it has found one.

    python - <<'PY'
    import json
    d = json.load(open("manifests/MAN-tools.v1.json", encoding="utf-8"))
    out = []
    def walk(o, path):
        if isinstance(o, dict):
            if "value" in o and "status" in o:
                out.append((path, o["status"])); return
            for k, v in o.items(): walk(v, (path + "." + k) if path else k)
        elif isinstance(o, list):
            for i, v in enumerate(o): walk(v, "%s[%d]" % (path, i))
    walk(d, "")
    print(len(out))
    PY

It prints 63 for `MAN-tools.v1.json`, and the same walk over the other three
manifests gives the counts of F-5. The generator that emitted the F-1 table
runs this walk and asserts that the set of paths it is about to print equals
the set the walk finds, so the table cannot silently omit a field or invent
one; the assertion held when the table was produced.

**V — v1 against v2.** The walk of **T** over both files, keyed by path, with
each shared path's value compared as its JSON encoding.

    python - <<'PY'
    import json
    def flat(p):
        d = json.load(open(p, encoding="utf-8")); out = {}
        def walk(o, path):
            if isinstance(o, dict):
                if "value" in o and "status" in o:
                    out[path] = json.dumps(o["value"], sort_keys=True); return
                for k, v in o.items(): walk(v, (path + "." + k) if path else k)
            elif isinstance(o, list):
                for i, v in enumerate(o): walk(v, "%s[%d]" % (path, i))
        walk(d, "")
        return out
    v1 = flat("manifests/MAN-tools.v1.json")
    v2 = flat("manifests/MAN-tools.v2.json")
    shared = sorted(set(v1) & set(v2))
    print(len(v1), len(v2), len(shared), len(set(v1) - set(v2)))
    same = [k for k in shared if v1[k] == v2[k]]
    print(len(same), len(shared) - len(same))
    for k in shared:
        if v1[k] != v2[k]: print(k)
    PY

It prints `63 137 63 0`, then `59 4`, then the four paths: both
`build.extra_build_packages` and both `fixture.dataset`.

**Q — what reads the other manifests.** Both searches cover the same four file
types; an earlier form of the second omitted `*.c`.

    grep -rn 'MAN-fvc2002\|MAN-minutia' --include='*.sh' --include='*.py' \
      --include='Makefile' --include='*.c' . | grep -v '^./quality/'
    grep -rn 'checksums' --include='*.sh' --include='*.py' \
      --include='Makefile' --include='*.c' .

Both return nothing, and both exit 1.

## What was left unchecked

- **The two `superseded` fields were not measured at all.** Rows 23 and 54
  carry a verdict and a pointer, not a measurement. Whether `FVC2002 Db1_b` was
  ever a wrong description of the directory those images were read from is not
  established here; what is established is that a later manifest replaced it
  with a subset id.
- **The judgement in F-1's last column.** Which mechanism counts as having
  "measured" a field is a reading of what a failing command would have implied,
  not a measurement of its own. The criterion is stated in the Method, the four
  rows where it is most arguable are named in F-3, and a reader who applies it
  differently gets different counts from the same table.
- **The correction of any field.** A manifest is immutable and this record
  produces no version. `MAN-tools.v1.json` is not edited by this task and
  neither is `MAN-tools.v2.json`.
- **Whether correcting a frozen manifest in a later version, rather than
  elsewhere, is the right practice.** That is a decision, no refinement takes
  it, and this record does not.
- **Why each expired field was not revisited.** That is a question about
  process rather than a measurement. F-2 records when, not why.
- **The contents of `MAN-minutia.v1.json` and `MAN-fvc2002.v1.json`** beyond
  the counts of F-5.
- **The 74 fields `MAN-tools.v2.json` carries that v1 does not**, including the
  whole `iso-extract` entry. F-4 audits only the 63 paths the two share.
- **How many times `scripts/check_tools.sh` ran between the manifest being
  issued and this record.** F-3 establishes that at least one run happened,
  from `INV-005` F-11, and measures what the script covers. It does not count
  the runs: the remaining evidence for that is captured output, which the
  Method excludes.
- **Every `note` except the five read in F-1.** Notes carry no status and get
  no verdict; five were read because they carry numbers or assertions a reader
  would take for measurements, and the rest were not read at all.
- **Whether `2015-03-04` is the release date.** What was measured is that the
  publisher's page still prints `(03/04/2015)` beside release 5.0.0, and that
  the server's `last-modified` for the archive is one day earlier. Which of the
  two is the release date is not established here and was not established when
  the field was written.
- **The figure `2179` in `docs/tools.md`** for the number of C sources, headers
  and makefiles compared against the mirror. Block **X** counts 2302 for the
  same corpus, and the difference is the definition of the file set — this
  record's set is `.c`, `.h`, `.mak` and files named `Makefile` or `makefile`,
  and what the earlier set was is not recorded anywhere this record could read.
  Both counts report 0 differing in content.
- **Whether the mirror's stored blobs are LF for every file**, as opposed to
  the 3879 compared here being byte-identical to the archive when checked out
  with the conversion off. The measurement covers the paths present in both
  trees and nothing else.
- **`MAN-tools.v2.json`'s own exposure.** F-4 reports that the current script
  reads 18 of the 63 shared paths from the manifest; it does not count the
  coverage of v2's other fields, and the `iso-extract` entry in particular was
  written by the task immediately before this one and audited by nothing since.
