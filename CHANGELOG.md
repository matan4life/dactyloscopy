# Changelog

Dated entries, newest first. An entry records what changed in the repository.
Numbers never appear here: a result lives in `runs/` and in the `run:` commit
that records it.

## 2026-09-21

- The status in `README.md`, the publication sentence in `CONTRIBUTING.md`
  and this file brought up to date. The last two had stood since the days
  the repository held documents only; the status since 2026-09-07.

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
