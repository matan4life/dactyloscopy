# REF-016 — The composition of a run record

Date: 2026-09-21
Rests on: `quality/INV-017-run-record-composition.md`, and for two grounds
`quality/INV-005-fvc2002-corpus.md` and
`quality/INV-004-nbis-acknowledged-defects.md` as `INV-017` cites them. Closes
`M-1`, issue #1, which `REF-002` names as blocking the trailer set of a `run:`
commit and the flag that marks a run provisional. Every factual claim below is
a reference to a fact of one of those investigations, by its identifier. This
refinement measures nothing and states no fact of its own.

## Numbering

This refinement takes 016, the next free number after `REF-015`. The gaps at
001 and 004 are explained in `REF-002` and `REF-006`.

## Why this refinement exists

`M-1` has been open since the repository was created. `REF-002` states it as
the author's account of a specification pending import, and that import has
not happened; `runs/README.md` names six things a record must name and nothing
in the tree says what form they take or whether six is enough. Every run this
repository could make waited on that, and no run had been made.

`INV-017` made one, on both subsets of `DB1`, wrote it down as a candidate
record, and read the record back three ways. What each reading needed is
measured there, field by field (`INV-017` F-5). This refinement takes the
composition from those facts and decides nothing the facts do not reach.

## Decision 1 — a run is a comparison under a list, and nothing else is

**A run is the scoring of a comparison list: a set of pairs, each labelled
genuine or impostor, each given a score by a matcher. A run record is the
record of that and of nothing else.**

An investigation that reports numbers is not a run and writes no run record.
`INV-014` and `INV-015` each say in their own "left unchecked" that no
`results.json` was written because no matcher, protocol or metric was in
scope; `INV-017` is the first record in the tree whose numbers come from a
comparison list. The distinction is the one `runs/README.md` draws — a
`results.json` per run, with the pair list and score vector it was computed
from — and this decision states it so that the gap the earlier records fell
into, where a number reported by an investigation had no place in the tree,
does not recur: an investigation's aggregate is derived data, which
`REF-015` decides, and a run's observation is a run's.

## Decision 2 — a record is two documents, bound by a digest

**A run record is `results.json` beside `observation.json`. `results.json`
carries the observation's sha256 and byte count; the observation is the pair
list with its scores and whatever the tools say must accompany a score.**

`INV-017` F-2 is the ground: what ties a record to its observation is the
digest, and a record without it is a record of some observation. F-5's table
gives the second half: the observation carries the per-image minutia count and
the matcher's error stream by row, because `MAN-tools.v2` records that
`bozorth3` returns 0 below its minutia floor and 4000 on overflow, and a score
vector alone cannot tell either from a verdict (`INV-017` F-7, and `INV-004`
B-3 through the manifest). What must accompany a score is therefore the
matcher's to say, through its manifest, and the observation carries it.

## Decision 3 — the fields of `results.json`

**A `results.json` carries the following, and a record missing any of them is
not a result.** Each is the field `INV-017` F-5 measured a reading to need,
named by the reading.

| block | field | needed by |
| --- | --- | --- |
| `record` | `kind`, `schema`, `created`, `provisional` with its note | every reading: which composition this record follows |
| `dataset` | the manifest id; the manifest's path and sha256; the set's checksum list by path, sha256 and entry count; the count of images used; that every image used was verified against the list | F-3: a re-run has to know it ran on the set, not on a directory with its name |
| `protocol` | an id, `null` until a protocol manifest exists; the comparison lists by name, sha256 and status; a note saying what the lists are | F-3: the pairs are the lists, and the lists are known by digest |
| `tools` | per tool, the command, the flags, the binary path, the sha256 the manifest records and the sha256 measured in the image | F-3: neither tool reports a version, so the digest is the identity (`MAN-tools.v2`) |
| `tools_manifest` | path and sha256 | F-3 |
| `code` | `revision`, `dirty`, `branch`, `image_id`, each with a status; the sha256 of each module that ran | F-5: the image has no `git`, and a record made from a dirty tree must say so |
| `seed` | the value, or `null` with a sentence saying nothing is drawn | F-5: this run draws nothing, and a reader must be told that rather than left to infer it |
| `n_genuine`, `n_impostor`, `n_images` | counts | F-2: the observation's lists must add up to them |
| `metrics` | per metric, its id and version from `MAN-metrics.v1`, the value as a fraction, the registered definition text, and the operating point where the definition has one | F-4: the text is what a reader computes from |
| `metrics_manifest` | path and sha256 | Decision 6: the registration the ids resolve against |
| `observation` | path, sha256, bytes | F-2 |

Two fields the record carries beyond that table, for the reason each states:
every open reading of a metric whose definition admits more than one,
computed and stored (`INV-017` F-4, last table), so that "the choices do not
matter here" is a fact of the record and not an assurance; and the
definition text copied in full rather than only referenced, so that the
record can be read without the manifest and checked against it with.

**What the record does not carry.** A wall clock: `INV-017` F-1 lists none,
and the record reports what was computed, not how long it took. Anything from
which a minutia could be reconstructed: the observation is names, labels,
integer scores and counts.

## Decision 4 — provenance crosses from the host, or the run is provisional

**The code revision, whether the tree was dirty, the branch and the image id
are read on the host and passed into the container; a record whose revision
or dirty flag is unverified, or whose tree was dirty, is provisional, and a
provisional record cannot support a claim.**

