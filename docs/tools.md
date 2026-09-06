# External tools: what was checked

Captured output. The decisions behind it are in
[quality/REF-005-external-tool-provenance.md](../quality/REF-005-external-tool-provenance.md),
and the facts they were taken against are frozen in
[manifests/MAN-tools.v1.json](../manifests/MAN-tools.v1.json).

Everything below is what the commands printed, on 2026-09-06. Each block names
the command above it: most come from `make image` and `make check-tools`, and
the rest were run directly, because no target exists for downloading an
archive or looking inside an image.

## Where the source comes from

The publisher serves the archive over HTTPS, with no registration:

    $ Invoke-WebRequest -Uri https://nigos.nist.gov/nist/nbis/nbis_v5_0_0.zip -Method Head
    status: 200
      Content-Type: application/zip
      Content-Length: 52595795
      Last-Modified: Tue, 03 Mar 2015 20:57:05 GMT
      ETag: "3228c53-5106893bf8a40"
      Server: cloudflare

The NIGOS products page lists the release beside that file:

    $ (Invoke-WebRequest .../image-group-open-source-server-nigos).Content -replace '<[^>]+>',' '
    ... NBIS Software See the NBIS home page for more information.  Release 5.0.0 -
    Test 5.0.0 - stable version - (03/04/2015) - changelog Release 4.2.0 - Test
    4.2.0 - stable version - (10/30/2013) Release 4.1.0 - Test 4....

Downloaded and identified:

    $ Invoke-WebRequest -Uri https://nigos.nist.gov/nist/nbis/nbis_v5_0_0.zip -OutFile nbis_v5_0_0.zip
    downloaded in 34.1s
    size: 52595795 bytes
    sha256: 0adf8ab0f6b0e4208de50ca00ba21d3d77112ecd66288757ddfed21f6bee92c3

    $ first 4 bytes (zip magic is 50 4B 03 04)
    50 4B 03 04

The page's date and the server's `Last-Modified` differ by one day: the page
says 03/04/2015, the header says 3 March 2015. Both were read directly; the
manifest records the page's date as the release date and notes the header.

## The archive against the mirror the recipe was built on

The archive unpacks into a top-level `Rel_5.0.0`; the clone is flat, so the
paths were aligned before comparing.

    $ git clone https://github.com/lessandro/nbis && git checkout 3d3b05f0144b706bed56407957bc00779baf2fa5
    official files: 3879
    mirror files:   3879
    common paths:   3879

    GROUP 1 byte-identical:             593
    GROUP 2 differ only in whitespace:  3286
    GROUP 3 genuinely different:        0
    only in official: 0
    only in mirror:   0

Group 2 was normalised explicitly rather than waved through, and the
normalisation needed was narrower than "whitespace":

    among the 3286:
      line endings only: 3286

    files where the official copy has more CR bytes (i.e. CRLF upstream, LF in the mirror): 0
    files where the mirror has more CR bytes: 3286

So the archive is the one with Unix line endings and the mirror is the one
carrying CRLF, and nothing else separates those files.

The question that matters is whether anything a tool compiles from differs:

    C sources, headers and makefiles compared: 2179
    of those, differing after line-ending normalisation: 0

Group 3 is empty, so no file `mindtct` or `bozorth3` builds from differs
between the two in content.

## Building the official tree

`rules.mak` does not exist until `setup.sh` generates it, and line 142 of the
generated file is the same `CFLAGS` assignment the recipe expects, so the same
patch applies unchanged:

    --- line 142 of rules.mak before setup (does it exist yet?):
      rules.mak not present before setup.sh
    --- line 142 after setup.sh:
    CFLAGS	:= -O2 -w -ansi -D_POSIX_SOURCE $(ENDIAN_FLAG) $(NBIS_JASPER_FLAG) $(NBIS_OPENJP2_FLAG) $(NBIS_PNG_FLAG) $(ARCH_FLAG)
    --- the CFLAGS assignment, wherever it is:
    142:CFLAGS	:= -O2 -w -ansi -D_POSIX_SOURCE $(ENDIAN_FLAG) $(NBIS_JASPER_FLAG) $(NBIS_OPENJP2_FLAG) $(NBIS_PNG_FLAG) $(ARCH_FLAG)

Built in a scratch directory, the binary is the same size as the one from the
mirror but not the same bytes:

    patch applied to line 142
    build finished
    -rwxr-xr-x 1 root root 960024 /out/mindtct-official
    6f7ade082b5139e7a1d3be60a35de6b299f7a389a1a084903e85cd91da526a3d  /out/mindtct-official

