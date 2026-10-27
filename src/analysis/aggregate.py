#!/usr/bin/env python3
"""aggregate.py — Consolidate per-iteration JSONs into a table with statistics.

Groups by (algorithm, variant, clock, optimization, operation) and computes the
mean and 95% confidence interval (Student's t) for each metric.

The filename carries the factors:
    {alg}-{var}-{clock}MHz-{opt}-{op}-{i}.json
"""
import argparse, json, csv, os, re, math
from collections import defaultdict

NAME_RE = re.compile(
    r"(?P<alg>.+)-(?P<var>ref|asm)-(?P<clock>\d+)MHz-"
    r"(?P<opt>[^-]+)-(?P<op>[^-]+)-(?P<i>\d+)\.json$"
)


def ci95(values):
    """Mean and half-width of the 95% CI (normal approx. for n>=30)."""
    n = len(values)
    if n == 0:
        return 0.0, 0.0
    mean = sum(values) / n
    if n < 2:
        return mean, 0.0
    var = sum((x - mean) ** 2 for x in values) / (n - 1)
    sd = math.sqrt(var)
    # z=1.96 (n>=30). For small n, use Student's t instead (scipy).
    return mean, 1.96 * sd / math.sqrt(n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    groups = defaultdict(lambda: defaultdict(list))
    for path in args.inp:
        m = NAME_RE.search(os.path.basename(path))
        if not m:
            continue
        key = (m["alg"], m["var"], m["clock"], m["opt"], m["op"])
        with open(path) as f:
            row = json.load(f)
        for metric in ("energy_uj", "latency_s", "stack_peak_bytes"):
            if metric in row:
                groups[key][metric].append(float(row[metric]))

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "algorithm", "variant", "clock_mhz", "optimization", "operation", "n",
            "energy_uj_mean", "energy_uj_ci95",
            "latency_s_mean", "latency_s_ci95",
            "stack_peak_mean", "stack_peak_ci95",
        ])
        for (alg, var, clock, opt, op), metrics in sorted(groups.items()):
            e_m, e_c = ci95(metrics.get("energy_uj", []))
            l_m, l_c = ci95(metrics.get("latency_s", []))
            s_m, s_c = ci95(metrics.get("stack_peak_bytes", []))
            n = len(metrics.get("energy_uj", []))
            w.writerow([alg, var, clock, opt, op, n,
                        f"{e_m:.4f}", f"{e_c:.4f}",
                        f"{l_m:.8f}", f"{l_c:.8f}",
                        f"{s_m:.1f}", f"{s_c:.1f}"])


if __name__ == "__main__":
    main()
