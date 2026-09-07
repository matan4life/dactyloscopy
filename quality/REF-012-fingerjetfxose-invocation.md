# REF-012 — The invocation this repository drives FingerJetFXOSE with

Date: 2026-09-07
Rests on: `quality/INV-003-fingerjetfxose-source-and-resolution.md` and
`quality/INV-007-fingerjetfxose-built.md`. Extends `REF-005`, whose rule this
applies. Uses `REF-007` and `REF-011`. Every factual claim below is a reference
to a fact of a named investigation, by its identifier. This refinement measures
nothing and states no fact of its own.

## Numbering

This refinement takes 012, the next free number. The gap at 001 is explained in
`REF-002` and the gap at 004 in `REF-006`.

## Why this refinement exists

`REF-005` decided that the invocation is part of a tool's identity, that a tool
offering more than one output convention is not fully identified by its
version, and that a run which does not name the invocation has not named the
tool. For the extractor already in the image that invocation was decided and
frozen. For this one it never was.

`REF-011` admitted the tool and decided that a caller this repository owns
drives it. That caller cannot be written until the two values it passes are
settled, and settling them in the code would put a decision where no record
could find it. They are settled here.

## Decisions

### A. The declared resolution is 500

The caller passes 500 as the resolution, for every image, whatever the corpus
says about itself.

**Why that value and not the one a dataset reports.** Four facts, all already
in the record, point the same way.

- `INV-003` S-8: the library assigns its internal minutia resolution the
  literal 500 whatever it is told, and the line that would carry the declared
  value through is commented out beside the authors' own remark that it is
  broken.
- `INV-003` S-10: the project's own self-test has the correct assertion
  commented out and asserts the pinned value in its place.
- `INV-003` S-11: inside the window from 450 to 550 the resampling target size
  and the resize routine do not reference the declared value at all.
- `INV-003` F-4: 500 is the one declared value at which the export resolution
  the caller's argument produces equals the library's own default, so it is the
  one value at which the two cannot disagree.

`REF-007` decision 4 already restricted the corpus for this reason, and this
decision is that restriction seen from the other side: having chosen the
corpora, the value passed to the tool follows.

`INV-007` measured its fixture with this value. A different value would make
every figure in that record incomparable with anything produced afterwards, and
`INV-007` states under what it left unchecked that it tried no other.

**Rejected: declaring each subset's reported resolution.** `REF-007` decision 4
rejected it on three grounds, and the third is decisive on its own: what a
declaration other than the reference one does to the coordinates is not
established, because `INV-003` X-1 is in `CONFLICT`, and this repository's own
rule forbids a decision to rest on a field in that state. A caller that passed
a dataset's reported resolution would be resting on it.

### B. The output is ISO/IEC 19794-2:2005, not ANSI INCITS 378-2004

The caller asks the library for the ISO format.

**They are not interchangeable.** `INV-003` F-1 measures that the two carry
different angular grids — 256 levels of 360/256 degrees against 180 levels of 2
degrees — and `INV-003` S-3 that their record headers differ in length. A
reader written for one does not read the other, and a number computed from one
is not comparable with a number computed from the other.

**Why ISO.** It is what this repository has already committed to reading.
`REF-006` decision 1 decided that the canon is a superset of ISO 19794-2 rather
than a design of its own, `manifests/MAN-minutia.v1.json` is that format, and
`REF-006` decision 3 makes a byte-for-byte round trip through a tool's own
format one of the only two external tests a reader and a writer can be held to.
Choosing ANSI would require a second reader, for a format the canon does not
adopt, and would put the angle on a grid `REF-006` decision 2 did not choose.

**Nothing consumes this template today, and the decision does not pretend
otherwise.** The matcher in the image reads `.xyt` files as
`manifests/MAN-tools.v1.json` records its invocation, not templates of either
format. So this choice rests on what the repository has committed to, and on
nothing a consumer requires, because there is no consumer.

**This does not answer `REF-005`'s open question about the coordinate
convention.** That question, tracked as `D-1`, is about which convention the
matcher requires from the *other* extractor's `.xyt` output. It concerns a
different pair of tools and a different file format, and nothing here narrows
or widens it.

### C. The invocation is frozen in the manifest

The two parameter values above, the input format the caller accepts, the output
file it writes and the exit codes it returns are recorded in the tool's
manifest entry, as `REF-005` requires of every tool: the command, the flags,
the input format and the outputs.

The reason `REF-005` gives applies here in its strongest form. It observed that
where a tool offers more than one output convention, two invocations of one
binary on one input can agree on their summaries while agreeing on nothing a
reader reads. `INV-003` F-1 measures exactly that for this tool: the same
library, the same image, two formats, two grids.

Exit codes are part of it because `REF-011` decided the caller is ours: a
caller that failed silently would be a caller whose failure a run could not
see, and the codes are what a run has to read.

### D. The build number passed is the constant 0

`REF-011` decision 4 already decided that the build number is passed explicitly
rather than derived from a clone's commit count. It did not decide the value.
The value is the constant **0**.

**It is a constant, and that is the property being chosen.** Any fixed value
makes the recipe independent of the clone, which is what `REF-011` decision 4
required; 0 is the least of them and carries no implication of a version.

**Nothing that crosses into the runtime depends on it.** `INV-007` F-4 measures
which artefacts change when only this define changes, and the shared library —
which `REF-011` decision 2 sends across the stage boundary — is among those
that do not. The caller `REF-011` decided this repository writes did not exist
when `INV-007` measured, so nothing is claimed about it; the manifest records
what the build produces rather than predicting it.

It is recorded as part of the build recipe, with the fixed build path
`REF-011` decision 4 also requires, because a recipe that omits either does not
reproduce.

**A ground that was offered and is not used.** The brief that commissioned this
refinement gave a second reason for the value: that 0 is what the project's own
version logic falls back to when it cannot reach git. No investigation in this
repository records that. `INV-007` F-4 records only how that logic computes the
value when it *can* reach git. Using the fallback as a ground would be stating
a fact no record carries, so it is not used, and the decision rests on the two
grounds above, which are sufficient.

## Rejected

- **Declaring each subset's reported resolution.** Rejected in A, on `REF-007`
  decision 4, whose third ground is that it depends on a `CONFLICT` field.
- **Leaving the resolution for the caller's author to choose.** Rejected in the
  premise of this refinement: `REF-005` makes the invocation part of the tool's
  identity, and a value chosen in code is a decision no record could be found
  to have taken.
- **ANSI INCITS 378-2004 as the output format.** Rejected in B: a different
  grid, a different header length, a second reader for no benefit, and a grid
  the canon does not adopt.
- **Both formats, written side by side.** Rejected: it doubles what a fixture
  must pin and what a run must name, to produce a second file nothing reads. If
  a consumer for the other format ever exists, it arrives with a record saying
  what it is for.
- **Deriving the build number from the clone.** Rejected by `REF-011` decision
  4, restated here only because D fixes the value that decision left open.

## Open

- ⟨OPEN⟩ `D-1`, unchanged: which coordinate convention the matcher requires
  from the other extractor. B states explicitly that it does not touch it.
- ⟨OPEN⟩ `INV-003` X-1 stays in `CONFLICT`. A rests on `REF-007` decision 4,
  which was itself written so as not to depend on it, and nothing above reads
  it.
- ⟨OPEN⟩ What this tool does at a declared resolution other than 500. `INV-007`
records that it tried none, and A is a decision about which value to pass, not
a finding about the others.
