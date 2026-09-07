# REF-008 — Freezing the minutia canon format

Date: 2026-09-07
Rests on: `quality/INV-002-minutia-formats.md`,
`quality/INV-003-fingerjetfxose-source-and-resolution.md` and
`quality/INV-004-nbis-acknowledged-defects.md` for the facts, and on
`REF-006` and `REF-007` for the decisions this one carries out. Every factual
claim below is a reference to an identifier in those records. This refinement
measures nothing and states no number of its own.

## Numbering

This refinement takes 008, the next free number. The gap at 001 is explained in
`REF-002` and the gap at 004 in `REF-006`.

## What is being decided

`REF-006` decided that there would be a canonical minutia record and what it
would promise. It did not say what the file looks like. This refinement settles
that, and freezes it as `manifests/MAN-minutia.v1.json`.

The freezing happens now, before any reader or writer exists, and that order is
itself one of the decisions. What is not decided here: how a canon file is
produced, what reads it, what language any of that is written in, or where in
the tree it lives.

## Where the definition lives, and how the directory contract is met

The brief that commissioned this work asked for the format under `manifests/`
and asked that the repository's own contract be followed instead if it said
otherwise. It was checked, clause by clause.

`manifests/README.md` admits "frozen, machine-readable manifests" named
`MAN-<name>.v<N>.json`, requires that a manifest name the INVs and REFs that
produced it, requires immutability and versioning, and excludes input data,
minutiae, derived artifacts, results, and anything edited by hand after issue.
A format definition is none of the excluded things, it is frozen and
machine-readable, and it takes the name. `workflow/` was considered and
rejected: its contract is about how a derived artifact is *produced*, and a
format is not a production rule.

One clause needed a reading rather than a match: **"every number in it carries a
status ... A number without a status does not belong here."** A JSON Schema
cannot carry a status inside its own keywords without ceasing to be a JSON
Schema, and it contains two kinds of number, which the clause does not
distinguish because it was written before there was a schema to write.

The reading taken: the four-status vocabulary governs values this repository
asserts about the world — a count, a checksum, a resolution, a scale read off a
tool. A schema also contains bounds that assert nothing and merely define the
format's own shape. The manifest therefore carries an annotation block, under a
keyword a validator ignores, in which **every** number in the file is
enumerated: the asserting ones with a status and the record they rest on, the
structural ones named as structural and given none.

This is a reading, not a match, and it is recorded here rather than left in the
file so that a later reader can disagree with it in one place. The alternative
was to keep the definition outside `manifests/` and leave that directory for
observations only. Rejected: the format is exactly the kind of thing the
directory exists for — frozen, versioned, machine-readable, and something a run
record must be able to point at — and moving it would have solved a wording
problem by putting the artefact somewhere its own contract fits worse.

## Decisions

### 1. Every field is an integer, and there is no floating point in the canon

Not "integers where convenient": nowhere, at any depth, including inside the
opaque block that preserves a source's own header.

Two implementations of a reader must agree on values exactly. A float makes
that unattainable: the same decimal literal parses to different values under
different runtimes, arithmetic on it is not associative, and the only way to
compare two floats is with a tolerance — which is a number somebody has to
choose, defend, and carry into every comparison that follows. An integer
comparison needs none of that. This is the same reason `INV-002` F-16's unit
was chosen: it is the coarsest unit in which every angular grid in play is a
whole number, so no conversion between the formats rounds.

The alternative was to store angles and reliabilities as floats and compare
with a tolerance. Rejected: the tolerance would become a field of every run
record, and a difference smaller than it would be invisible rather than
absent.

The limit of what the schema can enforce here is recorded in the manifest and
was measured rather than assumed: JSON Schema's integer type tests the value
and not its spelling, so a file that writes an integer with a fractional part
validates. The canonical serialisation below never produces one.

### 2. Units are declared in the file, not carried in field names

`angle` and `reliability` are bare names, and the file states its own scales in
a `conventions` block whose every entry is a constant.

The alternative was `angle_deg32` and `reliability_milli`: a unit in the name.
Rejected for two reasons. A name is not machine-readable — nothing can check
that a file's contents match the unit its field names claim — while a constant
in a `conventions` block can be asserted by a reader on load and by a validator
before that. And a name that carries a unit becomes wrong rather than absent
if the unit ever changes, whereas a stated convention that changes makes the
file fail validation, which is the correct outcome: a file that needs different
conventions is a different format.

Stating the conventions in every file rather than in the schema alone also
means a canon file that has travelled away from this repository still says what
its numbers mean.

**This supersedes a name in `REF-006`, and the change is stated rather than made
quietly.** `REF-006` decision 4 named the field `reliability_milli`, carrying
its unit in its name. The field frozen here is `reliability`, with the unit in
`conventions`. Nothing about that decision changes — the field is still read
from the source's own detail output, still never derived from quality, still
absent rather than null when the source provides none. Only the spelling
changes, and it changes for the reason above. `REF-006`'s text is left as it
was: a refinement that is superseded in part is superseded in the open, not
edited afterwards to look as though it always said the new thing.

### 3. `angle_levels` belongs to `produced_by`, not to `conventions`

The source's angular quantisation is a fact about the source, not a property of
the canon. `conventions` says what the canon's own units are; `produced_by`
says what the tool that filled the file could express.

