# INV-005 — What the FVC2002 copy on this machine consists of

Date: 2026-09-07

## Numbering

This record takes 005, the next free investigation number after `INV-004`. The
reservation at 001 is explained in `REF-002`.

## Question

A copy of the FVC2002 distribution was placed where the container expects input
data. Three questions about it, in the order they can be answered:

1. Is the copy faithful to the tree it was copied from?
2. What does the corpus consist of — how many files, of what dimensions, and
   are any two of them the same file?
3. Is the tree the official distribution?

The third is the one that cannot be answered here, and most of what follows
exists so that the difference between the first and the third is not blurred.

## Method

**The source.** A tree on this machine at
`C:\Users\yurii\Downloads\fingerprint_experiments\data\FVC2002`, holding
`Dbs/`, `Doc/` and `Src/`. It reached this machine through a third-party
redistribution, not from the organisers.

**The copy.** `robocopy /E /COPY:DAT /XJ`, which copies bytes and does not
follow junctions. It reported 3528 files copied, 0 failed, 0 mismatched, 14
directories, 431.19 MB. No repacking, no renaming, no flattening: the
distribution's own layout is what keeps this copy comparable with anyone
else's.

The copy is a copy and not a link. `find -type l` over the target returns
nothing, and the source was checked for a reparse point before the copy began.
A junction inside a directory Docker mounts surfaces as a silently empty mount
rather than an error, so this is checked rather than assumed.

**The target.** `$LABDATA/raw/fvc2002`, with `$LABDATA` resolved as
`.env.example` specifies. `$LABDATA/derived` was created empty. Nothing under
either is committed.

**The measurements** were made from inside the runtime image, with
`/data/raw` mounted read-only, by one pass over every file. Pillow reads each
TIFF's header for its dimensions and mode; the digest is over the whole file.
Nothing was sampled: every count below is over all 3520 images.

No pixel value, no image and no minutia appears in this record or in anything
it produced. The per-file lists carry a digest and a file name.

## Measured facts

Status `VERIFIED` throughout this section: each was measured here, over the
whole corpus, by the commands in "Reproducing this".

### F-1 — The tree — VERIFIED

Three directories at the top: `Dbs`, `Doc`, `Src`. **3528** files in total.

- `Doc/` holds one file, `FVC2002_results_summary.pdf`.
- `Src/` holds three: `inc/fvc2002.h`, `skeletons/Enroll_XXXX.c` and
  `skeletons/Match_XXXX.c`.
- `Dbs/` holds eight subset directories and four index files.

Summed over every file in the tree: **452 143 653** bytes, of which
**451 890 560** are the 3520 images. The remainder is the four index files, the
summary PDF and the three participant skeleton sources.

### F-2 — Counts, and that nothing else is present — VERIFIED

| subset | directory | files | `.tif` | anything else |
| --- | --- | --- | --- | --- |
| DB1_A | `Dbs/Db1_a` | 800 | 800 | 0 |
| DB1_B | `Dbs/Db1_b` | 80 | 80 | 0 |
| DB2_A | `Dbs/Db2_a` | 800 | 800 | 0 |
| DB2_B | `Dbs/Db2_b` | 80 | 80 | 0 |
| DB3_A | `Dbs/Db3_a` | 800 | 800 | 0 |
| DB3_B | `Dbs/Db3_b` | 80 | 80 | 0 |
| DB4_A | `Dbs/Db4_a` | 800 | 800 | 0 |
| DB4_B | `Dbs/Db4_b` | 80 | 80 | 0 |

**3520** images. 800 in each `_A` subset, 80 in each `_B`. No file with any
other extension in any subset directory.

### F-3 — Dimensions, on every image — VERIFIED

Each subset contains exactly **one** distinct image size, and it is the same
for the `_A` and `_B` halves of a database:

