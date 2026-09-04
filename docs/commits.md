# Commits

The working form for a commit in this repository. The reasoning behind it is
in [quality/REF-002-commit-convention.md](../quality/REF-002-commit-convention.md);
this page says how, not why.

Every number, commit id, dataset name and tool name on this page is there to
show the form. No run has produced them, and none of them is a choice this
repository has made.

## Subject

`<kind>: <summary>`

- at most 72 characters, prefix included;
- no trailing full stop;
- lower case after the prefix, imperative mood: `add`, `record`, `adopt`;
- one kind per commit, and a change spanning two kinds is split.

`run:` is the one exception among the eight kinds: its subject states the
result. The root commit of this repository is exempt from the form altogether;
no later commit is.

    run: eer@1 0.0323 on fvc2002/DB1_A, mindtct + bozorth3

## Kinds

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

## Body

Why, not what. Wrapped at 72 characters. Required for `ref:` and `run:`,
optional otherwise.

## Trailers

- `Key: value` lines at the end of the message, after a blank line. The
  block holds trailers and nothing else: a stray line hides every trailer in
  it, unless the block also carries a git-generated trailer such as
  `Signed-off-by` (see "What was checked").
- A key is letters, digits and hyphens, capitalised: `Dataset-Md5`. An
  underscore, a dot or a space in a key makes the line a non-trailer (see
  "What was checked").
- Only fields one would filter, sort or cross-check on. The set for each
  kind is a projection of that record's schema; for a `run:` commit that
  records an observation, that projection is open (M-1).
- A list is a repeated key. A metric and its value share one value:

      Result: eer@1 0.032264
      Result: auc@1 0.987210

  never a `Metric:` key paired with a `Value:` key.

## Examples

The trailer blocks below show the shape of a block, not the full set of keys
a commit will carry: for a run that set is open (M-1).

### A run

    run: eer@1 0.0323 on fvc2002/DB1_A, mindtct + bozorth3

    Baseline on the default subset, so that later runs have a number to
    move against.

    Result: eer@1 0.032264
    Result: auc@1 0.987210

### A retraction

A `run:` commit is never reverted. A wrong number is withdrawn by a later
`run:` commit that names it:

    run: retract eer@1 0.0323 on fvc2002/DB1_A

    The impostor score distribution is not independent of tuning, so every
    number derived from it is withdrawn.

    Retracts: a562db7
    Reason: impostor pairs were drawn from the tune subset

### A revert

`git revert` writes `Revert "<subject>"` and `This reverts commit <sha>.`
(see "What was checked"). Rewrite the subject to
`code: revert <what> (<sha>)`; keep the body line git wrote:

    code: revert add f.txt (f319192)

    This reverts commit f31919260c16334088ec0cb62d9f31abd6dc187d.

## Amending

Amend a commit only before it is pushed.

## Reading the log

The trailers of one message:

    $ git log -1 --format=%B a562db7 | git interpret-trailers --parse
    Result: eer@1 0.032264
    Result: auc@1 0.987210

Every run:

    $ git log --grep='^run: ' --format='%h %s'
    60b34ac run: eer@1 0.0311 on fvc2002/DB1_A, mindtct + bozorth3
    37c2554 run: retract eer@1 0.0323 on fvc2002/DB1_A
    a562db7 run: eer@1 0.0323 on fvc2002/DB1_A, mindtct + bozorth3

Every run with its results on one line, tab-separated. A commit without the
key yields an empty field, bracketed here so that it is visible:

    $ git log --grep='^run: ' --format='%h%x09[%(trailers:key=Result,valueonly=true,separator=; )]'
    60b34ac	[eer@1 0.031100]
    37c2554	[]
    a562db7	[eer@1 0.032264; auc@1 0.987210]

Every retraction and what it retracts:

    $ git log --grep='^Retracts: ' --format='%h %(trailers:key=Retracts,valueonly=true,separator=; )'
    37c2554 a562db7

