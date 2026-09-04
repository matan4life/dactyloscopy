# Dactyloscopy

A laboratory for fingerprint research. Its purpose is that every number it
produces can be traced to the data, the protocol, the metric definition and
the code revision that produced it. The accounting is the product; the
science is built on top of it.

## Status: skeleton

This repository was created on 2026-09-03. It holds the licensing, citation
metadata, issue taxonomy, directory contracts, the data policy and the commit
convention: documents only, nothing executable. No measurement has been made
inside it yet: there is no code, no manifest, no run and no number to cite.
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
Nothing is published yet — there is no manifest, no run and no score vector.
See [docs/data.md](docs/data.md).

## Layout

```
manifests/        frozen machine-readable manifests, immutable and versioned
quality/          the INV and REF chain
experiments/      experiment declarations
workflow/         rules for derived data
runs/             run records and the observations that support claims
scripts/          one-off and maintenance scripts, never part of a run
docs/             documentation, starting with the data policy
LICENSES/         the CC BY 4.0 text; the MIT text is in LICENSE at the root
.github/          issue forms
```

`manifests/`, `quality/`, `experiments/`, `workflow/`, `runs/` and `scripts/`
each carry a `README.md` stating what belongs in that directory and what does
not.

## Development

The implementation language and toolchain are not chosen yet. That decision
arrives together with the container image, and is recorded as a refinement
before any code appears.

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
[LICENSES/CC-BY-4.0.txt](LICENSES/CC-BY-4.0.txt). There is no code in the
repository yet, so CC BY 4.0 is what applies to the contents today. The two
licence texts themselves are reproduced on their own terms and are not under
CC BY 4.0.

Attribution is satisfied by citing this repository as
[CITATION.cff](CITATION.cff) describes, and by the DOI once a release has
been archived.

Which files fall on which side, what a reuser owes, what this repository owes
and what was checked: [docs/licensing.md](docs/licensing.md). Why the
boundary is drawn this way, and why the root `LICENSE` holds the code
licence: [quality/REF-003-licensing.md](quality/REF-003-licensing.md).
