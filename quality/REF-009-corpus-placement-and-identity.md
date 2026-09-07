# REF-009 — Placing a corpus, and what its manifest may claim

Date: 2026-09-07
Rests on: `quality/INV-005-fvc2002-corpus.md`. Every factual claim below is a
reference to a fact of that record, by its identifier. This refinement measures
nothing and states no number of its own.

## Numbering

This refinement takes 009, the next free number. The gap at 001 is explained in
`REF-002` and the gap at 004 in `REF-006`.

It exists because `manifests/README.md` requires it: a manifest names the INVs
and REFs that produced it, so a manifest cannot be issued without both. The
facts are in `INV-005`; the decisions taken on them are here.

## What is being decided

A corpus has arrived on the machine and has to be put somewhere, described, and
given an identity that a run record can point at. Four things follow from that
and are decided once, for this corpus and for the next one:

where the files live and how they are addressed; where the roles of the subsets
come from; how the per-file digests are carried; and what a digest is allowed to
be evidence of.

Not decided here: the protocol, the pair lists, any metric, and anything about
what is compared with what. Those are an experiment declaration and a protocol
manifest, and neither exists.

## Decisions

### 1. The distribution's own layout is kept, and our names map onto it

The tree is copied verbatim into the raw location — every directory the
distributor shipped, under the distributor's own names, with no repacking, no
renaming and no flattening. Our subset identifiers live in the manifest, which
maps each one onto the path the distributor used.

The layout is the only thing that makes this copy comparable with anyone
else's. Somebody who holds the same distribution can check their files against
our lists directly; somebody who holds a repacked copy has to reconstruct our
repacking first, and any difference between their reconstruction and ours looks
exactly like a difference in the data.

The alternative was to reorganise into a layout that suits this project — one
directory per subset under our own names, index files moved or dropped.
Rejected: it buys tidiness inside one repository and costs the ability to
verify anything against a copy from outside it. Mapping in the manifest costs
one field per subset and keeps both.

A second alternative was to link rather than copy. Rejected on a mechanism
`INV-005`'s method records: a junction inside a mounted directory surfaces as
an empty mount rather than an error, so the failure mode is a run that reads
nothing and reports nothing wrong.

### 2. The roles of the subsets come from the organisers, not from us

Which subset is an evaluation set and which is a tuning set is not this
project's choice. The competition defined it when it distributed the data:
one range of fingers was the benchmark evaluation set, and a separate range was
given to participants for parameter tuning. The manifest records the role each
subset was given, and attributes it.

This matters because a role we assigned would be a role we could reassign. A
role the organisers assigned is a fact about the data, and a result computed on
the tuning set is not a benchmark result no matter what this project would
prefer.

**The consequence is recorded rather than left to be noticed.** This project has
been using a tuning subset for its tool fixtures. That is legitimate for what it
was used for — checking that a tool in the image is the tool the manifest froze
— and it is not legitimate for reporting a result without naming the set the
result came from. The manifest states the role so that a run record which names
a subset also names what that subset is for.

The alternative was to leave roles out of the manifest and let each experiment
declare what it is using. Rejected: the role would then be restated once per
experiment, and a restatement can differ from the original. Naming it once, in
the manifest, with the source of the definition, means an experiment cites it
instead of repeating it.

### 3. Per-file digests are carried as standard lists, not as manifest fields

The digest of every file is recorded, one list per subset, in the format the
standard checksum tool reads and writes, under the directory
`manifests/README.md` reserves for them. The manifest names each list and
carries the digest **of the list**.

Two reasons, and they pull the same way. A manifest that carried an object per
file would be unreadable by a person and would bury the fields that are
decisions — the roles, the statuses, the mapping — under thousands of lines that
are not. And a list in the standard format is verified by the standard tool with
one command, so checking a corpus against this repository needs nothing from
this repository: no script, no dependency, no version of ours to install.

The digest of the list closes the chain: the manifest fixes the list, the list
fixes the files.

The alternative was one object per file in the manifest. Rejected above. A
second alternative was a single list for the whole corpus. Rejected: a subset is
the unit this project addresses data by, so it is the unit a checksum list
should be addressable by; and a corpus-wide list cannot be checked with one
`cd` and one command.

### 4. A digest may not be presented as evidence of authenticity

A digest taken from the tree it describes establishes that a copy is faithful to
that tree. It establishes nothing about where the tree came from. Using it for
the second is circular, and a manifest that lets a reader make that inference
has misled them whether or not it said anything false.

So the manifest states the two claims separately: that the copy is faithful,
which is `VERIFIED`, and that the tree is the official distribution, which is
`UNVERIFIED`. What supports the second is recorded as corroboration, in a field
that says it is corroboration: properties a faithful copy would have and a
corrupted or substituted one probably would not. None of them is a signature and
the manifest does not call them one.

Closing it needs something from outside this tree: a checksum the organisers
publish, or a second copy obtained independently. `INV-005` R-2 records that the
first could not be settled from here — not that it fails, but that the site
could not be read — and the question stays open rather than being closed in the
convenient direction.

The alternative was to record a single "verified" field over the corpus and let
the digests speak for it. Rejected: it is exactly the inference this decision
exists to prevent, and it would be the strongest-looking claim in the manifest
while being the weakest one in it.

### 5. The licence is recorded per subset, with its status and its source

Not once for the corpus: per subset, because it differs between them and it
determines who can reproduce what. A reader who holds only what is freely
distributed can reproduce a result computed on those subsets and cannot
reproduce one computed on the others, and that is a property of the result, not
of the reader.

The claim itself is second-hand (`INV-005` R-3), so it carries a status and
names where it came from. A licence statement in a manifest is the kind of field
that gets quoted onward, and one that is quoted onward without its provenance
becomes this repository's assertion rather than somebody else's report.

The alternative was to omit the licence until it could be verified. Rejected: a
missing field invites the reader to assume the permissive answer, and the
asymmetry between the two halves of this corpus is exactly what a reader needs
to know before planning to reproduce anything.

## Rejected

- **Reorganising the tree into a layout that suits this project.** Rejected in
  1: it costs verification against any copy from outside.
- **Linking instead of copying.** Rejected in 1: the failure mode is silence.
- **Letting each experiment declare the role of the subset it uses.** Rejected
  in 2: a restatement can differ from the original.
- **One object per file in the manifest.** Rejected in 3: it buries the fields
  that are decisions.
- **A single checksum list for the whole corpus.** Rejected in 3: the subset is
  the unit data is addressed by.
- **Treating a digest as evidence that the tree is authentic.** Rejected in 4,
  and it is the reason this refinement exists at all.
- **Omitting the licence until it can be verified.** Rejected in 5: absence
  reads as permission.

## Open

- ⟨OPEN⟩ Whether the tree is the official distribution. `INV-005` R-1. It closes
  when a checksum published by the organisers can be read, or when a second copy
  obtained independently agrees with this one — which is the two-sources
  condition this repository already requires before a field may be `VERIFIED`.
- ⟨OPEN⟩ Whether the organisers publish such a checksum at all. `INV-005` R-2
  records that this could not be established from here in either direction.
- ⟨OPEN⟩ The licence, which is second-hand. `INV-005` R-3.
- ⟨OPEN⟩ Whether every line of the index files names a pair that exists in the
  corpus, and whether the pairing follows the protocol its line counts imply.
  `INV-005` checked the shape of those files and one specific line; the protocol
  they define is not this refinement's subject and has no manifest yet.
