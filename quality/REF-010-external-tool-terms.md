# REF-010 — On what terms an external tool is present in this image

Date: 2026-09-07
Rests on: `quality/INV-006-external-tool-terms.md`. Every factual claim below
is a reference to a fact of that record, by its identifier. This refinement
measures nothing and states no fact of its own. Where they bind, it cites
`REF-003`, which decided this repository's own licence split, and `REF-005`,
which decided how an external tool enters at all.

## Numbering

This refinement takes 010, the next free number. The gap at 001 is explained in
`REF-002` and the gap at 004 in `REF-006`.

## Why this refinement exists

`REF-003` decided the licence of this repository's own code and documents, and
nothing else. `INV-006` opens by recording the gap that leaves: two external
binaries have been in the runtime image since `630afae` with no record of the
terms they are there under. That record establishes what those terms say. This
one turns them into a position.

## Decisions

### 1. This repository publishes the git tree, and never a container image

What is published is the tree at a `cite/` tag, which is the deposit `REF-003`
already decided the licence field of. **The image is not published.** No
registry push, no tarball of a layer, no artefact containing a compiled
binary.

This is written as a constraint on the repository rather than as an intention,
and the difference is the whole point. An intention binds nobody and cannot be
checked: a future task can act against it without noticing it existed. A
constraint can be checked, and it fixes the order of events — **if the image is
ever to be published, this refinement is superseded first, and the image
second.** A supersession that arrives after the publication is not a decision;
it is a note about something that already happened.

The alternative was to record that the image "is not intended for publication".
Rejected below, and it is the alternative this decision exists to refuse.

**The consequence, stated per component, because the components are not
alike.** Every licence `INV-006` found on a link line conditions its
requirements on redistribution, and this repository redistributes none of it.
What that means is different for each binary, and there is no single sentence
that covers them:

- **`bozorth3`.** `INV-006` F-4 records its whole link line: one archive of the
  project's own code, and the C mathematics library. No component that is not
  the project's own appears on it at all. Whatever is decided about
  third-party terms does not reach this binary.
- **`mindtct`.** `INV-006` F-5 records fourteen archives on its link line.
  `INV-006` F-6 counts, for each, the files carrying the header of F-1, and
  four of the fourteen carry none of it. Of those four, **one names its own
  licence and three do not**; and of the four, **two ship no licence file at
  all** and state their terms in a file that is not named for the purpose.
- **One file, not one library.** `INV-006` F-1 records that of the ten source
  and header files in one library on `mindtct`'s link line, nine carry the
  header of F-1 and one carries a different notice, naming a contractor and a
  contract number rather than the authorship the other nine name.
- **One library that the header does not settle.** `INV-006` F-6 records a
  fifth entry whose every file carries the header of F-1 and whose every file
  also states a retrieval from a source outside the publisher, naming
  institutions the header does not. It has no licence file. `INV-004` records
  separately that it contributes no symbol to the binary.

**"NBIS is public domain" is therefore not a sentence this repository can
write.** It would be a claim about fourteen archives on the strength of a
header that `INV-006` F-6 shows four of them do not carry, and that F-1 shows
one file inside a fifth does not carry either. Anything this repository says
about these terms is said per component or not at all.

### 2. No third-party licence text in the tree, and no identifier assigned

Two things are refused here, for different reasons, and both are worth writing
out because a reader will otherwise propose them.

**No copy of anyone else's licence text is added to this repository.** A copy
is vendoring, and it has the failure mode `REF-005` already rejected for
source: a copy drifts from the artefact it was taken from, and nothing detects
the drift, because a copy in a tree has no relationship to the thing it was
copied from that any tool checks. `INV-006` F-3 carries a path and a digest for
each of the documents it found, and a path plus a digest into an archive pinned
by checksum is an address, not a duplicate. It resolves to exactly one text and
it fails loudly if the archive is not the pinned one.

A `THIRD-PARTY-NOTICES` file is worse than a plain copy, because it adds an
assertion the plain copy does not make: that what this repository distributes
contains those components. By decision 1 it does not. A file whose whole
purpose is to accompany a distribution, in a repository that distributes none
of it, tells a reader something untrue in the one place they will look for the
truth.

**No licence identifier is assigned to any of these components, and no
machine-readable licence declaration covers them.** `INV-006` F-6 records that
of the four components on `mindtct`'s link line that do not carry the header of
F-1, three name no licence at all: the files that state their terms name no
licence in them. Assigning an identifier to those three would be this
repository's judgement about what somebody else's text amounts to, wearing the
clothes of a fact, in a field designed to be read by machines that cannot see
the difference.

Covering only the one component that does name itself is worse than covering
none. Partial coverage reads as complete: a reader who sees a declaration
assumes the absence of one elsewhere means there is nothing to declare, which
is the opposite of what `INV-006` F-6 found.

### 3. What is added instead: one paragraph, and not a licence file

`README.md` or a page under `docs/` gains one paragraph: what the image
contains, that this repository distributes none of it, and where the record is.
It is prose, it is short, and it is not a licence file.

