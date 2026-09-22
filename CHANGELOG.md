# Changelog

Dated entries, newest first. An entry records what changed in the repository.
Numbers never appear here: a result lives in `runs/` and in the `run:` commit
that records it.

## 2026-09-22

- An investigation's aggregate decided to be derived data under
  `$LABDATA/derived`, never committed (`REF-015`); the composition of a run
  record decided from what `INV-017` measured, closing `M-1` (`REF-016`,
  issue #1).
- `eer@1` and `auc@1` registered by id, version and full definition as
  `MAN-metrics.v1`; the matching instrument refuses a registration whose
  text is not the text it implements.
- The matching run verifies the dataset, tools and metrics manifests before
  it reads an image; the two metrics put under test; dead code dropped; the
  command in each `measure_*.sh` header and three Makefile recipes rewritten
  so that they run as printed.
- `INV-011` and `INV-012` say which of their numbers the tree cannot
  produce; two citations of a fact label `INV-003` does not have corrected.
- The first two `run:` commits: `mindtct` templates scored by `bozorth3`
  under the organisers' comparison lists on `fvc2002/DB1_B` and
  `fvc2002/DB1_A`, each recorded under `runs/` with its observation beside
  it, placed by `scripts/record_run.sh`.
- Every document brought to what the tree can back; issue #10 lists the
  numbers of `INV-002` to `INV-012` that no tracked file produces.
- The second extractor through the matcher: `iso-extract`'s ISO templates
  turned into the `.xyt` `bozorth3` reads, every difference between the two
  conventions a named parameter, each priced (`INV-018`); the run id now
  names its tools and `D-4` is closed (`REF-017`, issue #8); two more
  `run:` commits, `iso-extract + bozorth3` on both `DB1` subsets. The test
  suite is 78.
- One process pool for the three instruments that had each carried their
  own, `implementation/library/pool.py`, held to task order by a test; the
  suite is 82. Every command form under `scripts/` is a Python file,
  `python3 scripts/<name>.py`, in place of a shell script that embedded the
  same Python in a heredoc, and `make record-run` places a finished record.
  Each record whose command form changed says so and that its aggregate is
  byte for byte what the shell form returned.
- `REF-015` decision 3 carried out: every command form that reads a subset
  takes its manifest id, finds the directory through `MAN-fvc2002.v1` by
  the new `implementation/library/corpus.py` and verifies every image
  against the subset's checksum list first; every aggregate a
  `measure_*.py` writes goes under `$LABDATA/derived/<investigation>/`
  by default, under `<subset>/` where there is one, as
  `measure_conversion.py` already did. A run record now
  digests every library module loaded when it was composed, not two named
  ones. `corpus` is held by seven tests; the suite is 89.
- The first item of issue #10: `INV-012`'s statistics of F-2 to F-7 come
  back from the tree, by `implementation/library/angle_conventions_statistics.py`
  over the rows the sweep returns, printed as the record's own tables; the
  record says which one value differs in the third decimal and why. The
  suite is 96.
- The second item of issue #10: `INV-011`'s argument-swap test and the
  second table of its F-6 are made by `coordinate_frames_fixture.py`; the
  table comes back row for row, the swap test in every respect but the
  count under the correct call, whose placement the record had not stated.
- The third item of issue #10: the corpus is measured by an instrument in
  the tree, `implementation/library/corpus_inventory.py` with
  `scripts/measure_corpus.py`, over the root and every subset
  `MAN-fvc2002.v1` names; every count, size, digest, line and tag of
  `INV-005` F-1 to F-3 and F-6 to F-10 comes back. The suite is 99.

## 2026-09-21

- The status in `README.md`, the publication sentence in `CONTRIBUTING.md`
  and this file brought up to date. The last two had stood since the days
  the repository held documents only; the status since 2026-09-07.
- A matching instrument put in the tree: `implementation/library/matching.py`
  makes a run on a subset addressed by its manifest id, and `run_record.py`
  composes the record and re-derives its numbers; the command forms are
  `scripts/run_matching.sh` and `scripts/reproduce_matching.sh`, reached
  through `make run-matching` and `make reproduce-matching`. The
  definitions the instrument computes under are its own text, no tracked
  file then defining either metric.
- `INV-017`: the first runs under a comparison list inside this system, on
  `fvc2002/DB1_B` and `fvc2002/DB1_A` over the organisers' own lists, made
  to find what a run record must carry.
- Three sentences in `INV-013`, `INV-014` and `INV-015` cut back to what
  the list or table beside each shows.

## 2026-09-09

- The instruments of `INV-015` and `INV-016` run in a process pool and
  return the same bytes as before; each of the five measurement records
  says where its instrument lives and what re-running it from the tree
  returns.

## 2026-09-08

- Six investigations on the tools and the corpus: the coordinate frame each
  extractor reports in (`INV-011`), the angle each reports for a known
  orientation (`INV-012`), what the standard's previews and NIST's report
  card say (`INV-013`), how the two extractors differ on the same images
  (`INV-014`), which warp family predicts a held-out correspondence between
  two impressions of one finger (`INV-015`), and the localization noise
  floor of `mindtct` under exact geometry (`INV-016`).
- Every measurement instrument put in the tree under
  `implementation/library/`, with a command form under `scripts/`.

## 2026-09-07

- FingerJetFXOSE built from its pinned source, its terms read, and the tool
  admitted on a caller this repository owns (`INV-007`, `INV-008`,
  `REF-011`, `REF-012`); the tools manifest versioned to `MAN-tools.v2`
  with the extractor.
- The language, the toolchain and where code lives decided (`REF-013`).
- The FVC2002 corpus measured under `LABDATA` and its identity frozen as
  `MAN-fvc2002.v1`, with a per-file checksum list for every subset
  (`INV-005`, `REF-009`).
- The minutia canon format issued as a JSON Schema, `MAN-minutia.v1`
  (`REF-008`).
- What verifies a manifest, and when, decided and implemented (`INV-009`,
  `INV-010`, `REF-014`); the defects NBIS's own authors acknowledge read
  (`INV-004`); the terms on which NBIS is in the image read, and the
  position on the terms of any external tool decided (`INV-006`, `REF-010`).

## 2026-09-06

- A base image pinned by digest, with every `docker run` routed through
  `make`; `mindtct` and `bozorth3` built in a builder stage from NBIS source
  fetched from NIST and verified by checksum before unpacking; both frozen
  in a tools manifest and verified against it on every run (`REF-005`,
  `MAN-tools.v1`).
- The minutia formats measured over all eighty images of `Db1_b`
  (`INV-002`); the canonical minutia record decided (`REF-006`); the
  FingerJetFXOSE source confirmed at its pinned commit (`INV-003`); image
  metadata taken from the manifest and not from a tool (`REF-007`).

## 2026-09-04

- Six statements the repository could not back corrected in its documents.

## 2026-09-03

- Repository created: licensing, citation metadata, issue taxonomy, directory
  contracts, the data policy and the commit convention. Documents only: no
  code, no toolchain, no CI.
- Code is licensed MIT; every file that is a document rather than code is
  licensed CC BY 4.0. The reasoning is in `quality/REF-003-licensing.md`.
- Nothing is carried over from the earlier codebase.
- No measurement has been made inside this system.
