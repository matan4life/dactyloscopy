# External tools: what was checked

Captured output. The decisions behind it are in
[quality/REF-005-external-tool-provenance.md](../quality/REF-005-external-tool-provenance.md),
and the facts they were taken against are frozen in
[manifests/tools.json](../manifests/tools.json).

Everything below was produced on 2026-09-06 and is what the commands printed.
Each block names the command above it: most come from `make image` and
`make check-tools`, and the blocks that look inside the image were run with
`docker run` directly, because no target exists for inspecting an image.

## Both stages build

    $ make image
    #1 [internal] load build definition from Dockerfile
    #2 [internal] load metadata for docker.io/library/python:3.12-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254
    #3 [internal] load .dockerignore
    #4 [nbis-builder 1/7] FROM docker.io/library/python:3.12-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254
    #5 [nbis-builder 6/7] RUN sed -i '142s/-O2 -w -ansi/-O2 -w -ansi -fcommon/' rules.mak     && sed -n '142p' rules.mak     && sed -n '142p' rules.mak | grep -q -- '-fcommon'
    #6 [nbis-builder 2/7] RUN apt-get update     && apt-get install -y --no-install-recommends         build-essential         ca-certificates         cmake         git     && rm -rf /var/lib/apt/lists/*
    #7 [stage-1 3/4] COPY --from=nbis-builder /src/mindtct/bin/mindtct /usr/local/bin/mindtct
    #8 [nbis-builder 7/7] RUN make config && make it
    #9 [nbis-builder 5/7] RUN mkdir -p /usr/local/nbis     && ./setup.sh /usr/local/nbis --without-X11 --64
    #10 [nbis-builder 3/7] WORKDIR /src
    #11 [nbis-builder 4/7] RUN git clone "https://github.com/lessandro/nbis" .     && git checkout --quiet "3d3b05f0144b706bed56407957bc00779baf2fa5"     && test "$(git rev-parse HEAD)" = "3d3b05f0144b706bed56407957bc00779baf2fa5"
    #12 [stage-1 2/4] RUN pip install --no-cache-dir         numpy==2.5.2         pytest==9.1.1         pillow==12.3.0
    #13 [stage-1 4/4] WORKDIR /work
    #14 writing image sha256:3c956aefb97e13f2ad133793907f0cc138eea019934f0ee9a28190ea639135e0 done
    #14 naming to docker.io/library/dactyloscopy:dev done

    image id:
    sha256:3c956aefb97e13f2ad133793907f0cc138eea019934f0ee9a28190ea639135e0
    base, as pinned in the Dockerfile:
    FROM python:3.12-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254 AS nbis-builder
    FROM python:3.12-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254

Only the step headers are kept above; the `CACHED` markers and the compiler
output between them are cut. BuildKit numbers steps in the order it schedules
them rather than in file order, so the builder stage is steps 4, 5, 6, 8, 9,
10 and 11, the runtime is steps 7, 12 and 13, and step 7 is the one file that
crosses from the first into the second.

The first build, before any layer was cached, failed twice, and the Dockerfile
carries the answer to each. `setup.sh` refused an install directory that did
not exist:

    #9 2.001 Directory "/usr/local/nbis" doesn't exist!

and `make config` stopped in the package it builds first:

    #11 0.382 /bin/sh: 9: cmake: not found
    #11 0.382 make[2]: *** [/src/buildutil/openjp2_libs.mak:65: config] Error 1

## What ended up in the runtime image

    $ docker image ls dactyloscopy:dev --format '{{.Repository}}:{{.Tag}}  {{.Size}}'
    dactyloscopy:dev  236MB

The search below covers the whole filesystem rather than `PATH` alone, and
names six NBIS binaries. One line comes back:

    $ docker run --rm dactyloscopy:dev bash -c 'find / -type f \( -name bozorth3 -o -name nfiq -o -name mindtct -o -name an2ktool -o -name dpyimage -o -name cwsq \) 2>/dev/null; test -d /usr/local/nbis && echo "/usr/local/nbis PRESENT" || echo "/usr/local/nbis absent"; command -v gcc cc make cmake git || echo "no build tooling on PATH"'
    /usr/local/bin/mindtct
    /usr/local/nbis absent
    no build tooling on PATH

