# REF-013 — The language, the toolchain, and where code lives

Date: 2026-09-07
Rests on: `REF-005`, `REF-006` and `REF-011`, and on the `Dockerfile` and the
directory contracts already in the tree. Every factual claim below is a
reference to one of those, quoted where it decides something. This refinement
measures nothing and states no fact of its own.

## Numbering

This refinement takes 013, the next free number. The gap at 001 is explained in
`REF-002` and the gap at 004 in `REF-006`.

## Why this refinement exists, in the tree's own words

`REF-006` deferred this decision and named what it was deferring it to, at its
lines 183 and 184:

> This decision names no language, no package and no directory. Those are
> decided with the container image, and are not decided here.

The container image exists. The decision does not, and two directory contracts
have been pointing at a place that has never existed. `scripts/README.md`:

> A script here is never part of a run. Nothing in this directory produces a
> number that is reported anywhere; anything that does belongs with the
> implementation and is invoked by a run.

and `experiments/README.md`:

> Results and observations belong in `runs/`; code belongs with the
> implementation.

Neither sentence resolves, because no directory answers to "the
implementation".

`REF-011` decision 5 then requires a manifest to carry the git blob id of a
source file this repository writes. A blob id is an address, and the file has
no path. That is the immediate occasion and it is not the scope: the same
absence would stop the kernel, the metrics and the protocol on the day any of
them is written.

## Decisions

### 1. Language

**Python 3.12 for the implementation that a run executes in this process.**

The ground is that `REF-006` deferred the choice to the image and the image has
already answered it. The `Dockerfile` pins
`python:3.12-slim-bookworm` by digest at both of its stages, and installs
`numpy`, `pytest` and `pillow` at exact versions. Choosing that language costs
nothing and changes nothing; it names what is there.

**C for source that links a third-party library and crosses into the runtime as
a binary**, compiled in a builder stage from the same pinned base. Two
requirements already in the tree force this. `REF-005` requires the builder
stage and the runtime image to start from the same pinned base, so that a
binary is never compiled against a newer C library than the runtime provides.
`REF-011` decision 2 requires this repository's caller to cross the stage
boundary as a file, alongside the shared library it links. A file that links a
shared library and is executed by the runtime is a compiled binary, and the
language it is written in is the one that library's interface is published in.

**Rejected: a language the image does not carry.** It would mean changing the
image. Changing the image means rebuilding it, and
`manifests/MAN-tools.v1.json` freezes two binaries by digest against the image
as it is, so both would have to be rebuilt and re-verified. That is a real
cost, paid to buy something this repository has not asked for.

### 2. Test runner

**`pytest`, at the version the image pins.** Same ground as decision 1: it is
already installed, at an exact version, in the image every run uses. `make
test` already invokes it.

**What a test in this repository is for.** `REF-005` and `REF-006` already
imply it and it is stated here so that nobody has to infer it. `REF-005`
decided that a conversion is verified on decoded pixels and never on encoded
bytes, because a container's bytes depend on the compressor's version while the
pixels do not — that is, a check that fails for a reason nobody cares about is
a check people learn to ignore. `REF-006` decision 3 kept the minutia order
precisely so that a byte-for-byte round trip stays available as a test.

So a test here checks a property that could be wrong: **byte-exactness where
the bytes are stable, and a declared tolerance where they are not.** A test
that fails for an uninteresting reason is a defect in the test.

### 3. One implementation root, and the split inside it

**The implementation lives in one directory, `implementation/`**, so that both
sentences quoted above resolve to one place rather than to two or to none.

**Inside it, two directories:**

- **`implementation/library/`** — code that runs in this process: readers,
  writers, metrics, protocol, the kernel. Imported, never invoked as a command.
- **`implementation/tools/`** — source that is compiled in a builder stage into
  a binary that crosses into the runtime image, and is invoked there as a
  command across a subprocess boundary.

**The reason for the split is that the two are pinned differently, and the tree
already says so.** `REF-006`, at its lines 171 to 176:

> `REF-005` puts an external binary behind a subprocess boundary and pins it by
> checksum because its provenance is separate from this repository's: nobody
> here built it and nothing here changes when it does. A reader written here has
> no separate provenance. It is pinned by the code revision that every run
> record already names, and giving it a digest as well would create a second
> identity for one thing, which then has to be kept in agreement with the first.

**`REF-011` decision 5 gives this repository's caller both a blob id and a
binary digest, and that is not a contradiction of the passage above.** It reads
like one, so the reason is written here rather than left to be reconstructed.

The passage is about a *reader called in this process*. Such a reader is never
an artefact: it is the code revision, and a digest would be a second name for
one thing. The caller is different at run time. It is a file in the image,
executed across a subprocess boundary, and at that moment it is an artefact in
exactly the sense `REF-005` pins artefacts — with the one addition that its
provenance is not separate, which is why `REF-011` decision 5 records where it
came from as well as what it became.

**The rule this refinement takes from that, stated so that it decides cases
nobody has seen yet: code that stays in this process is pinned by the run's code
revision; code that becomes an artefact in the image is pinned like an artefact,
and its source is pinned as well, because its provenance is not separate.**

