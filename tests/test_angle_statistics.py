"""The statistics over `INV-012`'s rows, held to their conventions.

`angle_conventions_statistics` turns the 648 rows of the angle sweep into
the circular means, counts and tables the record carries. What could be
wrong: the circular mean, the wrap of a residual, the nearest point of the
32-value grid, the grid itself, and the count a threshold produces. Every
row below is written by the test; the module reads no image and no file.
"""

import math

from implementation.library import angle_conventions_statistics as m
from implementation.library import iso_xyt


def row(truth, m_theta, m_dir, i_theta, family="ending", phi=0, j=0,
        m_type="RIG", i_type=1):
    return {"family": family, "phi": phi, "j": j, "truth": truth,
            "n_xyt": 9, "n_ist": 9, "iso_rc": 0, "m_dist": 1.0,
            "m_theta": m_theta, "m_qual": 50, "m_dir": m_dir,
            "m_type": m_type, "i_dist": 1.0, "i_theta": i_theta,
            "i_type": i_type}


def test_grid_is_the_set_inv_002_lists():
    assert sorted(m.XYT_GRID) == list(iso_xyt.MINDTCT_GRID)


def test_circular_mean_crosses_zero():
    mean, R = m.circular_mean([350.0, 10.0])
    assert abs(mean) < 1e-9 or abs(mean - 360.0) < 1e-9
    assert abs(R - math.cos(math.radians(10.0))) < 1e-12


def test_circular_mean_of_opposites_has_no_concentration():
    _, R = m.circular_mean([0.0, 180.0])
    assert R < 1e-12


def test_wrap_lands_in_the_half_open_interval():
    assert m.wrap(180.0) == 180.0
    assert m.wrap(180.5) == -179.5
    assert m.wrap(-181.0) == 179.0
    assert m.wrap_byte(255 - 0) == -1
    assert m.wrap_byte(128) == 128


def test_nearest_grid_is_circular():
    assert m.nearest_grid(355.0) == 0
    assert m.nearest_grid(5.0) == 0
    assert m.nearest_grid(6.0) == 11


def test_within_half_step_is_inclusive_and_counts_the_boundary():
    # residual after the half turn: exactly 5.625 (in), 5.626 (out)
    rows = [row(truth=174.375, m_theta=0, m_dir=8, i_theta=0),
            row(truth=174.374, m_theta=0, m_dir=8, i_theta=0, j=1)]
    x = m.statistics(rows)["xyt"]
    assert x["within_half_step"] == 1
    assert x["n"] == 2


def test_between_tools_is_iso_minus_native():
    rows = [row(truth=0.0, m_theta=180, m_dir=8, i_theta=0),
            row(truth=90.0, m_theta=270, m_dir=0, i_theta=64, phi=90)]
    b = m.statistics(rows)["between_tools"]
    assert abs(b["circular_mean"] - 180.0) < 1e-9
    assert abs(b["R"] - 1.0) < 1e-12
