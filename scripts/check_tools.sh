#!/usr/bin/env bash
# Verify that the external tools in this image are the ones
# manifests/MAN-tools.v2.json describes. Run inside the container:
# "make check-tools FVC_DB1_B=<path>".
#
# This script produces no number that any result depends on. It compares what
# the image does against facts already frozen in the manifest, and exits
# non-zero when they disagree, which is what scripts/README.md admits here.
#
# It is driven by the manifest and not by a list written here: the tools, the
# files each one is made of, the digests, the linked libraries, the fixtures
# and the exit codes are all read from it. A tool added to the manifest is
# checked by this script without the script being edited.
#
# Usage: check_tools.sh <directory holding FVC2002 Db1_b TIFFs>

set -euo pipefail

FIXTURE_DIR="${1:-${FVC_DB1_B:-}}"
REPO="${REPO:-/work}"
MANIFEST="${MANIFEST:-$REPO/manifests/MAN-tools.v2.json}"
WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT

fail() { printf 'FAIL: %b\n' "$1" >&2; exit 1; }

# manifest_get <tool> <expression over the tool object, bound to t>
manifest_get() {
    python3 -c 'import json,sys; t=json.load(open(sys.argv[1]))["tools"][sys.argv[2]]; print(eval(sys.argv[3]))' \
        "$MANIFEST" "$1" "$2"
}

# digest_matches <path> <expected sha256>. Prints nothing; returns 0 or 1.
# Written as a function so that section 5 can exercise it against a file it
# has deliberately corrupted, rather than only against files that pass.
digest_matches() {
    [ "$(sha256sum "$1" | cut -d' ' -f1)" = "$2" ]
}

# blob_id <path>: the git blob id of a file, computed without git, which the
# runtime image does not carry. A blob is hashed as "blob <length>\0<content>".
blob_id() {
    python3 -c '
import hashlib, sys
data = open(sys.argv[1], "rb").read()
sys.stdout.write(hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest())
' "$1"
}

