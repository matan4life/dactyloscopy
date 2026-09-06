# The base is pinned by digest, not by tag. A tag moves: python:3.12-slim-bookworm
# points at a different image every time the upstream is rebuilt, and a run
# recorded against a tag cannot be reproduced. The digest is resolved with
# "docker buildx imagetools inspect"; the command and its output are recorded in
# docs/container.md.
FROM python:3.12-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254

# Exact versions, and only these two. Every package in the image is a field of
# the environment a run record has to name, so the set is kept small and fixed
# rather than resolved at build time.
RUN pip install --no-cache-dir \
        numpy==2.5.2 \
        pytest==9.1.1

WORKDIR /work

# /work is a bind mount, not a copy. The image pins the environment, git pins
# the code, and a run record names both; copying the repository in would merge
# the two and make an edit require a rebuild.
ENV PYTHONPATH=/work

# No .pyc files: they would be written into the bind mount, which is the
# author's working tree.
ENV PYTHONDONTWRITEBYTECODE=1
