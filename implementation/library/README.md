# implementation/library/

Code that runs in this process and is imported, never invoked as a command; pinned by the code revision a run record names.
A module here is reached by its path from the repository root, which the image makes importable by setting `PYTHONPATH=/work`. `quality/REF-013` decision 5 says why there is no packaging file: nothing here is built as a distribution or installed from an index.
Where a module also needs a command form, the command lives in `scripts/` and does nothing but import and call, so that a run and a person reach the same code by the same path.
Not here: source that is compiled into a binary, or anything that shells out to one of this repository's own files.
