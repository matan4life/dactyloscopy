"""Verify a manifest against the things it names, and report what it did not.

The mechanism `REF-014` decides. It walks a manifest for fields carrying a
value and a status, derives each field's class from the shape it sits in rather
than from an annotation the manifest carries (`REF-014` decision 1), checks the
classes it can check, and reports every field it could not check and why
(`REF-014` decisions 2 and 3).

The three classes are `REF-014`'s:

  recomputable   the value can be produced again by running something
  derivable      the value asserts something about a file this repository
                 controls, and the field does not say which file
  external       the value is a claim about the outside world, bound to the
                 pin in the same block

Nothing here shells out, and nothing here is invoked as a command:
`REF-013` decision 3 puts code that runs in this process in this directory and
keeps command invocation out of it. `scripts/verify_manifests.sh` is the
command, and a run imports `verify` directly.

The reading rule of `REF-014` decision 7 is implemented here and nowhere else:
a field whose status is `CONFLICT` is never read. The verifier records that it
refused, and refusing counts as a failure, because a manifest that carries a
`CONFLICT` field a mechanism needs is a manifest that cannot be used.
"""

import hashlib
import json
import os

# REF-014 decision 7. VERIFIED and APPROX may be read; UNVERIFIED may be read
# but not used as a number a result depends on, which is a rule for a run
# rather than for this verifier; CONFLICT may not be read at all.
UNREADABLE = ("CONFLICT",)

RECOMPUTABLE = "recomputable"
DERIVABLE = "derivable"
EXTERNAL = "external"


class Field:
    """One field of a manifest, with what the verifier made of it."""

    def __init__(self, path, value, status, cls, parent):
        self.path = path
        self.value = value
        self.status = status
        self.cls = cls
        self.parent = parent
        self.checked = False
        self.ok = None
        self.detail = ""

    def check(self, ok, detail):
        self.checked = True
        self.ok = ok
        self.detail = detail
        return self

    def skip(self, detail):
        self.checked = False
        self.detail = detail
        return self


def walk(node, path=""):
    """Yield (path, field object, parent object) for every value+status field.

    The same walk `INV-009` and `INV-010` count with: an object carrying both a
    value and a status is a field, and the walk does not descend into one.
    """
    if isinstance(node, dict):
        if "value" in node and "status" in node:
            yield path, node, None
            return
        for key, child in node.items():
            child_path = "%s.%s" % (path, key) if path else key
            for found, obj, parent in walk(child, child_path):
                # The parent is the object the field sits in, so it is filled
                # at the level that found the field and never overwritten on
                # the way back up.
                yield found, obj, node if parent is None else parent
    elif isinstance(node, list):
        for index, child in enumerate(node):
            for found, obj, parent in walk(child, "%s[%d]" % (path, index)):
                yield found, obj, node if parent is None else parent


def _blocks(path):
    return path.split(".")


def classify(path, field, parent):
    """Derive the class from the shape, never from an annotation.

    The rules are structural and there are four of them, in order. They are
    stated in REF-014 and repeated here because this function is what makes
    them operative; a divergence between the two shows up in the report, which
    prints the class of every field.
    """
    parts = _blocks(path)

    # 1. Anything inside a `source` block is a claim about an artefact this
    #    repository did not make, bound to the pin in the same block.
    if "source" in parts:
        return EXTERNAL

    # 1b. Anything inside a `build` block describes the recipe: a package
    #     list, a patch, a command, a path inside a builder stage that the
    #     runtime cannot see. REF-014 places these in class two by name.
    if "build" in parts:
        return DERIVABLE

    # 2. A field the verifier has a shape for is recomputable.
    if _check_spec(path, field, parent) is not None:
        return RECOMPUTABLE

    # 3. A fixture value is recomputable, by running the tool that produced it.
    #    This verifier does not run tools; the report says who does.
    if "fixture" in parts or "cases" in parts or "pairs" in parts:
        return RECOMPUTABLE

    # 4. Everything else asserts something about a file this repository
    #    controls, and does not say which.
    return DERIVABLE


def _sibling(parent, key):
    node = parent.get(key) if isinstance(parent, dict) else None
    if isinstance(node, dict) and "value" in node:
        return node
    return None


