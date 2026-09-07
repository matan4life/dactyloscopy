# INV-010 — What reads a manifest in this repository

Date: 2026-09-07

## Numbering

This record takes 010, the next free investigation number after `INV-009`. The
reservation at 001 is explained in `REF-002`.

## Question

`INV-009` audited one manifest and found that 47 of its 63 fields were never
measured in a way that could have caught the manifest being wrong. Four
manifests are live. So: **what reads a manifest in this repository, field by
field, what does that cost, and what happens to a manifest nothing reads?**

## Method

**What was measured against.** The tree at commit `87b4a8b` and the image built
from its `Dockerfile`, image id
`sha256:e0ded5a5dcc8f594df58ab904be76605ad26492da834130592091b1348f7c3fc`. The
corpus is the copy under `$LABDATA/raw/fvc2002`, mounted read-only; nothing
below writes to it.

**How "reads" was decided: by instrument, not by reading the script.** A
`sitecustomize.py` on `PYTHONPATH` replaces `json.load` with a version that
wraps the result in a proxy and records the dotted path of every value read out
of it. Python imports `sitecustomize` at interpreter startup when it is on the
path, so every `python3` inside a shell script loads it without the script
being edited. The whole file is under "Reproducing this" as block **T**.

A field counts as read when some recorded path is that field's `.value`, or
lies inside it. That is the question the record is about: a mechanism that
never fetches a value cannot notice the value going wrong.

**A defect in the instrument, found and fixed before any number below was
taken.** The first version replaced `json.loads` as well. CPython implements
`json.load` as `loads(fp.read())`, so the result was wrapped twice, and the
outer `dict.__init__` enumerated the inner proxy on construction. That recorded
446 reads nobody made — including reads of `status`, which is exactly what F-5
asks about, and it would have produced the opposite answer there. The fix is to
replace `json.load` alone and call the unpatched `loads` inside it. Every
number below is from the fixed instrument; the run that produced them recorded
100 accesses, all of them to the one file the script opens.

**What was not used to decide anything.** Reading the script and reasoning
about what it must fetch. `INV-009` did that, carefully, and its F-3 still
missed a whole mechanism; this record measures instead. Where a measurement and
a reading of the source disagree, the measurement is what is recorded.


## F-1 — coverage, per field, across all four live manifests

**42 of 332 fields are read by anything. 290 are read by nothing.**

| manifest | fields with a value and a status | read | read by |
| --- | --- | --- | --- |
| `MAN-fvc2002.v1` | 124 | 0 | — |
| `MAN-minutia.v1` | 8 | 0 | — |
| `MAN-tools.v1` | 63 | 0 | — |
| `MAN-tools.v2` | 137 | 42 | `scripts/check_tools.sh` |
| **total** | **332** | **42** | |

`scripts/check_tools.sh` is the only reader. It opened one file during the run,
`manifests/MAN-tools.v2.json`, and made 100 accesses to it. `python -m pytest`
was run under the same instrument and opened no manifest at all: the only JSON
it loaded was `.pytest_cache/v/cache/nodeids`.

**What is read, by kind.** All 42 are in `MAN-tools.v2`, and they are the
fields that name a thing the script can go and measure: each tool's
`binary.*_path` and `*_sha256`, its `identity.parts.*` and
`identity.composed_sha256`, its `runtime.*shared_libraries`, the three mindtct
fixture cases, the six bozorth3 pair scores, the three iso-extract fixture
cases and `iso-extract.invocation.exit_codes`.

**What is not read, by kind.** Every `source.*` field of both NBIS tools and of
the extractor — the archive URL, its digest and size, the release and its date,
the upstream name, the mirror, the commit and tree of the pinned source. Every
`build.*` field: the base image, the setup command, the patch, the make
invocation, the package lists, the clone path, the build number, the gate, the
compile line, what is copied. Every `invocation.*` field except the extractor's
exit codes: the commands, the flags, the input and output formats, the declared
resolution, the two bozorth3 defaults, the overflow sentinel. Every
`size_bytes`. Every `fixture.dataset` and `fixture.image_digests`. Every field
of the identity scheme block, of `what_changed_from_v1`, and of
`not_in_this_manifest`. And every field of the other three manifests.

