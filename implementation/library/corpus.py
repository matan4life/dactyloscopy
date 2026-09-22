"""Where a subset is and what it holds, from its manifest id and nothing else.

A dataset is addressed by its manifest id, `<competition>/<subset>`, never by
a path written in code. This module turns the id into a directory through
`MAN-fvc2002.v1` - `distribution.root` names `$LABDATA` and
`subsets.<id>.path` the directory under it - and into the per-file checksum
list the manifest carries beside it, checked against the digest the manifest
records for the list before a line of it is used. `verify_images()` then
holds a directory to that list, so that an instrument given the directory
can be shown to have read the subset and not a directory that merely has
its name.

Two callers: `matching.resolve()`, which adds the comparison lists and the
tools to what this returns; and the command form of every instrument that
takes a subset, which verifies the images before the instrument reads one.
`REF-014` decision 7 is implemented in `read_field()`: a field whose status
is CONFLICT is never read.
"""
import hashlib
import json
import os

UNREADABLE = ("CONFLICT",)


def read_field(manifest, *path):
    """Read a value-and-status field, refusing a CONFLICT.

    `REF-014` decision 7: a field whose status is CONFLICT is never read. A
    run that needs such a field cannot proceed, and says so, rather than
    proceeding on a default."""
    node = manifest
    for key in path:
        node = node[key]
    status = node.get("status")
    if status in UNREADABLE:
        raise ValueError("%s has status %s and may not be read"
                         % ("/".join(path), status))
    return node["value"], status


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fp:
        for chunk in iter(lambda: fp.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def subset(repo_root, subset_id):
    """The subset's directory and checksum list, from `MAN-fvc2002.v1`.

    Returns the manifest by path and digest and as loaded, the id, the
    corpus root the manifest resolves to, the subset directory under it, and
    the checksum list by path, digest, entry count and the expected digest
    of every file it names. The list is checked against the digest the
    manifest records for it here; the files are checked against the list by
    `verify_images()`."""
    mpath = os.path.join(repo_root, "manifests", "MAN-fvc2002.v1.json")
    with open(mpath, encoding="utf-8") as fp:
        corpus = json.load(fp)
    root_decl, _ = read_field(corpus, "distribution", "root")
    root = os.path.expandvars(root_decl)
    if "$" in root:
        raise ValueError("the corpus root %r did not resolve; LABDATA is not "
                         "set" % root_decl)
    sub_rel, _ = read_field(corpus, "subsets", subset_id, "path")
    subset_dir = os.path.join(root, sub_rel)
    # The set's identity is the digest of its per-file checksum list, which
    # the manifest carries beside the list's path.
    list_rel, _ = read_field(corpus, "subsets", subset_id, "checksums")
    list_path = os.path.join(repo_root, list_rel)
    list_declared = corpus["subsets"][subset_id]["checksums"]["sha256"]
    list_got = sha256_of(list_path)
    if list_got != list_declared:
        raise ValueError("%s: sha256 %s, manifest says %s"
                         % (list_rel, list_got, list_declared))
    expected = {}
    with open(list_path, encoding="ascii") as fp:
        for line in fp:
            digest, name = line.split()
            expected[name] = digest
    return {
        "corpus_manifest": {"path": "manifests/MAN-fvc2002.v1.json",
                            "sha256": sha256_of(mpath)},
        "manifest": corpus,
        "subset_id": subset_id, "corpus_root": root, "subset_dir": subset_dir,
        "checksum_list": {"path": list_rel, "sha256": list_got,
                          "entries": len(expected), "expected": expected},
    }


def verify_images(sub, names=None):
    """Every named image in the subset directory digests to what the
    checksum list says, or the caller stops.

    `names` is the list of files an instrument will read; with `names` left
    out, every `.tif` in the directory is checked and the directory must
    hold exactly the files the list names, no more and no fewer, which is
    what an instrument that lists the directory itself will read. Returns
    the number of files verified."""
    expected = sub["checksum_list"]["expected"]
    if names is None:
        names = sorted(f for f in os.listdir(sub["subset_dir"])
                       if f.lower().endswith(".tif"))
        missing = sorted(set(expected) - set(names))
        if missing:
            raise ValueError("%s: %d files the checksum list names are not "
                             "in the directory, the first %s"
                             % (sub["subset_id"], len(missing), missing[0]))
    for name in names:
        if name not in expected:
            raise ValueError("%s is absent from the checksum list %s"
                             % (name, sub["checksum_list"]["path"]))
        got = sha256_of(os.path.join(sub["subset_dir"], name))
        if got != expected[name]:
            raise ValueError("%s: sha256 %s, the checksum list says %s"
                             % (name, got, expected[name]))
    return len(names)
