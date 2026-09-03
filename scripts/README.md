# scripts/

One-off and maintenance scripts: fetching a pinned third-party binary and verifying its checksum, refreshing tool pins, tidying the tree.
A script here is never part of a run. Nothing in this directory produces a number that is reported anywhere; anything that does belongs with the implementation and is invoked by a run.
Not here: experiment logic, metric code, or anything a result depends on.