**`MAN-tools.v1` is not merely unread: the current script cannot read it.**
Pointed at it with `MANIFEST=`, `scripts/check_tools.sh` completes sections 1
and 2 and then dies in section 3 with `KeyError: 'identity'`, because v1 was
issued before identities were compositions and carries no `identity` block. So
the file that `MAN-tools.v2` supersedes, and that old results reproduce
against, cannot be verified by the mechanism that verifies its successor.

### The table

One row per field, generated from the four files by the script under block
**F1** in "Reproducing this". That script asserts that the set of paths it
prints equals the set an independent walk of each file finds, so the table
cannot omit a field or invent one; the assertion held when the table was
produced.

| manifest | field | status | read by |
| --- | --- | --- | --- |
| MAN-fvc2002.v1 | `distribution.root` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `distribution.layout` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `distribution.files_total` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `distribution.images_total` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `distribution.bytes_total` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `distribution.provenance` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `distribution.copy_faithful_to_source_tree` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `distribution.correspondence_to_official_distribution` | UNVERIFIED | nothing |
| MAN-fvc2002.v1 | `distribution.corroboration_of_authenticity` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `distribution.attributed_but_not_read` | UNVERIFIED | nothing |
| MAN-fvc2002.v1 | `distribution.publisher_checksums` | UNVERIFIED | nothing |
| MAN-fvc2002.v1 | `index_files.index_a.MFA.sha256` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `index_files.index_a.MFA.bytes` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `index_files.index_a.MFA.lines` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `index_files.index_a.MFR.sha256` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `index_files.index_a.MFR.bytes` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `index_files.index_a.MFR.lines` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `index_files.index_B.MFA.sha256` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `index_files.index_B.MFA.bytes` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `index_files.index_B.MFA.lines` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `index_files.index_B.MFR.sha256` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `index_files.index_B.MFR.bytes` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `index_files.index_B.MFR.lines` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB1_A.path` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB1_A.role` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB1_A.fingers` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB1_A.impressions_per_finger` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB1_A.images` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB1_A.width` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB1_A.height` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB1_A.mode` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB1_A.bytes_per_file` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB1_A.resolution_dpi` | UNVERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB1_A.checksums` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB1_A.licence` | UNVERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB1_B.path` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB1_B.role` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB1_B.carries_the_tool_fixture` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB1_B.fingers` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB1_B.impressions_per_finger` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB1_B.images` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB1_B.width` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB1_B.height` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB1_B.mode` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB1_B.bytes_per_file` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB1_B.resolution_dpi` | UNVERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB1_B.checksums` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB1_B.licence` | UNVERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB2_A.path` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB2_A.role` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB2_A.fingers` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB2_A.impressions_per_finger` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB2_A.images` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB2_A.width` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB2_A.height` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB2_A.mode` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB2_A.bytes_per_file` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB2_A.resolution_dpi` | UNVERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB2_A.checksums` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB2_A.licence` | UNVERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB2_B.path` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB2_B.role` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB2_B.fingers` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB2_B.impressions_per_finger` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB2_B.images` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB2_B.width` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB2_B.height` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB2_B.mode` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB2_B.bytes_per_file` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB2_B.resolution_dpi` | UNVERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB2_B.checksums` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB2_B.licence` | UNVERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB3_A.path` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB3_A.role` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB3_A.fingers` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB3_A.impressions_per_finger` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB3_A.images` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB3_A.width` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB3_A.height` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB3_A.mode` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB3_A.bytes_per_file` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB3_A.resolution_dpi` | UNVERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB3_A.checksums` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB3_A.licence` | UNVERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB3_B.path` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB3_B.role` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB3_B.fingers` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB3_B.impressions_per_finger` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB3_B.images` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB3_B.width` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB3_B.height` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB3_B.mode` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB3_B.bytes_per_file` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB3_B.resolution_dpi` | UNVERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB3_B.checksums` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB3_B.licence` | UNVERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB4_A.path` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB4_A.role` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB4_A.fingers` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB4_A.impressions_per_finger` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB4_A.images` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB4_A.width` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB4_A.height` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB4_A.mode` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB4_A.bytes_per_file` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB4_A.resolution_dpi` | UNVERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB4_A.checksums` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB4_A.licence` | UNVERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB4_B.path` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB4_B.role` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB4_B.fingers` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB4_B.impressions_per_finger` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB4_B.images` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB4_B.width` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB4_B.height` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB4_B.mode` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB4_B.bytes_per_file` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB4_B.resolution_dpi` | UNVERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB4_B.checksums` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `subsets.fvc2002/DB4_B.licence` | UNVERIFIED | nothing |
| MAN-fvc2002.v1 | `observations.byte_identical_files` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `observations.duplicate_pair_is_a_defined_comparison` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `observations.resolution_declared_in_the_files` | VERIFIED | nothing |
| MAN-fvc2002.v1 | `observations.distinct_digests` | VERIFIED | nothing |
| MAN-minutia.v1 | `x-manifest.asserted_numbers.angle_full_circle` | VERIFIED | nothing |
| MAN-minutia.v1 | `x-manifest.asserted_numbers.angle_maximum` | VERIFIED | nothing |
| MAN-minutia.v1 | `x-manifest.asserted_numbers.angle_levels_native_step` | VERIFIED | nothing |
| MAN-minutia.v1 | `x-manifest.asserted_numbers.angle_levels_ansi_step` | VERIFIED | nothing |
| MAN-minutia.v1 | `x-manifest.asserted_numbers.angle_levels_iso_step` | VERIFIED | nothing |
| MAN-minutia.v1 | `x-manifest.asserted_numbers.angle_levels_maximum` | VERIFIED | nothing |
| MAN-minutia.v1 | `x-manifest.asserted_numbers.quality_maximum` | VERIFIED | nothing |
| MAN-minutia.v1 | `x-manifest.asserted_numbers.reliability_maximum` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.mindtct.source.kind` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.mindtct.source.url` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.mindtct.source.archive_sha256` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.mindtct.source.archive_size_bytes` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.mindtct.source.release` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.mindtct.source.release_date` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.mindtct.source.upstream` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.mindtct.source.mirror_previously_used` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.mindtct.build.base_image` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.mindtct.build.setup` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.mindtct.build.patch` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.mindtct.build.make` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.mindtct.build.extra_build_packages` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.mindtct.build.artifact_copied` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.mindtct.binary.path` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.mindtct.binary.sha256` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.mindtct.binary.size_bytes` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.mindtct.runtime.shared_libraries` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.mindtct.invocation.command` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.mindtct.invocation.flags` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.mindtct.invocation.input_format` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.mindtct.invocation.outputs` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.mindtct.fixture.dataset` | UNVERIFIED | nothing |
| MAN-tools.v1 | `tools.mindtct.fixture.conversion` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.mindtct.fixture.cases.101_1.minutiae` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.mindtct.fixture.cases.101_1.xyt_sha256` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.mindtct.fixture.cases.101_2.minutiae` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.mindtct.fixture.cases.101_2.xyt_sha256` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.mindtct.fixture.cases.102_1.minutiae` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.mindtct.fixture.cases.102_1.xyt_sha256` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.bozorth3.source.kind` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.bozorth3.source.url` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.bozorth3.source.archive_sha256` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.bozorth3.source.archive_size_bytes` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.bozorth3.source.release` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.bozorth3.source.release_date` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.bozorth3.source.upstream` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.bozorth3.source.mirror_previously_used` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.bozorth3.build.base_image` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.bozorth3.build.setup` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.bozorth3.build.patch` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.bozorth3.build.make` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.bozorth3.build.extra_build_packages` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.bozorth3.build.artifact_copied` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.bozorth3.binary.path` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.bozorth3.binary.sha256` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.bozorth3.binary.size_bytes` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.bozorth3.runtime.shared_libraries` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.bozorth3.invocation.command` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.bozorth3.invocation.flags` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.bozorth3.invocation.default_max_minutiae` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.bozorth3.invocation.default_minminutiae` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.bozorth3.invocation.input` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.bozorth3.fixture.dataset` | UNVERIFIED | nothing |
| MAN-tools.v1 | `tools.bozorth3.fixture.source_of_xyt` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.bozorth3.fixture.pairs.101_1 101_1` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.bozorth3.fixture.pairs.101_1 101_2` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.bozorth3.fixture.pairs.101_1 102_1` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.bozorth3.fixture.pairs.101_2 101_2` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.bozorth3.fixture.pairs.101_2 102_1` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.bozorth3.fixture.pairs.102_1 102_1` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.bozorth3.fixture.symmetry` | VERIFIED | nothing |
| MAN-tools.v1 | `tools.bozorth3.fixture.determinism` | VERIFIED | nothing |
| MAN-tools.v2 | `what_changed_from_v1` | VERIFIED | nothing |
| MAN-tools.v2 | `identity_scheme.encoding` | VERIFIED | nothing |
| MAN-tools.v2 | `identity_scheme.one_part_form` | VERIFIED | nothing |
| MAN-tools.v2 | `identity_scheme.composed_is_derived` | VERIFIED | nothing |
| MAN-tools.v2 | `identity_scheme.why_this_manifest_records_rather_than_claims` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.mindtct.identity.parts.binary` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.mindtct.identity.composed_sha256` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.mindtct.source.kind` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.mindtct.source.url` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.mindtct.source.archive_sha256` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.mindtct.source.archive_size_bytes` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.mindtct.source.release` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.mindtct.source.release_date` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.mindtct.source.upstream` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.mindtct.source.mirror_previously_used` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.mindtct.build.base_image` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.mindtct.build.setup` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.mindtct.build.patch` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.mindtct.build.make` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.mindtct.build.extra_build_packages` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.mindtct.build.artifact_copied` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.mindtct.binary.path` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.mindtct.binary.sha256` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.mindtct.binary.size_bytes` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.mindtct.runtime.shared_libraries` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.mindtct.invocation.command` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.mindtct.invocation.flags` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.mindtct.invocation.input_format` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.mindtct.invocation.outputs` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.mindtct.fixture.dataset` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.mindtct.fixture.image_digests` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.mindtct.fixture.conversion` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.mindtct.fixture.cases.101_1.source_sha256` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.mindtct.fixture.cases.101_1.minutiae` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.mindtct.fixture.cases.101_1.xyt_sha256` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.mindtct.fixture.cases.101_2.source_sha256` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.mindtct.fixture.cases.101_2.minutiae` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.mindtct.fixture.cases.101_2.xyt_sha256` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.mindtct.fixture.cases.102_1.source_sha256` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.mindtct.fixture.cases.102_1.minutiae` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.mindtct.fixture.cases.102_1.xyt_sha256` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.bozorth3.identity.parts.binary` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.bozorth3.identity.composed_sha256` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.bozorth3.source.kind` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.bozorth3.source.url` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.bozorth3.source.archive_sha256` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.bozorth3.source.archive_size_bytes` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.bozorth3.source.release` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.bozorth3.source.release_date` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.bozorth3.source.upstream` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.bozorth3.source.mirror_previously_used` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.bozorth3.build.base_image` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.bozorth3.build.setup` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.bozorth3.build.patch` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.bozorth3.build.make` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.bozorth3.build.extra_build_packages` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.bozorth3.build.artifact_copied` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.bozorth3.binary.path` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.bozorth3.binary.sha256` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.bozorth3.binary.size_bytes` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.bozorth3.runtime.shared_libraries` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.bozorth3.invocation.command` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.bozorth3.invocation.flags` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.bozorth3.invocation.default_max_minutiae` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.bozorth3.invocation.default_minminutiae` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.bozorth3.invocation.overflow_sentinel` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.bozorth3.invocation.input` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.bozorth3.fixture.dataset` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.bozorth3.fixture.image_digests` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.bozorth3.fixture.source_of_xyt` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.bozorth3.fixture.pairs.101_1 101_1` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.bozorth3.fixture.pairs.101_1 101_2` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.bozorth3.fixture.pairs.101_1 102_1` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.bozorth3.fixture.pairs.101_2 101_2` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.bozorth3.fixture.pairs.101_2 102_1` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.bozorth3.fixture.pairs.102_1 102_1` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.bozorth3.fixture.symmetry` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.bozorth3.fixture.determinism` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.iso-extract.identity.parts.library` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.iso-extract.identity.parts.caller_source` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.iso-extract.identity.parts.caller` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.iso-extract.identity.composed_sha256` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.iso-extract.source.kind` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.iso-extract.source.url` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.iso-extract.source.commit` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.iso-extract.source.tree` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.iso-extract.source.commit_date` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.iso-extract.source.tags_in_repository` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.iso-extract.source.submodule` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.iso-extract.source.upstream` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.iso-extract.source.terms` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.iso-extract.build.base_image` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.iso-extract.build.clone_path` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.iso-extract.build.configure` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.iso-extract.build.build_number` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.iso-extract.build.make` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.iso-extract.build.gate` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.iso-extract.build.compile_caller` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.iso-extract.build.extra_build_packages` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.iso-extract.build.artifacts_copied` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.iso-extract.binary.caller_path` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.iso-extract.binary.caller_sha256` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.iso-extract.binary.caller_size_bytes` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.iso-extract.binary.library_path` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.iso-extract.binary.library_sha256` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.iso-extract.binary.library_size_bytes` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.iso-extract.binary.library_version_reported` | UNVERIFIED | nothing |
| MAN-tools.v2 | `tools.iso-extract.runtime.library_resolution` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.iso-extract.runtime.caller_shared_libraries` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.iso-extract.runtime.library_shared_libraries` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.iso-extract.invocation.command` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.iso-extract.invocation.flags` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.iso-extract.invocation.declared_resolution_dpi` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.iso-extract.invocation.output_format` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.iso-extract.invocation.input_format` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.iso-extract.invocation.outputs` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.iso-extract.invocation.exit_codes` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.iso-extract.invocation.diagnostics` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.iso-extract.fixture.dataset` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.iso-extract.fixture.image_digests` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.iso-extract.fixture.conversion` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.iso-extract.fixture.cases.101_1.source_sha256` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.iso-extract.fixture.cases.101_1.minutiae` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.iso-extract.fixture.cases.101_1.template_bytes` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.iso-extract.fixture.cases.101_1.template_sha256` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.iso-extract.fixture.cases.101_2.source_sha256` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.iso-extract.fixture.cases.101_2.minutiae` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.iso-extract.fixture.cases.101_2.template_bytes` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.iso-extract.fixture.cases.101_2.template_sha256` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.iso-extract.fixture.cases.102_1.source_sha256` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.iso-extract.fixture.cases.102_1.minutiae` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.iso-extract.fixture.cases.102_1.template_bytes` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.iso-extract.fixture.cases.102_1.template_sha256` | VERIFIED | `scripts/check_tools.sh` |
| MAN-tools.v2 | `tools.iso-extract.fixture.record_length_relation` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.iso-extract.fixture.determinism` | VERIFIED | nothing |
| MAN-tools.v2 | `tools.iso-extract.fixture.corroboration` | VERIFIED | nothing |
| MAN-tools.v2 | `not_in_this_manifest` | VERIFIED | nothing |

