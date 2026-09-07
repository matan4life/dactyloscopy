# REF-011 — Admitting FingerJetFXOSE, where REF-005 does not reach

Date: 2026-09-07
Rests on: `quality/INV-003-fingerjetfxose-source-and-resolution.md`, the source
read, and `quality/INV-007-fingerjetfxose-built.md`, the tool built and run.
Extends `REF-005`. Applies `REF-007` and `REF-010`. Every factual claim below
is a reference to a fact of a named investigation, by its identifier. This
refinement measures nothing and states no fact of its own.

## Numbering

This refinement takes 011, the next free number. The gap at 001 is explained in
`REF-002` and the gap at 004 in `REF-006`.

## Why this refinement exists

`REF-005` decided that a tool after the first is added by writing a manifest
entry, not by amending a refinement. That was the point of writing it in
general form, and for a second NBIS tool it held.

It does not hold here. This tool breaks three of `REF-005`'s assumptions at
once, and a manifest entry cannot decide any of them:

- **There is no publisher archive to pin by checksum.** `INV-007`'s Method
  records that the project publishes no archive, carries no tag at all, and
  that GitHub's generated tarballs are not byte-stable.
- **Part of what runs it is ours.** `INV-007` F-6 and F-8 make the upstream
  sample unusable, and what replaces it is source this repository writes.
- **More than one file has to cross the stage boundary.** `REF-005` says
  exactly one per tool does.

So the tool is admitted here, and `REF-005` is extended rather than
contradicted: everything it decided that still applies still applies, and the
three places it does not reach are decided below.

## Decisions

### 1. The tool is driven by a caller this repository owns

Not by the upstream sample. The reason is not preference; it is that the
condition `REF-005` already imposes cannot be met through the sample.

`REF-005` requires that what reaches a tool be verified pixel-identical to the
dataset, on decoded pixels rather than encoded bytes. `INV-007` F-6 measures
that the sample's reader begins its pixel buffer one byte early, on the
separator, and F-6's arithmetic shows that its own short-read check **cannot
fire for any well-formed PGM**, because such a file always carries exactly one
byte more than the read starts short by. `INV-007` F-8 then shows that the
reference reader, given a buffer shifted in exactly that way, reproduces the
sample's template byte for byte on all three images.

The required check is therefore not merely hard to pass through the sample. It
is unpassable by construction: the buffer the extractor receives is not the
image, and nothing in the sample's path can report that.

`REF-007`'s resolution of `D-2` already holds that a caller of our own is not a
modified tool. That decision was taken on `INV-003` S-14, which found the
hardcoded resolution in the sample and the resolution parameter in the
library's own entry point. This decision uses it and adds nothing to it.

**Rejected, each with its reason.**

- **The sample, unmodified.** Every number this repository reported for this
  extractor would be a number about a buffer beginning with a separator byte.
  `INV-007` F-8 records that the count moves in both directions across the
  three images, and that one image keeps its count while its template changes,
  so the defect is not a bias that could be characterised once and carried in a
  record.
- **A patch to the sample.** `REF-007` decision 4 rejects patching an external
  tool: the patch is a second artefact with no publisher, carried and justified
  here and reapplied at every upstream change. That ground is sufficient and it
  is the only one this refinement is entitled to use — see "What this
  refinement could not decide" below.
- **Compensating in the file handed to the sample.** A derivation from `INV-007`
  F-6 and F-7, not a measurement: cancelling the shift would mean writing a file
  whose separator byte carries the value the first pixel should have. The parse
  F-6 describes stops at the first byte that is not a digit, so that byte must
  be one a PGM header may use as a separator. An image whose first pixel is not
  such a value cannot be encoded that way, so there is no general encoding that
  cancels the shift.

### 2. Dynamic linking, and two files cross the stage boundary

`REF-005` says exactly one file per tool crosses into the runtime. This is the
first tool for which that is wrong, and the reason is precisely the thing that
makes this tool different: part of what runs it is ours.

Two files cross: the shared library, and the caller this repository builds from
its own source. `INV-007` F-2 records that the two are separable artefacts of
one build, and that a dynamically linked sample resolves the library at run
time while a statically linked one does not.

