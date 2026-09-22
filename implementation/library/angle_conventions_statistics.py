"""The statistics of `quality/INV-012` F-2 to F-7, as a function over the
rows `angle_conventions.measure()` returns.

The record reports circular means and concentrations, extremes, counts
within a step, a per-orientation table, the per-family means of F-6 and the
distinct-value counts of F-7; until this module existed they were computed
by a script that was not kept, and the record said so (issue #10). Nothing
here reads an image or a template: the input is the 648 rows, one per
constructed point, each carrying the constructed direction and what each
tool reported for it.

Conventions, stated because the record's numbers depend on them: a circular
mean is the direction of the mean unit vector and R its length; a residual
is wrapped into (-180, 180]; "within" a step is `<=`; "nearest grid point"
is the nearest on the circle; `round` is Python's, half to even, which no
count below is sensitive to - half-up gives the same counts, checked on
these rows. Imported, never invoked as a command; the command form is
`scripts/measure_angle_conventions.py`, which prints `report()`.
"""
import math

XYT_STEP = 11.25          # mindtct's 32-level grid, INV-002 F-6
BYTE_STEP = 360.0 / 256   # the ISO theta byte's unit, INV-003 F-1
XYT_GRID = tuple((270 - math.floor(11.25 * d + 0.5)) % 360 for d in range(32))


def wrap(a):
    """Into (-180, 180]."""
    a = a % 360.0
    return a - 360.0 if a > 180.0 else a


def wrap_byte(b):
    """Into (-128, 128]."""
    b = b % 256
    return b - 256 if b > 128 else b


def circular_mean(angles):
    """(mean direction in [0, 360), R) of angles in degrees."""
    if not angles:
        raise ValueError("a circular mean over no angles")
    c = sum(math.cos(math.radians(a)) for a in angles) / len(angles)
    s = sum(math.sin(math.radians(a)) for a in angles) / len(angles)
    return math.degrees(math.atan2(s, c)) % 360.0, math.hypot(c, s)


def circular_distance(a, b, period=360.0):
    x = (a - b) % period
    return min(x, period - x)


def nearest_grid(angle):
    return min(XYT_GRID, key=lambda g: circular_distance(g, angle))


def _xyt(rows):
    """F-2: mindtct's .xyt angle and .min index against the construction."""
    diff = [(r["m_theta"] - r["truth"]) % 360.0 for r in rows]
    mean, R = circular_mean(diff)
    res = [wrap(r["m_theta"] - r["truth"] - 180.0) for r in rows]
    _, R_sum = circular_mean([(r["m_theta"] + r["truth"]) % 360.0
                              for r in rows])
    dirs = sorted({r["m_dir"] for r in rows})
    return {
        "n": len(rows),
        "images_with_exactly_9": sum(1 for r in rows if r["n_xyt"] == 9) // 9,
        "pairing_max_distance": max(r["m_dist"] for r in rows),
        "circular_mean": mean, "R": R,
        "difference_min": min(diff), "difference_max": max(diff),
        "residual_min": min(res), "residual_max": max(res),
        "residual_mean": sum(res) / len(res),
        "within_half_step": sum(1 for x in res if abs(x) <= XYT_STEP / 2),
        "equals_nearest_grid_of_truth_plus_180": sum(
            1 for r in rows
            if r["m_theta"] == nearest_grid((r["truth"] + 180.0) % 360.0)),
        "reflection_R": R_sum,
        "min_index_distinct": len(dirs),
        "min_index_min": dirs[0], "min_index_max": dirs[-1],
        "min_index_rule": sum(
            1 for r in rows
            if r["m_dir"] == round(8 - r["truth"] / XYT_STEP) % 32),
        "min_index_at_grid_points": {
            phi: sorted({r["m_dir"] for r in rows if r["phi"] == phi})
            for phi in (0, 90, 180, 270)},
        "xyt_from_min_index": sum(
            1 for r in rows
            if (270 - math.floor(XYT_STEP * r["m_dir"] + 0.5)) % 360
            == r["m_theta"]),
    }