## F-2 — the checksum lists

`manifests/checksums/fvc2002/` holds eight lists, one per subset, 3520 entries
in all: 800 for each `_A` subset and 80 for each `_B`.

**Nothing reads them.** A search of every file in the tree, of any type, for
the string `checksums` returns only prose: `README.md`, `CONTRIBUTING.md`,
`docs/data.md`, `manifests/README.md`, the `.gitattributes` line that marks the
directory generated, and the manifests themselves, which name the lists as
values. No script, no test and no `Makefile` target opens one (**Q**).

**The lists have digests of their own, and nothing verifies those either.**
`MAN-fvc2002.v1.json` records a `sha256` beside each `checksums` value. All
eight match the files in the tree today, checked here in 68 ms (**C**), and no
mechanism in the repository performs that check.

**What happens today if a corpus file changes.** Measured on a writable copy of
`Db1_b`, flipping one byte and running the only mechanism that touches corpus
files at all (**B**):

| byte changed in `101_1.tif` | decoded pixels change? | `check_tools.sh` |
| --- | --- | --- |
| 145623, the last byte of 145624 | yes | exit 0, not caught |
| 72812, in the middle | yes | exit 1, caught, the template digest differs |
| 200, in the header | no | exit 0, not caught |

The middle row is the case the tool fixture is for. The first row is the
finding: a byte changed, the decoded pixels changed, and the check passed,
because one pixel at the end of the image moves no minutia. The third row is a
true negative — a TIFF metadata byte that changes no pixel.

