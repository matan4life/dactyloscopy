# Manifest verification: what it checks and what it printed

Captured output. The decision behind it is
[quality/REF-014-manifest-verification.md](../quality/REF-014-manifest-verification.md),
and the two investigations it rests on are
[quality/INV-009-man-tools-v1-audit.md](../quality/INV-009-man-tools-v1-audit.md),
which audited one manifest field by field, and
[quality/INV-010-manifest-readers.md](../quality/INV-010-manifest-readers.md),
which measured what reads a manifest at all.

Everything below was run on 2026-09-07 and is what the commands printed.

## What this is for

`INV-010` F-1 measured that of the 332 fields the four live manifests carry, 42
were read by anything and 290 by nothing, and that the 42 were all in one
manifest and all read by one script. A result that names a manifest nothing
verifies is traceable to a claim rather than to a fact.

`make verify` is the answer, and its most important output is not the pass. It
is the count of what it did not check.

## The command

    $ make verify                    # every manifest, without the corpus
    $ make verify LABDATA=<root>     # and every corpus digest the manifests name

`LABDATA` is optional and the difference is reported rather than hidden. A
manifest that declares a distribution root declares it in terms of `$LABDATA`,
which `docs/data.md` makes the only way a dataset is addressed, so the verifier
expands the environment and finds the data the manifest names rather than
assuming a layout.

## What it printed, with the corpus

380 lines, of which the summaries are quoted in full below and the lists of
unchecked field names are cut at the first few of each group; nothing else is
altered.

    $ make verify LABDATA=<root>
    === MAN-fvc2002.v1.json
      124 fields with a value and a status: 16 checked, 108 not
        recomputable  124 fields,  16 checked, 0 failed, 0 refused
      checked:
        ok   recomputable subsets.fvc2002/DB1_A.path  Dbs/Db1_a: present
        ok   recomputable subsets.fvc2002/DB1_A.checksums  manifests/checksums/fvc2002/DB1_A.sha256: list digest matches, 800 files, 0 differing
        ok   recomputable subsets.fvc2002/DB1_B.path  Dbs/Db1_b: present
        ok   recomputable subsets.fvc2002/DB1_B.checksums  manifests/checksums/fvc2002/DB1_B.sha256: list digest matches, 80 files, 0 differing
        ... six more subsets, 800 or 80 files each, 0 differing ...
      not checked here, 108 fields:
        not checked here: needs the corpus measured, and no field says where this number was measured from (108)
          recomputable distribution.root
          recomputable distribution.layout
          recomputable distribution.files_total
          ... 105 more ...

    === MAN-minutia.v1.json
      8 fields with a value and a status: 0 checked, 8 not
        external        8 fields,   0 checked, 0 failed, 0 refused
      not checked here, 8 fields:
        not checked here: a claim about the outside world, and this block carries no pin to bind it (8)
          external    x-manifest.asserted_numbers.angle_full_circle
          external    x-manifest.asserted_numbers.angle_maximum
          ... six more ...

    === MAN-tools.v1.json
      63 fields with a value and a status: 6 checked, 57 not
        derivable      21 fields,   0 checked, 0 failed, 0 refused
        external       12 fields,   0 checked, 0 failed, 0 refused
        recomputable   30 fields,   6 checked, 0 failed, 0 refused
      checked:
        ok   recomputable tools.mindtct.binary.path  /usr/local/bin/mindtct: present
        ok   recomputable tools.mindtct.binary.sha256  /usr/local/bin/mindtct: matches
        ok   recomputable tools.mindtct.binary.size_bytes  /usr/local/bin/mindtct: matches
        ok   recomputable tools.bozorth3.binary.path  /usr/local/bin/bozorth3: present
        ok   recomputable tools.bozorth3.binary.sha256  /usr/local/bin/bozorth3: matches
        ok   recomputable tools.bozorth3.binary.size_bytes  /usr/local/bin/bozorth3: matches
      not checked here, 57 fields:
        ... by reason, then by name ...

    === MAN-tools.v2.json
      137 fields with a value and a status: 15 checked, 122 not
        derivable      46 fields,   0 checked, 0 failed, 0 refused
        external       19 fields,   0 checked, 0 failed, 0 refused
        recomputable   72 fields,  15 checked, 0 failed, 0 refused
      checked:
        ok   recomputable tools.mindtct.identity.composed_sha256  recomputed from 1 parts: matches
        ok   recomputable tools.mindtct.binary.path  /usr/local/bin/mindtct: present
        ... twelve more: two more composed identities, and four files, each
            with its path, its digest and its size ...

    === coverage over every manifest
      332 fields with a value and a status
      37 checked, 0 of them failing
      295 not checked here, 0 of those refused for their status
      11.1% of fields checked

    every check that ran, passed
    $ echo $?
    0

## What it printed, without the corpus

    $ make verify
    LABDATA is not set, so a manifest that names its data through it
    finds nothing and its corpus checks are reported as not run.

    === MAN-fvc2002.v1.json
      124 fields with a value and a status: 0 checked, 124 not
    ...
    === coverage over every manifest
      332 fields with a value and a status
      21 checked, 0 of them failing
      311 not checked here, 0 of those refused for their status
      6.3% of fields checked
      LABDATA was not set, so no corpus digest was verified

    every check that ran, passed

