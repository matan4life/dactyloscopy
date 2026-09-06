# REF-005 — External tool provenance

Date: 2026-09-06
Rests on: no investigation. This refinement records decisions about how an
external tool enters this repository. Every fact a decision was taken against
is frozen in `manifests/MAN-tools.v1.json`, and the output that establishes it is in
`docs/tools.md`; where a decision rests on a report this repository has not
verified, the sentence says so. This refinement carries no measured value of
its own.

## Decision

An external tool is compiled from pinned source inside the image and reaches
the runtime as a binary. Its provenance, its build, its invocation convention
and the fixture that proves it works are recorded in `manifests/MAN-tools.v1.json`,
one entry per tool.

The sections below state the decisions in general form. Each applies to every
tool that follows the first, and a second tool is added by writing a manifest
entry, not by amending this file.

### The source of record is the publisher's own artefact

Source is fetched from whoever publishes the tool, and pinned by a checksum
of the exact artefact. The checksum is verified before anything is unpacked,
and a mismatch stops the build rather than warning, so a substituted or
truncated download cannot become a binary.

Pinning by checksum is what makes the publisher the source of record. A URL
alone names a location, and a location can serve different bytes tomorrow; the
checksum names the artefact itself, and the manifest carries it beside the
release the publisher assigned.

An earlier version of this refinement stated that the publisher distributes
only through a request form a build cannot fetch, and used that to justify a
third-party mirror. That statement was false: the publisher serves the archive
over plain HTTPS with no registration. It is corrected here rather than
quietly removed, because the repository's own rule is that a claim which
turned out to be wrong is withdrawn in the open.

The mirror is not disowned. The build recipe was worked out against it, and
what it produces was checked against an independently built binary from
another decade before the publisher's archive was ever fetched. Where a tool
has no publisher-served artefact, a mirror pinned by commit remains the
fallback, on the terms the earlier text set out: the correspondence to the
upstream release is then `UNVERIFIED`, and the tool is not described as that
release.

The alternative was to vendor the archive and commit it. Rejected: the
repository does not carry third-party source, and a checksum in a manifest is
addressable by anyone reading it, while a copy on the author's disk is not.

### The whole upstream tree is built, and one binary is kept

The upstream build is invoked the way the upstream documents it, in full, and
not narrowed to the one wanted tool. A narrowed build is a build the upstream
never runs, so its failures are ours to diagnose alone, and the time it saves
is spent in a stage that is thrown away. Building everything buys a build
that either works or fails for a reason the upstream would recognise.

Exactly one file per tool crosses the stage boundary. No compiler, no source
tree, and no sibling tool the current task does not need. A binary that is not
used is a binary whose provenance nobody checks, and it would still be in the
image.

The alternative was to build only the wanted package. The brief that
commissioned this work reports that pruning the build fails in ways unrelated
to the tool; that report is not verified here, and the decision does not
depend on it. Building everything costs time in a stage that is discarded,
which is cheap enough that the narrower build has nothing to offer.

### The builder matches the runtime distribution

The builder stage and the runtime image start from the same pinned base. A
binary compiled against a newer C library than the runtime provides fails at
run time, and it fails in a way that looks like a broken tool rather than a
broken image. Sharing one base makes the mismatch impossible rather than
unlikely, and leaves one digest to keep current instead of two.

### Binaries live in the image, not in git

A compiled binary is not committed. The image pins the environment, git pins
the code, and a run record names both; a binary in git would belong to neither
field and would have to be rebuilt for every platform anyway.

### The invocation convention is part of the tool's identity

A tool that offers more than one output convention is not fully identified by
its version. Where the conventions transform the coordinates, two invocations
of one binary on one input can agree on their summaries while agreeing on
nothing a matcher reads, and a number computed under one convention is not
comparable with a number computed under the other.

The invocation is therefore frozen in the manifest beside the commit: the
command, the flags, the input format, and the outputs it writes. A run that
does not name the invocation has not named the tool.

For the minutiae extractor the decision is to call it with no flags, and in
particular without the flag that switches its output to the ANSI INCITS
378-2004 convention. This is a decision and not a detail: the alternative
convention transforms the coordinates, so adopting it later invalidates every
number computed before the switch. Which convention downstream matching
requires is an open question, recorded below and in the manifest; until it is
answered, the convention that changes nothing is the one in use.

### Input format follows the tool, not the dataset

Where a tool accepts one image format and the dataset ships another, the
conversion happens before the tool and is verified to preserve pixels, rather
than the tool being adapted to the dataset.

The alternative is a wrapper that teaches the tool the dataset's format.
Rejected: a wrapper is source with no upstream, carried, compiled and
maintained here, and every number would depend on it. A format conversion
whose fidelity can be checked pixel by pixel is a smaller thing to trust, and
the check is cheap enough to run every time. Which formats a given tool
accepts and refuses is a measured fact, carried by that tool's manifest
entry.

The conversion is checked on decoded pixels, never on the encoded file: a
container format's bytes depend on the compressor's version while the pixels
do not, and a checksum over the encoded file would fail for reasons that have
nothing to do with the tool.

## Rejected

- **A third-party mirror while the publisher serves the artefact directly.**
  Rejected once it was established that the publisher does serve it: a mirror
  adds a party to trust and buys nothing. It stays the fallback only where no
  publisher-served artefact exists.
- **Pinning the download by URL alone.** Rejected: a URL names a location, and
  the same location can serve different bytes later. The checksum names the
  artefact.
- **Vendoring third-party source or binaries into the repository.** Excluded by
  the repository's own rules, and it would move the provenance question from a
  checksum to a file nobody can trace.
- **Building only the needed package.** Rejected above: the saving is in a
  stage that is discarded anyway.
- **Adapting the tool to the dataset's image format.** Rejected above in favour
  of a verified conversion.
- **Recording the tool by version alone.** Rejected: the version does not
  determine the output convention, and the convention determines whether two
  numbers may be compared.

## Open

- ⟨OPEN⟩ Which output convention downstream matching requires. The extractor
  offers its own convention and ANSI INCITS 378-2004, and this repository has
  not measured how they differ. The choice is made when there is a matcher to
  be fed and a number that depends on it, not before.
