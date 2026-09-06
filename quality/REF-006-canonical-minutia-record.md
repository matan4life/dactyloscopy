# REF-006 — The canonical minutia record

Date: 2026-09-06
Rests on: `quality/INV-002-minutia-formats.md`. Every factual claim below is a
reference to a fact of that record, by its identifier. This refinement
measures nothing and states no number of its own.

## Numbering

This refinement takes 006, and 004 is left free. The author's account is that
004 was allocated in an earlier brief to a refinement on metric definitions,
which was deferred before it was written; the number is left to it. That
account is not verified here and nothing below rests on it. The gap at 001 is
explained in `REF-002`.

Numbers are allocated upward and a gap is never backfilled, so that the
identifier of a record also says when it was taken. `quality/README.md` states
the shape of the file name; the allocation rule is the one `REF-002` set by
precedent when it explained why 001 was empty rather than reusing it.

## What is being decided

More than one extractor will be used. One is already in the image; another
writes an ISO template (INV-002 R-3, R-4); nothing rules out a third. Each
writes its own format, a matcher reads another, and every pair of formats
differs in at least the origin of the y axis, the unit of the angle and the
direction the angle points (INV-002 F-5, F-13, R-1, R-2). The decisions below
are written to hold for an extractor that is not yet named: a new one is
accommodated by a reader, not by an amendment here. A representation that a
conversion may pass through is therefore
needed before any reader or writer is written, and the alternative to deciding
it now is deciding it once per converter, in whichever direction each
conversion happened to be written first.

This refinement decides what that representation is and what it promises. It
decides nothing about the language it is written in, the layout of the tree, or
which extractor is used for which run.

## Decisions

### 1. The canon is a superset of ISO 19794-2, not an independent design

Where the standard defines a semantics, the canon takes it unchanged and adds
fields beside it rather than reinterpreting it. Where the standard defines
nothing the canon needs, the canon defines it, and says so in the place it is
defined.

The alternative was to design a representation from first principles. Rejected:
a representation designed here would have to be defended here, against every
reviewer who knows the standard, and every difference from it would be a
difference someone has to be told about. A superset moves the burden the right
way round: only the additions need defending.

This decision does not say what the standard's semantics are. No investigation
in this repository has read the standard's text — INV-002's facts about it are
reported from outside and carry status `UNVERIFIED` (R-1, R-2, R-4). Which
field means what, in the standard's own words, is a fact, and it belongs to an
investigation that reads the standard, not to this file. That investigation is
a precondition for a reader or a writer, and is recorded as open below.

### 2. The canon's own conventions, stated once

Three conventions, chosen here so that no converter has to choose them:

- the origin is at the top left, y increasing downward;
- the angle points in the direction the standard's angle points, not the
  direction the extractor already in the image uses;
- the angle is stored as an integer in units of 1/32 degree.

The unit is the one INV-002 F-16 shows to be the smallest in which all three
angular grids in play are whole numbers. Storing the angle in it means no
conversion between the formats named in INV-002 ever rounds, and F-17 gives
the exactness for the two grids that matter most.

The consequence is stated here rather than discovered later: emitting the
native format of the extractor already in the image needs **both** a flip of
the y axis (INV-002 F-5) **and** a rotation of the angle (INV-002 R-2, which is
reported from outside and not verified here). A converter that applies one and
not the other produces a file that loads, plots, and matches nothing. Leaving
either implicit is what invites that.

The alternative was to store the angle in degrees, or in the unit of whichever
format the value arrived in. Rejected: both lose. Degrees cannot hold the ISO
grid exactly, and carrying the source's unit means the unit travels as a field
that every consumer must branch on — which is the same as having no convention.

### 3. The canon preserves the source's minutia order

A canon record is a sequence, not a set. Minutiae keep the order the source
gave them, and nothing sorts them on the way in or on the way out.

The formats order their minutiae differently, and a canon that imposes an order
of its own cannot round-trip any of them byte for byte. Two byte-for-byte
round-trips are the only external tests available: a file produced by a tool,
read into the canon and written back, either is the same file or is not, and no
opinion enters. Sorting on emission would trade both of those tests for
tidiness.

The alternative was a canonical order — by position, or by quality descending.
Rejected: it buys a stable diff between two records of the same image and costs
the only test that a reader and a writer can be held to. A stable diff can be
had at display time, where it changes nothing.

### 4. Quality and reliability are separate observed fields

Two fields, both read, neither derived. They are defined by the role the
source gives them, not by the file they happen to arrive in, so an extractor
this refinement does not name is accommodated by saying which of its outputs
fills which field:

- `quality`, an integer on the scale 0..100: the per-minutia confidence an
  extractor puts in the file a matcher reads. For the extractor now in the
  image that is the fourth column of `.xyt`.
- `reliability_milli`, an integer on the scale 0..1000: the finer confidence an
  extractor reports in its own detail output, where it has one. For the
  extractor now in the image that is the reliability printed in `.min`.

Both scales are the canon's, declared here. Neither is a measured range:
INV-002 F-9 records what these two columns were observed to take on one set of
images, and observing a range is not the same as knowing one. A value outside
the declared scale is a defect to be raised, not clamped, and an extractor
whose own scale differs is converted on the way in, by its reader.

