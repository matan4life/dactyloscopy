# manifests/

Frozen, machine-readable manifests: `MAN-<name>.v<N>.json`, and the per-file checksum lists under `checksums/` that they refer to.
A manifest names the INVs and REFs that produced it, and every number in it carries a status: `VERIFIED`, `APPROX`, `UNVERIFIED` or `CONFLICT`. A number without a status does not belong here.
What a status means at read time, decided in `quality/REF-014` and stated here because this is where a reader of manifests looks: a `CONFLICT` field is never read, and code that needs its value fails rather than falling back; an `UNVERIFIED` field may be read and reported but not used as a number a result depends on; an `APPROX` field may be used, and a result that depends on one names it. `implementation/library/manifest_verify.py` implements the first of those and reports any field it refused to read.
Every manifest here is verified by `make verify`, which checks what it can, names every field it could not check and why, and prints how much of each manifest that came to. A manifest is not exempt for being superseded.
A manifest is immutable and versioned. A correction is a new version file, with a new INV and a new REF behind it; the old version stays, because old results are reproduced against it.
Not here: input data, minutiae, derived artifacts, results, and anything edited by hand after it was issued.