A byte changed in `103_1.tif`, which is in the same subset but is not one of
the three fixture images, leaves `check_tools.sh` at exit 0 as well; nothing in
the repository reads that file.

The checksum list does catch all of these, by construction, and nothing runs
it: `sha256sum -c` over the modified copy reported `103_1.tif: FAILED` and 79
OK.

So of the 3520 files the corpus manifest names, **three are indirectly
observed, through what two tools compute from them, and 3517 are observed by
nothing** — and the three are observed in a way that a change to their bytes
can pass through.

## F-3 — cost, measured

Timed inside the image, with the corpus mounted read-only (**C**):

| what | time |
| --- | --- |
| `scripts/check_tools.sh` against `MAN-tools.v2`, all sixteen sections | 1187 ms |
| the eight checksum lists against their recorded digests | 68 ms |
| all 3520 corpus digests, `sha256sum -c` per subset | 6312 ms |
| **all of the above** | **≈ 7.6 s** |

Per subset, for the 3520:

| subset | images | result | time |
| --- | --- | --- | --- |
| `fvc2002/DB1_A` | 800 | 800 OK, 0 FAILED | 1618 ms |
| `fvc2002/DB1_B` | 80 | 80 OK, 0 FAILED | 139 ms |
| `fvc2002/DB2_A` | 800 | 800 OK, 0 FAILED | 1634 ms |
| `fvc2002/DB2_B` | 80 | 80 OK, 0 FAILED | 173 ms |
| `fvc2002/DB3_A` | 800 | 800 OK, 0 FAILED | 1176 ms |
| `fvc2002/DB3_B` | 80 | 80 OK, 0 FAILED | 116 ms |
| `fvc2002/DB4_A` | 800 | 800 OK, 0 FAILED | 1279 ms |
| `fvc2002/DB4_B` | 80 | 80 OK, 0 FAILED | 139 ms |
| **total** | **3520** | **3520 OK, 0 FAILED** | **6312 ms** |

