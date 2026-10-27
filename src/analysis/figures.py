#!/usr/bin/env python3
"""figures.py — Generate the final plots from the aggregated table.

Reads summary_table.csv and produces a trade-off plot (energy vs. stack) with
error bars (95% CI), as a vector PDF for the LaTeX paper.
"""
import argparse, csv
from collections import defaultdict


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # group points by algorithm
    pts = defaultdict(lambda: {"x": [], "xe": [], "y": [], "ye": []})
    with open(args.inp) as f:
        for row in csv.DictReader(f):
            alg = row["algorithm"]
            pts[alg]["x"].append(float(row["energy_uj_mean"]))
            pts[alg]["xe"].append(float(row["energy_uj_ci95"]))
            pts[alg]["y"].append(float(row["stack_peak_mean"]))
            pts[alg]["ye"].append(float(row["stack_peak_ci95"]))

    fig, ax = plt.subplots(figsize=(6, 4))
    for alg, p in pts.items():
        ax.errorbar(p["x"], p["y"], xerr=p["xe"], yerr=p["ye"],
                    fmt="o", capsize=3, label=alg)
    ax.set_xlabel("Energy per operation (uJ)")
    ax.set_ylabel("Peak stack (bytes)")
    ax.set_title("Energy vs. memory trade-off")
    ax.axhline(6144, ls="--", color="#c8102e", label="SRAM limit (6 KB)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(args.out)
    print(f"[figures] -> {args.out}")


if __name__ == "__main__":
    main()