**The reason for dynamic linking is identity, not licence.** `REF-005` already
divides the world in two: the image pins the environment, git pins the code,
and a run record names both. A static link fuses a third-party library and our
own source into one artefact with one digest, and that digest can no longer
tell a change in our source from a change in theirs. The division `REF-005`
draws would survive in the record and stop existing in the artefact.

`REF-010`'s conclusion points the same way, and is recorded here as agreement
and never as the reason. `REF-010` decision 1 holds that this repository
publishes the tree and never an image, so nothing is distributed and nothing
in `REF-010` is active. A reason that is currently inactive is not a reason; if
it were the ground for this decision, the decision would evaporate the moment
`REF-010` were superseded, and identity would not.

**`fjfxSample` does not cross.** Once the caller exists the sample has no
purpose, and `REF-005`'s own words are that a binary that is not used is a
binary whose provenance nobody checks, and it would still be in the image.

### 3. A tool with no published artefact is pinned by commit and tree

`REF-005` is written around a source of record that is "the publisher's own
artefact", pinned by a checksum of exactly that artefact. `INV-007`'s Method
records that there is none here: no published archive, no tag in the
repository, and generated tarballs whose bytes are not stable.

The pin is therefore **the commit id together with the tree hash**, both
verified before the build, as `INV-007`'s Method records them.

**This is a different kind of pin, and the manifest says so rather than letting
the two look alike.** A checksum of a release names an artefact a publisher
issued; anyone can obtain that artefact and compare. A commit id with its tree
hash addresses content — the tree hash is what makes it a statement about
content rather than about a label — but there is no publisher-issued artefact
behind it, so there is nothing to compare a release against. What can be
checked is that the tree is the tree; what cannot be checked is that anybody
published it.

The `cxxtest` submodule is pinned the same way, by the commit id `INV-007`'s
Method records, and is named in the manifest as the fourth party it is: not
this project, not the publisher of the other tools, and pinned by the weaker
kind of pin for the same reason.

### 4. The build recipe fixes the path and passes the build number

`INV-007` F-4 measures two things this refinement must act on, and they are not
the same kind of thing.

**The path is part of the recipe.** `INV-007` F-4 records that a first attempt
built two trees at two different paths and found 5 of 12 artefacts differing,
that this measured the path and not the build, and that with every build at one
path all 12 are byte-identical. So the build is reproducible with respect to
repetition and not with respect to the directory it runs in. The stage
therefore **fixes the build path**, and that path is part of the recipe the
manifest records. Without it no digest the manifest carries reproduces
anywhere, including here.

**The build number is passed explicitly.** `INV-007` F-4 records that
`-DFRFXLL_BUILD` changes 4 of 12 artefacts and that `cmake/version.cmake`
computes it from the clone's commit count when it is not given. A value derived
from a clone's history is not a property of the source tree the pin fixes: two
clones of the same commit can differ in it. The stage passes it explicitly.

**The honest form of the second reason.** `INV-007` F-4 records the split of 4
against 8 and states that it does not explain it, and it lists the library that
decision 2 sends across the boundary among the artefacts that do not change. So
this is a **guard against an unexplained boundary**, not a response to a
measured drift on the shipping path. No drift on that path has been measured,
and a refinement claiming otherwise would be claiming a fact it does not have.

### 5. Identity is a composition over named parts

A tool that is wholly external has one part: the digest of its binary. This one
has three, because part of what runs it is ours:

| part | label | what it is |
| --- | --- | --- |
| the library | `library` | sha256 of the shared library that crosses the boundary |
| the caller's source | `caller_source` | the git blob id of the caller's source file |
| the built caller | `caller` | sha256 of the binary built from it |

**A blob id and not a commit id, for two reasons.** A commit that issues a
manifest cannot contain its own hash, so a manifest that identified our source
by commit could never be written in the commit that introduces it. And
`INV-003`'s Method already found the second reason: a digest of a working copy
is a fact about a machine, because a checkout can transform bytes, while a blob
id is a fact about the content in the repository.

