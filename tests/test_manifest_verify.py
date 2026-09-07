"""What the manifest verifier classifies, checks, and refuses to read.

`REF-014` decision 1 puts a field's class in the verifier rather than in the
manifest, and names the cost: the classification lives in code, where this
repository normally refuses to put a decision. It is paid down three ways, and
this file is the third — a test that holds the verifier's classification of a
named set of fields, so that the rules cannot drift away from the refinement
without something failing.

The other two are that the rules are stated in `REF-014`, and that the verifier
prints the class it assigned to every field, which `scripts/verify_manifests.sh`
does.

Every manifest here is written by the test. `REF-013` section 6 keeps corpus
images, minutiae and templates out of this directory, and nothing below needs
one: the verifier's subject is a JSON file and the files it names.
"""

import json

import pytest

from implementation.library import manifest_verify as mv


def field(value, status="VERIFIED", **extra):
    out = {"value": value, "status": status}
    out.update(extra)
    return out


def write(tmp_path, name, obj):
    path = tmp_path / name
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    return str(path)


# --- the walk ------------------------------------------------------------

def test_the_walk_finds_a_field_and_does_not_descend_into_it():
    """A value-and-status object is a field, and its keys are not fields.

    The same walk `INV-009` and `INV-010` counted 63, 332 and 137 with. If it
    descended into a field, every `value` and `status` would be counted again
    and every number in those records would be wrong.
    """
    doc = {"a": field(1), "b": {"c": field("x"), "d": {"e": field([1, 2])}}}
    found = [p for p, _f, _parent in mv.walk(doc)]
    assert found == ["a", "b.c", "b.d.e"]


def test_the_parent_is_the_object_the_field_sits_in():
    """Not the outermost one.

    The first version of the walk overwrote the parent on the way back up, so
    a field's siblings were the manifest's top-level keys and no sibling rule
    could fire. The classification depends on siblings, so this is the test
    that keeps that bug out.
    """
    doc = {"outer": {"inner": {"path": field("/x"), "sha256": field("d")}}}
    parents = {p: parent for p, _f, parent in mv.walk(doc)}
    assert set(parents["outer.inner.path"]) == {"path", "sha256"}


# --- the classification ---------------------------------------------------

CLASSIFICATION = [
    # (path, the object it sits in, the class REF-014 puts it in)
    ("tools.mindtct.source.url",
     {"url": field("https://example.invalid/a.zip")}, mv.EXTERNAL),
    ("tools.mindtct.source.archive_sha256",
     {"archive_sha256": field("0" * 64)}, mv.EXTERNAL),
    ("tools.mindtct.build.extra_build_packages",
     {"extra_build_packages": field(["a", "b"])}, mv.DERIVABLE),
    ("tools.mindtct.build.clone_path",
     {"clone_path": field("/w/src")}, mv.DERIVABLE),
    ("tools.mindtct.binary.path",
     {"path": field("/usr/local/bin/mindtct")}, mv.RECOMPUTABLE),
    ("tools.mindtct.binary.sha256",
     {"path": field("/usr/local/bin/mindtct"), "sha256": field("0" * 64)},
     mv.RECOMPUTABLE),
    ("tools.mindtct.fixture.cases.101_1.minutiae",
     {"minutiae": field(33)}, mv.RECOMPUTABLE),
    ("tools.mindtct.invocation.command",
     {"command": field("mindtct <a> <b>")}, mv.DERIVABLE),
    ("x-manifest.asserted_numbers.angle_maximum",
     {"angle_maximum": field(255)}, mv.DERIVABLE),
]


@pytest.mark.parametrize("path,parent,expected", CLASSIFICATION)
def test_the_class_is_the_one_the_refinement_gives(path, parent, expected):
    """One row per rule of REF-014, so a rule cannot change unnoticed."""
    key = path.rsplit(".", 1)[1]
    assert mv.classify(path, parent[key], parent) == expected