525 bytes out of 960024 differ, in 13 runs, and every one of them is
attributable to the directory the build ran in:

    differing runs: 13
      offset 872-891 (20 bytes): GNU build-id
      offset 677441-677491 (51 bytes): /build/openjp2/src/lib/openjp2/src/lib/openjp2/cio.c
      offset 678049-678138 (90 bytes): /build/openjp2/src/lib/openjp2/src/lib/openjp2/image.c
      ... nine more, all openjp2 source paths ...

    official build paths embedded: ['/build/openjp2/src/lib/openjp2/src/lib/openjp2/']
    mirror   build paths embedded: ['/src/openjp2/src/lib/openjp2/src/lib/openjp2/']

Rebuilt in the same directory the image uses, the two sources give one binary:

    official source, built in /src: 4d587263e242781e97afe236f5c8c46f275eb617c42e47f34d969c536c122c53
    mirror source,   built in /src: 4d587263e242781e97afe236f5c8c46f275eb617c42e47f34d969c536c122c53
    byte-identical: True

## The gate: the fixture against the official build

    === the official build against the fixture ===
      101_1  minutiae 33  sha256 4aebdeeeab9fe3dd21f0bf2815df09f92da00c2c6ed6d906c0e2a61955b46437  MATCH
      101_2  minutiae 24  sha256 a9baeb93db9fe96b4a686032e5bb94fc044945081140b147471ee13015e611bc  MATCH
      102_1  minutiae 62  sha256 ac7a7d3e878848d491e82ca488f7c1dd4fe99742d8ecac46b150ab60ead2c16e  MATCH

    === and all eight outputs against the image's own mindtct ===
      101_1  identical 8/8, differing 0
      101_2  identical 8/8, differing 0
      102_1  identical 8/8, differing 0

    GATE: PASSED

## The checksum is a gate, not a warning

With the recorded checksum the fetch step reports `OK`:

    #8 4.754 /tmp/nbis.zip: OK

With a wrong one the build stops there:

    $ docker build --build-arg NBIS_SHA256=0000...0000 --target nbis-builder .
    #7 4.932 /tmp/nbis.zip: FAILED
    #7 4.932 sha256sum: WARNING: 1 computed checksum did NOT match
    #7 ERROR: process "/bin/sh -c curl ... | sha256sum -c - ..." did not complete successfully: exit code: 1
    build exit (nonzero expected): 1

The host must be reachable for the build to work at all. It answered from this
machine; a network that blocks nigos.nist.gov will fail the fetch step rather
than fall back to anything.

## Both stages build

    #1 [internal] load build definition from Dockerfile
    #2 [internal] load metadata for docker.io/library/python:3.12-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254
    #3 [internal] load .dockerignore
    #4 [nbis-builder 1/7] FROM docker.io/library/python:3.12-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254
    #5 [nbis-builder 5/7] RUN mkdir -p /usr/local/nbis     && ./setup.sh /usr/local/nbis --without-X11 --64
    #6 [stage-1 4/5] COPY --from=nbis-builder /src/bozorth3/bin/bozorth3 /usr/local/bin/bozorth3
    #7 [nbis-builder 7/7] RUN make config && make it
    #8 [nbis-builder 2/7] RUN apt-get update     && apt-get install -y --no-install-recommends         build-essential         ca-certificates         cmake         curl         unzip     && rm -rf /var/lib/apt/lists/*
    #9 [stage-1 3/5] COPY --from=nbis-builder /src/mindtct/bin/mindtct /usr/local/bin/mindtct
    #10 [nbis-builder 3/7] WORKDIR /src
    #11 [nbis-builder 6/7] RUN sed -i '142s/-O2 -w -ansi/-O2 -w -ansi -fcommon/' rules.mak     && sed -n '142p' rules.mak     && sed -n '142p' rules.mak | grep -q -- '-fcommon'
    #12 [nbis-builder 4/7] RUN curl -fsSL --retry 3 -o /tmp/nbis.zip "https://nigos.nist.gov/nist/nbis/nbis_v5_0_0.zip"     && echo "0adf8ab0f6b0e4208de50ca00ba21d3d77112ecd66288757ddfed21f6bee92c3  /tmp/nbis.zip" | sha256sum -c -     && unzip -q /tmp/nbis.zip -d /tmp/nbis     && mv /tmp/nbis/Rel_5.0.0/* /src/     && rm -rf /tmp/nbis.zip /tmp/nbis
    #13 [stage-1 2/5] RUN pip install --no-cache-dir         numpy==2.5.2         pytest==9.1.1         pillow==12.3.0
    #14 [stage-1 5/5] WORKDIR /work
    #15 writing image sha256:720568f0723c1f451658246d196276ed8f9e26c02da5ed91e76b0cf42e535d3e done
    #15 naming to docker.io/library/dactyloscopy:dev done
    image id:
    sha256:720568f0723c1f451658246d196276ed8f9e26c02da5ed91e76b0cf42e535d3e
    base, as pinned in the Dockerfile:
    FROM python:3.12-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254 AS nbis-builder
    FROM python:3.12-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254