**The scalar identifier.** `sha256` over a canonical encoding of the parts: one
part per line, as `label=value`, each line terminated by a newline, in **this
order**, fixed here and not left to whoever writes the code:

    library=<sha256>
    caller_source=<blob id>
    caller=<sha256>

A newline cannot occur inside a hex digest, so the concatenation is
unambiguous and no length prefix or escaping is needed. The labels carry which
hash function produced which value, which matters because a blob id and a
sha256 are different functions and both are hex.

A one-part composition is the same encoding with one line, `binary=<sha256>`.

The scalar is **derived**: anyone holding the parts recomputes it, so it cannot
disagree with them. That is why it may travel where the parts cannot.

**Where each goes.** The parts go in the manifest, which is where a value with
a status belongs. The scalar goes in the `run:` trailer and in the run record.
In `REF-002`'s own terms a trailer is an index and not a copy: the scalar is a
key to look the parts up by, not a second place they are written.

**`MAN-tools.v2` restates `mindtct` and `bozorth3` under the same rule**, as
one-part compositions. The manifest is then homogeneous in the rule and not in
the field count, and that is the right kind of homogeneity: two tools having a
different number of parts is not inhomogeneity when one of them contains none
of this repository's code and the other does. A rule that forced them to the
same shape would have to either invent a part for the tools that have none or
drop a part from the tool that has them.

### 6. The caller is not named after the upstream project

The caller is called **`iso-extract`**. It is not named `fjfx`-anything, and it
does not carry the upstream project's name, the publisher's name, or any
abbreviation of either.

The ground this refinement is entitled to use: a name that borrows another
project's asserts a relationship this repository has not established, and
`REF-005` makes a tool's identity a thing that is recorded rather than implied.
A caller named after the library would be read as a build of the library, which
is exactly what decision 5 exists to keep distinguishable.

The brief that commissioned this refinement offered a second ground, in this
tool's own terms. That ground is not available here: no investigation in this
repository has read those terms, and using one would be stating a fact this
refinement does not have. See "What this refinement could not decide".

The name is settled here and not left to the code, because the manifest and the
Dockerfile both use whatever it says, and a name decided in two places is a
name that will differ in two places.

### 7. The acknowledgement, and why it cannot be written yet

`REF-010` decision 4 applies: attribution in this repository is discharged by
citation, and where an external tool's own terms ask that a particular sentence
be used in acknowledging it, that sentence becomes the form of the citation,
written **because attribution is owed** and not because an obligation attaches.

**Applying it to this tool is blocked, and the block is the point of recording
it.** `REF-010` decision 4 is conditioned on what a tool's terms ask for.
`INV-006` covers what is already in the image and says so; `INV-007` states in
its own Method that its subject is the build and what the tool does, and its
"Not in this record" excludes any licence reading. So no record in this tree
says what this tool's terms ask for, or whether they ask for anything.

The decision is therefore: **an acknowledgement is written in `docs/`, in the
form `REF-010` decision 4 prescribes, and its wording comes from an
investigation that reads this tool's terms.** That investigation does not
exist. Until it does, the acknowledgement is not written, and this refinement
does not guess at its wording — writing a sentence attributed to terms nobody
here has read would be exactly the fabrication `REF-010` decision 2 refuses for
identifiers.

### 8. The corpus restriction stands unchanged

`REF-007` decision 4 excludes `fvc2002/DB2` from any comparison involving this
extractor. **Nothing here narrows it and nothing here widens it.**

This is stated rather than left silent because a reader who sees a refinement
admitting the tool will ask whether the exclusion was reconsidered. It was not
reconsidered, and the reason is that nothing new bears on it: `INV-007` states
under what it left unchecked that it tried no declared resolution other than
the one the sample passes, and the reference reader passes the same one so that
it differs from the sample in one thing only. The facts `REF-007` decision 4
rests on are unchanged and so is the decision.

### 9. `INV-003` R-6 is correct and is now explained

`INV-003` R-6 recorded three pairs of numbers as `UNVERIFIED`, reported from
outside this repository. `INV-007` F-8 reproduces them exactly, as the figures
the upstream sample produces, and shows what they are figures of: templates
taken from a buffer that begins with the separator byte.