From the host, including everything docker does:

| what | time |
| --- | --- |
| `make check-tools` end to end | 1.652 s |
| `docker run --rm dactyloscopy:dev true`, the floor | 0.395 s |

So a container costs about four tenths of a second and every manifest this
repository holds can be verified in full in under eight seconds, corpus
included.

## F-4 — where the read-time rule is stated

`INV-003` X-1 and `REF-012` A both rest on "this repository's own rule" that a
`CONFLICT` field is forbidden to read, and neither names where it is written.

**It is written in `README.md`, in the third of the four absolute
prohibitions**, and `README.md` is the only file git tracks that states it
(**S**):

> 3. **Never mark a field `VERIFIED`** unless it was measured here or two
>    independent sources agree. One source is `APPROX`. Two sources that
>    disagree are `CONFLICT`, and reading a `CONFLICT` field raises rather than
>    falling back to a default.

The prohibition above it carries a second read-time rule, for the other status
that is not `VERIFIED`:

> 2. **Never invent a number.** … An unknown value carries the status
>    `UNVERIFIED`, and the code refuses to use it.

**Where it is not.** `manifests/README.md` is the directory contract for
manifests and the place a reader would look. It states the vocabulary and says
nothing about reading:

> A manifest names the INVs and REFs that produced it, and every number in it
> carries a status: `VERIFIED`, `APPROX`, `UNVERIFIED` or `CONFLICT`. A number
> without a status does not belong here.

