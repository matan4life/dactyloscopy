# Contributing

This is a single-author research repository. It is public so that its results
can be checked, not because it is looking for contributors. Read
[README.md](README.md) first: it states the record model and the four rules
that everything here follows.

## The most valuable contribution

The most valuable contribution is demonstrating that a number here is wrong.
Every claim in this repository is recomputable from published observations:
per-file checksums, pair lists and score vectors, described in
[docs/data.md](docs/data.md). If you recompute a metric from those and obtain
a different value, open an investigation issue with the command you ran and
the value you got. That report is worth more than any patch.

## Issues

Blank issues are disabled. Every issue is opened through one of the forms,
and each form applies its label.

| Label | Meaning |
| --- | --- |
| `inv` | An investigation: a question, how it will be measured, what would make the answer wrong. |
| `ref` | A refinement: a decision to be taken on the facts of named investigations. |
| `man` | A manifest to be issued or re-versioned as the consequence of a refinement. |
| `open-question` | A question with an identifier, such as `M-2` or `D-5`, that nothing may settle silently. |
| `external-debt` | Something owed by someone or something outside this repository. |
| `blocks:kernel` | Added to an issue that blocks work on the domain-free accounting layer. |
| `blocks:number` | Added to an issue that blocks the production of a number. |

**An issue never holds a decision.** An issue asks; it does not answer. A
decision lives in a `quality/REF-nnn-*.md` file, together with the
alternatives considered and why each was rejected, and it rests only on facts
recorded in `quality/INV-nnn-*.md` files. An issue is closed by referencing
the commit that adds that file. A decision written in a comment is not a
decision, and is not acted on.

## Git

- Commits go straight to `main`. A branch is opened only when a change can
  break runs that already happened.
- Every commit is signed. `main` rejects unsigned commits, force pushes,
  deletions and non-linear history.
- The unit of a commit is a runnable state, not a feature.
- Every commit subject is `<kind>: <summary>`, one of eight kinds; trailers,
  where a commit carries them, index the record it adds. The form is in
  [docs/commits.md](docs/commits.md); the reasoning is in
  [quality/REF-002-commit-convention.md](quality/REF-002-commit-convention.md).
- The only tag form is `cite/<slug>`, annotated, created when numbers from
  that state are quoted somewhere outside. After a `cite/` tag, the history
  behind it is never rewritten.
- Everything in the tree is English: code, comments, documentation, commit
  messages, issue titles and bodies.

## Quality gates

The implementation language and toolchain are not chosen yet, so no automated
gate exists; it arrives with that refinement. Until then a commit is checked
by hand against what this file and [README.md](README.md) state: English
only, LF line endings, no biometric data, no invented number.

Dependencies are added deliberately and rarely. Do not introduce one to save
five lines.

## Data

Biometric data is never committed: no fingerprint images, no minutiae, in any
form, not in a fixture, not temporarily, not in a branch. The extensions
`.tif .tiff .bmp .pgm .raw .ist .xyt .min` are refused by `.gitignore`. A commit
that adds one is an incident; see [SECURITY.md](SECURITY.md).