They were correctly reported and they are now explained. `REF-002` decides that
history is not rewritten, so `INV-003` is not edited; this refinement carries
the pointer instead, so that a reader arriving at R-6 does not take those
numbers for a property of the tool. They are a property of the tool driven by
that sample, and decision 1 is why this repository will not drive it that way.

## What this refinement could not decide

Three of the grounds the brief offered rest on the content of this tool's
licence terms: that a patch would oblige the tree to be marked as carrying a
modified version, that a condition forbids the upstream names in a derived
product's name, and the sentence an acknowledgement should use.

**No investigation in this repository has read those terms.** `INV-006` reads
the terms of what is already in the image and states that this tool is outside
its scope; `INV-007` excludes licence reading from its own. A refinement that
cited them would be introducing facts, which `quality/README.md` forbids here
and which this repository forbids everywhere without a record behind them.

So decisions 1 and 6 are taken on the grounds that were available, which are
sufficient on their own, and decision 7 is taken as far as it can be and
blocked where it cannot. The gap is on the open list.

## Rejected

- **The upstream sample, unmodified.** Rejected in 1: it makes every number a
  number about a shifted buffer, and `INV-007` F-8 shows the effect is not a
  characterisable bias.
- **A patch to the sample.** Rejected in 1 on `REF-007` decision 4.
- **Encoding the input so as to cancel the shift.** Rejected in 1: no general
  encoding exists.
- **Static linking.** Rejected in 2: it fuses their code and ours into one
  digest and destroys the distinction `REF-005` is built on.
- **Resting the linking decision on `REF-010`.** Rejected in 2: `REF-010`
  decision 1 makes that ground inactive, and a decision resting on it would
  evaporate if `REF-010` were superseded.
- **Shipping `fjfxSample` as well.** Rejected in 2 on `REF-005`'s own ground.
- **Treating a commit id as a checksummed release.** Rejected in 3: it
  addresses content but names no artefact anyone published, and the manifest
  says which kind it is.
- **Letting `cmake/version.cmake` derive the build number.** Rejected in 4: it
  is computed from a clone's history rather than from the pinned tree.
- **A single digest as the tool's identity.** Rejected in 5: one digest over
  their library and our source cannot distinguish a change in one from a change
  in the other.
- **Identifying our source by commit id.** Rejected in 5: the commit that
  issues a manifest cannot contain its own hash.
- **A digest of the caller's source as checked out.** Rejected in 5 on
  `INV-003`'s Method: it is a fact about a machine.
- **Forcing every tool in the manifest to the same field count.** Rejected in
  5: it would invent a part or drop one.
- **Naming the caller after the upstream project.** Rejected in 6.

## Open

- ⟨OPEN⟩ **This tool's terms have not been read here.** Three grounds the brief
  offered are unavailable for that reason, and decision 7 is blocked on it. It
  closes with an investigation that reads them, in the way `INV-006` read the
  terms of what is already in the image.
- ⟨OPEN⟩ `INV-003` X-1 stays in `CONFLICT`. Nothing above rests on it, and
  `INV-007` states that it decoded a template exactly far enough to read one
  byte and left the conflict untouched.
- ⟨OPEN⟩ The split `INV-007` F-4 reports, of 4 artefacts changing with the
  build number against 8 that do not, is unexplained. Decision 4 guards against
  it rather than relying on an explanation.
- ⟨OPEN⟩ Whether the reading defect of `INV-007` F-6 is also in
  `frfxllSample`, which `INV-007` records it built, digested and never ran.
- ⟨OPEN⟩ **`INV-003` F-2's split of the ISO record is wrong, and this is not
  the place to correct it.** F-2 gives the record as `24 + 6 + 6n`, and the sum
  is right: `INV-007` F-8 records that every template's length obeys it.
  The split is not. `INV-007` F-8 reads the minutia count at offset 27, derived
  from the serializer's own lines, which puts four bytes before the minutiae and
  two after them, not six before and none after. A parser written from F-2's
  split starts six bytes late. It needs its own investigation and a manifest
  correction; `REF-002` and the immutability rule mean neither happens by
  editing F-2.
