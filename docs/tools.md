# External tools: what was checked

Captured output. The decisions behind it are in
[quality/REF-005-external-tool-provenance.md](../quality/REF-005-external-tool-provenance.md)
and, for the third tool,
[quality/REF-011-fingerjetfxose-admission.md](../quality/REF-011-fingerjetfxose-admission.md)
and [quality/REF-012-fingerjetfxose-invocation.md](../quality/REF-012-fingerjetfxose-invocation.md).
The facts they were taken against are frozen in
[manifests/MAN-tools.v2.json](../manifests/MAN-tools.v2.json).
[Version 1](../manifests/MAN-tools.v1.json) is not withdrawn: it describes an
image with two tools in it, and results recorded against it are reproduced
against it.

Everything below is what the commands printed. The two NBIS sections were
captured on 2026-09-06 and re-run unchanged on 2026-09-07; everything about
the third tool was captured on 2026-09-07. Each block names the command above
it: most come from `make image` and `make check-tools`, and the rest were run
directly, because no target exists for downloading an archive or looking
inside an image.

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

That the build directory is part of the result is not a curiosity of this
tree. The same thing was measured for the third tool, and it is why that
tool's build path is written into the recipe.

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

## The third tool has no archive to check

FingerJetFXOSE publishes no archive and carries no tag, which
`quality/INV-007` records under its Method, so there is no file to checksum
the way the NBIS archive above is checksummed. The pin is a commit id together
with its tree hash, and both are verified with `test` rather than printed, so
a mismatch stops the build. The submodule's commit is checked after the update
and not taken from `.gitmodules`.

    #7 [fjfx-builder 3/9] RUN git clone --no-checkout "https://github.com/FingerJetFXOSE/FingerJetFXOSE.git" /w/src     && cd /w/src     && git checkout --detach "1726ba08bf7f2137d2f861ac1ae124d5cd355eee"     && test "$(git rev-parse HEAD)" = "1726ba08bf7f2137d2f861ac1ae124d5cd355eee"     && test "$(git rev-parse HEAD^{tree})" = "e523e7b7ad5ab6d6e8b0a6fd163696f13e4a8b48"     && git submodule update --init --recursive     && test "$(git -C cxxtest rev-parse HEAD)" = "a19f85fdf90f97e16d6e3e7e3d2d68c31cd89e3c"
    #7 0.159 Cloning into '/w/src'...
    #7 1.974 HEAD is now at 1726ba0 Merge pull request #21 from hidjp/master
    #7 1.990 Submodule 'cxxtest' (https://github.com/CxxTest/cxxtest.git) registered for path 'cxxtest'
    #7 1.991 Cloning into '/w/src/cxxtest'...
    #7 3.515 Submodule path 'cxxtest': checked out 'a19f85fdf90f97e16d6e3e7e3d2d68c31cd89e3c'
    #7 DONE 3.5s

What that buys and what it does not: the tree is the tree, and nobody
published it. `quality/REF-011` decision 3 records the difference and the
manifest carries the two kinds of pin under different field names rather than
letting them look alike.

## What the third build printed

`cmake` is run directly rather than through the project's `runCMake.sh`,
because that script accepts no extra define and `quality/REF-012` D requires
the build number to be passed rather than derived from the clone.

Across the eight steps that follow that stage's `FROM` the log carries **0**
compiler diagnostics — no `[-W...]` marker anywhere — and **14** lines
containing
"warning". Ten are `update-alternatives` complaining about manual pages while
`apt` installs the toolchain. Four are `SyntaxWarning: invalid escape sequence
'\s'` from `cxxtest/python/python3/cxxtest/cxxtest_parser.py`, the fourth
party's code under this image's Python; `quality/INV-007` F-1 recorded the
same four. Seven lines match "error", and all seven are the package name
`liberror-perl`.