| database | measured size | distinct sizes found | mode | file size |
| --- | --- | --- | --- | --- |
| DB1 | 388 x 374 | 1 | `L` | 145 624 bytes, every file |
| DB2 | 296 x 560 | 1 | `L` | 166 272 bytes, every file |
| DB3 | 300 x 300 | 1 | `L` | 90 512 bytes, every file |
| DB4 | 288 x 384 | 1 | `L` | 111 104 bytes, every file |

All 3520 checked, none sampled. **Nothing differs**: no image in any subset has
a size other than its database's. Every image is 8-bit greyscale, and within a
subset every file is the same number of bytes, which is what an uncompressed
TIFF of a fixed size gives.

DB1's measured size agrees with `INV-002` F-1, which measured the same thing on
`Db1_b` for a different purpose.

The counts and the per-file sizes reconstruct the total independently: 880
files per database times the four file sizes above sums to **451 890 560**
bytes, which is the image total measured in F-1. A wrong count or a wrong file
size in any of the four rows would break that equality.

### F-4 — The copy is faithful to the source tree — VERIFIED

The four index files were digested on the source before the copy and on the
target after it. All four agree, and all four agree with the values recorded in
the brief that commissioned this work:

    a90b5c6a1d731bf013aa9284c237f9c409be2b2e67dcff15c0c538f7a9724c1b  index_a.MFA
    cbcbd83d5b121e48b44bd3201a92f18b7adcb085c7530bdf7c8b253f1a1105f6  index_a.MFR
    684bff5e66cac5ebab73f8a5f908ad8315eb76d40b803ae83fbc94efeedfd044  index_B.MFA
    eeffbe180b1ee48203dfb3757b2c31b750869ef99c56360be3af08d16035aebe  index_B.MFR

These are text files carrying CRLF, so they are the files a line-ending
normalisation would have changed. It did not.

**What this establishes and what it does not.** It establishes that the bytes
on the target are the bytes on the source. It establishes nothing about whether
the source is the official distribution, because the digests were taken from
that same source: using them for authenticity would be circular. See R-1.

### F-5 — Every file digested, and the lists check — VERIFIED

One `sha256sum`-format list per subset, under
`manifests/checksums/fvc2002/`. Run against the mounted corpus, one command per
subset:

    DB1_A   800 OK, 0 not OK
    DB1_B    80 OK, 0 not OK
    DB2_A   800 OK, 0 not OK
    DB2_B    80 OK, 0 not OK
    DB3_A   800 OK, 0 not OK
    DB3_B    80 OK, 0 not OK
    DB4_A   800 OK, 0 not OK
    DB4_B    80 OK, 0 not OK
    ---
    3520 files verified, 0 failures

The lists themselves:

    11e365c8af1daee531cdc5619b421517562ab8588a400cad1c099fd13acca7d2  DB1_A.sha256
    4127e484a99b90ba2def64aad7315dffa88d42ba1a2412f64412b2f8674c7dd9  DB1_B.sha256
    8161073dbdcdad700efc83c796c7fc0cbdba5b4be9e9efe6d2a5181141cdd8a0  DB2_A.sha256
    daf7ab5d45895bd53ce77c2767174d604b9b799fc9845fe203e0e3c3b184eef6  DB2_B.sha256
    e0e5e1c3672bfcd514b0d4a856911d7e207a11df08fb7b8a618a261e97cfdfce  DB3_A.sha256
    189b7ec60520353913d52e8f90a0f96f36a922d1a9538c481cbc585525be43c6  DB3_B.sha256
    677137822a90e4f93cb4928c6bb38beec09c17fab9db05535610770b929fc892  DB4_A.sha256
    860d8cdfc5c63863ec6e3eeb90bdc9ad6c9dc318e312377e7e082d335427d404  DB4_B.sha256

Each list is ASCII, LF-terminated, one line per file, sorted by name.

### F-6 — Exactly one pair of byte-identical files in the whole corpus — VERIFIED

Searched within each subset and across all eight:

- **DB1_A: `81_5.tif` and `81_7.tif` share a digest.**
- DB1_B, DB2_A, DB2_B, DB3_A, DB3_B, DB4_A, DB4_B: **no two files share a
  digest** in any of them.
