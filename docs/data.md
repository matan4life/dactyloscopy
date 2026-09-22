# Data

## Why no input data is in the repository

Fingerprint images and minutiae are personal data. This repository is public,
so anything pushed can be cloned, forked or crawled before it is noticed, and
nothing added to it can be assumed removable afterwards. So no
input data lives in the tree: not in a fixture, not temporarily, not in a
branch. The extensions `.tif .tiff .bmp .pgm .raw .ist .xyt .min` are ignored
by `.gitignore`, which stops an accident and not an intent: `git add -f`
overrides it, and no enforcing gate exists; the toolchain refinement,
`REF-013`, brought none. A commit that adds such a file is an incident; see
[SECURITY.md](../SECURITY.md).

## Where input data lives

Input data is mounted read-only from outside the tree. One environment
variable locates it, and `.env.example` documents it:

- `LABDATA` is the variable every run reads: the root that holds every
  location. One check, `make check-tools`, takes the fixture directory as
  `FVC_DB1_B` instead, because it predates the corpus manifest.
- `$LABDATA/raw` is the raw location. The `Makefile` mounts it read-only into
  the container, and it is never written to.
- `$LABDATA/derived` is the derived location. The `Makefile` mounts it
  read-write; what is written there is regenerable and never committed.

`.env.example` also names `LAB_RAW` and `LAB_DERIVED` as overrides of the two
locations, resolved before `$LABDATA/<name>`, with an error that names every
missing location at once. Nothing in the tree reads either variable or raises
that error: every location a manifest names is resolved through `LABDATA`
alone, and the command forms that take a path take it as an argument.

Code never carries a dataset path as a literal. A dataset is addressed by its
manifest id, `<competition>/<subset>`, for example `fvc2002/DB1_A`, and the
manifest is what ties that id to checksums of the files it consists of.

## What is published instead

Of the three things below, the first now exists: `manifests/checksums/fvc2002/`
carries one `sha256sum`-format list per subset, and
`manifests/MAN-fvc2002.v1.json` names each list and the digest of that list.
`make verify LABDATA=<root>` checks both halves — each list against the digest
recorded for it, and every file the list names against the corpus — and
`docs/manifests.md` records what that printed. The other two exist but are
not published yet: `INV-017` made a matching run on `fvc2002/DB1_B` and
`fvc2002/DB1_A`, and its pair lists and score vectors live under
`$LABDATA/derived`, outside the tree, with their digests recorded in that
investigation; the two runs recorded under `runs/` carry theirs beside the
record, as `REF-016` decides. What follows is
the policy that governs publication, and the reason each part of it is safe
to publish.

| Published, or to be | What it is | Why it is safe |
| --- | --- | --- |
| Per-file checksums | One digest per input file, listed under `manifests/checksums/`. Published for FVC2002. | A digest reveals nothing about the file's content. It lets anyone who holds the dataset confirm they hold the same bytes, and it is how a manifest names its data. |
| Pair lists | The list of comparisons made in a run: which two files were compared, and whether the pair is genuine or impostor. | File names and labels only. The images stay where they were. |
| Score vectors | The matcher's score for each pair in the pair list. | A score describes a comparison, not a finger. Every metric here is a function of the score vector and the pair labels alone. |

Every metric in this repository will be recomputable from the pair list and
the score vector alone, without access to the images. That is what will make a
claim here checkable by someone who has never seen the data.

## Minutiae are not published either

A minutiae template (`.xyt`, `.min`, `.ist`) is not an anonymised summary of
an image. An image sufficient to fool a matcher can be reconstructed from it.
Minutiae are therefore treated exactly like images: never committed, never
published, never attached to an issue, never pasted into a report.
