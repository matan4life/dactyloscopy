# REF-014 — What verifies a manifest, and when

Date: 2026-09-07
Rests on: `quality/INV-009-man-tools-v1-audit.md` and
`quality/INV-010-manifest-readers.md`. Extends `REF-005`, whose rule about
external tools this generalises to manifests. Every factual claim below is a
reference to a fact of one of those two investigations, by its identifier. This
refinement measures nothing and states no fact of its own.

## Numbering

This refinement takes 014, the next free number. The gap at 001 is explained in
`REF-002`, the gap at 004 in `REF-006`.

## Why this refinement exists

`INV-010` F-1 measured that of the 332 fields the four live manifests carry,
**42 are read by anything and 290 are read by nothing**. All 42 are in one
manifest and all are read by one script. `INV-010` F-2 measured that nothing
reads the eight checksum lists, that nothing verifies the digests
`MAN-fvc2002.v1` records for them, and that of 3520 corpus files three are
observed at all — indirectly, through what two tools compute from them, in a
way a changed byte can pass through.

`REF-005` decided that an external tool is admitted by recording its provenance
and checking it. Nothing decided the same for a manifest. A result that names a
manifest nothing verifies is traceable to a claim rather than to a fact, and
this repository exists to make that distinction hold.

## The three classes, and the test for assigning a field

Every field with a value and a status falls into exactly one of three classes.
The test is what a machine would have to do to disagree with the value.

**Class one, recomputable.** The value can be produced again by running
something: a digest, a size, a linked-library list, a fixture count, a score, a
file's presence at a path. `INV-010` F-1 measured that all 42 read fields are
of this class, and that many more like them are not read: every `size_bytes`,
the eight `checksums` digests, the 3520 entries those lists hold.

**Class two, derivable from a file this repository controls.** The value
asserts something about the `Dockerfile`, a script, or another tracked file: a
package list, a patch line, a command, an invocation, a copy. Such a value is
mechanically checkable **only if the field says where to look**, and no field
says. `INV-009` F-1 places `build.setup`, `build.patch`, `build.make` and
`build.artifact_copied` here, checkable in that record only because a person
wrote the comparison and named the file.

**Both fields that failed in `INV-009` are in class two, and that is not a
coincidence.** Class one re-measures itself: whatever reads it must run the
thing that produces it, so it cannot drift without something noticing. Class
three, below, was never expected to be automatic. Class two is the one that
looks checkable and is not, and it is where a value can sit beside a file that
has stopped matching it for 30 commits — `INV-009` F-2's measurement of
`build.extra_build_packages`.

**Class three, a claim about the outside world.** What a publisher calls a
release, what a page prints beside it, what a licence file names itself, what a
mirror contained. `INV-009` F-1 verified several of these by fetching the
outside world; that is a person deciding to go and look, not a mechanism.

## Class three is bound to its pin

A pin fixes an object. It does not fix what anyone says about that object.

But because the object is pinned, a claim about it cannot expire. It was either
right when it was written or wrong when it was written, and nothing that
happens afterwards changes which. `MAN-tools.v2`'s `source.release` says the
publisher calls this archive 5.0.0; the archive is pinned by digest, so that
sentence is as true or as false today as on the day it was written.

**So class three needs no recurring check — until the pin moves.** Change the
archive digest, the upstream commit, the tree hash or the base image, and every
claim attached to that pin becomes a claim about a different object.

**That is mechanical, and it needs no understanding of the claims.** The pin is
itself a class-one field: a digest, a commit id, a tree hash. A verifier that
checks the pin can say "the pin these were written against has changed, so
every class-three field beside it is stale" without reading one of them.
Re-reading them is then a person's work, and its output is an investigation, in
the way `INV-006` and `INV-008` read terms and `INV-009` re-fetched a
publisher's page.

## What no mechanism catches: wrong at birth

A value that was false when it was written, and is about something that does
not change, will agree with itself forever.

`INV-009` found one, in the note of a `VERIFIED` field.
`MAN-tools.v1`'s `mirror_previously_used` carries the figures of the comparison
between the archive and the mirror: 593 files byte-identical, 3286 differing in
line endings. `INV-009` re-ran that comparison and got 3879 and 0, then
measured that the recorded figures come back exactly when the mirror is checked
out with `core.autocrlf=true`. They describe a git setting on one machine, not
the two trees they claim to compare. Nothing this refinement decides would
catch it: re-measurement agrees with the wrong thing, the pin never moves, and
the field stays `VERIFIED`. That it is a note rather than a value changes
nothing about the shape of the failure — a value can be wrong at birth in
exactly the same way, and no mechanism decided here would know.