**No refinement states it either.** Searching every file git tracks for the
three phrasings the rule is written in returns four lines and no more: the two
in `README.md` above, and two that invoke the rule without saying where it
lives — `INV-003` line 360, "By this repository's own rule a `CONFLICT` field is
forbidden to read", and `REF-007` line 141, "a decision may not rest on a field
this repository is forbidden to read". Eleven refinements exist and none of
them states it.

**No code implements it.** See F-5: nothing reads a status at all.

## F-5 — what `check_tools.sh` does when a field it reads is not `VERIFIED`

**Nothing, because it never looks.** Of the 100 accesses the instrument
recorded during a full run, **zero** are to a `status` (**T**). The script
fetches `.value` and never the field it sits beside.

Measured directly as well as by instrument. Two fields the script does read —
`tools.mindtct.binary.sha256` and `tools.bozorth3.fixture.pairs.101_1 101_1` —
were set to `CONFLICT` in one copy of the manifest and to `UNVERIFIED` in
another, with the values left alone, and the script was pointed at each
(**N**):

| statuses | `scripts/check_tools.sh` |
| --- | --- |
| as issued, both `VERIFIED` | exit 0 |
| both `CONFLICT` | exit 0 |
| both `UNVERIFIED` | exit 0 |

A `CONFLICT` field is forbidden to read by `README.md` prohibition 3, and the
only thing in this repository that reads manifest fields reads them without
looking.