def test_a_build_path_is_not_looked_for_in_the_runtime():
    """`build.clone_path` names a directory in a stage that is thrown away.

    The verifier reported it as a failure until this rule was added, which is
    the finding that produced the rule: a path is only a path the runtime can
    see when the block it sits in describes the runtime.
    """
    parent = {"clone_path": field("/w/src")}
    assert mv._check_spec("tools.x.build.clone_path",
                          parent["clone_path"], parent) is None


# --- what it checks -------------------------------------------------------

def test_a_digest_that_matches_passes_and_one_that_does_not_fails(tmp_path):
    target = tmp_path / "artefact.bin"
    target.write_bytes(b"some bytes")
    good = mv._sha256_file(str(target))

    for digest, expected_ok in ((good, True), ("0" * 64, False)):
        path = write(tmp_path, "m-%s.json" % expected_ok, {
            "tools": {"t": {"binary": {
                "path": field(str(target)),
                "sha256": field(digest),
            }}}})
        fields = {f.path: f for f in mv.verify(path, str(tmp_path))}
        checked = fields["tools.t.binary.sha256"]
        assert checked.checked is True
        assert checked.ok is expected_ok


def test_a_missing_file_fails_rather_than_being_skipped(tmp_path):
    path = write(tmp_path, "m.json", {
        "tools": {"t": {"binary": {
            "path": field(str(tmp_path / "absent.bin")),
            "sha256": field("0" * 64),
        }}}})
    fields = {f.path: f for f in mv.verify(path, str(tmp_path))}
    assert fields["tools.t.binary.path"].ok is False
    assert fields["tools.t.binary.sha256"].ok is False
    assert "no such file" in fields["tools.t.binary.sha256"].detail


def test_a_size_is_checked_against_the_file(tmp_path):
    """A field nothing read before this verifier existed.

    `INV-010` F-1 measured `binary.size_bytes` among the 290 fields nothing
    reads. It is checked now, and this is the test that says so.
    """
    target = tmp_path / "artefact.bin"
    target.write_bytes(b"0123456789")
    path = write(tmp_path, "m.json", {
        "tools": {"t": {"binary": {
            "path": field(str(target)),
            "size_bytes": field(10),
        }}}})
    fields = {f.path: f for f in mv.verify(path, str(tmp_path))}
    assert fields["tools.t.binary.size_bytes"].ok is True


def test_a_checksum_list_is_verified_against_the_files_it_names(tmp_path):
    """Both halves, and the second is the one that can be skipped silently.

    The verifier passed this field while opening no listed file at all, until
    the checksums rule was put before the generic digest rule: the field
    carries a digest of the list, and checking that alone is a check that
    never touches the data.
    """
    data = tmp_path / "corpus" / "subset"
    data.mkdir(parents=True)
    (data / "one.tif").write_bytes(b"one")
    (data / "two.tif").write_bytes(b"two")

    listing = tmp_path / "list.sha256"
    listing.write_text(
        "%s  one.tif\n%s  two.tif\n" % (mv._sha256_file(str(data / "one.tif")),
                                        mv._sha256_file(str(data / "two.tif"))),
        encoding="utf-8")

    doc = {"subsets": {"s": {
        "path": field("subset"),
        "checksums": field("list.sha256", sha256=mv._sha256_file(str(listing))),
    }}}
    path = write(tmp_path, "m.json", doc)

    fields = {f.path: f for f in mv.verify(
        path, str(tmp_path), corpus_root=str(tmp_path / "corpus"))}
    checksums = fields["subsets.s.checksums"]
    assert checksums.ok is True
    assert "2 files, 0 differing" in checksums.detail

    # One byte changed in one listed file, and the field must fail.
    (data / "two.tif").write_bytes(b"TWO")
    fields = {f.path: f for f in mv.verify(
        path, str(tmp_path), corpus_root=str(tmp_path / "corpus"))}
    assert fields["subsets.s.checksums"].ok is False
    assert "1 differing" in fields["subsets.s.checksums"].detail