def _check_spec(path, field, parent):
    """What the verifier can measure for this field, or None.

    Four shapes, each read off the field's own object or its siblings:

      digest-of-named-file   the field's object carries a `sha256` beside a
                             value that is a repository-relative path
      digest-of-sibling      `<label>_sha256` with a `<label>_path` beside it,
                             or `sha256` with `path`
      size-of-sibling        `<label>_size_bytes` or `size_bytes`, likewise
      path-exists            a `<label>_path` or `path` value
      checksum-list          a `checksums` value beside a `path`, verified
                             against a corpus when one is mounted
    """
    parts = _blocks(path)
    key = parts[-1]

    # A `source` or `build` block is not measured from the runtime image: the
    # first names an artefact outside this repository and the second names the
    # recipe and the builder stage, whose paths do not exist here. Returning
    # nothing keeps classify and this function from disagreeing.
    if "source" in parts or "build" in parts:
        return None

    # A checksums field before the generic digest rule, because it carries a
    # sha256 of its own and would otherwise be satisfied by checking the list
    # against that digest while never opening a single file the list names.
    if key == "checksums" and _sibling(parent, "path"):
        return ("checksum-list", field["value"], _sibling(parent, "path")["value"])

    if "sha256" in field and isinstance(field.get("value"), str):
        return ("digest-of-named-file", field["value"], field["sha256"])

    for suffix, kind in (("sha256", "digest-of-sibling"),
                         ("size_bytes", "size-of-sibling")):
        if key == suffix or key.endswith("_" + suffix):
            label = key[:-len(suffix)].rstrip("_")
            path_key = (label + "_path") if label else "path"
            sibling = _sibling(parent, path_key)
            if sibling:
                return (kind, sibling["value"], field["value"])

    if key == "path" or key.endswith("_path"):
        # A `path` beside a `checksums` names a directory in the corpus, not
        # in this repository or in the image. The shape says which it is.
        if _sibling(parent, "checksums"):
            return ("corpus-path-exists", field["value"], None)
        return ("path-exists", field["value"], None)

    return None


