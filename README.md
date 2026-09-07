# Dactyloscopy

A laboratory for fingerprint research. Its purpose is that every number it
produces can be traced to the data, the protocol, the metric definition and
the code revision that produced it. The accounting is the product; the
science is built on top of it.

## Status: tools, no run

This repository was created on 2026-09-03 and this section was last corrected
on 2026-09-07. It held documents only until 2026-09-06; that is no longer the
state, and the sentence saying so stood for a day longer than it was true.

What exists now: the licensing, citation metadata, issue taxonomy, directory
contracts, the data policy and the commit convention it started with; the
investigation and refinement chain in `quality/`; four frozen manifests, two
of them versions of the tools manifest, one a corpus and one the minutia canon
format; a container image pinned by digest, carrying two NBIS tools and one
extractor this repository drives through a caller of its own; the source of
that caller, and a test suite that holds it to what it reads.

What does not exist: a protocol, a metric, a run, a score vector, and any
number to cite. No comparison has been made inside this system.

Nothing is carried over from an earlier codebase.

## The record: INV -> REF -> MAN

Every claim rests on a chain of three kinds of file, each resting only on the
one before it.

| Record | Path | Holds |
| --- | --- | --- |
| Investigation | `quality/INV-nnn-*.md` | A question, a method, measured facts, a command that reproduces them, a date, and an explicit list of what was left unchecked. No decisions, no judgements, no recommendations. |
| Refinement | `quality/REF-nnn-*.md` | A decision taken on the facts of named investigations, with the alternatives considered and why each was rejected. No new facts: every factual claim is a reference to an INV. |
| Manifest | `manifests/MAN-<name>.v<N>.json` | The frozen, machine-readable consequence. Names the INVs and REFs that produced it. No number without a status. |

A fact, a decision and its consequence never share a file. A manifest is
immutable: a correction is a new version file, plus a new INV, plus a new REF,
and the old version stays so that old results reproduce against it. A result
that does not name the manifests it used is not a result.

## Absolute prohibitions

1. **Never commit biometric data.** No fingerprint images, no minutiae, in any
   form, ever: not in a fixture, not temporarily, not in a branch. A commit
   that adds one is an incident.
2. **Never invent a number.** Not a metric, not a checksum, not a resolution,
   not a count. An unknown value carries the status `UNVERIFIED`, and the code
   refuses to use it. Placeholder values, "example" numbers and plausible-looking
   defaults are prohibited in manifests, tests and docs.
3. **Never mark a field `VERIFIED`** unless it was measured here or two
   independent sources agree. One source is `APPROX`. Two sources that
   disagree are `CONFLICT`, and reading a `CONFLICT` field raises rather than
   falling back to a default.
4. **Never silently resolve an open question.** Open questions are tracked as
   issues. A task that needs one settled stops and says so.

## Data policy

Nothing biometric is ever committed. Fingerprint images and minutiae are
personal data, and an image good enough to fool a matcher can be reconstructed
from minutiae, so minutiae are not published either. Input data is mounted
read-only from outside the tree and addressed by manifest id, never by path.

What will be published instead: per-file checksums, pair lists and score
vectors, from which every metric will be recomputable without the images.
The checksums exist: `manifests/checksums/fvc2002/` lists every image in
the corpus by digest and `manifests/MAN-fvc2002.v1.json` names the subsets.
There is no run, so there is no pair list and no score vector yet.
See [docs/data.md](docs/data.md).

## Layout

```
manifests/        frozen machine-readable manifests, immutable and versioned
quality/          the INV and REF chain
implementation/   the code a run executes and the source of what it invokes
tests/            tests, run by pytest inside the image
experiments/      experiment declarations
workflow/         rules for derived data
runs/             run records and the observations that support claims
scripts/          one-off and maintenance scripts, never part of a run
docs/             documentation, starting with the data policy
LICENSES/         the CC BY 4.0 text; the MIT text is in LICENSE at the root
.github/          issue forms
```

`manifests/`, `quality/`, `implementation/`, `implementation/tools/`,
`tests/`, `experiments/`, `workflow/`, `runs/` and `scripts/` each carry a
`README.md` stating what belongs in that directory and what does not. A
directory is created by the commit that first puts a file in it, and its
contract arrives with it.

## Development

Python 3.12 for code a run executes in the container's own process, and C for
source that links a third-party library and crosses into the runtime image as
a binary. `pytest` is the test runner. All three are the versions the image
pins, and the choice is recorded in
[quality/REF-013-implementation-layout.md](quality/REF-013-implementation-layout.md),
which also decides the split between `implementation/library/` and
`implementation/tools/` and why there is no packaging file.

Everything runs inside the image `make image` builds: `make test` for the
suite, `make check-tools` to verify the tools against their manifest. What
those printed is in [docs/tools.md](docs/tools.md) and
[docs/container.md](docs/container.md).

## Citation

No DOI exists, because nothing from this repository has been cited yet. A DOI
is minted when a GitHub Release is published, and a Release is only ever made
from a `cite/<slug>` tag — created when numbers from that state are quoted
somewhere outside the repository. The tag alone archives nothing. The metadata
that a future DOI will carry lives in [CITATION.cff](CITATION.cff) and
[.zenodo.json](.zenodo.json).

## Licence

Two licences apply. Code is licensed MIT, and its text is in
[LICENSE](LICENSE). Every file that is a document rather than code — the
documentation, the record chain in `quality/`, manifests, experiment
declarations, run records and the observations that support a claim — is
licensed CC BY 4.0, and its text is in
[LICENSES/CC-BY-4.0.txt](LICENSES/CC-BY-4.0.txt). Both now apply to real
files: the caller under `implementation/`, the suite under `tests/` and the
scripts under `scripts/` are code, and everything else in the tree is a
document. The two licence texts themselves are reproduced on their own terms
and are not under CC BY 4.0.

Attribution is satisfied by citing this repository as
[CITATION.cff](CITATION.cff) describes, and by the DOI once a release has
been archived.

Which files fall on which side, what a reuser owes, what this repository owes
and what was checked: [docs/licensing.md](docs/licensing.md). Why the
boundary is drawn this way, and why the root `LICENSE` holds the code
licence: [quality/REF-003-licensing.md](quality/REF-003-licensing.md).
