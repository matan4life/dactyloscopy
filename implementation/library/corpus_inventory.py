"""The corpus, measured: the instrument of `quality/INV-005` F-1 to F-3,
F-6, F-7, F-9 and F-10.

One pass over every file under the corpus root `MAN-fvc2002.v1` resolves:
the tree's file and byte totals; per subset the file count, the extensions
present, the distinct image sizes, modes and file sizes; every digest,
grouped to find byte-identical files within a subset and across subsets;
the index files read as bytes, their line endings and fields counted; the
five TIFF tags of F-9 read per file; and the finger and impression ranges
the file names carry. Nothing sampled, nothing read from a manifest as a
fact: the manifest gives the root, the subset paths and the index-file
names, and everything else is measured.

What leaves this process is counts, sizes, digests and file names - the
per-file digests are the lists `manifests/checksums/` already publishes -
and never a pixel. Imported, never invoked as a command; the command form
is `scripts/measure_corpus.py`, which prints `report()` and writes the
inventory as derived data.
"""
import hashlib
import os
from collections import Counter, defaultdict

from PIL import Image

from implementation.library import corpus

TAGS = ((282, "XResolution"), (283, "YResolution"), (296, "ResolutionUnit"),
        (259, "Compression"), (262, "PhotometricInterpretation"))


def _walk(root):
    """Every regular file under root: (relative path, bytes)."""
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for name in sorted(filenames):
            path = os.path.join(dirpath, name)
            out.append((os.path.relpath(path, root).replace(os.sep, "/"),
                        os.path.getsize(path)))
    return out


def _subset(path):
    """One subset directory: counts, sizes, modes, digests, tags."""
    names = sorted(os.listdir(path))
    tifs = [n for n in names if n.lower().endswith(".tif")]
    others = [n for n in names if n not in tifs]
    sizes, modes, lengths, tags = Counter(), Counter(), Counter(), {}
    for n, _ in TAGS:
        tags[n] = Counter()
    digests = {}
    for n in tifs:
        full = os.path.join(path, n)
        with open(full, "rb") as fp:
            data = fp.read()
        digests[n] = hashlib.sha256(data).hexdigest()
        lengths[len(data)] += 1
        im = Image.open(full)
        sizes[im.size] += 1
        modes[im.mode] += 1
        for tag, _ in TAGS:
            v = im.tag_v2.get(tag)
            tags[tag][repr(v) if v is not None else "absent"] += 1
    by_digest = defaultdict(list)
    for n, d in digests.items():
        by_digest[d].append(n)
    dup = sorted(sorted(v) for v in by_digest.values() if len(v) > 1)
    fingers = Counter()
    impressions = Counter()
    for n in tifs:
        stem = n[:-4]
        f, i = stem.split("_")
        fingers[int(f)] += 1
        impressions[int(i)] += 1
    fs, ims = sorted(fingers), sorted(impressions)
    return {
        "files": len(names), "tif": len(tifs), "other": len(others),
        "other_names": others,
        "sizes": {"%dx%d" % k: v for k, v in sorted(sizes.items())},
        "modes": dict(sorted(modes.items())),
        "file_sizes": {str(k): v for k, v in sorted(lengths.items())},
        "tags": {"%d %s" % (tag, name): dict(sorted(tags[tag].items()))
                 for tag, name in TAGS},
        "duplicates_within": dup,
        "distinct_digests": len(by_digest),
        "fingers": {"min": fs[0], "max": fs[-1], "count": len(fs),
                    "contiguous": fs == list(range(fs[0], fs[-1] + 1))},
        "impressions": {"min": ims[0], "max": ims[-1], "count": len(ims),
                        "contiguous": ims == list(range(ims[0],
                                                        ims[-1] + 1))},
        "fingers_times_impressions": len(fs) * len(ims),
        "digests": digests,
    }


