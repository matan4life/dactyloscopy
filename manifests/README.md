# manifests/

Frozen, machine-readable manifests: `MAN-<name>.v<N>.json`, and the per-file checksum lists under `checksums/` that they refer to.
A manifest names the INVs and REFs that produced it, and every number in it carries a status: `VERIFIED`, `APPROX`, `UNVERIFIED` or `CONFLICT`. A number without a status does not belong here.
A manifest is immutable and versioned. A correction is a new version file, with a new INV and a new REF behind it; the old version stays, because old results are reproduced against it.
Not here: input data, minutiae, derived artifacts, results, and anything edited by hand after it was issued.
