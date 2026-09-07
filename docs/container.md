# The container and the command menu

The image pins the environment, git pins the code, and a run record names
both. This page says how to use them and records what was checked; the
`Makefile` is the only place a `docker run` invocation is written, so a
command that produced a number can be read back from the tree rather than
from a shell history.

Every command below was run on 2026-09-06 and the output shown is what it
printed, except where a section says it was re-captured on 2026-09-07 — the
day the image gained a third tool and the day the manifest verifier was added.
A section that was re-captured says so and says what it used to claim.

## The machine it was checked on

    $ docker --version
    Docker version 29.4.3, build 055a478
    $ docker info --format '{{.ServerVersion}} {{.OSType}}'
    29.4.3 linux
    $ make --version
    GNU Make 4.4.1
    Built for Windows32
    $ uname -a
    MINGW64_NT-10.0-26200 <host> 3.6.10-710e5275.x86_64 2026-07-28 09:32 UTC x86_64 Msys

One field of that last line is not as printed: the hostname was replaced with
`<host>`, because it names the author's machine and a reader can check nothing
against it. The kernel string, the architecture and the `Msys` marker are the
evidence and stand unaltered.

The shell is Git Bash on Windows, and Docker Desktop runs a Linux engine.
`make` is a native Windows build on `PATH` in both Git Bash and PowerShell.

## The base image is pinned by digest

A tag moves. `python:3.12-slim-bookworm` points at a different image every
time the upstream is rebuilt, so a run recorded against the tag cannot be
reproduced. The digest was resolved before the `FROM` line was written:

    $ docker buildx imagetools inspect python:3.12-slim-bookworm
    Name:      docker.io/library/python:3.12-slim-bookworm
    MediaType: application/vnd.oci.image.index.v1+json
    Digest:    sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254

    Manifests:
      Name:        docker.io/library/python:3.12-slim-bookworm@sha256:9c47360a2a0355e2da18516d0b1c2126ec22c195d2185e97347c9d98398c5bef
      MediaType:   application/vnd.oci.image.manifest.v1+json
      Platform:    linux/amd64

The same value read back from the pulled image:

    $ docker inspect --format '{{index .RepoDigests 0}}' python:3.12-slim-bookworm
    python@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254

The first digest is the multi-platform index and is what `FROM` carries; the
one under `Manifests` belongs to the `linux/amd64` image inside it.

## Windows paths: the hazard, and what handles it

Under Git Bash and MSYS a POSIX path in a `docker run -v` argument is
rewritten before docker sees it. The rewriting is silent in the sense that
docker is never told, and the mount lands somewhere else entirely:

    $ docker run --rm -v "$(pwd):/work" alpine:3 ls /work
    ls: C:/Program Files/Git/work: No such file or directory

`/work` became `C:/Program Files/Git/work`. With the rewriting turned off the
same command mounts what it says:

    $ MSYS_NO_PATHCONV=1 docker run --rm -v "$(pwd):/work" alpine:3 ls /work
    CHANGELOG.md
    CITATION.cff
    CLAUDE.local.md
    CODE_OF_CONDUCT.md
    CONTRIBUTING.md
    LICENSE

The `Makefile` therefore prefixes every docker invocation with
`MSYS_NO_PATHCONV=1`, takes the repository path from `pwd -W` and converts
`LABDATA` with `cygpath -m`, so that docker receives Windows paths and the
shell leaves them alone. The mounts are verified from inside the container
further down, not assumed.

## The six checks

### 1. `make image` builds and prints a digest

    $ make image
    ...
    image id:
    sha256:fb6119434a4877aa18fe231b6449f5777de16c3e7b2e8b89d619f00265e6c7fa
    base, as pinned in the Dockerfile:
    FROM python:3.12-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254

The build log is cut at the `...`. The identifier printed is the image ID,
which is the digest of the image configuration. A locally built image has no
repository digest until it is pushed, so the ID is what identifies this build,
and the `FROM` line is printed beside it because that is the pin a run record
has to carry.

### 2 and 3. The session, its mounts, and the read-only raw directory

`make shell` opens an interactive session, which cannot be captured here, so
the command it runs was taken from `make -n` and then run with the same
mounts, reading its commands from a script instead of a terminal.

    $ LABDATA=/d/tmp/labdata-demo make -n shell | tail -1
    MSYS_NO_PATHCONV=1 docker run --rm -it -v "D:/My PET Projects/dactyloscopy:/work" -v "D:/tmp/labdata-demo/raw:/data/raw:ro" -v "D:/tmp/labdata-demo/derived:/data/derived" -w /work "dactyloscopy:dev" bash