def _index_file(path):
    """An index file as bytes: size, lines, endings, fields, names."""
    with open(path, "rb") as fp:
        data = fp.read()
    lines = data.split(b"\n")
    if lines and lines[-1] == b"":
        lines.pop()
    crlf = sum(1 for l in lines if l.endswith(b"\r"))
    fields = Counter(len(l.rstrip(b"\r").split()) for l in lines)
    names = sorted({f.decode("ascii") for l in lines
                    for f in l.rstrip(b"\r").split()})
    return {
        "bytes": len(data), "lines": len(lines), "crlf_lines": crlf,
        "fields_per_line": {str(k): v for k, v in sorted(fields.items())},
        "distinct_names": len(names),
        "all_tif": all(n.lower().endswith(".tif") for n in names),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def measure(repo_root):
    """The whole inventory, from the manifest's root and subset paths."""
    ids = []
    root = None
    for subset_id in corpus.subset_ids(repo_root):
        sub = corpus.subset(repo_root, subset_id)
        root = sub["corpus_root"]
        ids.append((subset_id, sub["subset_dir"],
                    sub["checksum_list"]["expected"]))
    files = _walk(root)
    top = sorted({p.split("/")[0] for p, _ in files})
    subsets = {}
    for subset_id, sub_dir, expected in ids:
        s = _subset(sub_dir)
        # the digests measured here against the list the manifest names
        s["matches_checksum_list"] = (s["digests"] == expected)
        subsets[subset_id] = s
    image_bytes = sum(int(k) * v for s in subsets.values()
                      for k, v in s["file_sizes"].items())
    across = defaultdict(list)
    for subset_id, s in subsets.items():
        for n, d in s["digests"].items():
            across[d].append((subset_id, n))
    cross_pairs = sorted(
        (a, b) for group in across.values() if len(group) > 1
        for i, a in enumerate(group) for b in group[i + 1:] if a[0] != b[0])
    for s in subsets.values():
        del s["digests"]
    dbs = os.path.join(root, "Dbs")
    index = {n: _index_file(os.path.join(dbs, n))
             for n in sorted(os.listdir(dbs))
             if os.path.isfile(os.path.join(dbs, n))}
    # F-8: the one duplicated pair, in which index file
    lines_with = {}
    dups = [pair for s in subsets.values() for pair in s["duplicates_within"]]
    for n in index:
        with open(os.path.join(dbs, n), "rb") as fp:
            text = fp.read().decode("ascii")
        lines_with[n] = {" ".join(p): text.count(" ".join(p) + "\r\n")
                         for p in dups}
    return {
        "root_files": len(files), "root_bytes": sum(b for _, b in files),
        "image_bytes": image_bytes, "top_level": top,
        "not_images": sorted((p, b) for p, b in files
                             if not p.lower().endswith(".tif")),
        "subsets": subsets,
        "distinct_digests": len(across),
        "duplicate_pairs_across_subsets": cross_pairs,
        "index_files": index,
        "duplicate_pairs_in_index_files": lines_with,
    }


def report(inv):
    """Print the inventory as the tables `INV-005` carries."""
    print("== F-1, the tree: %d files, %d bytes, of which %d bytes are the "
          "images" % (inv["root_files"], inv["root_bytes"],
                      inv["image_bytes"]))
    print("   top-level: %s" % ", ".join(inv["top_level"]))
    for p, b in inv["not_images"]:
        print("   %-40s %d bytes" % (p, b))
    print()
    print("== F-2, counts")
    print("| subset | files | `.tif` | anything else |")
    print("| --- | --- | --- | --- |")
    for sid, s in inv["subsets"].items():
        print("| %s | %d | %d | %d |" % (sid.split("/")[1], s["files"],
                                          s["tif"], s["other"]))
    print("%d images; %d distinct digests over all subsets; %d byte-identical "
          "pairs spanning two subsets"
          % (sum(s["tif"] for s in inv["subsets"].values()),
             inv["distinct_digests"],
             len(inv["duplicate_pairs_across_subsets"])))
    print()
    print("== F-3, dimensions on every image")
    print("| subset | distinct sizes | mode | file sizes | matches the "
          "checksum list |")
    print("| --- | --- | --- | --- | --- |")
    for sid, s in inv["subsets"].items():
        print("| %s | %s | %s | %s | %s |" % (
            sid.split("/")[1],
            ", ".join("%s (%d)" % kv for kv in s["sizes"].items()),
            ", ".join("%s (%d)" % kv for kv in s["modes"].items()),
            ", ".join("%s bytes (%d)" % kv for kv in s["file_sizes"].items()),
            "yes" if s["matches_checksum_list"] else "NO"))
    print()
    print("== F-6, byte-identical files")
    for sid, s in inv["subsets"].items():
        if s["duplicates_within"]:
            print("   %s: %s" % (sid, "; ".join(
                " and ".join(g) for g in s["duplicates_within"])))
        else:
            print("   %s: no two files share a digest" % sid)
    print("   across subsets: %d pairs"
          % len(inv["duplicate_pairs_across_subsets"]))
    print()
    print("== F-7, the index files")
    print("| file | bytes | lines | CRLF lines | fields per line | distinct "
          "names | all `.tif` |")
    print("| --- | --- | --- | --- | --- | --- | --- |")
    for n, f in inv["index_files"].items():
        print("| `%s` | %d | %d | %d | %s | %d | %s |" % (
            n, f["bytes"], f["lines"], f["crlf_lines"],
            ", ".join("%s (%d)" % kv for kv in f["fields_per_line"].items()),
            f["distinct_names"], "yes" if f["all_tif"] else "no"))
    print()
    print("== F-8, the duplicated pair in the index files")
    for n, d in inv["duplicate_pairs_in_index_files"].items():
        for pair, count in d.items():
            print("   %-12s %s: %d line(s)" % (n, pair, count))
    print()
    print("== F-9, TIFF tags, per subset")
    for sid, s in inv["subsets"].items():
        print("   %s: %s" % (sid, "; ".join(
            "%s %s" % (tag, ", ".join("%s in %d" % kv for kv in v.items()))
            for tag, v in s["tags"].items())))
    print()
    print("== F-10, fingers and impressions from the file names")
    print("| subset | fingers | contiguous | impressions | names | fingers x "
          "impressions |")
    print("| --- | --- | --- | --- | --- | --- |")
    for sid, s in inv["subsets"].items():
        f, i = s["fingers"], s["impressions"]
        print("| %s | %d to %d | %s | %d to %d | %d | %d |" % (
            sid.split("/")[1], f["min"], f["max"],
            "yes" if f["contiguous"] and i["contiguous"] else "no",
            i["min"], i["max"], s["tif"], s["fingers_times_impressions"]))