## Reproducing this

Every block was run on 2026-09-07 against the tree at `87b4a8b`. `$SP` is a
scratch directory outside the tree; `$FIX` is the read-only mount of the
FVC2002 `Db1_b` images and `$CORPUS` of the whole corpus. No image, minutia or
template leaves a container, and nothing writes into the corpus.

**T — the instrument, and the run that produced F-1 and F-5.** The file below
is `$SP/track/sitecustomize.py`. It records, for every JSON file a process
loads, the path of each value read out of it.

    import atexit, json, os
    _OUT = os.environ.get("TRACK_OUT")
    _records = []

    def _emit(source, path, kind):
        _records.append("%s\t%s\t%s" % (source, path, kind))

    def _wrap(value, source, path):
        if isinstance(value, dict):
            return _TrackedDict(value, source, path)
        if isinstance(value, list):
            return _TrackedList(value, source, path)
        _emit(source, path, "leaf")
        return value

    class _TrackedDict(dict):
        def __init__(self, data, source, path):
            super().__init__(data); self._source = source; self._path = path
        def _child(self, key):
            return "%s.%s" % (self._path, key) if self._path else str(key)
        def __getitem__(self, key):
            return _wrap(super().__getitem__(key), self._source, self._child(key))
        def get(self, key, default=None):
            return self[key] if key in self else default
        def __iter__(self):
            _emit(self._source, self._path, "keys"); return super().__iter__()
        def keys(self):
            _emit(self._source, self._path, "keys"); return super().keys()
        def items(self):
            _emit(self._source, self._path, "keys")
            return [(k, _wrap(super(_TrackedDict, self).__getitem__(k),
                              self._source, self._child(k))) for k in super().keys()]
        def values(self):
            _emit(self._source, self._path, "keys")
            return [_wrap(super(_TrackedDict, self).__getitem__(k),
                          self._source, self._child(k)) for k in super().keys()]

    class _TrackedList(list):
        def __init__(self, data, source, path):
            super().__init__(data); self._source = source; self._path = path
        def __getitem__(self, index):
            if isinstance(index, slice):
                return super().__getitem__(index)
            return _wrap(super().__getitem__(index), self._source,
                         "%s[%d]" % (self._path, index))
        def __iter__(self):
            _emit(self._source, self._path, "elements")
            return iter([_wrap(v, self._source, "%s[%d]" % (self._path, i))
                         for i, v in enumerate(super().__iter__())])

    _real_loads = json.loads

    def _tracked_load(fp, *args, **kwargs):
        # Deliberately not json.load: CPython implements it as loads(fp.read()),
        # so patching both wraps twice and the outer dict.__init__ enumerates
        # the inner proxy, recording reads nobody made.
        return _wrap(_real_loads(fp.read(), *args, **kwargs),
                     getattr(fp, "name", "<stream>"), "")

    if _OUT:
        json.load = _tracked_load
        @atexit.register
        def _flush():
            if _records:
                open(_OUT, "a", encoding="utf-8").write("\n".join(_records) + "\n")