`REF-003` set the precedent for this exact move. Faced with a repository whose
licensing has more than one part, it kept the root `LICENSE` simple and put the
complexity in `README.md`, on the guidance it quotes and cites there. The
situation here is the same shape one step further out: the complexity is not
even about what this repository licenses, and it belongs in prose that a person
reads rather than in a file that a tool parses and misreports.

The alternative was a licence file of some kind at the root. Rejected: a root
licence file is read as a statement about what the repository distributes, and
`REF-003` already put the one such statement this repository is entitled to
make in that position.

### 4. Attribution is by citation, and a required sentence goes into it

`REF-003` decided that attribution in this repository is discharged by
citation: the repository as `CITATION.cff` describes it, and the DOI once a
release has been archived. That decision is extended here, as a general rule
and not as an application to any particular tool.

**The rule.** Where an external tool's own terms ask that a particular sentence
be used in acknowledging it, that sentence is used as the form of the citation.
And the record says, in the same place, that it is written **because
attribution is owed**, not because an obligation attaches.

Both halves are load-bearing.

Without the sentence, the citation is worse than it needs to be. Someone has
written down the form in which they wish to be acknowledged; using a different
form when theirs is available is a discourtesy that costs nothing to avoid.

Without the stated reason, the record contradicts itself. A reader would find
an acknowledgement in `docs/` and, beside it, a refinement saying no obligation
applies, with nothing joining the two. The natural reading of that pair is that
one of them is wrong. Saying why the sentence is there joins them: the
acknowledgement is a courtesy this repository chooses, and decision 1 is why it
is a choice rather than a requirement.

This decision names no tool. Applying it is the business of the refinement that
admits a tool, on the facts of an investigation that has built and run it.

### 5. The boundary: what this repository deliberately introduces

This refinement covers artefacts this repository **deliberately introduces**,
by building them from source it pinned and putting the result in an image it
specified. It does not cover the base image or the packages the distribution
ships in it.

**This boundary is a choice, and the reason is worth stating so that a reader
sees a decision rather than an omission.** The two classes differ in what this
repository did. A binary built here from a pinned archive exists because a
refinement chose the archive, the version and the build; nobody else made that
choice and nobody else can be pointed at for it. A package that arrives inside
a base image is used unmodified and unrepackaged, on the terms its distributor
already ships it under, in the same way every user of that image uses it. The
first is this repository's act; the second is this repository's dependency.

`INV-006` F-8 measured one number about the second class and opened no file in
it, deliberately. That count is the boundary marker: it says the class exists
and is not empty, and it says nothing else, which is exactly what a boundary
marker should say.

The alternative was to extend the same treatment outward until it stopped. It
does not stop: the base image rests on a distribution, which rests on a
toolchain, and a record that follows the chain becomes an inventory nobody
maintains and nobody reads. The boundary is drawn where this repository's own
decisions end.

## Rejected

- **Vendoring third-party licence texts into the tree.** Rejected in 2: a copy
  drifts from what it was copied from and nothing detects the drift, which is
  the failure `REF-005` already refused for source. `INV-006` F-3's path and
  digest are an address into a pinned archive instead.
- **A `THIRD-PARTY-NOTICES` file.** Rejected in 2: beyond copying, it asserts
  that what this repository distributes contains those components, and by
  decision 1 it does not.
- **Licence identifiers, or a machine-readable declaration.** Rejected in 2:
  `INV-006` F-6 records that three of the four components in question name no
  licence, so an identifier would be a judgement presented as a fact.
- **Partial coverage — an identifier for the one component that names
  itself.** Rejected in 2, and rejected more firmly than full coverage:
  incomplete coverage reads as complete, so it misleads where silence would
  not.
- **A single sentence characterising the terms of NBIS as a whole.** Rejected
  in 1: `INV-006` F-6 shows four archives on one link line carry a different
  header, F-1 shows one file inside a fifth carries a different notice again,
  and F-4 shows the other binary has no such component at all. One sentence
  cannot be true of all of that.
- **Recording that the image "is not intended for publication".** Rejected in
  1: an intention cannot be checked and binds no later task. The constraint,
  and the ordering it fixes — supersede this refinement first, publish second —
  is what makes the position hold.
- **Reading the terms from anywhere but the archive `MAN-tools.v1.json`
  pins.** Rejected: `INV-006`'s method records that it read the pinned archive
  and not the mirror that manifest also names, and that every path it reports
  was found by searching that archive. A term read from a mirror, a website or
  a package description is a term nobody can check against the artefact this
  repository actually builds.

## Open

- ⟨OPEN⟩ Whether title 17 section 105 has any effect outside the United States.
  `INV-006` leaves it unchecked, as a legal question nothing in this
  repository can measure. **No decision above depends on it**, and that is
  deliberate: decision 1 makes the question moot for what this repository does
  today, and if it ever stops being moot the answer is needed before, not
  after.
- ⟨OPEN⟩ Whether the export-control statement `INV-006` F-2 quotes is current.
  It is a claim made at the release the pinned archive is, and `INV-006` checks
  it against nothing.
- ⟨OPEN⟩ The eleven documents `INV-006` F-3 digested and did not read. None
  belongs to a component on a link line of F-4 or F-5, which is why they were
  not read; if a later build links something they belong to, they are read
  first.