The sixteen fields that move between the two runs are the eight subset paths
and the eight checksum lists. A skipped check is reported as skipped, never as
a pass: `REF-014` decision 4 requires that, because a skip reported as a pass
is the failure the whole mechanism exists to remove.

## What it costs

    make verify                    0.682 - 0.729 s over four runs
    make verify LABDATA=<root>    13.4 - 31.6 s over five runs

The second reads 452 MB across a Windows bind mount and digests 3520 files, and
it is the spread rather than the figure that is worth recording: the fastest
run followed one that had just read the same files, and the three consecutive
runs taken afterwards were 31.5, 30.4 and 31.6 s. `INV-010` F-3 measured
`sha256sum -c` doing the same work in 6.312 s; this verifier opens and digests
each file from Python, and both numbers are from this machine and this mount.

`REF-014` decision 4 rests on the order of magnitude, not on a ceiling, and
says so.

## The coverage is the point

11.1% of fields checked is not a good number. It is the honest one, and it is
printed on every run.

`REF-014` says why each class is where it is. **Recomputable** fields are the
ones a machine could produce again, and the verifier checks the ones it can
produce from the image, the repository and the corpus; for the rest it says
what would have to run — a tool, the dynamic loader, the corpus, or a fetch of
the pinned object. **External** fields are claims about the outside world,
bound to the pin in the same block: a pinned object cannot make a claim about
it expire, so those need no recurring check until the pin moves, and the report
names the pin each one is bound to. **Derivable** fields assert something about
a file this repository controls and do not say which file, and the verifier
does not guess: `INV-009` records, under block **D** of its "Reproducing this",
that a substring search for the four package names of `extra_build_packages`
finds all four in the `Dockerfile`, because a second builder stage installs
exactly that set. A check that can be satisfied by the wrong file reports a
pass.

So the 295 are the size of the gap, printed rather than implied. `INV-009`
found a mechanism that printed "all checks passed" over 42 of 63 fields; the
whole difference here is that the denominator is on the screen.

**Where the classification is an approximation, and it says so by printing.**
The rules are structural: a block decides the class, and a block is not always
homogeneous. `MAN-fvc2002.v1` comes out entirely `recomputable` because its
fields are overwhelmingly measurements of a corpus, and a handful inside it are
not — `distribution.provenance` and `distribution.licence` are claims about
the outside world sitting in a block full of counts. `REF-014` decision 1
anticipates exactly this: the class is printed for every field so that a reader
can compare it with the refinement, which is what the classification living in
code costs and how that cost is paid.

## What the other mechanism covers, and why the two do not add up

`scripts/check_tools.sh` reads 42 fields of `MAN-tools.v2` — `INV-010` F-1
measured exactly which — and runs the tools to check its fixtures.
`make verify` checks 37 fields across all four manifests without running a
tool. The two sets overlap in the binary paths and digests and diverge
everywhere else: `binary.size_bytes` and the eight checksum lists are in the
290 `INV-010` found nothing reading, and the fixture counts, scores, exit codes
and identities are checked by the tools script and reported by the verifier as
not checked here.

Neither is a superset of the other, and the verifier says so in the reason it
prints beside each fixture field: *needs the tool run; scripts/check_tools.sh
covers the tool fixtures*.

## The failure path, exercised

Three copies of the manifests were edited, one defect each, and the verifier
was pointed at them with `REPO=`:

    $ docker run --rm -v "<tampered>:/tampered:ro" -v "<repo>:/work:ro" \
        -w /work -e REPO=/tampered dactyloscopy:dev bash scripts/verify_manifests.sh
      21 checked, 2 of them failing
      311 not checked here, 1 of those refused for their status
    FAIL: 3 checks did not pass
      MAN-fvc2002.v1.json  subsets.fvc2002/DB1_B.checksums  manifests/checksums/fvc2002/DB1_B.sha256: 4127e484a99b90ba2def64aad7315dffa88d42ba1a2412f64412b2f8674c7dd9, recorded 1111111111111111111111111111111111111111111111111111111111111111
      MAN-tools.v1.json  tools.bozorth3.binary.size_bytes  status is CONFLICT: REF-014 decision 7 forbids reading it
      MAN-tools.v2.json  tools.mindtct.binary.sha256  /usr/local/bin/mindtct: 4d587263e242781e97afe236f5c8c46f275eb617c42e47f34d969c536c122c53, recorded 0000000000000000000000000000000000000000000000000000000000000000
    $ echo $?
    1

The three defects are a wrong binary digest, a checksum list whose recorded
digest no longer matches it, and a status set to `CONFLICT` on a field the
verifier would otherwise have checked. The third is the reading rule: the value
was correct, and the point is that it was never fetched.