One warning `INV-007` F-1 did record is absent here: CMake's `Ignoring empty
string ("") provided on the command line`, which `runCMake.sh` causes by
passing an unset variable unquoted. Calling `cmake` directly removes it.

## The gate: upstream's own tests

They run in the builder stage, before anything is copied out, and they exit
non-zero on a failure, so a regression in the pinned source stops the image
from being built rather than being found by a run.

    #11 [fjfx-builder 7/9] RUN ./testFRFXLL && ./testFRFXLLInternals
    #11 0.143 Running testFRFXLL tests (91 tests)...........................................................................................OK!
    #11 0.241 Running testFRFXLLInternals tests (137 tests).........................................................................................................................................OK!
    #11 DONE 0.3s

91 and 137, the counts `quality/INV-007` F-3 recorded.

## The caller, and how it finds the library

The caller is compiled in the same stage. The step prints nothing of its own,
which is the point: `gcc -Wall -Wextra -pedantic` emits no diagnostic. What it
does print is the three `readelf` lines that state how the library is
resolved, and it then asserts them, so this is a check and not a note.

    #13 [fjfx-builder 9/9] RUN gcc -std=c99 -O2 -Wall -Wextra -pedantic         -I /w/src/FingerJetFXOSE/libFJFX/include         -o /w/iso-extract /w/iso-extract.c         -L /w/src/FingerJetFXOSE/dist/Linux-x86_64/x64 -lFJFX     && readelf -d /w/src/FingerJetFXOSE/dist/Linux-x86_64/x64/libFJFX.so         | grep -E 'SONAME'     && readelf -d /w/iso-extract | grep -E 'NEEDED|RPATH|RUNPATH'     && readelf -d /w/iso-extract | grep -q 'NEEDED.*\[libFJFX\.so\]'     && ! readelf -d /w/iso-extract | grep -qE 'RPATH|RUNPATH'
    #13 0.246  0x000000000000000e (SONAME)             Library soname: [libFJFX.so]
    #13 0.247  0x0000000000000001 (NEEDED)             Shared library: [libFJFX.so]
    #13 0.247  0x0000000000000001 (NEEDED)             Shared library: [libc.so.6]
    #13 DONE 0.3s

Two `NEEDED` entries and no `RPATH` or `RUNPATH`: nothing in the caller points
at a directory inside the builder stage. `ldconfig` in the runtime stage is
what puts `/usr/local/lib` in the loader's cache, and that is the whole of the
resolution mechanism.

## What the build context contains

`.dockerignore` excludes everything and then admits one file back by name.
Measured against the same context and the same `.dockerignore`, by copying the
whole context into a throwaway image and listing it:

    $ printf 'FROM busybox\nCOPY . /ctx\nRUN find /ctx -type f | sed "s|^/ctx|.|" | sort\n' > ctx.Dockerfile
    $ docker build --progress=plain --no-cache -f ctx.Dockerfile .
    transferring context: 130B done
    ./implementation/tools/iso-extract.c

One file. The `.git` directory, the manifests, the records and the rest of the
tree are not uploaded to the daemon.

## The library came out at the digest another record predicted

`quality/INV-007` F-4 measured that this project's build depends on the
directory it runs in, and F-2 recorded the digests of a build at `/w/src`. The
recipe therefore fixes the clone path at `/w/src`, which turns those digests
into a prediction. The prediction held:

    $ docker run --rm dactyloscopy:dev sha256sum /usr/local/lib/libFJFX.so
    ba453c674a82f4e9dd74985a4840285a07e5681defcde790d32473a7f4de1bf1  /usr/local/lib/libFJFX.so

That is the digest and the size `INV-007` F-2 recorded, from a build that
differs from it in the build number alone — `INV-007` F-1 built with 71, this
recipe passes 0. `INV-007` F-4 lists `libFJFX.so` among the artefacts that do
not change with that define, so this is that finding reproduced rather than a
coincidence.

Rebuilding the whole stage from scratch with `--no-cache-filter fjfx-builder`
gave the same image id as the cached build, `sha256:e0ded5a5dcc8f59...`, so
nothing in the stage varies between runs on this machine.

## The reader, and why the sample is not used

`quality/INV-007` F-6 measured that the sample program upstream ships leaves
its header parse one byte before the raster, and that its own short-read check
cannot fire on a well-formed PGM. `quality/REF-011` decision 1 replaces it
with a caller this repository owns. That the replacement actually fixes the
defect was checked by building a mutant of it: one line removed, the line that
consumes the single whitespace byte between the maximum value and the raster,
which is exactly where the sample stops.

    $ sed "s/^    pos++;$//" /w/iso-extract.c > /w/mutant.c && gcc ... -o /w/mutant /w/mutant.c ... -lFJFX
    -- correct reader:
    iso-extract: /w/t.pgm: extraction failed, the library returned 3
    exit=11
    -- mutant reader:
    iso-extract: /w/t.pgm: bytes present after the pixel data
    exit=9

The image is a synthetic 200 x 200 field, generated in that container, that
the library finds no fingerprint in — hence code 11 from the correct reader,
which is the library declining and not a parse failure. The mutant never gets
that far: reading from one byte early it sees one byte more than it needs and
exits 9. So a reader carrying the upstream defect fails on a well-formed file
here, and `tests/test_iso_extract.py`, which requires exit 0 on one, is what
holds the reader to it.

## Three stages build

    #1 [internal] load build definition from Dockerfile
    #2 [internal] load metadata for docker.io/library/python:3.12-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254
    #3 [internal] load .dockerignore
    #4 [fjfx-builder 1/9] FROM docker.io/library/python:3.12-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254
    #5 [internal] load build context
    #6 [fjfx-builder 2/9] RUN apt-get update     && apt-get install -y --no-install-recommends         build-essential         ca-certificates         cmake         git     && rm -rf /var/lib/apt/lists/*
    #7 [fjfx-builder 3/9] RUN git clone --no-checkout ... && test ... && git submodule update --init --recursive && test ...
    #8 [fjfx-builder 4/9] WORKDIR /w/src/FingerJetFXOSE/build/Linux-x86_64/x64
    #9 [fjfx-builder 5/9] RUN cmake -G "Unix Makefiles" -D32BITS=OFF -D64BITS=ON -DFRFXLL_BUILD=0         /w/src/FingerJetFXOSE     && make -j1
    #10 [fjfx-builder 6/9] WORKDIR /w/src/FingerJetFXOSE/dist/Linux-x86_64/x64
    #11 [fjfx-builder 7/9] RUN ./testFRFXLL && ./testFRFXLLInternals
    #12 [fjfx-builder 8/9] COPY implementation/tools/iso-extract.c /w/iso-extract.c
    #13 [fjfx-builder 9/9] RUN gcc -std=c99 -O2 -Wall -Wextra -pedantic ... -lFJFX     && readelf ...
    #14 [nbis-builder 6/7] RUN sed -i '142s/-O2 -w -ansi/-O2 -w -ansi -fcommon/' rules.mak     && sed -n '142p' rules.mak     && sed -n '142p' rules.mak | grep -q -- '-fcommon'
    #15 [nbis-builder 4/7] RUN curl -fsSL --retry 3 -o /tmp/nbis.zip "https://nigos.nist.gov/nist/nbis/nbis_v5_0_0.zip"     && echo "0adf8ab0f6b0e4208de50ca00ba21d3d77112ecd66288757ddfed21f6bee92c3  /tmp/nbis.zip" | sha256sum -c -     && unzip -q /tmp/nbis.zip -d /tmp/nbis     && mv /tmp/nbis/Rel_5.0.0/* /src/     && rm -rf /tmp/nbis.zip /tmp/nbis
    #16 [stage-2 2/8] RUN pip install --no-cache-dir         numpy==2.5.2         pytest==9.1.1         pillow==12.3.0
    #17 [nbis-builder 3/7] WORKDIR /src
    #18 [nbis-builder 5/7] RUN mkdir -p /usr/local/nbis     && ./setup.sh /usr/local/nbis --without-X11 --64
    #19 [stage-2 5/8] COPY --from=fjfx-builder /w/src/FingerJetFXOSE/dist/Linux-x86_64/x64/libFJFX.so /usr/local/lib/libFJFX.so
    #20 [nbis-builder 7/7] RUN make config && make it
    #21 [nbis-builder 2/7] RUN apt-get update     && apt-get install -y --no-install-recommends         build-essential         ca-certificates         cmake         curl         unzip     && rm -rf /var/lib/apt/lists/*
    #22 [stage-2 3/8] COPY --from=nbis-builder /src/mindtct/bin/mindtct /usr/local/bin/mindtct
    #23 [stage-2 4/8] COPY --from=nbis-builder /src/bozorth3/bin/bozorth3 /usr/local/bin/bozorth3
    #24 [stage-2 6/8] COPY --from=fjfx-builder /w/iso-extract /usr/local/bin/iso-extract
    #25 [stage-2 7/8] RUN ldconfig
    #26 [stage-2 8/8] WORKDIR /work
    #27 writing image sha256:e0ded5a5dcc8f594df58ab904be76605ad26492da834130592091b1348f7c3fc done
    #27 naming to docker.io/library/dactyloscopy:dev done

Only the step headers are kept; the `CACHED` markers and the compiler output
between them are cut, and four of the longest command lines are elided at
`...`. BuildKit numbers steps in the order it schedules them rather than in
file order, which is why the two builder stages interleave. Four steps copy
out of a builder now: two per stage.

## What ended up in the runtime image

The search covers the whole filesystem rather than `PATH` alone, and names six
NBIS binaries and every artefact of the FingerJetFXOSE build. Four files come
back:

    $ docker run --rm dactyloscopy:dev bash -c 'find / -type f \( -name bozorth3 -o -name nfiq -o -name mindtct -o -name an2ktool -o -name dpyimage -o -name cwsq -o -name iso-extract -o -name "libFJFX*" -o -name "fjfxSample*" -o -name "frfxllSample*" -o -name "libFRFXLL*" \) 2>/dev/null; test -d /usr/local/nbis && echo "/usr/local/nbis PRESENT" || echo "/usr/local/nbis absent"; test -d /w && echo "/w PRESENT" || echo "/w absent"; command -v gcc cc make cmake git || echo "no build tooling on PATH"'
    /usr/local/lib/libFJFX.so
    /usr/local/bin/iso-extract
    /usr/local/bin/bozorth3
    /usr/local/bin/mindtct
    /usr/local/nbis absent
    /w absent
    no build tooling on PATH

`fjfxSample` is not among them, and `quality/REF-011` decision 2 excludes it by
name: once the caller exists the sample has no purpose, and a binary nobody
uses is a binary whose provenance nobody checks. Neither is `libFRFXLL.so`,
which `libFJFX.so` links statically.

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
      gcc         absent
      cc          absent
      g++         absent
      make        absent
      cmake       absent
      git         absent
      /src        absent
      /w          absent
      mindtct     /usr/local/bin/mindtct
      bozorth3    /usr/local/bin/bozorth3
      iso-extract /usr/local/bin/iso-extract

    === 2. every file the manifest names is the file it froze ===
      mindtct     binary   4d587263e242781e97afe236f5c8c46f275eb617c42e47f34d969c536c122c53  matches
      bozorth3    binary   24fb809830f6a940dc27290b700b1d8e581a1f5c2c6bb9a97a856f96e8cdb287  matches
      iso-extract caller   b198f4f9d7709f54d235f82805638d271d809978602029982e046b2262038c1a  matches
      iso-extract library  ba453c674a82f4e9dd74985a4840285a07e5681defcde790d32473a7f4de1bf1  matches

    === 3. the source a caller was compiled from ===
      iso-extract 782026178aee86bae9f4a3897da7a68664c0b941  matches

    === 4. each identity recomputed from its parts ===
      mindtct     72be8e16c000c98ea9d655f526ef2fde569793eb812f85de15cbfde6e40e630a  from binary
      bozorth3    2c8f59c2f889bf90ed2c53e4eeca3556654bfb8dc222a432178d159a653de650  from binary
      iso-extract 9dbf5f4c3564cd2df7019144f69b2fabdcd505d73dabc51512c04f5157dd8097  from library,caller_source,caller

    === 5. the three checks above can fail ===
      digest      a modified copy of mindtct binary is rejected
      blob id     a source with one byte added hashes differently
      identity    mindtct     moves when binary changes
      identity    bozorth3    moves when binary changes
      identity    iso-extract moves when library changes

    === 6. what they link against ===
      mindtct     binary   libm.so.6 libc.so.6 ld-linux-x86-64.so.2
      bozorth3    binary   libm.so.6 libc.so.6 ld-linux-x86-64.so.2
      iso-extract caller   libFJFX.so libc.so.6 ld-linux-x86-64.so.2
      iso-extract library  libc.so.6 ld-linux-x86-64.so.2
      every file links exactly what the manifest records

    === 7. usage ===
      mindtct:
        Invalid number of arguments on command line
        Usage : mindtct [-b] [-m1] <finger_img_in> <oroot>
                -b  = contrast boost image
      bozorth3:
        bozorth3: ERROR: no xyt-files are specified on the command line
        Usage:
           To compute match scores for fingerprint pairs:
      iso-extract:
        iso-extract: read a binary PGM, write an ISO/IEC 19794-2:2005 template
        usage: iso-extract <image.pgm> <template.ist>
          the image is 8-bit greyscale, binary PGM (P5), maximum value 255

    === 8. TIFF to PNG and to PGM carries the same pixels ===
      Pillow 12.3.0
      101_1  tif L (374, 388)  ->  png L  pixels identical: True
      101_1  tif L (374, 388)  ->  pgm L  pixels identical: True
      101_2  tif L (374, 388)  ->  png L  pixels identical: True
      101_2  tif L (374, 388)  ->  pgm L  pixels identical: True
      102_1  tif L (374, 388)  ->  png L  pixels identical: True
      102_1  tif L (374, 388)  ->  pgm L  pixels identical: True

    === 9. the mindtct fixture ===
      101_1  minutiae 33  sha256 4aebdeeeab9fe3dd21f0bf2815df09f92da00c2c6ed6d906c0e2a61955b46437  MATCH
      101_2  minutiae 24  sha256 a9baeb93db9fe96b4a686032e5bb94fc044945081140b147471ee13015e611bc  MATCH
      102_1  minutiae 62  sha256 ac7a7d3e878848d491e82ca488f7c1dd4fe99742d8ecac46b150ab60ead2c16e  MATCH

    === 10. mindtct determinism: the same PNG twice, all eight outputs ===
      brw  identical
      dm   identical
      hcm  identical
      lcm  identical
      lfm  identical
      min  identical
      qm   identical
      xyt  identical

    === 11. the bozorth3 fixture, the full pairwise matrix ===
      101_1  101_1  ->   216  MATCH
      101_1  101_2  ->    60  MATCH
      101_1  102_1  ->     9  MATCH
      101_2  101_2  ->   163  MATCH
      101_2  102_1  ->     4  MATCH
      102_1  102_1  ->   499  MATCH

    === 12. bozorth3 symmetry on the off-diagonal pairs ===
      101_1  101_2     60 == 60    symmetric
      101_1  102_1      9 == 9     symmetric
      101_2  102_1      4 == 4     symmetric

    === 13. bozorth3 determinism: one pair, five times ===
      101_1 101_1 -> 216 216 216 216 216
      one distinct value across five runs

    === 14. the iso-extract fixture ===
      101_1  minutiae 25  bytes 180  sha256 eb34422b99203d9d2cac3ce65756401927e5f2033bf252abce102429c7d7d07b  MATCH
      101_2  minutiae 17  bytes 132  sha256 2ad547355939d68693c7206ec1147f44c5f115bf874c25d1e4b1db40b172acc3  MATCH
      102_1  minutiae 60  bytes 390  sha256 5cdd58272e100e6441f6c3385080151919c473b90392c24e0fed4ba60a065072  MATCH
      every length obeys 24 + 6 + 6 * minutiae

    === 15. iso-extract determinism: the same PGM three times ===
      101_1  three runs byte-identical

    === 16. iso-extract refuses malformed input with the codes it records ===
      trailing   exit 9   no output file, one line on stderr: iso-extract: <tmp>/bad_trailing.pgm: bytes present after the pixel data
      short      exit 8   no output file, one line on stderr: iso-extract: <tmp>/bad_short.pgm: fewer pixel bytes than width times height
      magic      exit 4   no output file, one line on stderr: iso-extract: <tmp>/bad_magic.pgm: not a binary PGM: the magic is not P5
      maxval     exit 6   no output file, one line on stderr: iso-extract: <tmp>/bad_maxval.pgm: the maximum value is not 255
      header     exit 5   no output file, one line on stderr: iso-extract: <tmp>/bad_header.pgm: malformed PGM header
      dimension  exit 7   no output file, one line on stderr: iso-extract: <tmp>/bad_dimension.pgm: width or height is zero or above 65535

    all checks passed

    $ echo $?
    0

Two fields are replaced above: the fixture directory's path by `<fixture>`,
and the script's own `mktemp -d` directory by `<tmp>`, which differs on every
run. Nothing else in the transcript is altered. The images stay outside the
repository, as `docs/data.md` requires.

The two NBIS fixtures are re-run here rather than taken on trust: the image
changed when the third tool was added, so the evidence for the first two was
produced again in the new image.

The three templates in section 14 are the ones `quality/INV-007` F-8 recorded
for its reference reader, byte for byte. That reader was a Python instrument
of that investigation, was not adopted, and has no descendant in this image,
so a C program compiled here and that program agree on three images — and the
same table in `INV-007` records that neither agrees with the upstream sample.

## When a check does not pass

The checks are gates, and the failure path was exercised rather than
described. A copy of the manifest was edited, once per kind of check, and the
script was pointed at it with `MANIFEST=`. Each run stopped at the section
that caught it and exited 1.

A digest that does not match the file:

    $ docker run ... -e MANIFEST=/tampered/library-tampered.json ... bash scripts/check_tools.sh /fixture
    === 2. every file the manifest names is the file it froze ===
      ...
      iso-extract library  ba453c674a82f4e9dd74985a4840285a07e5681defcde790d32473a7f4de1bf1
                           expected 0000000000000000000000000000000000000000000000000000000000000000
    FAIL: iso-extract: the library in this image is not the file the manifest records
    exit: 1

A source whose blob id does not match the working copy:

    $ docker run ... -e MANIFEST=/tampered/source-tampered.json ...
    === 3. the source a caller was compiled from ===
      iso-extract 782026178aee86bae9f4a3897da7a68664c0b941
                  expected 0000000000000000000000000000000000000000
    FAIL: iso-extract: the working copy of the caller's source is not the blob the manifest records
    exit: 1

A composed identity that does not follow from the parts beside it:

    $ docker run ... -e MANIFEST=/tampered/identity-tampered.json ...
    === 4. each identity recomputed from its parts ===
      mindtct     72be8e16c000c98ea9d655f526ef2fde569793eb812f85de15cbfde6e40e630a  from binary
      bozorth3    2c8f59c2f889bf90ed2c53e4eeca3556654bfb8dc222a432178d159a653de650  from binary
    FAIL: iso-extract: the composed identity does not follow from the parts the manifest carries
      iso-extract 9dbf5f4c3564cd2df7019144f69b2fabdcd505d73dabc51512c04f5157dd8097
                  expected 0000000000000000000000000000000000000000000000000000000000000000
    exit: 1

A fixture number that the tool does not reproduce — here one minutia added to
one case, and nothing else:

    $ docker run ... -e MANIFEST=/tampered/fixture-tampered.json ...
    === 14. the iso-extract fixture ===
      101_1  minutiae 25  bytes 180  sha256 eb34422b99203d9d2cac3ce65756401927e5f2033bf252abce102429c7d7d07b  MISMATCH
             expected 26        180         eb34422b99203d9d2cac3ce65756401927e5f2033bf252abce102429c7d7d07b
      101_2  minutiae 17  bytes 132  sha256 2ad547355939d68693c7206ec1147f44c5f115bf874c25d1e4b1db40b172acc3  MATCH
      102_1  minutiae 60  bytes 390  sha256 5cdd58272e100e6441f6c3385080151919c473b90392c24e0fed4ba60a065072  MATCH
    FAIL: the iso-extract fixture does not reproduce; this is a finding, not a nuisance
    exit: 1

Section 5 of the script does the same thing on every run rather than only
here: it corrupts a copy of a binary, adds a byte to a copy of the source, and
recomputes each identity with one part changed, and it fails if any of those
still reports a match.

## The suite

    $ make test
    MSYS_NO_PATHCONV=1 docker run --rm -v "D:/My PET Projects/dactyloscopy:/work" -w /work "dactyloscopy:dev" python -m pytest
    ============================= test session starts ==============================
    platform linux -- Python 3.12.14, pytest-9.1.1, pluggy-1.6.0
    rootdir: /work
    collected 47 items

    tests/test_iso_extract.py ......................                         [ 46%]
    tests/test_manifest_verify.py .........................                  [100%]

    ============================== 47 passed in 0.60s ==============================

Re-captured on 2026-09-07, when `tests/test_manifest_verify.py` took the suite
from 22 tests to 47; the 22 in the first file are this page's, and the other 25
are `docs/manifests.md`'s. The suite needs no data: its image is generated by
the test from constants the test states. What it establishes about the reader,
and what it cannot, is written at the top of `tests/test_iso_extract.py`.

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
    fixture in manifests/MAN-tools.v2.json was recorded against:

      make check-tools FVC_DB1_B=/path/to/FVC2002/Dbs/Db1_b

    The directory is mounted read-only and no layout under LABDATA is
    assumed: that is not decided yet.
    make: *** [Makefile:74: check-tools] Error 1