def _iso(rows):
    """F-3: iso-extract's theta byte against the construction."""
    deg = [r["i_theta"] * BYTE_STEP for r in rows]
    diff = [(a - r["truth"]) % 360.0 for a, r in zip(deg, rows)]
    mean, R = circular_mean(diff)
    res = [wrap(a - r["truth"]) for a, r in zip(deg, rows)]
    bd = [circular_distance(r["i_theta"], round(r["truth"] / BYTE_STEP) % 256,
                            256) for r in rows]
    _, R_sum = circular_mean([(a + r["truth"]) % 360.0
                              for a, r in zip(deg, rows)])
    per_image = {}
    for r in rows:
        per_image[(r["family"], r["phi"])] = r["n_ist"]
    return {
        "n": len(rows),
        "images_accepted": sum(1 for r in rows if r["iso_rc"] == 0) // 9,
        "images_with_exactly_9": sum(1 for v in per_image.values() if v == 9),
        "images_with_10": sorted(k for k, v in per_image.items() if v == 10),
        "pairing_max_distance": max(r["i_dist"] for r in rows),
        "circular_mean": mean, "R": R,
        "residual_min": min(res), "residual_max": max(res),
        "residual_min_steps": min(res) / BYTE_STEP,
        "residual_max_steps": max(res) / BYTE_STEP,
        "within_half_step": sum(1 for x in res if abs(x) <= BYTE_STEP / 2),
        "byte_within_2_of_rounded_truth": sum(1 for x in bd if x <= 2),
        "byte_distance_max": max(bd),
        "reflection_R": R_sum,
    }


def _per_nominal(rows):
    """F-4: one row per nominal orientation, both families pooled."""
    out = []
    for phi in sorted({r["phi"] for r in rows}):
        rs = [r for r in rows if r["phi"] == phi]
        xres = [wrap(r["m_theta"] - r["truth"] - 180.0) for r in rs]
        b0 = round(phi / BYTE_STEP) % 256
        boff = [wrap_byte(r["i_theta"] - b0) for r in rs]
        ires = [wrap(r["i_theta"] * BYTE_STEP - r["truth"]) for r in rs]
        out.append({
            "nominal": phi, "n": len(rs),
            "xyt_values": sorted({r["m_theta"] for r in rs}),
            "xyt_residual_min": min(xres), "xyt_residual_max": max(xres),
            "b0": b0, "byte_offset_min": min(boff),
            "byte_offset_max": max(boff),
            "iso_residual_min": min(ires), "iso_residual_max": max(ires),
        })
    dev = [wrap(r["truth"] - r["phi"]) for r in rows]
    return {"rows": out, "truth_minus_nominal_min": min(dev),
            "truth_minus_nominal_max": max(dev)}


def _one_image(rows, phi=30):
    """F-4's worked example: every point of both families at one nominal."""
    return [{"family": r["family"], "point": r["j"], "constructed": r["truth"],
             "min_d": r["m_dir"], "min_type": r["m_type"],
             "xyt": r["m_theta"], "iso_byte": r["i_theta"],
             "iso_degrees": r["i_theta"] * BYTE_STEP, "iso_type": r["i_type"]}
            for r in rows if r["phi"] == phi]


def _between_tools(rows):
    """F-5: INV-002 R-2 taken the same way, ISO minus native."""
    mean, R = circular_mean([(r["i_theta"] * BYTE_STEP - r["m_theta"]) % 360.0
                             for r in rows])
    return {"circular_mean": mean, "R": R, "n": len(rows)}


def _families(rows):
    """F-6: labels per constructed family, and the mean per reported type."""
    labels = {}
    for fam in ("ending", "bifurcation"):
        rs = [r for r in rows if r["family"] == fam]
        labels[fam] = {
            "n": len(rs),
            "mindtct": {t: sum(1 for r in rs if r["m_type"] == t)
                        for t in ("RIG", "BIF")},
            "iso": {t: sum(1 for r in rs if r["i_type"] == t)
                    for t in (1, 2)},
        }
    groups = {}
    for t in ("RIG", "BIF"):
        g = [(r["m_theta"] - r["truth"]) % 360.0 for r in rows
             if r["m_type"] == t]
        groups["mindtct %s" % t] = _group(g)
    for t in (1, 2):
        g = [(r["i_theta"] * BYTE_STEP - r["truth"]) % 360.0 for r in rows
             if r["i_type"] == t]
        groups["iso-extract type %d" % t] = _group(g)
    return {
        "labels": labels, "groups": groups,
        "mindtct_groups_differ_by": _apart(groups["mindtct RIG"],
                                           groups["mindtct BIF"]),
        "iso_groups_differ_by": _apart(groups["iso-extract type 1"],
                                       groups["iso-extract type 2"]),
    }


def _group(angles):
    """A group's size, mean and R; a group nothing fell in has no mean."""
    if not angles:
        return {"n": 0, "circular_mean": None, "R": None}
    mean, R = circular_mean(angles)
    return {"n": len(angles), "circular_mean": mean, "R": R}


