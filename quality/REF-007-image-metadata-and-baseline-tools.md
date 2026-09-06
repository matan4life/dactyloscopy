# REF-007 — Image metadata, and the terms on which a tool is adopted

Date: 2026-09-06
Rests on: `quality/INV-003-fingerjetfxose-source-and-resolution.md`, and
`quality/INV-002-minutia-formats.md` for the canon this extends. Every factual
claim below is a reference to a fact of those records, by its identifier. This
refinement measures nothing and states no number of its own.

## Numbering

This refinement takes 007, the next free number. The gap at 001 is explained in
`REF-002` and the gap at 004 in `REF-006`.

## What is being decided

A minutiae extractor writes a template, and the template carries a header the
tool fills in: its resolution (`INV-003` S-4), and, among the parameters that
reach the serializer, the image's size and a quality for the finger (`INV-003`
S-13). A reader can take those fields as the image's description, and it is the
obvious thing to do, because they arrive in the same file as the minutiae and
cost nothing to read.

`INV-003` shows what that costs. In the tool examined there, the field a
template carries for resolution is written from a serializer parameter (S-13),
while the resolution the minutiae were actually computed at is pinned to a
constant with the authors' own comment saying it is broken (S-8), and their own
self-test asserts the broken value rather than the right one (S-10). A header
field is a claim by whoever wrote the file. It is not a measurement of the
image.

Two things follow that are worth deciding once: where the image's description
comes from, and on what terms a tool whose account of the image is unreliable
may be used at all. Neither is specific to the tool that prompted them.

## Decisions

### 1. Image metadata comes from the dataset manifest, never from a tool

Width, height, resolution, bit depth, colour interpretation: every one of them
is read from the dataset manifest that identifies the image, and never from a
file a tool wrote. What a tool states about an image is a claim to be checked
against the manifest, not data to be used.

This is general, and it applies to tools this repository already runs. The
detail output of the extractor already in the image carries an image size on
its first line (`INV-002` F-1), and that line is treated exactly the same way:
usable to check the manifest, never to populate a field.

The alternative was to read metadata from whichever file was at hand. Rejected:
it makes the value of a field depend on which tool ran, so two records of the
same image can disagree about the image, and neither is wrong by its own
lights. A manifest exists precisely so that there is one answer.

A second alternative was to read it from the image file's own header. Rejected
for the same reason in weaker form: an image header is also a claim, made by
whoever encoded the file, and it is the manifest's job to have checked it once
rather than every reader's job to trust it every time.

### 2. A disagreement between a tool's claim and the manifest fails the run

When a tool states something about the image that the manifest contradicts, the
run stops. It does not warn, prefer one source, or carry both.

There are three ways to arrive at such a disagreement, and all three are worth
learning about at once: the wrong file was read, the conversion before the tool
changed something it should not have, or the manifest is wrong. The first two
invalidate the run outright. The third invalidates every run that used that
manifest, which is a larger thing and should not wait.

The alternative was to log the disagreement and continue on the manifest's
value. Rejected: the manifest's value is right by decision 1, so continuing
produces numbers that are arithmetically fine and mean nothing, and the log
line is read after the numbers have been quoted. A check that does not stop
anything is a check nobody acts on.

### 3. The canon carries the tool's own record, separately and opaquely

Two blocks, and they never mix:

- `image` — the description of the image, populated from the dataset manifest
  by decision 1. This is the block that is read.
- the tool's own record — the bytes the tool wrote that the canon cannot
  reconstruct from its own fields: the record header, and any extended data
  block. Kept verbatim, kept opaque, and **never read as data**.

The second exists for one reason: so that a byte-identical round trip stays
possible. `REF-006` decision 3 keeps the minutia order for that test; a
template also has a header, and a round trip that reproduces the minutiae but
not the header is not a round trip. Keeping the header verbatim is what makes
the test total.

It holds only what is not reconstructible. The minutiae are already in the
canon and are not stored a second time: a second copy is a second thing to keep
in agreement, and the decision that it is never read would be much harder to
hold if it contained the data.

This does not reopen `REF-006` decision 5. What is forbidden there is reading
back a file this repository emitted; what is kept here is what the *tool*
wrote, which is how a canon record is built in the first place.

The alternative was to drop the tool's header once the manifest had been
checked against it. Rejected: it makes a byte-identical round trip impossible,
and that test is one of the two external checks a reader and a writer can be
held to. The other alternative was to merge the header's fields into `image`
where the manifest has no opinion. Rejected: it produces a block that is
authoritative in some fields and hearsay in others, with nothing in the record
saying which is which.

### 4. Where a tool is defective outside a window, restrict the corpus

The general rule: when a tool's behaviour is undefined or acknowledged broken
outside some window of its inputs, this repository uses the tool unmodified and
restricts the corpus to the window, rather than modifying the tool to widen it.
The restriction is recorded with its reason, so that a later reader sees a
choice rather than an omission.

Modifying the tool would move it out of `REF-005`'s reach: the source of record
there is the publisher's artefact pinned by a checksum, and a patch on top is a
second artefact with no publisher, carried and justified here, reapplied at
every upstream change. Restricting the corpus costs coverage, which is
visible, countable, and stated in the run. A modification costs provenance,
which is none of those.