**This is a known and accepted limit and not an oversight.** What catches it is
care at writing time and an occasional audit of the kind `INV-009` is. The
mechanism decided below reports what it did not check, so that the size of this
gap is visible rather than assumed away, but it does not close it.

## Decision 1 — the class is derived by the verifier, not declared

**The verifier holds the rules. No manifest gains an annotation.**

The alternative was to declare each field's class beside it. It is rejected,
and the reason is the finding this whole refinement rests on.

**Rejected: declaring the class in the manifest.** An annotation is a field. It
would be a field nothing reads except the verifier, carried beside a value,
asserting something about that value — which is the exact shape of
`build.extra_build_packages`, the field `INV-009` F-2 found standing false for
30 commits. `INV-010` F-1 measured 290 unread fields; this would add 332 more
of a kind that cannot be recomputed, because a class is not a thing you can go
and measure. And it costs four manifest re-issues, one of them of
`MAN-tools.v2`, issued the same day, each needing its own investigation and
refinement by `manifests/README.md`'s own rule.

**What the rejected option would have bought, stated so the trade is visible.**
The classification would live in a record rather than in code, which is where
this repository normally puts a decision. That is a real cost of deriving, and
it is paid down in three ways, all of them required by the decisions below: the
rules are stated in this refinement and are normative; the verifier prints the
class it assigned to every field, so a divergence between the code and this
record is visible in the output rather than buried; and a test holds the
verifier's classification of a named set of fields, so the rules cannot drift
silently.

**What deriving buys, and it is the property that decides it.** Coverage is
measured rather than declared. A declared classification can be wrong and
nothing would say so. A derived one is exercised on every run, and the run
reports how many fields it checked and how many it could not — so the coverage
number cannot lie about itself, which is precisely what `INV-009` found the
old arrangement doing.

## Decision 2 — what the verifier checks, and what it says about the rest

**Class one: checked.** Every field the verifier can recompute is recomputed
and compared with the value the manifest carries.

**Class three: not checked, and bound to its pin.** The verifier checks the
pins, which are class one. When a pin matches, the class-three fields beside it
are reported as *bound*, and nothing is read from them. When a pin does not
match, they are reported as *stale*, by name, and that is a failure.

**Class two: not checked, and reported by name.** The verifier does not guess
where to look, and does not search the tree for a value — `INV-009` F-2
measured why that fails: a naive search for the four package names of
`extra_build_packages` finds all four in the `Dockerfile`, because the fourth
is in a second builder stage the field is not about. A check that can be
satisfied by the wrong file is worse than no check, because it reports a pass.

So class two is reported, every run, as fields this mechanism cannot verify,
with a count. **That count is the honest form of the gap `INV-009` found**, and
making it visible on every run is the point.

**The consequence, stated rather than discovered later: `MAN-tools.v1` will
pass this verifier while carrying the two fields `INV-009` found failing.**
Both are class two. Nothing decided here catches them, and the verifier will
say, on every run, that it did not check them.

## Decision 3 — the verifier reports coverage, not only failures

Every run prints, per manifest and in total: how many fields it checked, how
many it could not, and which, by class. A verifier that reports only failures
hides its own blind spots, and hidden blind spots are what `INV-009` found and
what `INV-010` F-1 measured the size of.

This is the property this mechanism is built for. A run that prints "all checks
passed" over 42 of 332 fields is the arrangement being replaced.

## Decision 4 — when it runs, and what a failure does

`INV-010` F-3 measured the cost: the tools 1187 ms in the image, all 3520
corpus digests 6312 ms, the eight checksum lists 68 ms, a container 0.395 s,
and `make check-tools` 1.652 s end to end. Everything this repository holds
verifies in under eight seconds.

**So verification is cheap enough to be a precondition and is made one.**

- **A `make` target verifies every manifest**, and exits non-zero if any
  check fails. It is in the `Makefile`, which `REF-005`'s container work made
  the only place a `docker run` is written.
- **A failure stops the command.** A check that does not stop anything is a
  check nobody acts on, which is `INV-004` B-3's finding about a sentinel
  score, one level up.
- **The corpus part is skipped when no corpus is mounted, and says it skipped
  it.** A skipped check reported as skipped is honest; a skipped check reported
  as a pass is the failure this refinement exists to remove.

## Decision 5 — a recorded run may not start unverified

**A run that produces numbers verifies its dataset and tool manifests first,
and does not start if verification fails.**

The result contract already requires a run record to name every manifest it
used. `INV-010` F-3's measurement removes the only argument against making that
naming conditional on a check: at 7.6 seconds for everything, the cost is
smaller than the cost of one image conversion in the run itself.

No run mechanism exists yet, so this decision binds the one that is written
next rather than changing anything today. It is taken here because taking it
later means taking it against a run that already exists and already produces
numbers, which is the harder place to take it.