- Pairs spanning two different subsets: **0**.
- **3519** distinct digests over **3520** files, which is the same statement
  counted the other way.

### F-7 — The index files — VERIFIED

| file | bytes | lines | line ending | fields per line |
| --- | --- | --- | --- | --- |
| `index_a.MFA` | 93 258 | 4950 | CRLF on every line | 2 |
| `index_a.MFR` | 52 752 | 2800 | CRLF on every line | 2 |
| `index_B.MFA` | 945 | 45 | CRLF on every line | 2 |
| `index_B.MFR` | 5 880 | 280 | CRLF on every line | 2 |

Every line names two `.tif` files. What each file references:

| file | distinct file names referenced | all `.tif` |
| --- | --- | --- |
| `index_a.MFA` | 100 | yes |
| `index_a.MFR` | 800 | yes |
| `index_B.MFA` | 10 | yes |
| `index_B.MFR` | 80 | yes |

### F-8 — The duplicated pair is one of the genuine comparisons — VERIFIED

The question was whether `81_5.tif 81_7.tif` appears in `index_a.MFR`. It does,
exactly once, as one line:

    81_5.tif 81_7.tif

It does not appear in `index_a.MFA`.

**What follows, as a deduction rather than a prediction.** The two files are
byte-identical (F-6). A deterministic extractor is a function of the file's
bytes, so it returns the same template for both; `INV-002` F-15 measured that
determinism for the extractor in this repository's image, and
`manifests/MAN-tools.v1.json` records it. A deterministic matcher given two
identical templates therefore performs a self-comparison. So one of the 2800
comparisons `index_a.MFR` defines is a self-comparison for any deterministic
pipeline, not only for ours.

This record does not say what score that produces. It says the comparison is of
a file with itself.

### F-9 — No image in the corpus declares a resolution — VERIFIED

Read from the TIFF headers of all 3520 files, one subset at a time:

| tag | value found | in how many files |
| --- | --- | --- |
| 282 `XResolution` | absent | 3520 of 3520 |
| 283 `YResolution` | absent | 3520 of 3520 |
| 296 `ResolutionUnit` | absent | 3520 of 3520 |
| 259 `Compression` | 1, uncompressed | 3520 of 3520 |
| 262 `PhotometricInterpretation` | 1, black is zero | 3520 of 3520 |

Not one file in any subset carries a resolution tag. **The resolution of these
images is nowhere in the data.** It exists in the published specification, which
this repository has not read, and in the report recorded as `INV-002` R-5.

The consequence is direct and worth having beside the other two records that
touch it. `INV-004` M-2 established that the extractor in this repository's
image assumes a resolution when its input declares none, which is what a PNG
converted from these files does; `INV-003` established that the second
extractor's resolution handling is defective by its authors' own account. The
resolution is therefore an unverified field in three places at once — in the
dataset manifest, in the extractor's assumption, and in the second extractor's
parameter — and nothing in the corpus itself can settle it.

### F-10 — Which fingers each subset contains — VERIFIED

Derived from the file names in the checksum lists of F-5, which are the names of
every file in the corpus:

| subset | fingers | contiguous | impressions | names | fingers x impressions |
| --- | --- | --- | --- | --- | --- |
| DB1_A, DB2_A, DB3_A, DB4_A | 1 to 100 | yes | 1 to 8 | 800 | 800 |
| DB1_B, DB2_B, DB3_B, DB4_B | 101 to 110 | yes | 1 to 8 | 80 | 80 |

Every `_A` subset holds the same finger range and every `_B` subset holds the
same one, with no gap in either and no finger appearing in both. The count is
exactly the product, so no impression is missing and none is repeated.

This fact is the mapping only. **What those two ranges are for is the
organisers' definition and not a measurement**: they distributed fingers 1 to
100 as the benchmark evaluation set and fingers 101 to 110 to participants for
parameter tuning. This record measures which fingers are in which subset;
`REF-009` decision 2 is where the roles are assigned on that basis, and it
attributes them.