It is in the record for one purpose: so that a reader's angle arithmetic can be
checked against the grid the source actually used. `INV-002` F-7 is the reason
that check is worth having — the angle rule reported to that investigation was
wrong, and a rule that is wrong on part of a grid produces angles that are
plausible, in range, and off the grid. That whole class of error is caught by
one comparison, and only if the file says which grid it came from.

It is not there for emission. Which rounding rule applies when a canon angle is
written back to a tool's format is fixed by the target format, and `INV-004`
now establishes those rules from the NBIS source rather than by inference.

The alternative was to leave it out and let a reader infer the grid from the
angles present. Rejected: an inference from the data cannot distinguish a
coarse grid from a fine grid that happened to produce coarse values, and it
would silently agree with a reader that had already made an arithmetic error.

### 4. Canonical serialisation is for addressing; comparison is of parsed content

Two jobs, and conflating them costs something real, so they are separated.

**Addressing.** A canon file needs a stable digest that a run record can point
at, so the serialisation is pinned: keys sorted, a fixed indent, LF only, one
trailing newline, no byte-order mark, ASCII only. Two producers given the same
content produce the same bytes and therefore the same digest.

**Comparing two implementations.** When there is a reader in one language and a
reader in another, they are compared on **parsed content**, never on bytes. A
byte comparison would fail when someone changes an indent, and a failure for an
uninteresting reason trains people to ignore the check. This repository has
already refused that trade once: `REF-005` records that a format conversion is
verified on decoded pixels and never on encoded bytes, because a container's
bytes depend on the compressor's version while the pixels do not. The same
argument applies to JSON, and it is the same decision, taken twice for the same
reason.

The alternative was one rule for both jobs. Rejected in both directions:
comparing implementations by bytes fails for formatting; addressing by parsed
content gives no digest at all.

### 5. The format is frozen before it has a producer

Nothing implements this format yet, deliberately. No reader, no writer, no
validation tooling, no rule that generates a canon file.

A format that is written down after its first implementation is a description
of that implementation, including the parts that were accidents. Every
subsequent implementation then has to reproduce the accidents, and there is no
way to tell which parts were decided and which were merely done. Freezing first
inverts that: the first implementation has something to conform to, and where
it cannot conform the disagreement is visible as a disagreement rather than
settled quietly in favour of whoever wrote code first.

The cost is real and is accepted: some of what is frozen here will turn out to
be inconvenient, and correcting it means `v2`, a new investigation and a new
refinement, with `v1` left in place because results recorded against it must
still reproduce. That is the price of the same rule that makes a manifest
immutable, and it is cheaper than a format nobody can state.

## Rejected

- **Adopting one of the three tool formats as the canon.** The strongest
  alternative, and it fails on each candidate for its own reason. `.xyt` carries
  no minutia type at all (`INV-002`), so adopting it would make that loss
  permanent for every source that does report a type. ISO as written by the
  implementation `INV-003` examined has no way to say "unknown", so adopting it
  would force a tool's silence to be recorded as a positive claim. And the
  formats quantise angles on grids whose shared directions `INV-002` F-18
  counts, and there are very few of them, so adopting any one of them would put
  a rounding step into every conversion out of it. A canon whose unit is the one
  all three divide (`INV-002` F-16) has no such step.
- **Floats with a tolerance.** Rejected in 1.
- **Units in field names.** Rejected in 2.
- **Inferring the source's grid from the angles present.** Rejected in 3.
- **One serialisation rule for both addressing and comparison.** Rejected in 4.
- **Writing the format down after the first reader exists.** Rejected in 5.
- **Keeping the definition outside `manifests/`.** Rejected above, in the
  reading of the directory contract.

## What the schema cannot express, and what follows

The manifest enumerates this in full and states, for each item, that nothing
enforces it today. Three of them matter enough to be decisions rather than
notes:

- **An angle on the source's own grid.** Expressible only for the quantisations
  the format already knows, by conditional subschemas; not expressible in
  general, because JSON Schema has no arithmetic between two places in an
  instance. The first reader and the first writer must check it, and this
  refinement records that as a requirement on them rather than leaving it to be
  discovered.
- **A coordinate inside the image.** Not expressible for the same reason. Same
  requirement.
- **That the order of minutiae carries meaning.** Not expressible at all: a
  JSON array is ordered, so the order survives, but "do not sort this" is a
  statement about readers and writers. `uniqueItems` is deliberately absent, so
  two identical entries are legal, because a source may legitimately report
  them and dropping one would be a loss the canon exists to prevent.

## Open

- ⟨OPEN⟩ `D-3`, issue 7: what the standard's angle direction means in absolute
  terms. The manifest freezes the *label* `iso-19794-2` for the direction and
  says in the same breath that its meaning is not settled here. A file is
  therefore self-consistent and citable before the question is answered, and
  answering it does not invalidate a file — but until it is answered, no claim
  may be made about what a canon angle means physically.
- ⟨OPEN⟩ `D-4`, issue 8: the rotation between that direction and the native
  one. It is what an emission back to the native format needs, and nothing here
  supplies it.
- ⟨OPEN⟩ Whether `source_header` is enough for a byte-exact round trip of every
  source. It is defined as what the canon cannot reconstruct from its own
  fields, which is a definition and not a demonstration; the demonstration is
  the round trip, and there is nothing yet to run it with.
- ⟨OPEN⟩ The dataset manifest that `image.dataset` and `image.id` address does
  not exist. Until it does, those two fields name a thing this repository
  cannot check, and `INV-002`'s note that the fixture is identified by a
  directory name rather than a checksummed set applies to every canon file
  written before then.