# composed_identity <tool>: recompute the scalar from the parts, in the order
# and the encoding REF-011 decision 5 fixes.
composed_identity() {
    python3 -c '
import hashlib, json, sys
parts = json.load(open(sys.argv[1]))["tools"][sys.argv[2]]["identity"]["parts"]
blob = "".join("%s=%s\n" % (k, v["value"]) for k, v in parts.items()).encode("ascii")
sys.stdout.write(hashlib.sha256(blob).hexdigest())
' "$MANIFEST" "$1"
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

# Every file in the image that the manifest names, as "tool label path sha256".
# A tool's binary block names one file per <label>_path / <label>_sha256 pair,
# or a bare path / sha256 pair for a tool made of a single file.
python3 - "$MANIFEST" > "$WORKDIR/files.txt" <<'PY'
import json, sys
tools = json.load(open(sys.argv[1]))["tools"]
for tool, t in tools.items():
    b = t["binary"]
    if "path" in b and "sha256" in b:
        print(tool, "binary", b["path"]["value"], b["sha256"]["value"])
        continue
    for key in b:
        if key.endswith("_path") and key[:-5] + "_sha256" in b:
            label = key[:-5]
            print(tool, label, b[key]["value"], b[label + "_sha256"]["value"])
PY

echo "=== 1. the runtime image carries the tools and not the toolchain ==="
for tool in gcc cc g++ make cmake git; do
    command -v "$tool" >/dev/null 2>&1 && fail "$tool is present in the runtime image and should not be"
    printf '  %-11s absent\n' "$tool"
done
[ -d /src ] && fail "the NBIS source tree is present in the runtime image"
echo "  /src        absent"
[ -d /w ] && fail "the FingerJetFXOSE build tree is present in the runtime image"
echo "  /w          absent"
for tool in $TOOLS; do
    command -v "$tool" >/dev/null || fail "$tool is not on PATH"
    printf '  %-11s %s\n' "$tool" "$(command -v "$tool")"
done

echo
echo "=== 2. every file the manifest names is the file it froze ==="
while read -r tool label path expected; do
    [ -e "$path" ] || fail "$tool: $label is missing from the image at $path"
    actual="$(sha256sum "$path" | cut -d' ' -f1)"
    if digest_matches "$path" "$expected"; then
        printf '  %-11s %-8s %s  matches\n' "$tool" "$label" "$actual"
    else
        printf '  %-11s %-8s %s\n' "$tool" "$label" "$actual"
        printf '  %-11s %-8s expected %s\n' "" "" "$expected"
        fail "$tool: the $label in this image is not the file the manifest records"
    fi
done < "$WORKDIR/files.txt"

echo
echo "=== 3. the source a caller was compiled from ==="
# Only a tool with a caller_source part has one. The check is on the working
# copy in the bind mount, which is a fact about this checkout and not about
# the repository: that is the point. A checkout that transformed the bytes
# would show up here as a mismatch rather than being accepted quietly.
found_source=0
SOURCE_PATH=""
for tool in $TOOLS; do
    has="$(manifest_get "$tool" '"caller_source" in t["identity"]["parts"]')"
    [ "$has" = "True" ] || continue
    found_source=1
    expected="$(manifest_get "$tool" 't["identity"]["parts"]["caller_source"]["value"]')"
    src="$REPO/implementation/tools/$tool.c"
    [ -r "$src" ] || fail "$tool: the caller's source is not readable at $src"
    SOURCE_PATH="$src"
    actual="$(blob_id "$src")"
    if [ "$actual" = "$expected" ]; then
        printf '  %-11s %s  matches\n' "$tool" "$actual"
    else
        printf '  %-11s %s\n' "$tool" "$actual"
        printf '  %-11s expected %s\n' "" "$expected"
        fail "$tool: the working copy of the caller's source is not the blob the manifest records"
    fi
done
[ "$found_source" -eq 1 ] || echo "  no tool in this manifest has a source part"

echo
echo "=== 4. each identity recomputed from its parts ==="
for tool in $TOOLS; do
    expected="$(manifest_get "$tool" 't["identity"]["composed_sha256"]["value"]')"
    actual="$(composed_identity "$tool")"
    labels="$(manifest_get "$tool" '",".join(t["identity"]["parts"])')"
    if [ "$actual" = "$expected" ]; then
        printf '  %-11s %s  from %s\n' "$tool" "$actual" "$labels"
    else
        printf '  %-11s %s\n' "$tool" "$actual"
        printf '  %-11s expected %s\n' "" "$expected"
        fail "$tool: the composed identity does not follow from the parts the manifest carries"
    fi
done

echo
echo "=== 5. the three checks above can fail ==="
# A check that has never been seen to fail is a check nobody has tested. Each
# comparison is run once more against something deliberately wrong, and this
# section fails if any of them still reports a match.
read -r probe_tool probe_label probe_path _ < "$WORKDIR/files.txt"
cp "$probe_path" "$WORKDIR/corrupt.bin"
printf 'x' >> "$WORKDIR/corrupt.bin"
if digest_matches "$WORKDIR/corrupt.bin" "$(sha256sum "$probe_path" | cut -d' ' -f1)"; then
    fail "the digest comparison accepted a file that differs from the original"
fi
printf '  digest      a modified copy of %s %s is rejected\n' "$probe_tool" "$probe_label"

if [ "$found_source" -eq 1 ]; then
    cp "$SOURCE_PATH" "$WORKDIR/corrupt.c"
    printf '\n' >> "$WORKDIR/corrupt.c"
    original="$(blob_id "$SOURCE_PATH")"
    if [ "$(blob_id "$WORKDIR/corrupt.c")" = "$original" ]; then
        fail "the blob id of a modified source equalled the blob id of the original"
    fi
    printf '  blob id     a source with one byte added hashes differently\n'
fi

# The composition, with one part changed and nothing else. If the scalar did
# not move, it would not be an identity of the parts.
python3 - "$MANIFEST" <<'PY'
import hashlib, json, sys
tools = json.load(open(sys.argv[1]))["tools"]
for tool, t in tools.items():
    parts = t["identity"]["parts"]
    label = list(parts)[0]
    values = {k: v["value"] for k, v in parts.items()}
    def scalar(v):
        return hashlib.sha256(
            "".join("%s=%s\n" % (k, v[k]) for k in parts).encode("ascii")
        ).hexdigest()
    before = scalar(values)
    if before != t["identity"]["composed_sha256"]["value"]:
        raise SystemExit("FAIL: %s: recomputation disagrees with the manifest" % tool)
    moved = dict(values)
    moved[label] = "0" * len(values[label])
    if scalar(moved) == before:
        raise SystemExit("FAIL: %s: changing %s left the identity unchanged" % (tool, label))
    print("  identity    %-11s moves when %s changes" % (tool, label))
PY

echo
echo "=== 6. what they link against ==="
# The expected list is the manifest's, per file, and the comparison is on the
# set of names rather than on a substring: an extra library is as much a
# difference as a missing one.
python3 - "$MANIFEST" "$WORKDIR/files.txt" <<'PY'
import json, subprocess, sys

manifest = json.load(open(sys.argv[1]))
rows = [line.split() for line in open(sys.argv[2]) if line.strip()]
for tool, label, path, _sha in rows:
    runtime = manifest["tools"][tool]["runtime"]
    for key in (label + "_shared_libraries", "shared_libraries"):
        if key in runtime:
            expected = list(runtime[key]["value"])
            break
    else:
        raise SystemExit("FAIL: %s: the manifest lists no libraries for %s" % (tool, label))
    out = subprocess.run(["ldd", path], capture_output=True, text=True).stdout
    seen = []
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("linux-vdso"):
            continue
        if "=>" in line:
            seen.append(line.split("=>")[0].strip())
        elif line.startswith("/"):
            seen.append(line.split()[0].rsplit("/", 1)[-1])
    print("  %-11s %-8s %s" % (tool, label, " ".join(seen)))
    if sorted(seen) != sorted(expected):
        raise SystemExit("FAIL: %s %s: linked libraries %s, manifest says %s"
                         % (tool, label, sorted(seen), sorted(expected)))
print("  every file links exactly what the manifest records")
PY

echo
echo "=== 7. usage ==="
for tool in $TOOLS; do
    echo "  $tool:"
    "$tool" 2>&1 | head -3 | sed 's/^/    /' || true
done

echo
echo "=== 8. TIFF to PNG and to PGM carries the same pixels ==="
python3 - "$FIXTURE_DIR" "$WORKDIR" "$MANIFEST" <<'PY'
import json, sys
import numpy as np
from PIL import Image

fixture_dir, workdir, manifest_path = sys.argv[1], sys.argv[2], sys.argv[3]
tools = json.load(open(manifest_path))["tools"]
names = sorted(tools["mindtct"]["fixture"]["cases"])
print("  Pillow", __import__("PIL").__version__)
for name in names:
    tif = Image.open(f"{fixture_dir}/{name}.tif")
    pixels = np.array(tif)
    for ext in ("png", "pgm"):
        out = f"{workdir}/{name}.{ext}"
        tif.convert("L").save(out)
        same = np.array_equal(pixels, np.array(Image.open(out)))
        print(f"  {name}  tif {tif.mode} {pixels.shape}  ->  {ext} L  "
              f"pixels identical: {same}")
        if not same:
            raise SystemExit(f"FAIL: {name}: the {ext} does not carry the TIFF's pixels")
PY

echo
echo "=== 9. the mindtct fixture ==="
# Both NBIS tools are called as the manifest records: neither is given -m1.
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
echo "=== 10. mindtct determinism: the same PNG twice, all eight outputs ==="
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
echo "=== 11. the bozorth3 fixture, the full pairwise matrix ==="
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
echo "=== 12. bozorth3 symmetry on the off-diagonal pairs ==="
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
echo "=== 13. bozorth3 determinism: one pair, five times ==="
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
echo "=== 14. the iso-extract fixture ==="
# The PGM the tool reads was written in section 8 and its pixels were compared
# against the TIFF there, so what is checked here is the tool and not the
# conversion. The invocation is the manifest's: two arguments, no flags, and
# the declared resolution compiled in rather than passed.
python3 - "$MANIFEST" > "$WORKDIR/iso.txt" <<'PY'
import json, sys
cases = json.load(open(sys.argv[1]))["tools"]["iso-extract"]["fixture"]["cases"]
for name in sorted(cases):
    c = cases[name]
    print(name, c["minutiae"]["value"], c["template_bytes"]["value"],
          c["template_sha256"]["value"])
PY
while read -r name expected_count expected_bytes expected_sha; do
    iso-extract "$WORKDIR/$name.pgm" "$WORKDIR/$name.ist"
    bytes="$(stat -c '%s' "$WORKDIR/$name.ist")"
    sha="$(sha256sum "$WORKDIR/$name.ist" | cut -d' ' -f1)"
    count="$(python3 -c 'import sys; sys.stdout.write(str(open(sys.argv[1],"rb").read()[27]))' "$WORKDIR/$name.ist")"
    if [ "$count" = "$expected_count" ] && [ "$bytes" = "$expected_bytes" ] \
       && [ "$sha" = "$expected_sha" ]; then
        printf '  %-6s minutiae %-3s bytes %-4s sha256 %s  MATCH\n' \
            "$name" "$count" "$bytes" "$sha"
    else
        printf '  %-6s minutiae %-3s bytes %-4s sha256 %s  MISMATCH\n' \
            "$name" "$count" "$bytes" "$sha"
        printf '  %-6s expected %-3s       %-4s        %s\n' \
            "" "$expected_count" "$expected_bytes" "$expected_sha"
        status=1
    fi
    # The relation the manifest records between the count and the length,
    # checked here so that the two ends of the record agree independently.
    [ "$bytes" -eq $((24 + 6 + 6 * count)) ] \
        || fail "$name: the template length does not follow from the minutia count"
done < "$WORKDIR/iso.txt"
[ "$status" -eq 0 ] || fail "the iso-extract fixture does not reproduce; this is a finding, not a nuisance"
echo "  every length obeys 24 + 6 + 6 * minutiae"

echo
echo "=== 15. iso-extract determinism: the same PGM three times ==="
read -r first_iso _ _ _ < "$WORKDIR/iso.txt"
for i in 1 2 3; do
    iso-extract "$WORKDIR/$first_iso.pgm" "$WORKDIR/again.$i.ist"
done
if cmp -s "$WORKDIR/again.1.ist" "$WORKDIR/again.2.ist" \
   && cmp -s "$WORKDIR/again.2.ist" "$WORKDIR/again.3.ist"; then
    echo "  $first_iso  three runs byte-identical"
else
    fail "iso-extract is not deterministic on this image"
fi

echo
echo "=== 16. iso-extract refuses malformed input with the codes it records ==="
# The failure path is exercised and not merely documented. Each case below is
# built here, run, and checked on three things: the exit code the manifest
# lists, that nothing was written to standard output, and that no output file
# was left behind for a later step to pick up.
python3 - "$WORKDIR" <<'PY'
import os
import sys

work = sys.argv[1]
good = open(os.path.join(work, sorted(
    n[:-4] for n in os.listdir(work) if n.endswith(".pgm"))[0] + ".pgm"), "rb").read()
cases = {
    "trailing": (good + b"\x00", 9),
    "short": (good[:-1], 8),
    "magic": (b"P2" + good[2:], 4),
    "maxval": (b"P5\n8 8\n127\n" + b"\x80" * 64, 6),
    "header": (b"P5\n8 8\n", 5),
    "dimension": (b"P5\n0 8\n255\n", 7),
}
with open(os.path.join(work, "malformed.txt"), "w") as index:
    for name, (content, code) in cases.items():
        with open(os.path.join(work, "bad_%s.pgm" % name), "wb") as fp:
            fp.write(content)
        index.write("%s %d\n" % (name, code))
PY
# The codes the manifest lists, as integers, so that a case whose code is not
# in the manifest is a failure of this check rather than a silent difference.
manifest_get iso-extract '" ".join(line.split(" - ")[0] for line in t["invocation"]["exit_codes"]["value"])' \
    > "$WORKDIR/codes.txt"
while read -r name expected_code; do
    grep -qw "$expected_code" "$WORKDIR/codes.txt" \
        || fail "exit code $expected_code is not one the manifest lists"
    out="$WORKDIR/bad_$name.ist"
    set +e
    stdout="$(iso-extract "$WORKDIR/bad_$name.pgm" "$out" 2>"$WORKDIR/bad_$name.err")"
    code=$?
    set -e
    if [ "$code" != "$expected_code" ]; then
        printf '  %-10s exit %-3s expected %s\n' "$name" "$code" "$expected_code"
        fail "iso-extract returned the wrong code for a $name input"
    fi
    [ -z "$stdout" ] || fail "iso-extract wrote to standard output on a $name input"
    [ -s "$WORKDIR/bad_$name.err" ] || fail "iso-extract failed silently on a $name input"
    [ ! -e "$out" ] || fail "iso-extract left an output file behind on a $name input"
    printf '  %-10s exit %-3s no output file, one line on stderr: %s\n' \
        "$name" "$code" "$(head -1 "$WORKDIR/bad_$name.err")"
done < "$WORKDIR/malformed.txt"

echo
echo "all checks passed"