def _sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _verify_checksum_list(list_path, subset_path, corpus_root):
    """Every digest in one list against the corpus. Returns (ok, detail)."""
    if corpus_root is None:
        return None, "no corpus mounted"
    directory = os.path.join(corpus_root, subset_path)
    if not os.path.isdir(directory):
        return False, "no such directory: %s" % directory
    checked = failed = 0
    missing = []
    with open(list_path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            expected, name = line.split(None, 1)
            target = os.path.join(directory, name.strip())
            if not _inside(directory, target):
                return False, "a listed name escapes the subset: %s" % name.strip()
            if not os.path.exists(target):
                missing.append(name.strip())
                continue
            checked += 1
            if _sha256_file(target) != expected:
                failed += 1
    if missing:
        return False, "%d listed files missing, first %s" % (len(missing),
                                                             missing[0])
    return failed == 0, "%d files, %d differing" % (checked, failed)


def verify(manifest_path, repo_root, image_root="/", corpus_root=None):
    """Verify one manifest. Returns the list of Field objects it walked.

    `image_root` is where a value that is an absolute path is resolved, so
    that a manifest describing the runtime image is checked against the image
    the verifier is running in. `corpus_root` is where a subset path is
    resolved, and None means no corpus is mounted.
    """
    with open(manifest_path, encoding="utf-8") as handle:
        manifest = json.load(handle)

    # Where the data lives is the manifest's to say, not this function's. A
    # manifest that declares a distribution root declares it in terms of
    # $LABDATA, which docs/data.md makes the only way a dataset is addressed,
    # so expanding the environment is reading the manifest rather than
    # assuming a layout.
    declared = manifest.get("distribution", {}).get("root", {}).get("value")
    if corpus_root is None and isinstance(declared, str):
        expanded = os.path.expandvars(declared)
        if "$" not in expanded and os.path.isdir(expanded):
            corpus_root = expanded

    fields = []
    for path, node, parent in walk(manifest):
        status = node.get("status")
        cls = classify(path, node, parent)
        field = Field(path, node.get("value"), status, cls, parent)
        fields.append(field)

        if status in UNREADABLE:
            field.check(False, "status is %s: REF-014 decision 7 forbids "
                               "reading it" % status)
            continue

        spec = _check_spec(path, node, parent)
        if cls == EXTERNAL:
            field.skip("not checked here: a claim about the outside world, "
                       "bound to this block's pin")
            continue
        if spec is None:
            if cls == RECOMPUTABLE:
                field.skip("not checked here: needs the tool run; "
                           "scripts/check_tools.sh covers the tool fixtures")
            else:
                field.skip("not checked here: no field says which file to "
                           "derive it from")
            continue

        kind, first, second = spec
        if kind in ("digest-of-sibling", "size-of-sibling", "path-exists"):
            target, root = _resolve(first, repo_root, image_root)
            if not _inside(root, target):
                field.check(False, "%s: resolves outside %s" % (first, root))
                continue
        if kind == "digest-of-named-file":
            target = os.path.join(repo_root, first)
            if not _inside(repo_root, target):
                field.check(False, "%s: resolves outside the repository"
                            % first)
            elif not os.path.exists(target):
                field.check(False, "no such file: %s" % first)
            else:
                got = _sha256_file(target)
                field.check(got == second,
                            "%s: %s" % (first, "matches" if got == second
                                        else "%s, recorded %s" % (got, second)))
        elif kind == "digest-of-sibling":
            if not os.path.exists(target):
                field.check(False, "no such file: %s" % first)
            else:
                got = _sha256_file(target)
                field.check(got == second,
                            "%s: %s" % (first, "matches" if got == second
                                        else "%s, recorded %s" % (got, second)))
        elif kind == "size-of-sibling":
            if not os.path.exists(target):
                field.check(False, "no such file: %s" % first)
            else:
                got = os.path.getsize(target)
                field.check(got == second,
                            "%s: %s" % (first, "matches" if got == second
                                        else "%d, recorded %s" % (got, second)))
        elif kind == "corpus-path-exists":
            if corpus_root is None:
                field.skip("not checked here: no corpus mounted")
            else:
                target = os.path.join(corpus_root, first)
                if not _inside(corpus_root, target):
                    field.check(False, "%s: resolves outside the corpus root"
                                % first)
                else:
                    field.check(os.path.isdir(target),
                                "%s: %s" % (first,
                                            "present" if os.path.isdir(target)
                                            else "absent"))
        elif kind == "path-exists":
            field.check(os.path.exists(target),
                        "%s: %s" % (first, "present" if os.path.exists(target)
                                    else "absent"))
        elif kind == "checksum-list":
            list_path = os.path.join(repo_root, first)
            if not _inside(repo_root, list_path):
                field.check(False, "%s: resolves outside the repository"
                            % first)
            elif not os.path.exists(list_path):
                field.check(False, "no such list: %s" % first)
            else:
                # Two checks on one field, and both have to hold: the list is
                # the list the manifest recorded, and every file it names is
                # the file it says. The first alone would pass while nothing
                # in the corpus had been opened.
                recorded = node.get("sha256")
                got = _sha256_file(list_path)
                if recorded is not None and got != recorded:
                    field.check(False, "%s: %s, recorded %s"
                                % (first, got, recorded))
                    continue
                ok, detail = _verify_checksum_list(list_path, second,
                                                   corpus_root)
                if ok is None:
                    field.skip("not checked here: %s; the list itself matches "
                               "the digest recorded beside it" % detail)
                else:
                    field.check(ok, "%s: list digest matches, %s"
                                % (first, detail))
    return fields


def _resolve(value, repo_root, image_root):
    """Where a path value points, and the root it must stay under.

    Returns (path, root). A relative value is resolved against the repository
    and an absolute one against the image, and either way the caller checks
    containment: a value like `../../etc/passwd` resolves to a real file and
    would otherwise be reported present, which is the shape of failure this
    whole mechanism exists to remove.
    """
    if os.path.isabs(value):
        return os.path.join(image_root, value.lstrip("/")), image_root
    return os.path.join(repo_root, value), repo_root


def _inside(root, path):
    root = os.path.realpath(root)
    target = os.path.realpath(path)
    if root == os.sep:            # everything is under the filesystem root
        return True
    return target == root or target.startswith(root.rstrip(os.sep) + os.sep)


def summarise(fields):
    """Counts the report prints: by class, and checked against not."""
    summary = {"total": len(fields), "checked": 0, "failed": 0,
               "unchecked": 0, "by_class": {}}
    for field in fields:
        entry = summary["by_class"].setdefault(
            field.cls, {"total": 0, "checked": 0, "failed": 0})
        entry["total"] += 1
        if field.checked:
            summary["checked"] += 1
            entry["checked"] += 1
            if not field.ok:
                summary["failed"] += 1
                entry["failed"] += 1
        else:
            summary["unchecked"] += 1
    return summary