### F-11 — The tool fixture reproduces from this copy — VERIFIED

`manifests/MAN-tools.v1.json` records a fixture for both tools against three
images, and identifies them by the name of the directory they were read from,
with status `UNVERIFIED`, because no checksummed set existed to name instead.
One now does.

The three names appear in `DB1_B.sha256` at these digests:

    746707dbf23a59eff97d80b66ca8ee2a010bc179e69ebe41336e3740307bbf04  101_1.tif
    7419a15bddf0d67cfa04364b69a7f8f21396c4ac5a75ee0603ad337fe882a06e  101_2.tif
    59cbe6a35067cc34ef8ab3fd82c24d6c44816cf77db46b72353ffc493c82c551  102_1.tif

and `scripts/check_tools.sh`, run unchanged against the corpus copy rather than
against the directory the fixture was first recorded from, passes every check:
both binary digests match the manifest, the TIFF-to-PNG conversion is pixel
identical on all three, the three mindtct minutia counts and `.xyt` digests
match, all eight mindtct outputs are byte identical on a repeat, all six
bozorth3 scores match, symmetry holds on the three off-diagonal pairs, and five
repeated runs of one pair return one value.

So the images the tool fixture rests on are the images this corpus contains, at
digests this repository now publishes, and the fixture reproduces when they are
read from the corpus.

## Reported, and not established here

### R-1 — UNVERIFIED — whether this tree is the official distribution

It cannot be settled from inside this repository. The tree arrived through a
third-party redistribution, and every digest available here was taken from that
same tree.

What corroborates it, recorded as corroboration and not as proof. Each item is
something measured or computed here, over the whole corpus:

- the layout is the distribution's own, `Dbs/`, `Doc/` and `Src/`, and `Src/`
  holds three participant skeleton sources (F-1);
- each database holds exactly one distinct image size across every one of its
  files, and DB1's agrees with what `INV-002` F-1 measured on the same subset
  for another purpose (F-3);
- the file counts are 800 and 80, and each is exactly the number of fingers
  present times the number of impressions present, with none missing and none
  repeated (F-2, F-10);
- the index files carry 4950, 2800, 45 and 280 lines (F-7), which are exactly
  the pairwise counts the fingers and impressions present in the corpus give:
  100 * 99 / 2 = 4950 and 100 * (8 * 7 / 2) = 2800 for the hundred fingers of
  an `_A` subset, 10 * 9 / 2 = 45 and 10 * (8 * 7 / 2) = 280 for the ten of a
  `_B`.

Each of those is a property a faithful copy would have and a corrupted or
substituted one would probably not. None of them is a signature.

**What is not in that list, and why.** It would be natural to write that the
dimensions match the published specification, and that the line counts are the
ones the FVC protocol defines. Both are attributions to documents **no
investigation in this repository has read** — F-9 says so of the specification,
and R-2 records that the organisers' pages could not be fetched. An agreement
with a document nobody here has opened is not a measurement, and putting one in
a list of measurements would smuggle exactly the outside confirmation this
section exists to say the repository does not have. The internal arithmetic
above is what is established; the agreement with an outside authority is not.

### R-2 — UNVERIFIED — whether the organisers publish checksums

**This was not settled either way, and the record says so rather than closing
it.** The organisers' site could not be read from this environment:

- `bias.csr.unibo.it` presents a certificate naming only `biolab.csr.unibo.it`,
  so the fetch fails on a hostname mismatch;
- `biolab.csr.unibo.it` returns HTTP 404 for the FVC2002 path;
- the Internet Archive is not reachable from this environment.

A web search surfaced no published checksum for any FVC2002 archive. That is
weak evidence of absence and no evidence at all of what the page says. So this
repository has established neither that the organisers publish checksums nor
that they do not, and the question stays open.

### R-3 — UNVERIFIED — the licence, per set

