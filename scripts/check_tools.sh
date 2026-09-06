#!/usr/bin/env bash
# Verify that the external tools in this image are the ones
# manifests/MAN-tools.v1.json describes. Run inside the container:
# "make check-tools FVC_DB1_B=<path>".
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

# manifest_get <tool> <expression over the tool object, bound to t>
manifest_get() {
    python3 -c 'import json,sys; t=json.load(open(sys.argv[1]))["tools"][sys.argv[2]]; print(eval(sys.argv[3]))' \
        "$MANIFEST" "$1" "$2"
}

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

TOOLS="$(python3 -c 'import json,sys; print(" ".join(json.load(open(sys.argv[1]))["tools"]))' "$MANIFEST")"
status=0

echo "=== 1. the runtime image carries the tools and not the toolchain ==="
for tool in gcc cc g++ make cmake git; do
    command -v "$tool" >/dev/null 2>&1 && fail "$tool is present in the runtime image and should not be"
    printf '  %-9s absent\n' "$tool"
done
[ -d /src ] && fail "the NBIS source tree is present in the runtime image"
echo "  /src      absent"
for tool in $TOOLS; do
    command -v "$tool" >/dev/null || fail "$tool is not on PATH"
    printf '  %-9s %s\n' "$tool" "$(command -v "$tool")"
done

echo
echo "=== 2. each binary is the one the manifest froze ==="
for tool in $TOOLS; do
    expected="$(manifest_get "$tool" 't["binary"]["sha256"]["value"]')"
    path="$(manifest_get "$tool" 't["binary"]["path"]["value"]')"
    actual="$(sha256sum "$path" | cut -d' ' -f1)"
    if [ "$actual" != "$expected" ]; then
        printf '  %-9s %s\n' "$tool" "$actual"
        printf '  %-9s expected %s\n' "" "$expected"
        fail "$tool in this image is not the binary the manifest records"
    fi
    printf '  %-9s %s  matches\n' "$tool" "$actual"
done

echo
echo "=== 3. what they link against ==="
for tool in $TOOLS; do
    path="$(manifest_get "$tool" 't["binary"]["path"]["value"]')"
    echo "  $tool:"
    ldd "$path" | sed 's/^/  /'
    ldd "$path" | grep -qE '=> /lib/x86_64-linux-gnu/libm\.so' || fail "$tool: libm is not linked"
    ldd "$path" | grep -qE '=> /lib/x86_64-linux-gnu/libc\.so' || fail "$tool: libc is not linked"
    unexpected="$(ldd "$path" | grep '=>' | grep -vE 'lib(m|c)\.so' || true)"
    [ -z "$unexpected" ] || fail "$tool: unexpected shared libraries: $unexpected"
    echo "    only libm, libc and the loader"
done

echo
echo "=== 4. usage ==="
for tool in $TOOLS; do
    echo "  $tool:"
    "$tool" 2>&1 | head -3 | sed 's/^/    /' || true
done

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
echo "=== 6. the mindtct fixture ==="
# Both tools are called as the manifest records: neither is given -m1.
python3 - "$MANIFEST" > "$WORKDIR/cases.txt" <<'PY'
import json, sys
cases = json.load(open(sys.argv[1]))["tools"]["mindtct"]["fixture"]["cases"]
for name in sorted(cases):
    c = cases[name]
    print(name, c["minutiae"]["value"], c["xyt_sha256"]["value"])
PY
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
[ "$status" -eq 0 ] || fail "the mindtct fixture does not reproduce; this is a finding, not a nuisance"

echo
echo "=== 7. mindtct determinism: the same PNG twice, all eight outputs ==="
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
echo "=== 8. the bozorth3 fixture, the full pairwise matrix ==="
python3 - "$MANIFEST" > "$WORKDIR/pairs.txt" <<'PY'
import json, sys
pairs = json.load(open(sys.argv[1]))["tools"]["bozorth3"]["fixture"]["pairs"]
for key in sorted(pairs):
    a, b = key.split()
    print(a, b, pairs[key]["value"])
PY
while read -r a b expected; do
    got="$(bozorth3 "$WORKDIR/$a.xyt" "$WORKDIR/$b.xyt")"
    if [ "$got" = "$expected" ]; then
        printf '  %-6s %-6s -> %5s  MATCH\n' "$a" "$b" "$got"
    else
        printf '  %-6s %-6s -> %5s  MISMATCH, expected %s\n' "$a" "$b" "$got" "$expected"
        status=1
    fi
done < "$WORKDIR/pairs.txt"
[ "$status" -eq 0 ] || fail "the bozorth3 fixture does not reproduce; this is a finding, not a nuisance"

echo
echo "=== 9. bozorth3 symmetry on the off-diagonal pairs ==="
while read -r a b _; do
    [ "$a" = "$b" ] && continue
    ab="$(bozorth3 "$WORKDIR/$a.xyt" "$WORKDIR/$b.xyt")"
    ba="$(bozorth3 "$WORKDIR/$b.xyt" "$WORKDIR/$a.xyt")"
    if [ "$ab" = "$ba" ]; then
        printf '  %-6s %-6s %5s == %-5s symmetric\n' "$a" "$b" "$ab" "$ba"
    else
        printf '  %-6s %-6s %5s != %-5s ASYMMETRIC\n' "$a" "$b" "$ab" "$ba"
        status=1
    fi
done < "$WORKDIR/pairs.txt"
[ "$status" -eq 0 ] || fail "bozorth3 is not symmetric on this fixture"

echo
echo "=== 10. bozorth3 determinism: one pair, five times ==="
read -r a b _ < "$WORKDIR/pairs.txt"
scores=""
for _ in 1 2 3 4 5; do
    scores="$scores $(bozorth3 "$WORKDIR/$a.xyt" "$WORKDIR/$b.xyt")"
done
printf '  %s %s ->%s\n' "$a" "$b" "$scores"
distinct="$(printf '%s\n' $scores | sort -u | wc -l | tr -d ' ')"
[ "$distinct" -eq 1 ] || fail "bozorth3 returned more than one value for the same pair"
echo "  one distinct value across five runs"

echo
echo "all checks passed"