The split in the layout is that rule made visible. A file's directory says how
the thing it becomes is pinned.

### 4. Where tests live

**`tests/`, one directory at the repository root**, with its own contract
README in the form the existing eight use.

At the root rather than inside `implementation/`, because a test is not part of
the implementation: it is the thing that holds the implementation to something,
and the two are read by different people at different times. One directory
rather than one per implementation subdirectory, because the split of decision
3 is about how a thing is pinned, and that has no bearing on where its test
goes.

It is decided here rather than left to whoever writes the first test, for the
reason this whole refinement exists: a layout decided as a side effect of the
first file is a layout nobody chose.

### 5. What is not created, and why that is a decision

**No build or packaging file, and none is needed.** The `Dockerfile` sets
`WORKDIR /work` and `ENV PYTHONPATH=/work`, and `make test` runs `python -m
pytest` there with the repository bind-mounted. So a module under
`implementation/library/` is importable by its path from the repository root
with no packaging file at all, and `pytest` discovers `tests/` from the same
root. Nothing is missing, so nothing is added.

The code is run inside the image against the repository. It is not built as a
distribution and not installed from an index, so packaging metadata would
describe a distribution that does not exist.

**If a configuration file ever becomes necessary, its content is tool
configuration and not packaging metadata.** A file that configures how a tool
behaves is a fact about this repository's own workflow. A file that declares a
name, a version and dependencies for publication is a claim about an artefact
nobody publishes, and `REF-010` decision 1 already decided that what this
repository publishes is the tree.

**No linter or formatter configuration, and the deferral is recorded rather
than left as an absence.** The image carries neither, so adding one means
changing the image, which by decision 1's ground means rebuilding and
re-verifying two tools that a manifest has frozen. The absence is therefore a
decision and not an oversight, and it is revisited when the image is next
changed for a reason that already justifies the rebuild.

### 6. Every directory this creates carries a contract

`implementation/`, `implementation/library/`, `implementation/tools/` and
`tests/` each carry a `README.md` in the form the existing eight use: what
belongs there, and a `Not here:` line. A directory without a contract is a
directory whose contents drift, which is why every other top-level directory in
this tree has one.

**The directories and their READMEs are created by the commit that first puts a
file in each, not by this one.** An empty directory with a contract and nothing
to govern is a promise, and this repository records decisions rather than
promises. What each README must say is decided here:

- **`implementation/`** — the implementation this repository runs, split by how
  the thing a file becomes is pinned. Not here: manifests, records, experiment
  declarations, run records, or anything a directory contract already claims.
- **`implementation/library/`** — code that runs in this process and is
  imported, never invoked as a command; pinned by the code revision a run
  record names. Not here: source that is compiled into a binary, or anything
  that shells out to one of this repository's own files.
- **`implementation/tools/`** — source compiled in a builder stage into a
  binary that crosses into the runtime image and is invoked there as a command;
  pinned by the blob id of the source and the digest of the binary, both in the
  tools manifest. Not here: code that is imported rather than executed, and any
  third-party source, which `REF-005` keeps out of the tree entirely.
- **`tests/`** — tests, run by `pytest` inside the image. A test checks a
  property that could be wrong, and it uses synthetic inputs. Not here: a
  corpus image, a minutia, a template, a fixture that reaches outside the tree,
  or a test whose failure would be uninteresting.

**Naming.** Each name says what the thing is for and not what it is made of,
which is the form every existing top-level name takes. A directory named for a
language would have to be renamed the day a second language arrives, and the
split of decision 3 is not a split by language: it is a split by how the result
is pinned, and it would hold if both sides were written in the same language.

## Rejected

- **Putting the caller in `scripts/`.** That contract excludes it in terms: "A
  script here is never part of a run. Nothing in this directory produces a
  number that is reported anywhere." The caller's output is where numbers will
  come from.
- **Two implementation directories at the top level, one per language.**
Rejected: it leaves the two existing READMEs pointing at neither, and it names
directories for their technology, which decision 6 rejects on its own ground.
- **Deciding the layout inside the FingerJetFXOSE task.** Rejected: that is
settling a repository-wide question as a side effect of one tool, which is the
shape of decision this repository exists to avoid. It is why that task stopped
instead.
- **Naming a directory for the technology in it.** Rejected in 6.
- **A packaging file.** Rejected in 5: it would describe a distribution that
  does not exist.
- **Adding a linter now.** Rejected in 5: it costs a rebuild and a
  re-verification of two frozen tools, and buys nothing this repository has
  asked for. Deferred, not refused.
- **Tests beside the code they test.** Rejected in 4: the split inside
  `implementation/` is about pinning, and a test's location has nothing to do
  with how the thing it tests is pinned.

## Open

- ⟨OPEN⟩ Whether the kernel, the metrics and the protocol fit this layout
  without amendment. This refinement is written from one caller and three
directory contracts. The first substantial module is the test of it, and if it
does not fit, the correction is a new refinement rather than a directory that
quietly appears.
- ⟨OPEN⟩ Whether `implementation/library/` needs a split of its own. Nothing in
  it exists yet, so there is nothing to divide, and dividing it now would be
  deciding a shape from no cases.