Only the step headers are kept; the `CACHED` markers and the compiler output
between them are cut. BuildKit numbers steps in the order it schedules them
rather than in file order. Two steps now copy out of the builder, one per
tool.

## What ended up in the runtime image

The search below covers the whole filesystem rather than `PATH` alone, and
names six NBIS binaries. Two come back, and they are the two this project
uses:

    $ docker run --rm dactyloscopy:dev bash -c 'find / -type f \( -name bozorth3 -o -name nfiq -o -name mindtct -o -name an2ktool -o -name dpyimage -o -name cwsq \) 2>/dev/null; test -d /usr/local/nbis && echo "/usr/local/nbis PRESENT" || echo "/usr/local/nbis absent"; command -v gcc cc make cmake git || echo "no build tooling on PATH"'
    /usr/local/bin/bozorth3
    /usr/local/bin/mindtct
    /usr/local/nbis absent
    no build tooling on PATH

## The matcher's two silent defaults

`bozorth3` prints them in its own usage:

    $ bozorth3
    bozorth3: ERROR: no xyt-files are specified on the command line
    Usage:
    ...
       -m1                     all xyt files use representation according to ANSI INCITS 378-2004
       -n <max-minutiae>       set maximum number of munitiae to use from any file [150]; legal range is [0,200]
       -A parameter=<value>
              minminutiae=#    set minimum number of munitiae for match score to be more than 0 [10]

Both are recorded in the manifest as part of the invocation. Neither binds on
the fixture below, where the counts are 33, 24 and 62: all are above the
floor of 10 and below the cap of 150.

## The verification

    MSYS_NO_PATHCONV=1 docker run --rm -v "D:/My PET Projects/dactyloscopy:/work" -v "<fixture>:/fixture:ro" -w /work "dactyloscopy:dev" bash scripts/check_tools.sh /fixture
    === 1. the runtime image carries the tools and not the toolchain ===
      gcc       absent
      cc        absent
      g++       absent
      make      absent
      cmake     absent
      git       absent
      /src      absent
      mindtct   /usr/local/bin/mindtct
      bozorth3  /usr/local/bin/bozorth3

    === 2. each binary is the one the manifest froze ===
      mindtct   4d587263e242781e97afe236f5c8c46f275eb617c42e47f34d969c536c122c53  matches
      bozorth3  24fb809830f6a940dc27290b700b1d8e581a1f5c2c6bb9a97a856f96e8cdb287  matches

    === 3. what they link against ===
      mindtct:

The four lines `ldd` prints begin with a tab, so they are quoted unindented;
indenting them would put a space before a tab and alter captured output. Both
tools print the same four:

```
	linux-vdso.so.1 (0x000074313f118000)
	libm.so.6 => /lib/x86_64-linux-gnu/libm.so.6 (0x000074313ef57000)
	libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x000074313ed75000)
	/lib64/ld-linux-x86-64.so.2 (0x000074313f11a000)
only libm, libc and the loader
bozorth3:
	linux-vdso.so.1 (0x0000730348667000)
	libm.so.6 => /lib/x86_64-linux-gnu/libm.so.6 (0x00007303456c1000)
	libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007303454df000)
	/lib64/ld-linux-x86-64.so.2 (0x0000730348669000)
```

