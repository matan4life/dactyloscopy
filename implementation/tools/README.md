# implementation/tools/

Source compiled in a builder stage into a binary that crosses into the runtime image and is invoked there as a command, across a subprocess boundary.
Such a file has two identities and the tools manifest carries both: the git blob id of the source, which says what was compiled, and the sha256 of the binary, which says what runs. `quality/REF-013` decision 3 says why one is not enough, and `quality/REF-011` decision 5 fixes how the two are composed into the identity a run records.
A file here is also a file `.dockerignore` admits into the build context by name, so adding one is a change to what leaves this machine.
Not here: code that is imported rather than executed, and any third-party source, which `quality/REF-005` keeps out of this tree entirely — a third-party tool arrives through the build recipe, pinned and checked there.
