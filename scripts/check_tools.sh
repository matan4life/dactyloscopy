#!/usr/bin/env bash
# Verify that the external tools in this image are the ones manifests/MAN-tools.v1.json
# describes. Run inside the container: "make check-tools FVC_DB1_B=<path>".
#
# This script produces no number that any result depends on. It compares what
# the image does against facts already frozen in the manifest, and exits
# non-zero when they disagree, which is what scripts/README.md admits here.
#
# Usage: check_tools.sh <directory holding FVC2002 Db1_b TIFFs>

set -euo pipefail

FIXTURE_DIR="${1:-${FVC_DB1_B:-}}"
MANIFEST="${MANIFEST:-/work/manifests/MAN-tools.v1.json}"
WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT

fail() { printf 'FAIL: %b\n' "$1" >&2; exit 1; }

if [ -z "$FIXTURE_DIR" ]; then
    cat >&2 <<'EOF'
No fixture directory given, so nothing was checked.

Pass the directory holding the FVC2002 Db1_b images, either as the first
argument or in FVC_DB1_B:

  make check-tools FVC_DB1_B=/path/to/FVC2002/Dbs/Db1_b

The images are read-only and never leave the container. No layout under
LABDATA is assumed: that is not decided yet.
EOF
    exit 2
fi
[ -d "$FIXTURE_DIR" ] || fail "not a directory: $FIXTURE_DIR"
[ -r "$MANIFEST" ] || fail "manifest not readable: $MANIFEST"

echo "=== 1. the runtime image carries the tool and not the toolchain ==="
for tool in gcc cc g++ make cmake git bozorth3; do
    if command -v "$tool" >/dev/null 2>&1; then
        fail "$tool is present in the runtime image and should not be"
    fi
    printf '  %-9s absent\n' "$tool"
done
[ -d /src ] && fail "the NBIS source tree is present in the runtime image"
echo "  /src      absent"
command -v mindtct >/dev/null || fail "mindtct is not on PATH"
printf '  %-9s %s\n' "mindtct" "$(command -v mindtct)"

echo
echo "=== 2. the binary is the one the manifest froze ==="
expected_sha="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["tools"]["mindtct"]["binary"]["sha256"]["value"])' "$MANIFEST")"
actual_sha="$(sha256sum /usr/local/bin/mindtct | cut -d' ' -f1)"
printf '  sha256 %s\n' "$actual_sha"
if [ "$actual_sha" != "$expected_sha" ]; then
    printf '  expected %s\n' "$expected_sha"
    fail "the binary in this image is not the one manifests/MAN-tools.v1.json records"
fi
echo "  matches the manifest"

echo
echo "=== 3. what mindtct links against ==="
ldd /usr/local/bin/mindtct
ldd /usr/local/bin/mindtct | grep -qE '=> /lib/x86_64-linux-gnu/libm\.so' \
    || fail "libm not among the linked libraries"
ldd /usr/local/bin/mindtct | grep -qE '=> /lib/x86_64-linux-gnu/libc\.so' \
    || fail "libc not among the linked libraries"
unexpected="$(ldd /usr/local/bin/mindtct | grep '=>' | grep -vE 'lib(m|c)\.so' || true)"
[ -z "$unexpected" ] || fail "unexpected shared libraries:\n$unexpected"
echo "  only libm, libc and the loader"

echo
echo "=== 4. usage ==="
mindtct 2>&1 | head -4 || true

echo
echo "=== 5. TIFF to PNG carries the same pixels ==="
python3 - "$FIXTURE_DIR" "$WORKDIR" "$MANIFEST" <<'PY'
import json, sys
import numpy as np
from PIL import Image

fixture_dir, workdir, manifest_path = sys.argv[1], sys.argv[2], sys.argv[3]
names = sorted(json.load(open(manifest_path))["tools"]["mindtct"]["fixture"]["cases"])
print("  Pillow", __import__("PIL").__version__)
for name in names:
    tif = Image.open(f"{fixture_dir}/{name}.tif")
    png_path = f"{workdir}/{name}.png"
    tif.convert("L").save(png_path)
    same = np.array_equal(np.array(tif), np.array(Image.open(png_path)))
    print(f"  {name}  tif {tif.mode} {np.array(tif).shape}  ->  png L  pixels identical: {same}")
    if not same:
        raise SystemExit(f"FAIL: {name}: the PNG does not carry the TIFF's pixels")
PY

echo
echo "=== 6. the reference fixture ==="
# The invocation is the one the manifest records: no -m1. What -m1 would change
# is an open question, not a detail; quality/REF-005 says why.
python3 - "$MANIFEST" > "$WORKDIR/cases.txt" <<'PY'
import json, sys
cases = json.load(open(sys.argv[1]))["tools"]["mindtct"]["fixture"]["cases"]
for name in sorted(cases):
    c = cases[name]
    print(name, c["minutiae"]["value"], c["xyt_sha256"]["value"])
PY
status=0
while read -r name expected_count expected_sha; do
    mindtct "$WORKDIR/$name.png" "$WORKDIR/$name"
    count="$(wc -l < "$WORKDIR/$name.xyt" | tr -d ' ')"
    sha="$(sha256sum "$WORKDIR/$name.xyt" | cut -d' ' -f1)"
    if [ "$count" = "$expected_count" ] && [ "$sha" = "$expected_sha" ]; then
        printf '  %-6s minutiae %-3s sha256 %s  MATCH\n' "$name" "$count" "$sha"
    else
        printf '  %-6s minutiae %-3s sha256 %s  MISMATCH\n' "$name" "$count" "$sha"
        printf '  %-6s expected %-3s        %s\n' "" "$expected_count" "$expected_sha"
        status=1
    fi
done < "$WORKDIR/cases.txt"
[ "$status" -eq 0 ] || fail "the fixture does not reproduce; this is a finding, not a nuisance"

echo
echo "=== 7. determinism: the same PNG twice, all eight outputs ==="
first="$(head -1 "$WORKDIR/cases.txt" | cut -d' ' -f1)"
mindtct "$WORKDIR/$first.png" "$WORKDIR/again"
for ext in brw dm hcm lcm lfm min qm xyt; do
    if cmp -s "$WORKDIR/$first.$ext" "$WORKDIR/again.$ext"; then
        printf '  %-4s identical\n' "$ext"
    else
        printf '  %-4s DIFFERS\n' "$ext"
        status=1
    fi
done
[ "$status" -eq 0 ] || fail "mindtct is not deterministic on this image"

echo
echo "all checks passed"