Reported, second-hand, from a web search summarising pages that could not be
fetched here for the reason in R-2: set B of each database is a free download,
and the full databases including set A are distributed with the *Handbook of
Fingerprint Recognition* (Springer), on the DVD of the second edition and with
the third edition of 2022.

The source of this claim is a search engine's summary of the organisers' pages,
not the pages themselves. It is recorded per subset in the manifest because it
determines who can reproduce what, and it carries the status this paragraph
gives it.

## Reproducing this

The copy, from a Windows shell:

    robocopy "<source>\FVC2002" "%LABDATA%\raw\fvc2002" /E /COPY:DAT /R:2 /W:2 /XJ

Exit codes 0 to 7 are success for `robocopy`; 8 and above are failure.

The mount, as `make shell` builds it:

    docker run --rm -v "$LABDATA/raw:/data/raw:ro" \
                    -v "$LABDATA/derived:/data/derived" dactyloscopy:dev bash

and inside it, the three checks that the mount is what it claims to be — read
the listing, not the exit status, because a path mistake gives an empty
directory and a successful command:

    ls /data/raw/fvc2002/Dbs      # eight subsets and four index files
    touch /data/raw/x             # must fail: Read-only file system
    touch /data/derived/x         # must succeed

F-2 to F-8 come from one pass over the corpus inside that container: for each
subset, every file's dimensions and mode from `PIL.Image.open(...).size` and
`.mode`, its length from `stat`, and its SHA-256 over the whole file; then a
grouping of names by digest within each subset and across all eight; then the
index files read as bytes, counting `\r\n` against lines and splitting each
line on whitespace.

F-9 is a second pass over the same files, reading TIFF tags rather than image
properties, because a tag's absence cannot be seen through `Image.size` or
`Image.mode`. For every file, `PIL.Image.open(f).tag_v2.get(n)` for `n` in 282,
283, 296, 259 and 262, counted per subset so that a single differing file would
show as a second entry in the count.

F-10 needs no pass over the corpus at all: it is derived from the file names in
the lists F-5 produced, splitting each name on `_` and on the extension.

F-11 is `scripts/check_tools.sh`, unchanged, pointed at the corpus copy instead
of at the ad-hoc directory the fixture was first recorded against:

    docker run --rm -v "<repo>:/work"       -v "$LABDATA/raw/fvc2002/Dbs/Db1_b:/fixture:ro"       -w /work dactyloscopy:dev bash scripts/check_tools.sh /fixture

F-5's verification is the standard tool, one command per subset, run with the
subset directory as the working directory:

    cd /data/raw/fvc2002/Dbs/Db1_a
    sha256sum -c /work/manifests/checksums/fvc2002/DB1_A.sha256

The list format is chosen so that this command is the whole verification: no
script in this repository is needed to check a corpus against its manifest.

## What was left unchecked

- **Whether the source tree is the official distribution.** R-1. Everything
  measurable about the copy was measured; authenticity is not a property of the
  bytes in front of us.
- **What the organisers' pages say.** R-2. They could not be read from here,
  and no conclusion is drawn from that.
- **The licence.** R-3 is second-hand.
- **The resolution the images were captured at.** F-9 shows the files declare
  none, so the value that reaches a manifest is a report (`INV-002` R-5) and
  not a measurement. Nothing in this corpus can check it.
- **`Doc/` and `Src/` were digested as part of the tree but have no per-file
  list.** The eight lists cover the 3520 images. The PDF and the three source
  files are named in F-1 and are not otherwise checked; nothing in this
  repository reads them.
- **The index files' contents beyond their shape.** Line counts, line endings,
  field counts, the set of names referenced, and one specific line were
  checked. Whether every line names a pair that exists in the corpus, and
  whether the pairing follows the protocol the counts imply, was not.
- **Nothing was compared against another copy of FVC2002.** A second
  independent copy would turn R-1 from corroboration into agreement between two
  sources, which is what this repository's own rule requires before a field may
  be marked `VERIFIED`.
