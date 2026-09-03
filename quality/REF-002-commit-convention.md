# REF-002 — Commit convention

Date: 2026-09-03
Rests on: no investigation. Every statement below about how git behaves is
either cited to documentation (see References) or was verified by a command
whose output is recorded in `docs/commits.md`. This refinement adds no fact
of its own.

## Numbering

This refinement takes the number 002, and REF-001 is not missing by
accident. The author states that INV-001, REF-001 and the manifests they
issued exist in earlier work, are written in Russian, and are pending import
and translation; that statement is recorded here so that the gap at 001 is
not read as an error. It is not verified in this repository, and nothing
here rests on those records. The shape of the record chain,
INV -> REF -> MAN, is stated in `README.md`.

## Decision

The numbers, commit ids, dataset name and tool names in the examples below
are there to show the form. No run has produced them, and none of them is a
choice this refinement makes.

### Subject

`<kind>: <summary>`, at most 72 characters including the prefix, no trailing
full stop, lower case after the prefix, imperative mood: `add`, `record`,
`adopt`, never `added`.

One exception, stated here so that it is not read as an oversight: a `run:`
subject is a statement of a result, not an action, and reads

    run: eer@1 0.0323 on fvc2002/DB1_A, mindtct + bozorth3

The root commit of this repository is the single exception to everything
above: it creates the repository rather than recording a change of one kind,
and its subject is `Initial commit: repository skeleton`. No later commit is
exempt.

### Eight kinds, one per commit

A change spanning two kinds is split into two commits.

| Kind | What it records |
| --- | --- |
| `run:` | a run and its observation |
| `inv:` | an investigation |
| `ref:` | a refinement: a decision taken |
| `man:` | a manifest issued or versioned |
| `spec:` | a specification changed |
| `code:` | implementation |
| `infra:` | container, toolchain, automation |
| `docs:` | everything else written |

### Body

Why, not what. Wrapped at 72 characters. Required for `ref:` and `run:`,
optional otherwise.

### Trailers

`Key: value` lines at the end of the message, separated from the body by a
blank line. Git parses them natively and `git log --format` extracts them by
key [1][2]. A block that is not made only of trailers is recognised only if
it holds a git-generated or user-configured trailer and is at least 25%
trailers [1]; without one, a single line that is not a trailer hides every
trailer in the block (verified, `docs/commits.md`). The block therefore
holds trailers and nothing else.

A key containing an underscore, a dot or a space is not a trailer; a key of
letters, digits and hyphens is (verified, `docs/commits.md`). Git parses a
lower-case key too (verified, `docs/commits.md`), so capitalisation is a
convention of this repository rather than a requirement: `Dataset-Md5`,
never `dataset_md5`. Capitalised and hyphenated is the form of
`Signed-off-by`, written by git [4], and of `Co-authored-by`, read by
GitHub [7].

Two rules govern which trailers a commit carries:

1. **A trailer is an index, not a copy.** Only fields one would filter, sort
   or cross-check on. Mirroring a record file into trailers produces the same
   file twice, with every opportunity to diverge and no benefit.
2. **The trailer set is a projection of the record schema, never designed
   independently.** Designed separately, the two drift, and the cross-check
   they exist for becomes a comparison of two different things.

A repeated key is legal [1]; this convention uses it to express a list. Git
returns the values in the order the lines appear in the message (verified,
`docs/commits.md`), and `%(trailers:key=...)` given more than one key shows
the lines matching any of them [2] in that same single list, in message
order rather than in the order the keys were asked for (verified,
`docs/commits.md`). Nothing pairs one key's values with another's, so
`Metric:` and `Value:` as parallel repeated keys could not be read back as
pairs: one missing entry shifts every pair after it. A metric and its value
therefore travel in one value,

    Result: eer@1 0.032264
    Result: auc@1 0.987210

and never as separate `Metric:` and `Value:` keys.

### Amending

`git commit --amend` replaces the commit with a new one [4]. Before a push
that is a private matter. After a push, the replacement reaches `main` only
by a forced push [5] or inside a merge commit; `main` refuses force pushes
and non-linear history (`CONTRIBUTING.md`). So: amend before pushing, never
after.

### Reverting

`git revert` writes the subject `Revert "<subject>"` and a body line
`This reverts commit <sha>.` (verified, `docs/commits.md`; [3] documents the
body line as
`This reverts <full-object-name-of-the-commit-being-reverted>.`). The
subject does not match this convention and is rewritten to
`code: revert <what> (<sha>)`. The body line is kept as it is; it is body
text, not a trailer, and is not extractable by key (verified,
`docs/commits.md`).

**A `run:` commit is never reverted.** Evidence is not withdrawn from the
record by deletion; it is retracted.

