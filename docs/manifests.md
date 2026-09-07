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

375 lines, of which the summaries are quoted in full below and the lists of
unchecked field names are cut at the first few of each group; nothing else is
altered.

    $ make verify LABDATA=<root>
    === MAN-fvc2002.v1.json
      124 fields with a value and a status: 16 checked, 108 not
        derivable     108 fields,   0 checked, 0 failed
        recomputable   16 fields,  16 checked, 0 failed
      checked:
        ok   recomputable subsets.fvc2002/DB1_A.path  Dbs/Db1_a: present
        ok   recomputable subsets.fvc2002/DB1_A.checksums  manifests/checksums/fvc2002/DB1_A.sha256: list digest matches, 800 files, 0 differing
        ok   recomputable subsets.fvc2002/DB1_B.path  Dbs/Db1_b: present
        ok   recomputable subsets.fvc2002/DB1_B.checksums  manifests/checksums/fvc2002/DB1_B.sha256: list digest matches, 80 files, 0 differing
        ... six more subsets, 800 or 80 files each, 0 differing ...
      not checked here, 108 fields:
        not checked here: no field says which file to derive it from (108)
          derivable   distribution.root
          derivable   distribution.layout
          derivable   distribution.files_total
          ... 105 more ...

    === MAN-minutia.v1.json
      8 fields with a value and a status: 0 checked, 8 not
        derivable       8 fields,   0 checked, 0 failed
      not checked here, 8 fields:
        not checked here: no field says which file to derive it from (8)
          derivable   x-manifest.asserted_numbers.angle_full_circle
          derivable   x-manifest.asserted_numbers.angle_maximum
          ... six more ...

    === MAN-tools.v1.json
      63 fields with a value and a status: 6 checked, 57 not
        derivable      23 fields,   0 checked, 0 failed
        external       16 fields,   0 checked, 0 failed
        recomputable   24 fields,   6 checked, 0 failed
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
      137 fields with a value and a status: 12 checked, 125 not
        derivable      59 fields,   0 checked, 0 failed
        external       25 fields,   0 checked, 0 failed
        recomputable   53 fields,  12 checked, 0 failed
      checked:
        ok   recomputable tools.mindtct.binary.path  /usr/local/bin/mindtct: present
        ... eleven more: three files, each with its path, digest and size ...

    === coverage over every manifest
      332 fields with a value and a status
      34 checked, 0 of them failing
      298 not checked here
      10.2% of fields checked

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
      18 checked, 0 of them failing
      314 not checked here
      5.4% of fields checked
      LABDATA was not set, so no corpus digest was verified

    every check that ran, passed

The sixteen fields that move between the two runs are the eight subset paths
and the eight checksum lists. A skipped check is reported as skipped, never as
a pass: `REF-014` decision 4 requires that, because a skip reported as a pass
is the failure the whole mechanism exists to remove.

## What it costs

    make verify                    0.716 s
    make verify LABDATA=<root>    13.372 s

The second reads 452 MB across a bind mount and digests 3520 files.
`INV-010` F-3 measured `sha256sum -c` doing the same work in 6.312 s; this
verifier opens and digests each file from Python, and the difference is that.
Both are small enough for `REF-014` decision 4, which makes verification a
precondition rather than an occasional command.

## The coverage is the point

10.2% of fields checked is not a good number. It is the honest one, and it is
printed on every run.

`REF-014` says why each class is where it is. **Recomputable** fields are
checked. **External** fields — everything inside a `source` block — are claims
about an artefact this repository did not make, and they are bound to the pin
in the same block: a pinned object cannot make a claim about it expire, so
those need no recurring check until the pin moves. **Derivable** fields assert
something about a file this repository controls and do not say which file, and
the verifier does not guess: `INV-009` F-2 measured what guessing costs, when a
search for the four package names of `extra_build_packages` found all four in
the `Dockerfile` because the fourth was in a builder stage the field is not
about. A check that can be satisfied by the wrong file reports a pass.

So the 298 are the size of the gap, printed rather than implied. `INV-009`
found a mechanism that printed "all checks passed" over 42 of 63 fields; the
whole difference here is that the denominator is on the screen.

## What the other mechanism covers, and why the two do not add up

`scripts/check_tools.sh` reads 42 fields of `MAN-tools.v2` — `INV-010` F-1
measured exactly which — and runs the tools to check its fixtures.
`make verify` checks 34 fields across all four manifests without running a
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
      19 checked, 3 of them failing
    FAIL: 3 checks did not pass
      MAN-fvc2002.v1.json  subsets.fvc2002/DB1_B.checksums  manifests/checksums/fvc2002/DB1_B.sha256: 4127e484a99b90ba2def64aad7315dffa88d42ba1a2412f64412b2f8674c7dd9, recorded 1111111111111111111111111111111111111111111111111111111111111111
      MAN-tools.v1.json  tools.bozorth3.binary.size_bytes  status is CONFLICT: REF-014 decision 7 forbids reading it
      MAN-tools.v2.json  tools.mindtct.binary.sha256  /usr/local/bin/mindtct: 4d587263e242781e97afe236f5c8c46f275eb617c42e47f34d969c536c122c53, recorded 0000000000000000000000000000000000000000000000000000000000000000
    $ echo $?
    1

The three defects are a wrong binary digest, a checksum list whose recorded
digest no longer matches it, and a status set to `CONFLICT` on a field the
verifier would otherwise have checked. The third is the reading rule: the value
was correct, and the point is that it was never used.

`tests/test_manifest_verify.py` holds the same three, plus a changed byte in a
listed corpus file, plus the classification of nine named fields — which
`REF-014` decision 1 requires, since it put the classification in code.

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