**First application.** FingerJetFXOSE is used unmodified and restricted to
corpora at the resolution to which it pins its own internal value whatever it
is told (`INV-003` S-8). FVC2002 DB2, whose reported resolution differs
(`INV-002` R-5), is excluded from any comparison involving this extractor, and
this paragraph is the record of why.

A further tool is accommodated by an investigation and a manifest entry naming
its window, not by amending this file.

The alternative was to declare each image's true resolution. Rejected on three
grounds, in increasing order of weight. It buys nothing inside the window,
where `INV-003` S-11 shows the resampling path does not depend on the declared
value at all. Outside the window it produces a different extraction along a
path the authors themselves annotate as broken (`INV-003` S-8) and whose
defective behaviour their own self-test pins in place of the correct one
(`INV-003` S-10). And what a declaration other than the reference one does to
the coordinates is not established at all: `INV-003` X-1 is in `CONFLICT`, and
a decision may not rest on a field this repository is forbidden to read. An
option that depends on an unsettled question is not available until it is
settled.

A second alternative was to modify the tool so that it carries the declared
resolution through, which is what its authors' commented-out line would do.
Rejected: it is a patch to a defect in someone else's code, and the moment it
exists every number this repository produces depends on a build no one else
has.

### 5. A tool is adopted as a reproducible baseline, not as a correct one

What this repository requires of an external extractor is that it be
deterministic and that its provenance be pinned. It does not require, and does
not claim, that the tool is correct.

Stating this is the point. A baseline is useful when it is fixed and traceable:
two numbers computed against the same pinned tool are comparable to each other,
which is what a point of reference is for. None of that needs the tool to be
right, and nothing in a result computed against it may be phrased so as to
imply that it is. In particular, a disagreement between two adopted tools is
not evidence that either is wrong; it is a fact about the two tools.

FingerJetFXOSE is adopted on exactly these terms, and `INV-003` is why the
distinction has to be written down rather than assumed: a tool whose authors
annotate one of its own paths as broken can still be a perfectly good fixed
point, and calling it one is not a criticism.

The alternative was to say nothing and let adoption imply endorsement.
Rejected: it is the reading a later reader would take, and the record's purpose
is that nothing is implied.

## What D-2 resolved to

`D-2` asked whether the extractor should be used through its sample program
unmodified, and therefore restricted, **or** given the true resolution, thereby
becoming a tool this repository has modified.

It resolved to neither, because the question's premise was wrong. Passing the
true resolution never required modifying anything: `INV-003` S-14 shows the
hardcoded value is a literal in the sample program, while the library's own
entry point takes the resolution as a parameter. A caller of our own is not a
modified tool.

So the two options were never the two options. The tool is used unmodified and
the corpus is restricted — which resembles the first branch — but for a reason
the question did not contain: not because the tool cannot be told the
resolution, but because telling it something other than the reference value
runs a path its authors document as broken, and lands in a question `INV-003`
leaves in `CONFLICT`.

## Rejected

- **Reading image metadata from a tool's output.** Rejected in 1: it makes the
  image's description depend on which tool ran.
- **Reading it from the image file's header.** Rejected in 1: also a claim, and
  checking it once in a manifest is the manifest's purpose.
- **Warning on a disagreement and continuing.** Rejected in 2: it produces
  numbers that are arithmetically fine and mean nothing.
- **Discarding the tool's own header once checked.** Rejected in 3: it makes a
  byte-identical round trip impossible.
- **Merging the tool's header fields into the authoritative block.** Rejected
  in 3: a block that is part record and part hearsay, with no field saying
  which.
- **Declaring each image's true resolution to a tool defective outside its
  window.** Rejected in 4, including on the ground that it depends on a
  `CONFLICT` field.
- **Patching the tool to fix the defect.** Rejected in 4: every number would
  then depend on a build no one else has.
- **Letting adoption imply endorsement.** Rejected in 5.

## Open

- ⟨OPEN⟩ `D-3`, narrowed by `INV-003`: the *encoding* of ISO/IEC 19794-2:2005 —
  units, record layout, field packing — is now established from an
  implementation. What remains open is the *semantics*: what the angle means
  physically, in absolute terms, rather than relative to one extractor's
  internal convention. An implementation is not a specification, and decision 1
  of `REF-006` adopts the standard's semantics without this repository having
  read them.
- ⟨OPEN⟩ `D-4`: the rotation between the standard's angle and the native one.
  `INV-003` F-3 states the transform one library applies in its own units and
  goes no further; nothing here relates either to the other extractor's
  convention. `REF-006` decision 2 makes that rotation part of every emission.
- ⟨OPEN⟩ `INV-003` X-1 is in `CONFLICT` and stays there until a template is
  produced and decoded inside this repository, or the caller that produced the
  reported observation is available. Decision 4 is written so that nothing
  rests on it, and the exclusion it mandates does not become safe to lift if
  the conflict resolves one way rather than the other — that would need its own
  refinement.
- ⟨OPEN⟩ `D-1`, unchanged: which coordinate convention the matcher requires.