### Retraction

History is never rewritten. A wrong number therefore stays in the log and is
withdrawn by a later `run:` commit:

    run: retract eer@1 0.0323 on fvc2002/DB1_A

    The impostor score distribution is not independent of tuning, so every
    number derived from it is withdrawn.

    Retracts: a562db7
    Reason: impostor pairs were drawn from the tune subset

A single `git log` invocation cannot exclude retracted runs: none of git
log's commit-limiting options reads another commit's trailers [6]. Excluding
them takes a second pass over the `Retracts:` values. That filter arrives
with CI.

## Rejected

- **Conventional Commits** [8]. Its specification gives five reasons for
  using it [8]. Two of them, automatically generating a changelog and
  automatically determining a semantic version bump, need version numbers;
  this repository has none, nothing in the tree declares one, and the only
  tag form is `cite/`. A third, triggering build and publish processes,
  needs something to publish. The remaining two, communicating the nature of
  a change and offering a structured history to explore, are what the eight
  kinds above provide, in a vocabulary that has a term for an investigation
  and for a run. The specification's own structural types are `feat` and
  `fix`, tied to MINOR and PATCH, and for the rest it points at
  `@commitlint/config-conventional`, which "recommends `build:`, `chore:`,
  `ci:`, `docs:`, `style:`, `refactor:`, `perf:`, `test:`, and others" [8]:
  product vocabulary throughout. Keeping its syntax and replacing its
  vocabulary would keep the form and discard the reasons it exists.
- **Semantic versioning and `BREAKING CHANGE:`** [8][9]. MAJOR, MINOR and
  PATCH count incompatible changes, added functionality and bug fixes in an
  API [9]. There is no version here, so there is nothing for them to count.
- **Scopes in parentheses** [8]. A scope names the part of the codebase a
  commit touches. Here the kind already says which part of the record a
  commit adds to, and a second qualifier would either repeat the kind or
  name a directory of the implementation, which is not decided.
- **gitmoji** [10]. An emoji guide for commit messages. Its entries name
  activities: `:bug:` "Fix a bug.", `:sparkles:` "Introduce new features.",
  `:alembic:` "Perform experiments.", `:monocle_face:` "Data
  exploration/inspection." [10]. None of them names a record, and none says
  that a number was produced, so the objection made to the vocabulary of
  Conventional Commits applies unchanged.
- **commitlint** [11]. A linter for commit messages. Its getting-started
  guide installs it together with `@commitlint/config-conventional` [11],
  a "Shareable `commitlint` config enforcing conventional commits" [11]; the
  convention it checks is rejected above.

## Open

`M-1` and `M-2` are open questions of the Methodos specification, which like
`INV-001` and `REF-001` is pending import into this repository. `M-1` is the
composition of a run record; `M-2` is what enters the fingerprint that
groups runs into comparable families. Both are stated here as the author's
account, and neither is verified in this repository.

- ⟨OPEN⟩ The exact trailer set for a `run:` commit that records an
  observation. It is a projection of the run record, whose composition is
  open question M-1.
- ⟨OPEN⟩ How a provisional run is flagged. A run from a dirty tree or off
  the main branch cannot support a claim; the flag is part of M-1.
- ⟨OPEN⟩ A comparability identifier. Without one the log yields a column of
  incomparable numbers rather than a table. It is the fingerprint of the
  fixed slot, open question M-2.

## References

1. git-interpret-trailers: <https://git-scm.com/docs/git-interpret-trailers>
2. pretty formats, `%(trailers:...)`: <https://git-scm.com/docs/pretty-formats>
3. git-revert: <https://git-scm.com/docs/git-revert>
4. git-commit, `--amend` and `--signoff`: <https://git-scm.com/docs/git-commit>
5. git-push, push rules and `--force`: <https://git-scm.com/docs/git-push>
6. git-log, commit limiting: <https://git-scm.com/docs/git-log>
7. GitHub, `Co-authored-by`: <https://docs.github.com/en/pull-requests/committing-changes-to-your-project/creating-and-editing-commits/creating-a-commit-with-multiple-authors>
8. Conventional Commits 1.0.0: <https://www.conventionalcommits.org/en/v1.0.0/>
9. Semantic Versioning: <https://semver.org/>
10. gitmoji, guide and emoji list: <https://gitmoji.dev/>, <https://github.com/carloscuesta/gitmoji/blob/master/packages/gitmojis/src/gitmojis.json>
11. commitlint, getting started and `@commitlint/config-conventional`: <https://commitlint.js.org/guides/getting-started.html>, <https://github.com/conventional-changelog/commitlint/tree/master/@commitlint/config-conventional>
