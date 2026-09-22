"""The implementation check of `quality/INV-015`: two parameterisations agree.

`INV-015`'s M2 and M3 are one model written twice, so their fitted residuals
and their scale must agree exactly. They did not at 15 iterations of the
reweighting, and this check is what established that the cause was convergence
and not algebra: it fits 40 synthetic problems with planted outliers at four
iteration counts and reports the worst disagreement at each.

Imported, never invoked as a command; the command form is
`scripts/measure_warp_families.sh`.
"""

import numpy as np

from implementation.library.warp_families import (RS, apply_model, fit_radial,
                                                  fit_sim, rot)


def measure(iteration_counts=(15, 40, 120, 400), trials=40, seed=7):
    """Fit both parameterisations at each iteration count.

    Returns the worst disagreement in the scale and in the residual at each.
    """
    rows = []
    # One generator for the whole sweep, so that each iteration count is
    # given a fresh set of problems.  This is how the check was run for the
    # record, and moving the seeding inside the loop changes the numbers.
    rng2 = np.random.default_rng(seed)
    for iters in iteration_counts:
        worst_s, worst_r = 0.0, 0.0
        for _ in range(trials):
            n = int(rng2.integers(10, 40))
            V = rng2.normal(0, 90, (n, 2))
            th = rng2.normal(0, 0.2)
            s = 1.0 + rng2.normal(0, 0.02)
            T = (s * (V @ rot(th).T) + rng2.normal(0, 40, 2)
                 + rng2.normal(0, 3, (n, 2)))
            T[rng2.integers(0, n, max(1, n // 8))] += rng2.normal(0, 30, 2)
            m2 = fit_sim(V, T, iters=iters)
            m3 = fit_radial(V, T, (1,), iters=iters)
            ds = abs(m2["s"] - (1.0 + m3["c"][0] / RS))
            r2 = np.sqrt((np.hypot(*(T - apply_model(m2, V)).T) ** 2).mean())
            r3 = np.sqrt((np.hypot(*(T - apply_model(m3, V)).T) ** 2).mean())
            worst_s = max(worst_s, ds)
            worst_r = max(worst_r, abs(r2 - r3))
        rows.append({"iterations": iters, "max_scale_difference": worst_s,
                     "max_rms_difference": worst_r})
        print("iters %4d  max|ds| %.3e  max|d rms| %.3e"
              % (iters, worst_s, worst_r))
    return rows