The transcript continues:

        only libm, libc and the loader

    === 4. usage ===
      mindtct:
        Invalid number of arguments on command line
        Usage : mindtct [-b] [-m1] <finger_img_in> <oroot>
                -b  = contrast boost image
      bozorth3:
        bozorth3: ERROR: no xyt-files are specified on the command line
        Usage:
           To compute match scores for fingerprint pairs:

    === 5. TIFF to PNG carries the same pixels ===
      Pillow 12.3.0
      101_1  tif L (374, 388)  ->  png L  pixels identical: True
      101_2  tif L (374, 388)  ->  png L  pixels identical: True
      102_1  tif L (374, 388)  ->  png L  pixels identical: True

    === 6. the mindtct fixture ===
      101_1  minutiae 33  sha256 4aebdeeeab9fe3dd21f0bf2815df09f92da00c2c6ed6d906c0e2a61955b46437  MATCH
      101_2  minutiae 24  sha256 a9baeb93db9fe96b4a686032e5bb94fc044945081140b147471ee13015e611bc  MATCH
      102_1  minutiae 62  sha256 ac7a7d3e878848d491e82ca488f7c1dd4fe99742d8ecac46b150ab60ead2c16e  MATCH

    === 7. mindtct determinism: the same PNG twice, all eight outputs ===
      brw  identical
      dm   identical
      hcm  identical
      lcm  identical
      lfm  identical
      min  identical
      qm   identical
      xyt  identical

    === 8. the bozorth3 fixture, the full pairwise matrix ===
      101_1  101_1  ->   216  MATCH
      101_1  101_2  ->    60  MATCH
      101_1  102_1  ->     9  MATCH
      101_2  101_2  ->   163  MATCH
      101_2  102_1  ->     4  MATCH
      102_1  102_1  ->   499  MATCH

    === 9. bozorth3 symmetry on the off-diagonal pairs ===
      101_1  101_2     60 == 60    symmetric
      101_1  102_1      9 == 9     symmetric
      101_2  102_1      4 == 4     symmetric

    === 10. bozorth3 determinism: one pair, five times ===
      101_1 101_1 -> 216 216 216 216 216
      one distinct value across five runs

    all checks passed

    $ echo $?
    0

The fixture directory is mounted read-only and its path is replaced by
`<fixture>` above; nothing else in the transcript is altered. The images stay
outside the repository, as `docs/data.md` requires.

`mindtct`'s fixture is re-run here rather than taken on trust: the image
changed when the second binary was added, so the first tool's evidence was
produced again in the new image.

## When a digest does not match

The check is a gate, and the failure path was exercised rather than
described. A copy of the manifest was edited to carry a wrong digest, once
per tool, and the script was pointed at it:

    $ docker run ... -e MANIFEST=/tampered/mindtct-tampered.json dactyloscopy:dev bash scripts/check_tools.sh /fixture
    === 2. each binary is the one the manifest froze ===
      mindtct   4d587263e242781e97afe236f5c8c46f275eb617c42e47f34d969c536c122c53
                expected 0000000000000000000000000000000000000000000000000000000000000000
    FAIL: mindtct in this image is not the binary the manifest records
    exit: 1

    $ docker run ... -e MANIFEST=/tampered/bozorth3-tampered.json dactyloscopy:dev bash scripts/check_tools.sh /fixture
    === 2. each binary is the one the manifest froze ===
      mindtct   4d587263e242781e97afe236f5c8c46f275eb617c42e47f34d969c536c122c53  matches
      bozorth3  24fb809830f6a940dc27290b700b1d8e581a1f5c2c6bb9a97a856f96e8cdb287
                expected 0000000000000000000000000000000000000000000000000000000000000000
    FAIL: bozorth3 in this image is not the binary the manifest records
    exit: 1

Both values are printed, the run stops at that section, and the exit code is
non-zero.

## What the self-comparisons show, on three images

    $ for n in 101_1 101_2 102_1; do bozorth3 $n.xyt $n.xyt; done
    file    minutiae  self-comparison score
    101_1   33        216
    101_2   24        163
    102_1   62        499

Measured on these three images only: the self-comparison score rises with the
minutia count rather than reaching a fixed ceiling, so the score is not
normalised by the number of minutiae and a self-comparison does not give a
constant that other scores could be divided by. Three images are three
images; this is what was observed, not a property established of the tool.

## Without the fixture directory

    $ make check-tools
    FVC_DB1_B is not set, so nothing was checked.

    It names the directory holding the FVC2002 Db1_b images, which the
    fixture in manifests/MAN-tools.v1.json was recorded against:

      make check-tools FVC_DB1_B=/path/to/FVC2002/Dbs/Db1_b

    The directory is mounted read-only and no layout under LABDATA is
    assumed: that is not decided yet.
    make: *** [Makefile:78: check-tools] Error 1