The builder stage does produce a second binary, which stays there:

    $ docker build --target nbis-builder -t nbis-probe .
    $ docker run --rm nbis-probe bash -c 'ls /src/bozorth3/bin/; ls /src/mindtct/bin/'
    bozorth3
    mindtct

    $ docker image rm -f nbis-probe

## The verification

    MSYS_NO_PATHCONV=1 docker run --rm -v "D:/My PET Projects/dactyloscopy:/work" -v "<fixture>:/fixture:ro" -w /work "dactyloscopy:dev" bash scripts/check_tools.sh /fixture
    === 1. the runtime image carries the tool and not the toolchain ===
      gcc       absent
      cc        absent
      g++       absent
      make      absent
      cmake     absent
      git       absent
      bozorth3  absent
      /src      absent
      mindtct   /usr/local/bin/mindtct

    === 2. the binary is the one the manifest froze ===
      sha256 4d587263e242781e97afe236f5c8c46f275eb617c42e47f34d969c536c122c53
      matches the manifest

    === 3. what mindtct links against ===

The four lines `ldd` prints begin with a tab, so they are quoted unindented;
indenting them would put a space before a tab and alter captured output:

```
	linux-vdso.so.1 (0x00007101e4e01000)
	libm.so.6 => /lib/x86_64-linux-gnu/libm.so.6 (0x00007101e4c40000)
	libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007101e4a5e000)
	/lib64/ld-linux-x86-64.so.2 (0x00007101e4e03000)
```

The transcript continues:

      only libm, libc and the loader

    === 4. usage ===
    Invalid number of arguments on command line
    Usage : mindtct [-b] [-m1] <finger_img_in> <oroot>
            -b  = contrast boost image
            -m1 = output "*.xyt" according to ANSI INCITS 378-2004

    === 5. TIFF to PNG carries the same pixels ===
      Pillow 12.3.0
      101_1  tif L (374, 388)  ->  png L  pixels identical: True
      101_2  tif L (374, 388)  ->  png L  pixels identical: True
      102_1  tif L (374, 388)  ->  png L  pixels identical: True

    === 6. the reference fixture ===
      101_1  minutiae 33  sha256 4aebdeeeab9fe3dd21f0bf2815df09f92da00c2c6ed6d906c0e2a61955b46437  MATCH
      101_2  minutiae 24  sha256 a9baeb93db9fe96b4a686032e5bb94fc044945081140b147471ee13015e611bc  MATCH
      102_1  minutiae 62  sha256 ac7a7d3e878848d491e82ca488f7c1dd4fe99742d8ecac46b150ab60ead2c16e  MATCH

    === 7. determinism: the same PNG twice, all eight outputs ===
      brw  identical
      dm   identical
      hcm  identical
      lcm  identical
      lfm  identical
      min  identical
      qm   identical
      xyt  identical

    all checks passed

    $ echo $?
    0

The fixture directory is mounted read-only and its path is replaced by
`<fixture>` above; nothing else in the transcript is altered. The images stay
outside the repository, as `docs/data.md` requires.

`MATCH` compares against `manifests/tools.json`, which the script reads: the
counts and digests printed here were computed in this container from these
images, and the manifest holds what they are expected to equal. The binary's
own digest is checked the same way, against the same manifest.

## Without the fixture directory

    $ make check-tools
    FVC_DB1_B is not set, so nothing was checked.

    It names the directory holding the FVC2002 Db1_b images, which the
    fixture in manifests/tools.json was recorded against:

      make check-tools FVC_DB1_B=/path/to/FVC2002/Dbs/Db1_b

    The directory is mounted read-only and no layout under LABDATA is
    assumed: that is not decided yet.
    make: *** [Makefile:78: check-tools] Error 1

## The command menu after this change

    $ make help
    Targets:
      help         List the targets
      image        Build the image and print its digest
      shell        Interactive session in the container, with the data mounted
      test         Run pytest in the container; needs no data
      check-tools  Verify the external tools against manifests/tools.json

    Variables:
      IMAGE        image name and tag (currently dactyloscopy:dev)
      LABDATA      root of the data mounted into the container; required by shell
      FVC_DB1_B    directory of FVC2002 Db1_b images; required by check-tools
