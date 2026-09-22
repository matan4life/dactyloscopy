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
