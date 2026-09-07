# scripts/

One-off and maintenance scripts: fetching a pinned third-party binary and verifying its checksum, refreshing tool pins, tidying the tree.
A script here is never part of a run. Nothing in this directory produces a number that is reported anywhere; anything that does belongs with the implementation and is invoked by a run.
A script may be the command form of a module under `implementation/`, in which case it imports and calls and does nothing else, so that a run and a person reach the same code by the same path. `verify_manifests.sh` is that shape.
Not here: experiment logic, metric code, or anything a result depends on.