Each field is present when its source was read and absent otherwise, and
absence is representable — a record built from a matcher-facing file alone
carries no reliability, and must not carry a fabricated one. An extractor that
reports only one of the two fills only one.

The alternative was to store one and derive the other. Rejected on INV-002
F-10: the same printed reliability occurs with two different qualities, which
is a proof that no function of one yields the other, not a search that failed.
INV-002 F-11 is why this is the most dangerous option available rather than
merely a wrong one: the best closed form agrees on the great majority of
minutiae, and where it fails it fails by a margin too small to catch the eye,
so a derived field passes every spot check, every read-through, and every test
written by the person who derived it. F-12 gives the
mechanism that makes it hopeless in principle rather than unlucky in practice:
what is printed is a rounded projection, and the value it was rounded from is
not in the file.

Recording both fields also keeps the extractor's own confidence signal, which
is finer than the 0..100 column, available to any later work that wants it.

### 5. Tool formats are write-only

The canon is the only stored representation. A file in a tool's format is
generated from the canon, handed to the tool, and discarded. It is never read
back into the canon, and no canon record is ever built from a file this
repository itself emitted.

Every emission is lossy in at least the angle, and reading an emitted file back
compounds that loss once per round trip, silently, in a quantity nobody
measures. Forbidding the return path means loss can be counted once, at
emission, rather than accumulating across a pipeline.

Reading a tool's format is not forbidden — that is how a canon record is built
in the first place. What is forbidden is reading back a file this repository
wrote.

The alternative was to allow the return path and measure the loss. Rejected: it
is a measurement that would have to be repeated for every pair of formats and
every direction, and the result would be a table of tolerances, which is a
thing runs then have to carry.

### 6. Readers and writers are library code, not external tools

A reader or a writer of any of these formats is code in this repository, called
in process. It does not become a command-line tool with its own invocation, and
it is not given a digest of its own.

`REF-005` puts an external binary behind a subprocess boundary and pins it by
checksum because its provenance is separate from this repository's: nobody here
built it and nothing here changes when it does. A reader written here has no
separate provenance. It is pinned by the code revision that every run record
already names, and giving it a digest as well would create a second identity
for one thing, which then has to be kept in agreement with the first.

The alternative was a small command-line tool per format, matching the shape
`REF-005` sets for external tools. Rejected: it buys a uniform shape and costs
a digest to maintain, a subprocess per image, and an interface whose failures
are exit codes rather than exceptions.

This decision names no language, no package and no directory. Those are
decided with the container image, and are not decided here.

## An image with no minutiae

The behaviour is defined now, because the alternative is that it is defined by
whichever code path first meets such an image:

- a canon record for an image on which the extractor found nothing is **valid**
  and records zero minutiae. It is not an error, not a null, and not an absent
  file.
- the file emitted from it for a tool is **empty**, and that is the correct
  emission rather than a failure to emit.
- the per-image minutia count **travels with any score vector** computed from
  these records.

The third of these is not a convenience. `manifests/MAN-tools.v1.json` records
that the matcher already in the image returns a score of zero for a comparison
it declined to attempt, and that this is indistinguishable from a genuine
non-match unless the counts are known. An empty emission produces exactly that
ambiguity, and carrying the count is what keeps a downstream zero readable.

## Rejected

- **A representation designed from scratch.** Rejected in 1: every difference
  from the standard becomes something a reader has to be told.
- **Storing the angle in degrees, or in the source's own unit.** Rejected in 2:
  degrees cannot hold every grid exactly, and a per-record unit is not a
  convention.
- **A canonical minutia order.** Rejected in 3: it costs the only two external
  tests available.
- **Deriving quality from reliability, or reliability from quality.** Rejected
  in 4, and rejected specifically because it very nearly works.
- **Reading back a file this repository emitted.** Rejected in 5: it turns a
  loss that can be counted once into one that accumulates unmeasured.
- **A command-line tool per format.** Rejected in 6: a second identity for code
  that the run record already pins.
- **Deciding the canon per converter, as each is written.** Rejected in "What
  is being decided": it is one decision taken once per converter, in whichever
  direction each was written first.

## Open

- ⟨OPEN⟩ **The standard's semantics have not been read here.** Decision 1
  adopts them; no investigation in this repository establishes what they are.
  Which fields exist, what the type codes mean, where the origin sits and what
  range the quality takes are facts, and they need an investigation that reads
  the standard's text. No reader or writer may be written before it exists.
- ⟨OPEN⟩ **The rotation between the standard's angle and the native one is
  reported, not measured here.** INV-002 R-2 records the sample and the method
  it rests on, both from outside this repository. Decision 2 makes that
  rotation part of every emission, so a converter written before it is
  verified here rests on an unverified fact.
- ⟨OPEN⟩ `D-1`, already tracked: which coordinate convention the matcher
  requires. Decision 5 makes the emission write-only but does not say which
  convention is written.
- ⟨OPEN⟩ `D-2`, tracked with this refinement: whether the second extractor is
  used unmodified, and therefore restricted to the databases whose resolution
  matches the value its sample program hardcodes (INV-002 R-5), or given the
  true resolution, which makes it a modified tool this repository then owns
  under `REF-005`.
