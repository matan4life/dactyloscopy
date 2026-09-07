# implementation/

The implementation this repository runs: the code a run executes, and the source of the binaries a run invokes. `scripts/README.md` and `experiments/README.md` both say that code belongs "with the implementation"; this is the place they mean.
It is split by how the thing a file becomes is pinned, and not by language. `library/` holds code that runs in this process and is pinned by the code revision a run record already names. `tools/` holds source that is compiled into a binary crossing into the runtime image, which is pinned like any other artefact, by a digest, with the source pinned alongside it because its provenance is not separate. `quality/REF-013` decides the split and states the rule it comes from.
Not here: manifests, records, experiment declarations, run records, or anything a directory contract already claims.