def test_without_a_corpus_the_list_check_is_reported_as_not_run(tmp_path):
    """Skipped, and saying so. A skip reported as a pass is the failure
    `REF-014` decision 4 exists to remove."""
    listing = tmp_path / "list.sha256"
    listing.write_text("%s  one.tif\n" % ("0" * 64), encoding="utf-8")
    path = write(tmp_path, "m.json", {"subsets": {"s": {
        "path": field("subset"),
        "checksums": field("list.sha256",
                           sha256=mv._sha256_file(str(listing))),
    }}})
    fields = {f.path: f for f in mv.verify(path, str(tmp_path))}
    checksums = fields["subsets.s.checksums"]
    assert checksums.checked is False
    assert "no corpus mounted" in checksums.detail


# --- the reading rule -----------------------------------------------------

def test_a_conflict_field_is_not_read_and_is_a_failure(tmp_path):
    """`REF-014` decision 7, and `README.md` prohibition 3 before it.

    `INV-010` F-5 measured that the only thing reading manifests read no
    status at all, and that marking a field it depends on `CONFLICT` left it
    at exit 0. This is that measurement turned into a check.
    """
    target = tmp_path / "artefact.bin"
    target.write_bytes(b"some bytes")
    path = write(tmp_path, "m.json", {
        "tools": {"t": {"binary": {
            "path": field(str(target)),
            "sha256": field(mv._sha256_file(str(target)), status="CONFLICT"),
        }}}})
    fields = {f.path: f for f in mv.verify(path, str(tmp_path))}
    conflicted = fields["tools.t.binary.sha256"]

    assert conflicted.ok is False
    assert "CONFLICT" in conflicted.detail
    # The value would have matched. The point is that it was never used.
    assert "matches" not in conflicted.detail


@pytest.mark.parametrize("status", ["VERIFIED", "APPROX", "UNVERIFIED"])
def test_every_other_status_is_read(tmp_path, status):
    target = tmp_path / "artefact.bin"
    target.write_bytes(b"some bytes")
    path = write(tmp_path, "m-%s.json" % status, {
        "tools": {"t": {"binary": {
            "path": field(str(target)),
            "sha256": field(mv._sha256_file(str(target)), status=status),
        }}}})
    fields = {f.path: f for f in mv.verify(path, str(tmp_path))}
    assert fields["tools.t.binary.sha256"].ok is True


# --- the coverage report --------------------------------------------------

def test_the_summary_accounts_for_every_field(tmp_path):
    """Checked plus unchecked is the total, and the classes sum to it too.

    A coverage report that does not add up is a coverage report that can hide
    a field, which is what `REF-014` decision 3 is for.
    """
    target = tmp_path / "artefact.bin"
    target.write_bytes(b"x")
    path = write(tmp_path, "m.json", {
        "tools": {"t": {
            "source": {"url": field("https://example.invalid/a")},
            "build": {"setup": field("./setup.sh")},
            "binary": {"path": field(str(target)),
                       "sha256": field(mv._sha256_file(str(target)))},
        }}})
    fields = mv.verify(path, str(tmp_path))
    summary = mv.summarise(fields)

    assert summary["total"] == 4
    assert summary["checked"] + summary["unchecked"] == summary["total"]
    assert sum(e["total"] for e in summary["by_class"].values()) == summary["total"]
    assert summary["by_class"][mv.EXTERNAL]["total"] == 1
    assert summary["by_class"][mv.DERIVABLE]["total"] == 1
    assert summary["by_class"][mv.RECOMPUTABLE]["total"] == 2
    assert summary["failed"] == 0


def test_every_unchecked_field_says_why(tmp_path):
    """A field with no reason beside it is a field the report cannot explain."""
    path = write(tmp_path, "m.json", {
        "tools": {"t": {
            "source": {"release": field("5.0.0")},
            "build": {"make": field("make it")},
            "invocation": {"flags": field([])},
        }}})
    for f in mv.verify(path, str(tmp_path)):
        assert f.checked is False
        assert f.detail.startswith("not checked here: ")
