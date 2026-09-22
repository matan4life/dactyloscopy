"""The report of `quality/INV-015`: the aggregate turned into the tables.

Every table in the record is printed by this module from the aggregate
`warp_families.measure` returns, so that a reader reaches the record's numbers
by the same path the record did.

Imported, never invoked as a command; the command form is
`scripts/measure_warp_families.py`.
"""
import math

import numpy as np

BN = ["0-30", "30-60", "60-90", "90-120", "120-150", "150+"]
MODELS = ["M0", "M1", "M2", "M3", "M4", "M5", "M6", "M7",
          "M8l0", "M8l10", "M8l100", "M8l1000", "M8l10000"]


def report(d, tag="DB1_B"):
    """Print every table the record carries; return the same lines."""
    out = []

    def emit(line=""):
        print(line)
        out.append(line)

    def r1(tau, m, b, flag=None):
        if flag is None:
            n, ss = 0, 0.0
            for f in ("True", "False"):
                e = d["R1"].get("%d|%s|%s|%s" % (tau, m, b, f))
                if e:
                    n += e["n"]
                    ss += e["rms"] ** 2 * e["n"]
            return n, (math.sqrt(ss / n) if n else None)
        e = d["R1"].get("%d|%s|%s|%s" % (tau, m, b, flag))
        return (e["n"], e["rms"]) if e else (0, None)


    def p90(tau, m, b):
        n, s = 0, []
        for f in ("True", "False"):
            e = d["R1"].get("%d|%s|%s|%s" % (tau, m, b, f))
            if e:
                n += e["n"]
                s.append((e["n"], e["p90"]))
        return sum(a * b2 for a, b2 in s) / n if n else None

    emit("### %s: %d images, %d fingers, %d genuine pairs, ransac failures %d"
          % (tag, d["images"], d["fingers"], d["genuine_pairs"],
             d["ransac_failures"]))
    m = d["mask"]
    emit("mask area px2 %.0f..%.0f mean %.0f ; equiv radius %.1f..%.1f mean %.1f"
          % (min(m["area_px2"]), max(m["area_px2"]), np.mean(m["area_px2"]),
             min(m["equiv_radius_px"]), max(m["equiv_radius_px"]),
             np.mean(m["equiv_radius_px"])))
    emit("within-finger area sd %.0f..%.0f ; minutiae per image %d..%d"
          % (min(m["within_finger_area_spread"]),
             max(m["within_finger_area_spread"]),
             min(m["n_minutiae"]), max(m["n_minutiae"])))
    lc = np.array(m["area_lcm_px2"])
    qa = np.array(m["area_px2"])
    emit("qm>=1 area against lcm==0 area: mean ratio %.4f, max |diff| %.0f px2"
          % ((qa / lc).mean(), np.abs(qa - lc).max()))

    emit()
    emit("tau  medianN  minN maxN  excluded(N<8)  pairs used")
    for t in (3, 5, 8, 12, 15, 20):
        N = d["N_by_tau"][str(t)]
        emit("  %-4d %6.1f %5d %4d %8d %12d"
              % (t, np.median(N), min(N), max(N), d["excluded_by_tau"][str(t)],
                 len(N) - d["excluded_by_tau"][str(t)]))

    emit()
    emit("radial histogram of correspondences, 30 px bins")
    emit("  tau " + "".join("%9s" % b for b in BN))
    for t in (3, 5, 8, 12, 15, 20):
        emit("  %-4d" % t + "".join("%9d" % int(x)
                                     for x in d["radial_hist"][str(t)]))
    emit("convex-hull coverage of the mask, by band")
    for t in (3, 5, 8, 12, 15, 20):
        emit("  %-4d" % t + "".join("%9.3f" % x
                                     for x in d["hull_coverage"][str(t)]))

    for tau in (3, 5, 8, 12, 15, 20):
        emit()
        emit("== R-1 held-out RMS px, tau=%d" % tau)
        emit("%-10s" % "model" + "".join("%9s" % b for b in BN))
        for mm in MODELS:
            emit("%-10s" % mm + "".join(
                "%9s" % ("%.2f" % r1(tau, mm, b)[1] if r1(tau, mm, b)[1] else "-")
                for b in BN))
        emit("%-10s" % "n" + "".join("%9d" % r1(tau, "M1", b)[0] for b in BN))

    emit()
    emit("== R-1 90th percentile, tau=15")
    emit("%-10s" % "model" + "".join("%9s" % b for b in BN))
    for mm in MODELS:
        emit("%-10s" % mm + "".join(
            "%9s" % ("%.2f" % p90(15, mm, b) if p90(15, mm, b) else "-")
            for b in BN))

    emit()
    emit("== R-3 fit residual (FRE) RMS px, tau=15")
    emit("%-10s" % "model" + "".join("%9s" % b for b in BN))
    for mm in MODELS:
        e = [d["R3"].get("15|%s|%s" % (mm, b)) for b in BN]
        emit("%-10s" % mm + "".join("%9s" % ("%.2f" % x["rms"] if x else "-")
                                     for x in e))

    emit()
    emit("== R-2 held-out RMS inside / outside the fitting fold's hull, tau=15")
    emit("%-10s" % "model" + "".join("%19s" % b for b in BN))
    for mm in ("M1", "M4", "M5", "M7", "M8l10000"):
        row = ""
        for b in BN:
            ni, ri = r1(15, mm, b, "True")
            no, ro = r1(15, mm, b, "False")
            row += "%19s" % ("%s/%s" % ("%.2f" % ri if ri else "-",
                                        "%.2f" % ro if ro else "-"))
        emit("%-10s%s" % (mm, row))
    emit("%-10s" % "n in/out" + "".join(
        "%19s" % ("%d/%d" % (r1(15, "M1", b, "True")[0],
                             r1(15, "M1", b, "False")[0])) for b in BN))

    for TAU in (3, 8, 15, 20):
        emit()
        emit("== paired differences, mean(d_a - d_b) px +- se, tau=%d" % TAU)
        emit("%-20s" % "contrast" + "".join("%17s" % b for b in BN))
        seen0 = sorted({(k.split("|")[2], k.split("|")[3])
                        for k in d["paired"] if k.split("|")[0] == str(TAU)})
        for a, bb in seen0:
            row = ""
            for b in BN:
                e = d["paired"].get("%d|%s|%s|%s" % (TAU, b, a, bb))
                row += "%17s" % ("%+.3f+-%.3f" % (e["mean"], e["se"])
                                 if e and e["se"] else "-")
            emit("%-20s%s" % ("%s - %s" % (a, bb), row))

    emit()
    emit("== paired differences, mean(d_a - d_b) px with standard error, tau=15")
    emit("%-20s" % "contrast" + "".join("%17s" % b for b in BN))
    seen = set()
    for k in d["paired"]:
        t, b, a, bb = k.split("|")
        if t == "15":
            seen.add((a, bb))
    for a, bb in sorted(seen):
        row = ""
        for b in BN:
            e = d["paired"].get("15|%s|%s|%s" % (b, a, bb))
            row += "%17s" % ("%+.3f+-%.3f" % (e["mean"], e["se"])
                             if e and e["se"] else "-")
        emit("%-20s%s" % ("%s - %s" % (a, bb), row))
    emit()
    emit("%-20s" % "frac a better" + "".join("%17s" % b for b in BN))
    for a, bb in sorted(seen):
        row = ""
        for b in BN:
            e = d["paired"].get("15|%s|%s|%s" % (b, a, bb))
            row += "%17s" % ("%.3f" % e["frac_a_better"] if e else "-")
        emit("%-20s%s" % ("%s - %s" % (a, bb), row))

    emit()
    r5 = d["R5"]
    s = np.array([r["s"] for r in r5])
    sc = np.array([r["s_from_c1"] for r in r5])
    rm2 = np.array([r["rms_m2"] for r in r5])
    rm3 = np.array([r["rms_m3"] for r in r5])
    ar = np.array([r["sqrt_area_ratio"] for r in r5])
    emit("P-3: n=%d  max|s-(1+c1/rs)| = %.3e  max|rmsM2-rmsM3| = %.3e"
          % (len(s), np.abs(s - sc).max(), np.abs(rm2 - rm3).max()))
    A = np.stack([ar, np.ones(len(ar))], 1)
    sol = np.linalg.lstsq(A, s, rcond=None)[0]
    res = s - A @ sol
    se = math.sqrt((res ** 2).sum() / (len(s) - 2)
                   / ((ar - ar.mean()) ** 2).sum())
    emit("R-5: slope %.4f +- %.4f  intercept %.4f  r %.4f  resid sd %.5f"
          % (sol[0], se, sol[1], np.corrcoef(ar, s)[0, 1], res.std(ddof=2)))
    emit("     s %.5f..%.5f  sqrt(area ratio) %.3f..%.3f"
          % (s.min(), s.max(), ar.min(), ar.max()))

    r4 = d["R4"]
    c1 = np.array([r["c1"] for r in r4])
    c3 = np.array([r["c3"] for r in r4])
    cov = np.array([r["cov"] for r in r4])
    obs = np.cov(np.stack([c1, c3]))
    err = cov.mean(0)
    emit()
    emit("R-4: n=%d  c1 mean %.3f sd %.3f ; c3 mean %.3f sd %.3f"
          % (len(r4), c1.mean(), c1.std(ddof=1), c3.mean(), c3.std(ddof=1)))
    emit("  observed  cov [[%.1f %.1f][%.1f %.1f]] rho %.3f"
          % (obs[0, 0], obs[0, 1], obs[1, 0], obs[1, 1],
             obs[0, 1] / math.sqrt(obs[0, 0] * obs[1, 1])))
    emit("  error     cov [[%.1f %.1f][%.1f %.1f]] rho %.3f"
          % (err[0, 0], err[0, 1], err[1, 0], err[1, 1],
             err[0, 1] / math.sqrt(err[0, 0] * err[1, 1])))
    emit("  observed/error variance ratio: c1 %.3f  c3 %.3f"
          % (obs[0, 0] / err[0, 0], obs[1, 1] / err[1, 1]))

    emit()
    emit("step 5, per finger, observed residual / bootstrap null mean")
    emit("  finger    c1 obs   null  ratio |   c3 obs   null  ratio |"
          "  rot obs   null  ratio")
    for g, v in sorted(d["step5"].items()):
        emit("  %-8s %8.3f %6.3f %6.2f | %8.2f %6.2f %6.2f | %8.2f %6.3f %6.2f"
              % (g, v["c1"]["observed"], v["c1"]["null_mean"], v["c1"]["ratio"],
                 v["c3"]["observed"], v["c3"]["null_mean"], v["c3"]["ratio"],
                 v["rot"]["observed"], v["rot"]["null_mean"], v["rot"]["ratio"]))

    emit()
    emit("rotation diagnostics from the M4 fits at tau=15")
    allrot = []
    for g, rows in d["finger_coef"].items():
        for rw in rows:
            allrot.append((abs(rw[4]), rw[5], rw[9] if len(rw) > 9 else None))
    allrot = np.array([[a, b, c] for a, b, c in allrot], dtype=float)
    emit("  |rotation| deg: median %.2f  p90 %.2f  max %.2f ; over 20 deg: %d/%d"
          % (np.median(allrot[:, 0]), np.percentile(allrot[:, 0], 90),
             allrot[:, 0].max(), int((allrot[:, 0] > 20).sum()), len(allrot)))
    big = allrot[:, 0] > 20
    if big.sum():
        emit("  those pairs: N median %.0f (all pairs %.0f), ransac inliers "
              "median %.0f (all %.0f)"
              % (np.median(allrot[big, 1]), np.median(allrot[:, 1]),
                 np.median(allrot[big, 2]), np.median(allrot[:, 2])))

    emit()
    emit("step 6, distortion-free core: M1 fitted inside rho, held-out RMS")
    emit("%-8s" % "rho" + "".join("%9s" % b for b in BN))
    for rho in (40, 60, 80, 100, 120):
        row = ""
        for b in BN:
            e = d["core"].get("%d|%s" % (rho, b))
            row += "%9s" % ("%.2f" % e["rms"] if e and e["n"] >= 20 else "-")
        emit("%-8d%s" % (rho, row))
    emit("%-8s" % "n" + "".join(
        "%9d" % (d["core"].get("80|%s" % b, {"n": 0})["n"]) for b in BN))

    emit()
    emit("impostor control at tau=15: %d finger pairs, N median %.1f, "
          "usable %d" % (d["impostor_pairs"], np.median(d["impostor_N"]),
                         int((np.array(d["impostor_N"]) >= 8).sum())))
    emit("%-10s" % "model" + "".join("%9s" % b for b in BN))
    for mm in ("M1", "M4", "M7", "M8l10000"):
        row = ""
        for b in BN:
            e = d["impostor"].get("%s|%s" % (mm, b))
            row += "%9s" % ("%.2f" % e["rms"] if e else "-")
        emit("%-10s%s" % (mm, row))
    emit("%-10s" % "n" + "".join(
        "%9d" % (d["impostor"].get("M1|%s" % b, {"n": 0})["n"]) for b in BN))


    if "R1c" in d:
        emit()
        emit("== post-hoc: consistent-rotation subset, %d of %d pairs"
              % (d["consistent_n"], d["consistent_of"]))
        for TAU in (8, 15):
            emit("-- held-out RMS px, tau=%d" % TAU)
            emit("%-10s" % "model" + "".join("%9s" % b for b in BN))
            for mm in MODELS:
                row = ""
                for b in BN:
                    e = d["R1c"].get("%d|%s|%s" % (TAU, mm, b))
                    row += "%9s" % ("%.2f" % e["rms"] if e else "-")
                emit("%-10s%s" % (mm, row))
            emit("%-10s" % "n" + "".join(
                "%9d" % d["R1c"].get("%d|M1|%s" % (TAU, b), {"n": 0})["n"]
                for b in BN))
            emit("-- paired differences")
            seen1 = sorted({(k.split("|")[2], k.split("|")[3])
                            for k in d["paired_c"] if k.split("|")[0] == str(TAU)})
            for a, bb in seen1:
                row = ""
                for b in BN:
                    e = d["paired_c"].get("%d|%s|%s|%s" % (TAU, b, a, bb))
                    row += "%17s" % ("%+.3f+-%.3f" % (e["mean"], e["se"])
                                     if e and e["se"] else "-")
                emit("%-20s%s" % ("%s - %s" % (a, bb), row))
        rr = np.array(list(d["rot_resid"].values()))
        emit("rotation incidence residual, robust, per pair: median |e| %.2f deg, "
              "within 5 deg %d of %d" % (np.median(np.abs(rr)),
                                         int((np.abs(rr) <= 5).sum()), len(rr)))
    return out