Run against the verification script, and against the test suite:

    docker run --rm -v "<repo>:/work:ro" -v "$SP/track:/track" -v "$FIX:/fixture:ro" \
      -w /work -e PYTHONPATH=/track:/work -e TRACK_OUT=/track/v2.tsv \
      dactyloscopy:dev bash scripts/check_tools.sh /fixture
    docker run --rm -v "<repo>:/work:ro" -v "$SP/track:/track" \
      -w /work -e PYTHONPATH=/track:/work -e TRACK_OUT=/track/pytest.tsv \
      dactyloscopy:dev python -m pytest -q

`cut -f1 /track/v2.tsv | sort | uniq -c` prints `100
/work/manifests/MAN-tools.v2.json` and nothing else;
`grep -c status /track/v2.tsv` prints 0. The pytest run records one source,
`/work/.pytest_cache/v/cache/nodeids`.

Pointed at `MAN-tools.v1`, the same script prints its first two sections and
then:

    === 3. the source a caller was compiled from ===
    Traceback (most recent call last):
      ...
    KeyError: 'identity'
    exit=1

**F1 — the table.** `$SP/f1_table.py`, given the tracker output. It walks each
manifest for objects carrying both a `value` and a `status`, asks the tracker
output whether that field's `.value` was read, prints one row per field, and
asserts that what it printed equals what the walk found.

    python f1_table.py /track/v2.tsv

It prints the table above and then `total 332, read 42, unread 290`.

**Q — what reads the checksum lists.**

    grep -rn 'checksums' . --exclude-dir=.git

**C — cost.** One script inside the image, with the repository read-only and
the corpus read-only, timing each part with `date +%s%N`:

    for each subset in MAN-fvc2002.v1.json:
        cd $CORPUS/<subset path> && sha256sum -c <repo>/<subset checksums>
    python3: sha256 of each checksums file against its recorded digest
    bash /work/scripts/check_tools.sh /fixture

and from the host:

    time make check-tools FVC_DB1_B=<Db1_b>
    time docker run --rm dactyloscopy:dev true

**B — what a changed corpus file does.** Inside one container: `cp -r /fixture
/tmp/fx`, flip one byte with python, run `scripts/check_tools.sh /tmp/fx`,
restore, repeat at the next offset. The corpus mount is read-only and only the
copy under `/tmp` is written; the container is `--rm`.

**S — where the read-time rule is stated.**

    grep -rn 'CONFLICT' . --exclude-dir=.git --exclude-dir=.pytest_cache
    grep -rln 'forbidden to read\|raises rather than\|refuses to use it' . --exclude-dir=.git

**N — the status tamper.** Two copies of `MAN-tools.v2.json` with two read
fields' statuses changed and their values untouched, each run through
`MANIFEST=`:

    docker run --rm -v "<repo>:/work:ro" -v "$SP/tamp2:/t:ro" -v "$FIX:/fixture:ro" \
      -w /work -e MANIFEST=/t/status-CONFLICT.json \
      dactyloscopy:dev bash scripts/check_tools.sh /fixture

## What was left unchecked

- **Whether anything outside this repository reads these manifests.** The
  question is what this tree does.
- **Whether the 290 unread fields are true.** `INV-009` measured 63 of them and
  found two failing; the other 227 were not re-measured here. This record is
  about what reads a field, not about whether the field holds.
- **The contents of `MAN-fvc2002.v1` and `MAN-minutia.v1`.** Counted, not
  audited.
- **Whether `git` alone would catch a changed corpus file.** It would not — the
  corpus is outside the tree by `docs/data.md` — but no measurement of that was
  taken, because there is nothing to measure: `git status` in the repository
  says nothing about a file the repository does not contain.
- **Reading with a status other than the two tampered.** F-5 tampers
  `CONFLICT` and `UNVERIFIED` on two fields. `APPROX` was not tried, and no
  field in any live manifest currently carries it.
- **What the cost would be on another machine.** Every timing is from this one,
  through a Windows bind mount, and the corpus read is the part most sensitive
  to that.
- **Whether the tracker misses a read made without `json`.** A reader that
  parsed a manifest with `grep` or `sed` would not appear in it. The search of
  F-2 and the one behind F-1's "only reader" sentence are what cover that, and
  they are string searches, not instrument runs.