## Decision 6 — `MAN-tools.v1` is in scope

**Every manifest under `manifests/` is verified, superseded or not.**

`REF-002` keeps history rather than rewriting it, and old results reproduce
against the manifest they named. A superseded manifest that nothing verifies is
a manifest whose old results are traceable to a claim — the same defect as an
unverified current one, aimed at the past.

**The argument for excluding it, and why it loses.** `MAN-tools.v1` describes
an image that no longer exists, so it can be called frozen history. But
`INV-009` F-1 re-measured 61 of its 63 fields against today's image and 57 of
them hold, including both binary digests: most of what it says is still true of
what is here, and the parts that are not are worth knowing about rather than
declaring out of scope.

**The consequence for the mechanism.** `INV-010` F-1 measured that
`scripts/check_tools.sh` cannot be pointed at `MAN-tools.v1` at all: it dies
with `KeyError: 'identity'`, because v1 predates compositions. So the verifier
must not assume the shape of the newest manifest. It derives what it can check
from what a manifest carries, and a manifest carrying no `identity` block is
verified without one rather than refused.

## Decision 7 — the read-time rule, stated where a reader will find it

`INV-010` F-4 measured that the rule two records rest on is written in exactly
one place git tracks, `README.md` prohibition 3, and that
`manifests/README.md` — the directory contract, and the place a reader looks —
states the status vocabulary and says nothing about reading. `INV-010` F-5
measured that no code implements it: of 100 accesses in a full run, zero are to
a status, and marking a field a run depends on `CONFLICT` leaves the run at
exit 0.

**The rule, restated normatively here and added to `manifests/README.md`:**

- **`CONFLICT` — reading raises.** Code that needs the value of a `CONFLICT`
  field fails rather than falling back. This is `README.md` prohibition 3
  unchanged; what is new is that it is stated in the manifest contract and
  implemented.
- **`UNVERIFIED` — may not be used as a number a result depends on.** It may be
  read and printed, so that a record can say what is unknown. This is
  `README.md` prohibition 2's "the code refuses to use it", narrowed to say
  what "use" means.
- **`APPROX` — may be used, and the use is recorded.** A result that depends on
  an `APPROX` field names it. `INV-010` records, under what it left unchecked,
  that no field in any live manifest carries `APPROX` today, so this binds
  nothing yet and is stated so that the first one does not arrive undecided.

**The verifier implements the first of these for itself**, and reports any
field it would have checked but refused to read. Deciding it and not
implementing it is what `INV-010` F-4 and F-5 together found: a rule stated in
one file, restated in two records, and absent from the only code that reads a
manifest.

## Rejected

- **Declaring each field's class in the manifest.** Rejected in decision 1: it
  adds 332 unreadable-back fields of exactly the kind that failed, and costs
  four re-issues.
- **Searching the tree for a class-two value.** Rejected in decision 2 on
  `INV-009` F-2's measurement: the search passes on the wrong file.
- **Reporting only failures.** Rejected in decision 3: it is the arrangement
  `INV-009` found, which reported "all checks passed" over a manifest with two
  false fields.
- **Verifying only when something asks.** Rejected in decision 4 on `INV-010`
  F-3's measured cost.
- **Excluding `MAN-tools.v1` as frozen history.** Rejected in decision 6:
  `INV-009` F-1 measured that 57 of its 63 fields still hold against today's
  image, and old results name it.
- **Leaving the read-time rule where it is.** Rejected in decision 7: `INV-010`
  F-4 measured that the place it is written is not the place a reader of
  manifests looks, and F-5 that nothing implements it.
- **Extending the tools check into a second, parallel mechanism.** Rejected:
  `scripts/check_tools.sh` is already driven by the manifest rather than by a
  list inside it, and a second script with its own list is the shape this
  refinement is trying to remove. What is built generalises it.

## Open

- ⟨OPEN⟩ **Class two stays unchecked.** Closing it means a manifest whose
  class-two fields name the file and the line they are derived from, which is a
  change to what a manifest carries, and so a new version with its own
  investigation and refinement. Nothing here decides that shape.
- ⟨OPEN⟩ **Wrong at birth stays uncaught.** Stated above as an accepted limit.
  The only instrument for it is an audit, and no decision here schedules one.
- ⟨OPEN⟩ **Whether the two failing fields of `MAN-tools.v1` are corrected, and
  how a wrong value is withdrawn from a frozen manifest.** Out of scope here
  and unresolved.
- ⟨OPEN⟩ **`MAN-minutia.v1` is a JSON Schema, and its eight fields are inside
  it.** `INV-010` F-1 counts them and this refinement classes them like any
  other, but nothing here decides whether a schema should also be validated as
  a schema.