Note where the third one is counted. Two of the three are failures of a check,
so the run says "21 checked, 2 of them failing"; the refusal is not a check and
is counted among the 311 that were not checked, with its own tally. Counting a
refusal as a check would let a manifest raise its own coverage by marking a
field `CONFLICT`, and the coverage number is the one thing this mechanism is
built to get right.

Three more failures were found by probing rather than by tampering, and each
is now a check the verifier makes:

    manifests/ empty                     FAIL: manifests/MAN-*.json matched nothing, exit 1
    a manifest that is not JSON          FAIL: <name>  <the whole file>  not readable as JSON, exit 1
    a value of ../../../etc/passwd       FAIL: resolves outside /tampered, exit 1

The third was a pass before it was a failure. A manifest field whose value is a
relative path that climbs out of the repository resolved to a real file, and
the verifier reported it present and printed `100.0% of fields checked`. It is
the shape of failure this whole mechanism exists to remove — a check satisfied
by the wrong file — and it was found by trying to make the verifier lie rather
than by reading it. Every path check now requires the resolved path to stay
under the root it was resolved against, and a name inside a checksum list must
stay under its subset.

`tests/test_manifest_verify.py` holds all of it: the wrong digest, a list
whose recorded digest no longer matches, the changed byte in a listed corpus
file, the `CONFLICT` refusal and that it is not counted as a check, a
`CONFLICT` on `distribution.root`, the composed identity recomputed and
mis-stated, both escaping paths, and the classification of fourteen named
fields — which `REF-014` decision 1 requires, since it put the classification
in code.

## What an adversarial pass over the first version found

The verifier and the records were read by a set of checkers whose instruction
was to refute them. Six of their findings changed this mechanism, and they are
recorded because the report is supposed to be the mechanism's account of its
own blind spots, and these were blind spots in that account.

**A pin was reported as class three.** `REF-014` says in terms that "the pin is
itself a class-one field: a digest, a commit id, a tree hash", and the verifier
put `source.archive_sha256`, `source.commit` and `source.tree` inside the
`source` block with everything else and never touched them. The rule now takes
the pin out of that block first. The test that holds the classification had the
same error in it, and correcting the code made it fail, which is what that test
is for.

**A linked-library list, an identity and a corpus count were reported as class
two.** `REF-014`'s class one names a linked-library list and a fixture count by
name, and the verifier's default was class two, whose meaning is "asserts
something about a file this repository controls". None of them does.

**The reason printed beside a not-checked field was often false.** Every
class-two field carried "no field says which file to derive it from", including
the 116 fields of the corpus and canon manifests that assert nothing about any
file. Each reason now says what would have to run, and the one that covers the
rest says only that no shape in this verifier matches the field.

**A refusal was counted as a check.** A field refused for a `CONFLICT` status
was recorded with the same call as a failed check, so the coverage percentage
rose when a manifest got worse. Refusals are now their own tally, counted among
the not-checked.

**`distribution.root` was read before its status was.** It is the one value the
verifier fetches before the walk, because it locates the corpus, and it was
therefore the one place the reading rule could be worked around. Its status is
now checked first.

**A `CONFLICT` field's value was read in the course of classifying it.** The
verifier now classifies a refused field from its path alone and stores no value
for it, so the docstring's claim that the value is never read is true of the
code rather than of the intention.

Three further findings are recorded and not acted on. The classification is
structural and a block is not always homogeneous, which the section above
states. `scripts/verify_manifests.sh` carries the whole report as an embedded
program, so a run that imports the module gets `verify` and `summarise` and
must format its own output. And the fix that makes a `checksums` field verify
the corpus depends on a sibling key literally named `path`, so a manifest that
named it something else would fall back to checking the list against its own
digest.

## Two defects the report exposed while it was being built

Both would have passed silently, and both are why the report prints per-field
detail rather than a total.

**The walk overwrote a field's parent.** Every level of the recursion replaced
the parent on the way back up, so a field's siblings came out as the manifest's
top-level keys. Every rule that reads a sibling — a digest beside a path, a
size beside a path, a checksums list beside a subset path — silently found
nothing. The symptom was eight subset paths reported as absent, because
`Dbs/Db1_a` was being looked for in the repository instead of the corpus.

**The `checksums` field checked itself instead of the corpus.** It carries a
`sha256` of the list, and the generic "digest of a named file" rule matched
first, so the field passed while not one of the 3520 files the list names had
been opened. The output said `manifests/checksums/fvc2002/DB1_A.sha256:
matches`, which was true and was not the check anybody wanted. It now reads
`list digest matches, 800 files, 0 differing`, and both halves must hold.

## Where the reading rule now lives

`INV-010` F-4 measured that the rule two records rest on — a `CONFLICT` field
is forbidden to read — was written in exactly one file git tracks, `README.md`
prohibition 3, and not in `manifests/README.md`, which is where a reader of
manifests looks. F-5 measured that nothing implemented it.

`manifests/README.md` now states it, `REF-014` decision 7 decides its scope for
all four statuses, and `implementation/library/manifest_verify.py` implements
it: a `CONFLICT` field is never read, and refusing to read one is a failure.
