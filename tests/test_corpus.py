"""A subset from its manifest id, held to the checksum list it carries.

`corpus.subset()` turns `<competition>/<subset>` into a directory through a
manifest and `corpus.verify_images()` holds that directory to the per-file
checksum list the manifest names by digest. What could be wrong: a list
that is not the one the manifest digests; a file that is not the one the
list digests; a file the list names that is not there; a file that is there
and not in the list; a field whose status forbids reading it.

Every manifest, list and file below is written by the test into a temporary
directory. The files are a few bytes of text with an image's extension: no
image, no minutia, nothing from a corpus.
"""

import hashlib
import json
import os

import pytest

from implementation.library import corpus

SUBSET = "fvc2002/DB1_T"


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def fake_tree(root, files, list_digest=None, root_status="VERIFIED"):
    """A repository root with one manifest and one list, and a corpus root
    with one subset holding `files`, a name-to-bytes dict."""
    repo = os.path.join(root, "repo")
    data = os.path.join(root, "corpus", "Dbs", "Db1_t")
    os.makedirs(os.path.join(repo, "manifests", "checksums", "fvc2002"))
    os.makedirs(data)
    lines = []
    for name in sorted(files):
        with open(os.path.join(data, name), "wb") as fp:
            fp.write(files[name])
        lines.append("%s  %s\n" % (_sha(files[name]), name))
    list_rel = "manifests/checksums/fvc2002/DB1_T.sha256"
    with open(os.path.join(repo, list_rel), "w", encoding="ascii") as fp:
        fp.write("".join(lines))
    with open(os.path.join(repo, list_rel), "rb") as fp:
        digest = _sha(fp.read())
    manifest = {
        "distribution": {"root": {"value": os.path.join(root, "corpus"),
                                  "status": root_status}},
        "subsets": {SUBSET: {
            "path": {"value": "Dbs/Db1_t", "status": "VERIFIED"},
            "checksums": {"value": list_rel, "status": "VERIFIED",
                          "sha256": list_digest or digest}}},
    }
    with open(os.path.join(repo, "manifests", "MAN-fvc2002.v1.json"), "w",
              encoding="utf-8") as fp:
        json.dump(manifest, fp)
    return repo, data


FILES = {"a_1.tif": b"first", "a_2.tif": b"second", "b_1.tif": b"third"}


def test_subset_resolves_the_directory_and_the_list(tmp_path):
    repo, data = fake_tree(str(tmp_path), FILES)
    sub = corpus.subset(repo, SUBSET)
    assert sub["subset_id"] == SUBSET
    assert os.path.samefile(sub["subset_dir"], data)
    assert sub["checksum_list"]["entries"] == 3
    assert sub["checksum_list"]["expected"]["a_2.tif"] == _sha(b"second")
    assert sub["corpus_manifest"]["path"] == "manifests/MAN-fvc2002.v1.json"


def test_subset_refuses_a_list_the_manifest_does_not_digest(tmp_path):
    repo, _ = fake_tree(str(tmp_path), FILES, list_digest="0" * 64)
    with pytest.raises(ValueError, match="manifest says"):
        corpus.subset(repo, SUBSET)


def test_subset_refuses_a_conflict_field(tmp_path):
    repo, _ = fake_tree(str(tmp_path), FILES, root_status="CONFLICT")
    with pytest.raises(ValueError, match="CONFLICT"):
        corpus.subset(repo, SUBSET)


def test_verify_images_passes_the_directory_the_list_describes(tmp_path):
    repo, _ = fake_tree(str(tmp_path), FILES)
    sub = corpus.subset(repo, SUBSET)
    assert corpus.verify_images(sub) == 3
    assert corpus.verify_images(sub, ["b_1.tif"]) == 1


def test_verify_images_catches_a_changed_byte(tmp_path):
    repo, data = fake_tree(str(tmp_path), FILES)
    with open(os.path.join(data, "a_2.tif"), "wb") as fp:
        fp.write(b"secona")
    sub = corpus.subset(repo, SUBSET)
    with pytest.raises(ValueError, match="a_2.tif: sha256"):
        corpus.verify_images(sub)


def test_verify_images_catches_a_missing_file(tmp_path):
    repo, data = fake_tree(str(tmp_path), FILES)
    os.remove(os.path.join(data, "b_1.tif"))
    sub = corpus.subset(repo, SUBSET)
    with pytest.raises(ValueError, match="not in the directory"):
        corpus.verify_images(sub)


def test_verify_images_catches_a_file_the_list_does_not_name(tmp_path):
    repo, data = fake_tree(str(tmp_path), FILES)
    with open(os.path.join(data, "c_1.tif"), "wb") as fp:
        fp.write(b"stray")
    sub = corpus.subset(repo, SUBSET)
    with pytest.raises(ValueError, match="absent from the checksum list"):
        corpus.verify_images(sub)
    with pytest.raises(ValueError, match="absent from the checksum list"):
        corpus.verify_images(sub, ["c_1.tif"])
