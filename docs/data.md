# Data

## Why no input data is in the repository

Fingerprint images and minutiae are personal data. This repository is public
and permanently archived; nothing added to it can be reliably removed. So no
input data lives in the tree: not in a fixture, not temporarily, not in a
branch. The extensions `.tif .tiff .bmp .pgm .raw .ist .xyt .min` are refused
by `.gitignore`. A commit that adds one is an incident; see
[SECURITY.md](../SECURITY.md).

## Where input data lives

Input data is mounted read-only from outside the tree. Locations are resolved
from the environment, and `.env.example` documents the contract:

- `LABDATA` is the only required variable: the root that holds every
  location by default.
- `LAB_RAW` optionally overrides the raw location. It is opened read-only
  and never written to.
- `LAB_DERIVED` optionally overrides the derived location. It is read-write,
  regenerable, and never committed.

Each location resolves as `LAB_<NAME>`, then `$LABDATA/<name>`, then an error
that names every missing location at once.

Code never carries a dataset path as a literal. A dataset is addressed by its
manifest id, `<competition>/<subset>`, for example `fvc2002/DB1_A`, and the
manifest is what ties that id to checksums of the files it consists of.

## What is published instead

| Published | What it is | Why it is safe |
| --- | --- | --- |
| Per-file checksums | One digest per input file, listed under `manifests/checksums/`. | A digest reveals nothing about the file's content. It lets anyone who holds the dataset confirm they hold the same bytes, and it is how a manifest names its data. |
| Pair lists | The list of comparisons made in a run: which two files were compared, and whether the pair is genuine or impostor. | File names and labels only. The images stay where they were. |
| Score vectors | The matcher's score for each pair in the pair list. | A score describes a comparison, not a finger. Every metric here is a function of the score vector and the pair labels alone. |

Every metric in this repository can be recomputed from the pair list and the
score vector alone, without access to the images. That is what makes a claim
here checkable by someone who has never seen the data.

## Minutiae are not published either

A minutiae template (`.xyt`, `.min`, `.ist`) is not an anonymised summary of
an image. An image sufficient to fool a matcher can be reconstructed from it.
Minutiae are therefore treated exactly like images: never committed, never
published, never attached to an issue, never pasted into a report.
