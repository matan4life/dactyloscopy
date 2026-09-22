"""The two registered metrics, held to their definition texts.

`MAN-metrics.v1` registers `eer@1` and `auc@1` by text, and `REF-016`
decision 6 makes the text the definition a reader checks a number against.
These tests hold the implementation to the text on inputs small enough to
work by hand, and hold the implementation to the registration: if the text
in the manifest and the text in `matching.py` ever differ, the last test here
fails before a run would refuse.

Every score vector below is stated in the test. Nothing reads a corpus, a
template or a record; `INV-017` is where the metrics meet real scores, and
its exact rationals are quoted here as the values a reader can recompute from
its observation.
"""

from fractions import Fraction
import json
import os

import pytest

from implementation.library import matching as m

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ---------------------------------------------------------------- eer@1
def test_eer_separable_scores_give_zero():
    # every genuine above every impostor: the threshold just above the
    # impostors accepts all genuine, rejects all impostors
    eer, at = m.eer_at_1([10, 11, 12], [1, 2, 3])
    assert eer == 0.0
    assert at["threshold"] == 10 and at["fmr"] == 0.0 and at["fnmr"] == 0.0


def test_eer_reversed_scores_give_one():
    # genuine all below impostor: the gap |FMR - FNMR| is zero only where
    # both are 1, at t=10 (every impostor accepted, every genuine rejected),
    # so the EER of a perfectly reversed matcher is 1, not one half
    eer, at = m.eer_at_1([1, 2, 3], [10, 11, 12])
    assert at["threshold"] == 10
    assert (at["fmr"], at["fnmr"]) == (1.0, 1.0)
    assert eer == 1.0


def test_eer_is_the_mean_of_fmr_and_fnmr_at_the_minimising_threshold():
    # genuine 5,7,9,11  impostor 4,6,8,10: at t=8, FMR=2/4 (8,10), FNMR=2/4
    # (5,7); at t=9, FMR=1/4, FNMR=2/4; at t=7 FMR=3/4, FNMR=1/4. Minimum
    # gap 0 at t=8, EER = (0.5+0.5)/2
    eer, at = m.eer_at_1([5, 7, 9, 11], [4, 6, 8, 10])
    assert at["threshold"] == 8
    assert eer == 0.5


def test_eer_tie_takes_the_smallest_threshold():
    # all four scores equal: t=3 accepts everything (FMR 1, FNMR 0) and the
    # reject-all threshold t=4 rejects everything (FMR 0, FNMR 1); the gap
    # is 1 at both, an exact tie, and the definition takes the smaller
    eer, at = m.eer_at_1([3, 3], [3, 3])
    assert at["threshold"] == 3
    assert (at["fmr"], at["fnmr"]) == (1.0, 0.0)
    assert eer == 0.5


def test_eer_sweeps_one_threshold_above_the_largest():
    # with all scores equal and above nothing, the reject-all threshold is
    # the only one with FMR 0; the definition includes it in the sweep
    v = m.eer_variants([3, 3], [3, 3])
    assert v[">=, with reject-all, smallest"]["threshold"] == 3
    assert v[">=, with reject-all, largest"]["threshold"] == 4


def test_eer_variants_name_the_registered_reading():
    g, i = [5, 7, 9, 11], [4, 6, 8, 10]
    eer, at = m.eer_at_1(g, i)
    reg = m.eer_variants(g, i)[">=, with reject-all, smallest"]
    assert reg["eer"] == eer and reg["threshold"] == at["threshold"]


# ---------------------------------------------------------------- auc@1
def test_auc_separable_is_one_and_reversed_is_zero():
    assert m.auc_at_1([10, 11, 12], [1, 2, 3]) == 1.0
    assert m.auc_at_1([1, 2, 3], [10, 11, 12]) == 0.0


def test_auc_counts_a_tie_as_one_half():
    # genuine 1,3  impostor 1,3: pairs (1,1) tie, (1,3) lose, (3,1) win,
    # (3,3) tie -> (0.5 + 0 + 1 + 0.5) / 4 = 1/2
    assert m.auc_at_1([1, 3], [1, 3]) == 0.5


def test_auc_rank_form_equals_the_pairwise_probability():
    # a mixed case with ties across and within lists
    g, i = [2, 4, 4, 7, 9], [1, 4, 5, 5, 8, 9]
    assert m.auc_at_1(g, i) == m.auc_pairwise(g, i)
    # and the value by hand: wins + half ties over 30 pairs
    wins = sum(1 for a in g for b in i if a > b)
    ties = sum(1 for a in g for b in i if a == b)
    assert m.auc_at_1(g, i) == (wins + 0.5 * ties) / 30


def test_auc_is_exact_not_trapezoidal():
    # a case where trapezoidal integration over a grid of thresholds
    # would not give the Mann-Whitney value: three genuine, one impostor
    # sitting between them gives exactly 2/3
    assert m.auc_at_1([1, 5, 9], [4]) == float(Fraction(2, 3))


# ------------------------------------------------ the registration holds
def test_registered_definition_text_is_the_implemented_text():
    path = os.path.join(REPO, "manifests", "MAN-metrics.v1.json")
    with open(path, encoding="utf-8") as fp:
        man = json.load(fp)
    for name, text in m.METRICS.items():
        assert man["metrics"][name]["definition"]["value"] == text
        assert man["metrics"][name]["id"]["value"] == name
        assert man["metrics"][name]["version"]["value"] == 1


def test_metric_definitions_refuses_a_differing_registration(monkeypatch):
    monkeypatch.setitem(m.METRICS, "eer@1", m.METRICS["eer@1"] + " ")
    with pytest.raises(ValueError):
        m.metric_definitions(REPO)


# ------------------------------- the values INV-017 reports, as rationals
def test_inv_017_values_are_the_nearest_doubles_to_their_rationals():
    # INV-017 F-1: the doubles the instrument stored, and the exact
    # rationals three readers computed from the definition text
    assert float(Fraction(19, 336)) == 0.05654761904761905
    assert float(Fraction(1359, 1400)) == 0.9707142857142858
    assert float(Fraction(17887, 554400)) == 0.032263708513708515
    assert float(Fraction(5473093, 5544000)) == 0.987210137085137
