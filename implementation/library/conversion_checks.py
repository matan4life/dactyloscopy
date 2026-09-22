"""What the conversion's choices do to the number: the checks of
`quality/INV-018`.

`iso_xyt.to_xyt` takes three named parameters - the half turn applied to
the ISO angle, whether the angle is snapped to `mindtct`'s 32-value grid,
and whether the quality byte is kept - and the matching run records the
values it used. This module runs the same subset under every reading of
each parameter and returns the metrics side by side, so that the reading
the run took is a measured choice and the cost of each alternative is a
number in the record rather than an argument in the prose.

It also measures two properties of `bozorth3` the conversion leans on: that
an integer angle off `mindtct`'s grid is accepted and used, and that the
quality column does not enter the score below the minutia cap; and one of
`iso-extract`: how many templates exceed the cap of 150 that `MAN-tools.v2`
records, and which minutiae `bozorth3` keeps when one does.

Imported, never invoked as a command; the command form is
`scripts/measure_conversion.sh`. Nothing per-minutia leaves `measure()`.
"""
import os
import subprocess

from implementation.library import iso_xyt, matching

# every reading of each parameter, the run's own first
READINGS = [
    ("as run", {}),
    ("no turn", {"turn_deg": 0}),
    ("mirrored", {"sense": -1}),
    ("mirrored, no turn", {"sense": -1, "turn_deg": 0}),
    ("snapped to 32", {"quantise": "mindtct32"}),
    ("quality zeroed", {"quality": "zero"}),
]


def sweep(repo_root, subset_id, work=None):
    """The subset under every reading; returns one entry per reading. Each
    reading is the run's own conversion with one parameter changed."""
    out = []
    for name, params in READINGS:
        run = matching.measure(repo_root, subset_id, work,
                               extractor="iso-extract", conversion=params)
        g = [r[3] for r in run["observation"]["pairs"] if r[2] == "genuine"]
        i = [r[3] for r in run["observation"]["pairs"] if r[2] == "impostor"]
        out.append({
            "reading": name, "conversion": run["conversion"],
            "eer@1": run["metrics"]["eer@1"]["value"],
            "at": run["metrics"]["eer@1"]["at"],
            "auc@1": run["metrics"]["auc@1"]["value"],
            "genuine": {"min": min(g), "median": sorted(g)[len(g) // 2],
                        "max": max(g), "zeros": g.count(0)},
            "impostor": {"min": min(i), "median": sorted(i)[len(i) // 2],
                         "max": max(i), "zeros": i.count(0)},
            "counts": {"min": min(run["observation"]["minutia_count"].values()),
                       "max": max(run["observation"]["minutia_count"].values()),
                       "above_cap_150": sum(
                           1 for v in run["observation"]["minutia_count"].values()
                           if v > 150)},
            "refusals": len(run["observation"]["extractor_refusals"]),
        })
        print("  %-16s eer@1 %.6f at %d  auc@1 %.6f" % (
            name, out[-1]["eer@1"], out[-1]["at"]["threshold"],
            out[-1]["auc@1"]), flush=True)
    return out


def bozorth3_properties(work):
    """Three facts about the matcher, on a synthetic template pair that
    contains no fingerprint: an angle off the 32-value grid is accepted and
    changes the score; a zeroed quality column does not change it; and
    which minutiae survive above the cap of 150 - the first 150 in file
    order, or the 150 of highest quality. Returns what was observed."""
    os.makedirs(work, exist_ok=True)
    # a template of 40 points on a coarse lattice with angles on and off
    # the grid, and a second that is the first shifted by (3, 2) px
    rows_a = [(20 + 30 * (k % 8), 20 + 30 * (k // 8), (k * 37) % 360, 50)
              for k in range(40)]
    rows_b = [(x + 3, y + 2, t, q) for x, y, t, q in rows_a]

    def score(a, b):
        pa, pb = os.path.join(work, "a.xyt"), os.path.join(work, "b.xyt")
        with open(pa, "wb") as fp:
            fp.write(iso_xyt.write_xyt(a))
        with open(pb, "wb") as fp:
            fp.write(iso_xyt.write_xyt(b))
        r = subprocess.run(["bozorth3", pa, pb], check=True,
                           capture_output=True, text=True)
        return int(r.stdout.strip())

    base = score(rows_a, rows_b)
    off = score([(x, y, (t + 1) % 360, q) for x, y, t, q in rows_a], rows_b)
    zeroed = score([(x, y, t, 0) for x, y, t, q in rows_a],
                   [(x, y, t, 0) for x, y, t, q in rows_b])
    # 160 points: the 40 above at quality 50, then 120 far away that match
    # nothing, at quality 90; then the same with the qualities swapped
    far = [(1000 + 7 * k, 1000 + 5 * k, (k * 53) % 360, 90) for k in range(120)]
    over = score(rows_a + far, rows_b)
    over_rev = score(far + rows_a, rows_b)
    first150 = score((rows_a + far)[:150], rows_b)
    hi = [(x, y, t, 90) for x, y, t, q in rows_a]
    lo_far = [(x, y, t, 50) for x, y, t, q in far]
    over_hi = score(hi + lo_far, rows_b)
    over_hi_last = score(lo_far + hi, rows_b)
    return {
        "score": base, "score_angles_plus_one": off,
        "off_grid_angle_changes_score": off != base,
        "score_quality_zeroed": zeroed,
        "quality_changes_score_below_cap": zeroed != base,
        "score_first_150_of_160": first150,
        "score_160_matching_first_low_quality": over,
        "score_160_matching_last_low_quality": over_rev,
        "score_160_matching_first_high_quality": over_hi,
        "score_160_matching_last_high_quality": over_hi_last,
        "cap_keeps_file_order": over == first150 and over_rev != first150,
        "cap_keeps_highest_quality":
            over_hi == first150 and over_hi_last == first150
            and over != first150,
    }