No single `git log` invocation excludes retracted runs (REF-002, reference
6). It takes a second pass over the `Retracts:` values above, applied by
hand until CI provides it.

## What was checked

Every command on this page was run in a throwaway repository with
`git version 2.55.0.windows.5` on 2026-09-03, and the output shown is what
it printed. The checks below fix the wording above.

A subject of exactly 72 characters is stored and printed unchanged.
`git format-patch` prints the `Subject:` header over two lines, the second
beginning with a space, and the commit reads the same afterwards:

    $ git log -1 --format=%s 0947d5e | awk '{ print length }'
    72
    $ git log --oneline -1 0947d5e
    0947d5e code: add a subject line that is exactly seventy-two characters long, ok
    $ git format-patch -1 --stdout 0947d5e | grep -A1 '^Subject:'
    Subject: [PATCH] code: add a subject line that is exactly seventy-two
     characters long, ok
    $ git show -s --format=%s 0947d5e | awk '{ print length }'
    72

A key of letters, digits and hyphens is a trailer, and so is a lower-case
key, which is why capitalisation is a convention here and not a rule of
git. A key with an underscore, a dot or a space is not a trailer: the last
three commands print nothing.

    $ printf 'run: x\n\nDataset-Md5: abc\n' | git interpret-trailers --parse
    Dataset-Md5: abc
    $ printf 'run: x\n\nresult: eer@1 0.1\n' | git interpret-trailers --parse
    result: eer@1 0.1
    $ printf 'run: x\n\ndataset_md5: abc\n' | git interpret-trailers --parse
    $ printf 'run: x\n\nDataset.Md5: abc\n' | git interpret-trailers --parse
    $ printf 'run: x\n\nDataset Md5: abc\n' | git interpret-trailers --parse

One line that is not a trailer hides every trailer in the block, whether
that line carries no key at all or a rejected one: the first two commands
print nothing. The third adds a `Signed-off-by` line, and the block is then
parsed while the stray line is dropped:

    $ printf 'run: x\n\nResult: eer@1 0.1\nnot a trailer\nResult: auc@1 0.9\n' | git interpret-trailers --parse
    $ printf 'run: x\n\nResult: eer@1 0.1\ndataset_md5: abc\nResult: auc@1 0.9\n' | git interpret-trailers --parse
    $ printf 'run: x\n\nResult: eer@1 0.1\nnot a trailer\nResult: auc@1 0.9\nSigned-off-by: A <a@example.invalid>\n' | git interpret-trailers --parse
    Result: eer@1 0.1
    Result: auc@1 0.9
    Signed-off-by: A <a@example.invalid>

The values of a repeated key come back in the order they appear:

    $ printf 'run: x\n\nResult: b\nResult: a\nResult: c\n' | git interpret-trailers --parse
    Result: b
    Result: a
    Result: c

Asked for more than one key, `%(trailers:key=...)` returns one list, ordered
by where the lines sit in the message and not by the order the keys were
asked for. Two placeholders return two lists instead:

    $ git log -1 --format='%h [%(trailers:key=Retracts,key=Reason,valueonly=true,separator=; )]' 37c2554
    37c2554 [a562db7; impostor pairs were drawn from the tune subset]
    $ git log -1 --format='%h [%(trailers:key=Reason,key=Retracts,valueonly=true,separator=; )]' 37c2554
    37c2554 [a562db7; impostor pairs were drawn from the tune subset]
    $ git log -1 --format='%h [%(trailers:key=Retracts,valueonly=true,separator=; )] [%(trailers:key=Reason,valueonly=true,separator=; )]' 37c2554
    37c2554 [a562db7] [impostor pairs were drawn from the tune subset]

The message `git revert --no-edit` wrote for commit b295318, unedited. Its
body line is body text, not a trailer, so the second command prints nothing:

    $ git log -1 --format=%B 0a80e10
    Revert "code: add g.txt for the revert check"

    This reverts commit b2953187fb92e13df1e4801bcae1ec319f39b439.

    $ git log -1 --format=%B 0a80e10 | git interpret-trailers --parse