def _apart(a, b):
    if a["n"] == 0 or b["n"] == 0:
        return None
    return circular_distance(a["circular_mean"], b["circular_mean"])


def _quantisation(rows):
    """F-7: the distinct values each field took."""
    dirs = sorted({r["m_dir"] for r in rows})
    xyt = sorted({r["m_theta"] for r in rows})
    bytes_ = sorted({r["i_theta"] for r in rows})
    return {
        "min_index_distinct": len(dirs), "min_index_range": [dirs[0], dirs[-1]],
        "xyt_distinct": len(xyt),
        "xyt_is_the_inv_002_grid": xyt == sorted(XYT_GRID),
        "byte_distinct": len(bytes_),
        "byte_adjacent_differences": sorted({b - a for a, b
                                             in zip(bytes_, bytes_[1:])}),
    }


def statistics(rows):
    """Every statistic F-2 to F-7 report, from the rows alone."""
    return {"xyt": _xyt(rows), "iso": _iso(rows),
            "per_nominal": _per_nominal(rows), "one_image": _one_image(rows),
            "between_tools": _between_tools(rows), "families": _families(rows),
            "quantisation": _quantisation(rows)}


def _sgn(x, places=2):
    """Signed, as the record prints a range end: +2.46, -8.01."""
    return "%+.*f" % (places, x)


def _neg(x, places=3):
    """Unsigned when positive, a minus sign when negative, as the record
    prints a single value: 5.032, −8.008."""
    return ("%.*f" % (places, x)).replace("-", "−")


