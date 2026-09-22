"""The corpus inventory, held on files the test writes.

`corpus_inventory` measures a subset directory and an index file. What
could be wrong: a duplicate missed or invented, a file size or image size
miscounted, a CRLF miscounted, a field miscounted. Every image below is a
2 by 2 greyscale square written by the test; no fingerprint is involved.
"""

import os

from PIL import Image

from implementation.library import corpus_inventory as m


def write_tif(path, pixels):
    Image.frombytes("L", (2, 2), bytes(pixels)).save(path)


def test_subset_counts_sizes_modes_and_duplicates(tmp_path):
    d = str(tmp_path)
    write_tif(os.path.join(d, "1_1.tif"), [0, 1, 2, 3])
    write_tif(os.path.join(d, "1_2.tif"), [0, 1, 2, 3])   # the same bytes
    write_tif(os.path.join(d, "2_1.tif"), [9, 9, 9, 9])
    with open(os.path.join(d, "notes.txt"), "w") as fp:
        fp.write("x")
    s = m._subset(d)
    assert (s["files"], s["tif"], s["other"]) == (4, 3, 1)
    assert s["other_names"] == ["notes.txt"]
    assert s["sizes"] == {"2x2": 3}
    assert s["modes"] == {"L": 3}
    assert s["duplicates_within"] == [["1_1.tif", "1_2.tif"]]
    assert s["distinct_digests"] == 2
    assert s["fingers"] == {"min": 1, "max": 2, "count": 2,
                            "contiguous": True}
    assert s["impressions"] == {"min": 1, "max": 2, "count": 2,
                                "contiguous": True}
    assert s["tags"]["259 Compression"] == {"1": 3}


def test_index_file_counts_lines_endings_and_fields(tmp_path):
    p = str(tmp_path / "index.MFR")
    with open(p, "wb") as fp:
        fp.write(b"1_1.tif 1_2.tif\r\n1_1.tif 2_1.tif\r\n3_1.tif 3_2.tif\n")
    f = m._index_file(p)
    assert (f["lines"], f["crlf_lines"]) == (3, 2)
    assert f["fields_per_line"] == {"2": 3}
    assert f["distinct_names"] == 5
    assert f["all_tif"] is True
    assert f["bytes"] == 17 + 17 + 16


def test_walk_lists_every_file_with_its_size(tmp_path):
    os.makedirs(str(tmp_path / "a" / "b"))
    with open(str(tmp_path / "a" / "b" / "f"), "wb") as fp:
        fp.write(b"12345")
    with open(str(tmp_path / "g"), "wb") as fp:
        fp.write(b"")
    # top-down: a directory's own files come before its subdirectories'
    assert m._walk(str(tmp_path)) == [("g", 0), ("a/b/f", 5)]