Inside that container:

    ls /work | head -6
    CHANGELOG.md
    CITATION.cff
    CLAUDE.local.md
    CODE_OF_CONDUCT.md
    CONTRIBUTING.md
    Dockerfile

    python -c "import numpy; print('numpy', numpy.__version__)"
    numpy 2.5.2

    python -c "import sys; print('python', sys.version.split()[0])"
    python 3.12.14

    touch /data/raw/x
    touch: cannot touch '/data/raw/x': Read-only file system
    touch /data/raw/x -> exit 1

    touch /data/derived/probe
    touch /data/derived/probe -> exit 0

`ls /work` shows the repository, so the bind mount survived the path
handling; `numpy` reports the version the Dockerfile pins; `/data/raw` refuses
a write and `/data/derived` accepts one, which is the asymmetry the data
policy depends on.

`LABDATA` pointed at an empty directory holding only `raw/` and `derived/`.
The check is of the mounts, not of any data: no dataset was mounted, and
`docs/data.md` says why none may live in the repository.

### 4. `make test` runs pytest, and a failing test fails the target

Re-captured on 2026-09-07. Until then there was no suite, and this section
recorded that the target translated pytest's exit 5 — it collected nothing —
into success. There is a suite now, so that translation was removed: collecting
nothing would mean the mount or the suite is wrong, and `make test` reports it.

    $ make test
    MSYS_NO_PATHCONV=1 docker run --rm -v "D:/My PET Projects/dactyloscopy:/work" -w /work "dactyloscopy:dev" python -m pytest
    ============================= test session starts ==============================
    platform linux -- Python 3.12.14, pytest-9.1.1, pluggy-1.6.0
    rootdir: /work
    collected 47 items

    tests/test_iso_extract.py ......................                         [ 46%]
    tests/test_manifest_verify.py .........................                  [100%]

    ============================== 47 passed in 0.60s ==============================
    $ echo $?
    0

A failing test fails the target:

    $ printf 'def test_that_fails():\n    assert 1 == 2\n' > tests/test_sanity_probe.py
    $ make test
    FAILED tests/test_sanity_probe.py::test_that_fails - assert 1 == 2
    ========================= 1 failed, 47 passed in 0.63s =========================
    make: *** [Makefile:72: test] Error 1

The probe file was deleted afterwards and is not in the tree.

`test` mounts the repository and nothing else, so it needs no `LABDATA`. The
counts were re-captured on 2026-09-07: the suite was 22 tests over one file
until `tests/test_manifest_verify.py` took it to 47. What the suite checks is
`docs/tools.md`'s and `docs/manifests.md`'s subject, not this page's.

### 5. `make shell` without `LABDATA` starts nothing

    $ unset LABDATA; make shell
    LABDATA is not set, so nothing was started.

    It names the root the data is mounted from, and the container
    expects this layout under it:

      $LABDATA/raw        mounted read-only at /data/raw
      $LABDATA/derived    mounted read-write at /data/derived

    Set it for one command:

      LABDATA=/path/to/labdata make shell

    or export it in the shell. See docs/data.md for what may live there.
    make: *** [Makefile:45: shell] Error 1

The target fails, which is intended: a missing mount is not something to
proceed past. What it does not do is let docker produce the error, which
would name a path rather than the variable that has to be set.

### 6. `make help` lists every target

Re-captured twice on 2026-09-07: once because `check-tools` and `FVC_DB1_B`
existed and were not in the listing, and again when `verify` was added.

    $ make
    Targets:
      help         List the targets
      image        Build the image and print its digest
      shell        Interactive session in the container, with the data mounted
      test         Run pytest in the container; needs no data
      verify       Verify every manifest against what it names; LABDATA adds the corpus
      check-tools  Verify the tools in the image against manifests/MAN-tools.v2.json

    Variables:
      IMAGE        image name and tag (currently dactyloscopy:dev)
      LABDATA      root of the data mounted into the container; required by shell,
                   and by verify if the corpus is to be checked
      FVC_DB1_B    directory of FVC2002 Db1_b images; required by check-tools

What `verify` prints is `docs/manifests.md`'s subject.

`help` is the default goal, so `make` with no argument prints the menu rather
than doing something. The listing is generated from the `##` comments in the
`Makefile`, so a target added without one is invisible here; that is the only
way this section can go stale again.

## What the image does not contain

No C toolchain, no build tree, and no copy of the repository. `docs/tools.md`
records the search that establishes it and what it does find: three tools and
one shared library.

Corrected on 2026-09-07. This paragraph used to say "no matcher", which
stopped being true when `bozorth3` was added, and that the Dockerfile has no
`COPY` and `.dockerignore` excludes the whole build context, which stopped
being true when the caller's source had to reach the daemon to be compiled.

What holds now: `.dockerignore` excludes the whole context and then admits one
file back by name, `implementation/tools/iso-extract.c`, and `docs/tools.md`
records the measurement of what the daemon actually receives — that one file
and nothing else. Everything else, this repository's own code included,
reaches the container through the `/work` bind mount, which is why an edit
takes effect without a rebuild.
