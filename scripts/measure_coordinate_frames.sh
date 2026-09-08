#!/usr/bin/env bash
# Measure the coordinate frame each extractor reports in, and print the
# lines quality/INV-011 was written from. Run inside the container, with the
# three fixture images mounted read-only.
#
#   docker run --rm -v "<repo>:/work" -v "<fixture>:/fixture:ro" \n#     -w /work dactyloscopy:dev bash scripts/measure_coordinate_frames.sh /fixture
#
# This script produces no number of its own. It is the command form of
# implementation/library/coordinate_frames.py and
# implementation/library/coordinate_frames_fixture.py,
# which is where the mechanism lives; it imports and calls and does nothing
# else, which is what implementation/library/README.md and quality/REF-013
# decision 3 require.
#
# Usage: measure_coordinate_frames.sh <fixture directory>

set -euo pipefail

REPO="${REPO:-/work}"
FIXTURE="${1:?a fixture directory is required}"

[ -d "$FIXTURE" ] || { echo "FAIL: no such directory: $FIXTURE" >&2; exit 1; }

python3 - "$REPO" "$FIXTURE" <<'PY'
import json
import sys

sys.path.insert(0, sys.argv[1])
from implementation.library.coordinate_frames import measure as origin_test
from implementation.library.coordinate_frames_fixture import measure as fixture

origin_test()
print()
fixture(sys.argv[2], sys.argv[1])
PY