def report(st):
    """Print the tables as `INV-012` carries them, so that the record and
    the tree can be diffed line for line."""
    x, i = st["xyt"], st["iso"]
    print("== F-2, mindtct's .xyt angle over %d points" % x["n"])
    print("mindtct produced exactly 9 minutiae on %d of 72 images; largest "
          "pairing distance %.2f px" % (x["images_with_exactly_9"],
                                        x["pairing_max_distance"]))
    print("| statistic | value |")
    print("| --- | --- |")
    print("| circular mean of (reported − constructed) | **%.3f degrees** |"
          % x["circular_mean"])
    print("| concentration R of that difference | **%.5f** |" % x["R"])
    print("| the difference, least and greatest | %.3f and %.3f |"
          % (x["difference_min"], x["difference_max"]))
    print("| residual after subtracting 180, least and greatest | %s and %s |"
          % (_neg(x["residual_min"]), _sgn(x["residual_max"], 3)))
    print("| mean residual after subtracting 180 | %s |"
          % _neg(x["residual_mean"]))
    print("| residuals within half a grid step, 5.625 degrees | %d of %d |"
          % (x["within_half_step"], x["n"]))
    print("| reported equals the grid point nearest constructed + 180 | "
          "%d of %d |" % (x["equals_nearest_grid_of_truth_plus_180"], x["n"]))
    print("reflection test: R of (reported + constructed) = %.5f"
          % x["reflection_R"])
    print("== F-2, mindtct's .min direction index")
    print("the index took %d values, %d to %d"
          % (x["min_index_distinct"], x["min_index_min"], x["min_index_max"]))
    print("d == round(8 - constructed/11.25) mod 32       %d of %d"
          % (x["min_index_rule"], x["n"]))
    print("| constructed | 0 | 90 | 180 | 270 |")
    print("| --- | --- | --- | --- | --- |")
    print("| `.min` direction index | %s |" % " | ".join(
        ",".join(str(d) for d in x["min_index_at_grid_points"][phi])
        for phi in (0, 90, 180, 270)))
    print("(270 - round_half_up(11.25 d)) mod 360 equals the .xyt angle on "
          "%d of %d" % (x["xyt_from_min_index"], x["n"]))
    print()
    print("== F-3, iso-extract's theta byte over %d points" % i["n"])
    print("the library accepted %d of 72 images; exactly 9 minutiae in %d, "
          "10 in %d: %s; largest pairing distance %.2f px"
          % (i["images_accepted"], i["images_with_exactly_9"],
             len(i["images_with_10"]),
             ", ".join("%s at %d" % k for k in i["images_with_10"]),
             i["pairing_max_distance"]))
    print("| statistic | value |")
    print("| --- | --- |")
    print("| circular mean of (reported − constructed) | **%.3f degrees** |"
          % i["circular_mean"])
    print("| concentration R of that difference | **%.5f** |" % i["R"])
    print("| residual, least and greatest | %s and %s degrees |"
          % (_neg(i["residual_min"]), _sgn(i["residual_max"], 3)))
    print("| the same in byte steps | %s and %s |"
          % (_neg(i["residual_min_steps"], 2), _sgn(i["residual_max_steps"])))
    print("| residuals within half a byte step | %d of %d |"
          % (i["within_half_step"], i["n"]))
    print("| byte within 2 of `round(constructed / 1.40625)` | %d of %d, "
          "never more than %d |" % (i["byte_within_2_of_rounded_truth"],
                                    i["n"], i["byte_distance_max"]))
    print("reflection test: R of (reported + constructed) = %.5f"
          % i["reflection_R"])
    print()
    p = st["per_nominal"]
    print("== F-4, per nominal orientation; constructed minus nominal from "
          "%s to %s" % (_neg(p["truth_minus_nominal_min"], 2),
                        _sgn(p["truth_minus_nominal_max"])))
    print("| nominal | .xyt values | .xyt minus constructed, less 180 | "
          "iso bytes | iso minus constructed |")
    print("| --- | --- | --- | --- | --- |")
    for r in p["rows"]:
        print("| %d | %s | %s..%s | %d %s..%s | %s..%s |" % (
            r["nominal"], ",".join(str(v) for v in r["xyt_values"]),
            _sgn(r["xyt_residual_min"]), _sgn(r["xyt_residual_max"]),
            r["b0"], "%+d" % r["byte_offset_min"],
            "%+d" % r["byte_offset_max"],
            _sgn(r["iso_residual_min"]), _sgn(r["iso_residual_max"])))
    print()
    print("== F-4, one image in full: nominal 30")
    print("| family | point | constructed | `.min` d | `.min` type | `.xyt` | "
          "iso byte | iso degrees | iso type |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for r in st["one_image"]:
        print("| %s | %d | %.3f | %d | %s | %d | %d | %.3f | %d |" % (
            {"ending": "end", "bifurcation": "bif"}[r["family"]], r["point"],
            r["constructed"], r["min_d"], r["min_type"], r["xyt"],
            r["iso_byte"], r["iso_degrees"], r["iso_type"]))
    print()
    b = st["between_tools"]
    print("== F-5, ISO minus native over %d points: circular mean %.3f "
          "degrees, R %.5f" % (b["n"], b["circular_mean"], b["R"]))
    print()
    f = st["families"]
    print("== F-6, the families")
    print("| family, %d points each | `mindtct` `.min` | `iso-extract` |"
          % f["labels"]["ending"]["n"])
    print("| --- | --- | --- |")
    for fam, built in (("ending", "built as ridge endings"),
                       ("bifurcation", "built as bifurcations")):
        m, s = f["labels"][fam]["mindtct"], f["labels"][fam]["iso"]
        first = "RIG" if fam == "ending" else "BIF"
        second = "BIF" if fam == "ending" else "RIG"
        t = 1 if fam == "ending" else 2
        print("| %s | `%s` %d, `%s` %d | type %d on %d |"
              % (built, first, m[first], second, m[second], t, s[t]))
    print("| group | n | circular mean of (reported − constructed) | R |")
    print("| --- | --- | --- | --- |")
    for name, label in (("mindtct RIG", "`mindtct`, reported `RIG`"),
                        ("mindtct BIF", "`mindtct`, reported `BIF`"),
                        ("iso-extract type 1",
                         "`iso-extract`, reported type 1"),
                        ("iso-extract type 2",
                         "`iso-extract`, reported type 2")):
        g = f["groups"][name]
        if g["n"]:
            print("| %s | %d | %.3f | %.5f |"
                  % (label, g["n"], g["circular_mean"], g["R"]))
        else:
            print("| %s | 0 | no mean | no R |" % label)
    print("the two mindtct groups differ by %s degrees, the two iso-extract "
          "groups by %s" % tuple(
              "%.3f" % v if v is not None else "nothing, a group is empty"
              for v in (f["mindtct_groups_differ_by"],
                        f["iso_groups_differ_by"])))
    print()
    q = st["quantisation"]
    print("== F-7, the quantisation observed")
    print("mindtct .min direction: %d distinct values, %d..%d"
          % (q["min_index_distinct"], q["min_index_range"][0],
             q["min_index_range"][1]))
    print("mindtct .xyt angle: %d distinct values; the INV-002 F-8 set: %s"
          % (q["xyt_distinct"], q["xyt_is_the_inv_002_grid"]))
    print("iso-extract theta byte: %d distinct bytes; adjacent observed "
          "values differ by %s" % (q["byte_distinct"], ", ".join(
              str(d) for d in q["byte_adjacent_differences"])))