`INV-017` F-5 is the ground: the image carries no `git`, so no record made
inside it can learn its own revision, and the two runs made before the tree
was clean were provisional for exactly the reason the flag exists — the code
that ran was not the code any commit holds. The `Makefile` target is the only
place the four values are read, so a run that supports a claim is started
from there. Whether the tree is dirty is what `git status --porcelain`
prints, and `git status` honours the repository's own exclusions -
`.gitignore` and `.git/info/exclude` - as it does for every other purpose.
The two records `INV-017` rests on were made after a directory of working
notes was added to `.git/info/exclude`; the runs made while it was untracked
were provisional, and the records say so. A rule that ignored untracked
files on its own would have to decide which of them cannot change a run,
and would be wrong once; a rule that reads what `git` reports is the rule
`git` already enforces.

## Decision 5 — where a record lives, and what it is called

**A record lives at `runs/<id>/`, tracked, with its observation beside it
while the observation is at most 5 MB; above that the observation lives under
`$LABDATA/derived/observations/<id>/` and the record carries its sha256 and
byte count as it does anyway. The id is `<YYYYMMDD>-<subset>-<revision>`, the
subset's manifest id with its slash replaced and the revision's first seven
characters.**

`INV-017`'s two observations are 22 083 and 473 796 bytes; the larger is the
whole `DB1_A` list, and no subset of the corpus has more images than `DB1_A`
(`MAN-fvc2002.v1`). The 5 MB bound is this refinement's, chosen as ten times
the largest observation this corpus can produce, so that no run on it is
sent outside the tree and a corpus ten times larger would be; no tracked
document states a size rule, and this decision is where one now stands. The
digest route keeps the record checkable either way: a claim is checkable when
the observation can be fetched and verified against a recorded digest. The id
is made of three things that cannot become false later: the date sorts, the
subset locates, the revision pins the code. Two runs on one day, one subset
and one revision are the same run, since nothing is drawn; a counter suffix
is reserved for the day that stops being true.

## Decision 6 — the two metrics are registered, before any run cites them

**`eer@1` and `auc@1` are registered, each by id, version 1 and its full
definition as text, in `manifests/MAN-metrics.v1.json`. A run record names
each metric it reports by id and version, names the manifest by path and
sha256, and copies the registered text beside the value. The definition is
never edited: a changed definition is a new version under a new id@version,
and the old one stays.**

`INV-017` F-4 is the ground: three readers given the text and an observation,
and nothing else, returned the four numbers to the last double at the same
thresholds, so the text is sufficient to compute from; and `INV-017` found no
tracked file defining either metric, so a `run:` commit that named a
`metric_id` would have named nothing. The registered text is the text
`INV-017` tested, unchanged. The instrument reads the registered text at run
time and refuses to run if it differs from the text it implements, so that the
code and the registration cannot drift apart silently; the registration is
the manifest's and the implementation is the module's, and a reader checks
the number against the text, not against the code.

## Decision 7 — the `run:` commit and its trailers

**A `run:` commit adds one `runs/<id>/` directory. Its subject states the
headline metric in the form `docs/commits.md` illustrates. Its trailers are
`Result:` once per metric, `Dataset:` with the manifest id, and `Record:` with
the run id.** `REF-002` left the trailer set open as a projection of the
record; this is the projection: the three fields one would filter, sort or
cross-check the log on, and no more.

## Rejected

- **Adopting a specification not in the tree.** The brief for this refinement
  proposed adopting a mandatory field list, run statuses, a run-directory
  discipline and a size rule from documents this tree does not carry. A
  refinement rests on investigations in the tree and nothing else, for the
  reason `INV-015` gives about a document a later reader cannot check; the
  fields decided here are the ones `INV-017` measured a reading to need, and
  they overlap the proposed list where the measurement reached it.
- **A `status` vocabulary of `running`, `ok`, `refused`, `failed`.** Proposed
  by the same brief, and a good distinction — a refusal is counted, a failure
  is a bug. Rejected here because no run in `INV-017` refused or failed, so no
  fact grounds the vocabulary; it is left for the first run that does.
- **A free-form comparability key.** `M-2` stays open; nothing here computes a
  fingerprint. `INV-017` says which fields resolve to content — every digest
  in Decision 3 — and that is what a fingerprint would be computed over, when
  `M-2` decides which of them enter it. Deciding it here would settle `M-2`
  silently.
- **Leaving the metrics unregistered until a registry is designed.** A
  `run:` commit names a `metric_id`, and until Decision 6 there was nothing
  for it to name; running first and registering later would have put a
  number in the log under an id defined afterwards. The registry is one
  manifest with two entries, which is all the facts reach.
- **Registering the definitions the working rules state in one sentence
  each.** Those sentences are in a file the tree does not carry and leave the
  choices `INV-017` F-4 lists open; what is registered is the text three
  readers computed from, with every choice made in the text.
- **`set_md5`.** The name appears in `INV-002`, which expected a dataset
  manifest with such a field. The corpus manifest identifies a set by the sha256
  of its checksum list (`INV-005`, `MAN-fvc2002.v1`), and `INV-017` used that.
  The record carries the digest under the name of what it is; a field named for
  an algorithm the manifest does not use would be a field a reader has to
  translate.
- **A wall clock in the record.** `INV-017` F-1 does not measure one; a time
  depends on the machine and the load and is not a property of the run.

## Open

- ⟨OPEN⟩ `M-2`, which of Decision 3's digests enter the comparability
  fingerprint.
- ⟨OPEN⟩ A protocol manifest. Decision 3 carries `null` for the protocol id
  until one exists; `INV-017` used the organisers' lists by digest and left
  unchecked whether they are the competition's protocol as published.
- ⟨OPEN⟩ What a refused or failed run records. No run has refused or failed.
