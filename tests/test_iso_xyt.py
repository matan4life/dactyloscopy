"""The ISO-to-.xyt conversion, held to the three facts it implements.

`iso_xyt` turns an ISO/IEC 19794-2:2005 template into the `.xyt` file
`bozorth3` reads. The frame flip is `INV-011` F-1's, from the source; the
half turn is `INV-012` F-2 and F-3's, measured; the 32-value grid is
`INV-002` F-8's, listed. Each is a constant a test can hold the code to.

Every template below is built by the test, byte by byte, from the layout
`INV-011` F-2 derived: no template of any finger is read.
"""

import struct

from implementation.library import iso_xyt as m


def template(minutiae, width=388, height=374):
    """An ISO record with the given (x, y, theta_byte, quality, type)."""
    head = bytearray(28)
    head[0:8] = b"FMR\x00 20\x00"
    struct.pack_into(">I", head, 8, 28 + 6 * len(minutiae))
    struct.pack_into(">HH", head, 14, width, height)
    struct.pack_into(">HH", head, 18, 197, 197)
    head[27] = len(minutiae)
    body = b"".join(struct.pack(">HHBB", (t << 14) | x, y, tb, q)
                    for x, y, tb, q, t in minutiae)
    return bytes(head) + body


def test_grid_is_the_set_inv_002_lists():
    assert list(m.MINDTCT_GRID) == [
        0, 11, 22, 34, 45, 56, 67, 79, 90, 101, 112, 124, 135, 146, 157, 169,
        180, 191, 202, 214, 225, 236, 247, 259, 270, 281, 292, 304, 315, 326,
        337, 349]


def test_read_ist_decodes_the_layout():
    t = template([(100, 50, 0, 80, 1), (16383, 16383, 255, 100, 2)])
    mins, w, h = m.read_ist(t)
    assert (w, h) == (388, 374)
    assert mins == [(100, 50, 0, 80, 1), (16383, 16383, 255, 100, 2)]


def test_frame_flip_is_height_minus_y():
    # INV-011 F-1: y_xyt = ih - y_image, so row 0 reports ih and row ih
    # would report 0; x is unchanged
    rows = m.to_xyt([(10, 0, 0, 5, 0), (20, 374, 0, 5, 0)], 374, turn_deg=0)
    assert [(r[0], r[1]) for r in rows] == [(10, 374), (20, 0)]


def test_angle_is_byte_times_360_over_256_plus_the_turn():
    # byte 64 is a quarter turn; with the measured half turn it reports 270
    rows = m.to_xyt([(0, 0, 64, 0, 0)], 1)
    assert rows[0][2] == 270
    rows = m.to_xyt([(0, 0, 64, 0, 0)], 1, turn_deg=0)
    assert rows[0][2] == 90


def test_angle_wraps_and_rounds_to_a_degree():
    # byte 255 is 358.59375; plus 180 is 538.59375, mod 360 is 178.59375,
    # which rounds to 179
    rows = m.to_xyt([(0, 0, 255, 0, 0)], 1)
    assert rows[0][2] == 179


def test_sense_minus_one_mirrors_the_angle():
    rows = m.to_xyt([(0, 0, 64, 0, 0)], 1, turn_deg=0, sense=-1)
    assert rows[0][2] == 270


def test_snap_to_the_grid_takes_the_nearest_and_ties_low():
    assert m.snap_to_mindtct_grid(46) == 45
    assert m.snap_to_mindtct_grid(5) == 0
    assert m.snap_to_mindtct_grid(355) == 0
    assert m.snap_to_mindtct_grid(6) == 11        # 6 is nearer 11 than 0
    rows = m.to_xyt([(0, 0, 64, 0, 0)], 1, quantise="mindtct32")
    assert rows[0][2] in m.MINDTCT_GRID


def test_quality_kept_or_zeroed():
    assert m.to_xyt([(0, 0, 0, 77, 0)], 1)[0][3] == 77
    assert m.to_xyt([(0, 0, 0, 77, 0)], 1, quality="zero")[0][3] == 0


def test_write_xyt_is_four_integers_per_line():
    assert m.write_xyt([(1, 2, 3, 4), (5, 6, 7, 8)]) == b"1 2 3 4\n5 6 7 8\n"


def test_convert_counts_what_it_wrote():
    t = template([(100, 50, 0, 80, 1), (30, 40, 128, 9, 0)])
    xyt, n = m.convert(t, 374)
    assert n == 2
    assert xyt == b"100 324 180 80\n30 334 0 9\n"
