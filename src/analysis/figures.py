#!/usr/bin/env python3
"""figures.py — Generate the final trade-off plot from summary_table.csv.

Follows Raj Jain's "The Art of Computer Systems Performance Analysis" (Ch. 10)
and Tidyverse (ggplot2::theme_bw + Okabe-Ito colorblind-safe palette):
  - Axes starting strictly at zero (no truncated scales);
  - Explicit 95% Confidence Interval error bars on both axes;
  - Direct labeling of points and explicit SRAM capacity limit;
  - High data-ink ratio, subtle major grid, facet-strip header.
"""
import argparse
import csv
import os
from collections import defaultdict

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

OKABE_ITO_ALGS = {
    "kyber512": ("#0072B2", "o", "Kyber-512 (ML-KEM)"),
    "ctru-light": ("#D55E00", "s", "CTRU-Light"),
    "ecdh": ("#009E73", "^", "ECDH P-256 (Baseline)"),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--sram-limit", type=int, default=6144, help="SRAM limit in bytes (default: 6144 for ATmega4809)")
    args = ap.parse_args()

    plt.rcParams.update(
        {
            "figure.facecolor": "#FFFFFF",
            "axes.facecolor": "#FFFFFF",
            "axes.edgecolor": "#4D4D4D",
            "axes.linewidth": 0.8,
            "axes.grid": True,
            "axes.axisbelow": True,
            "grid.color": "#E5E5E5",
            "grid.linestyle": "-",
            "grid.linewidth": 0.6,
            "font.family": "sans-serif",
            "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
            "font.size": 9.5,
        }
    )

    pts = defaultdict(lambda: {"x": [], "xe": [], "y": [], "ye": [], "ops": []})
    with open(args.inp) as f:
        for row in csv.DictReader(f):
            alg = row["algorithm"]
            pts[alg]["x"].append(float(row["energy_uj_mean"]))
            pts[alg]["xe"].append(float(row["energy_uj_ci95"]))
            pts[alg]["y"].append(float(row["stack_peak_mean"]))
            pts[alg]["ye"].append(float(row["stack_peak_ci95"]))
            pts[alg]["ops"].append(row.get("operation", ""))

    fig, ax = plt.subplots(figsize=(7.5, 5.2))
    fig.subplots_adjust(left=0.11, right=0.96, top=0.82, bottom=0.15)

    max_x, max_y = 1.0, float(args.sram_limit)
    for alg, p in pts.items():
        color, marker, label = OKABE_ITO_ALGS.get(alg, ("#333333", "o", alg))
        ax.errorbar(
            p["x"],
            p["y"],
            xerr=p["xe"],
            yerr=p["ye"],
            fmt=marker,
            color=color,
            ecolor="#222222",
            elinewidth=1.1,
            capsize=4,
            markersize=6.5,
            markeredgecolor="#111111",
            markeredgewidth=0.8,
            label=label,
            zorder=4,
        )
        for x, xe, y, ye, op in zip(p["x"], p["xe"], p["y"], p["ye"], p["ops"]):
            max_x = max(max_x, x + xe)
            max_y = max(max_y, y + ye)
            if op:
                ax.annotate(
                    op,
                    xy=(x, y),
                    xytext=(5, 4),
                    textcoords="offset points",
                    fontsize=7.8,
                    color=color,
                    fontweight="bold",
                )

    ax.axhline(
        args.sram_limit,
        ls="--",
        lw=1.2,
        color="#C8102E",
        label=f"SRAM Limit ({args.sram_limit} B)",
        zorder=3,
    )
    ax.set_xlim(0, max_x * 1.18)
    ax.set_ylim(0, max_y * 1.15)
    ax.set_xlabel("Energy per Operation (µJ)")
    ax.set_ylabel("Stack Peak Memory Usage (Bytes)")
    ax.legend(loc="lower right", frameon=True, facecolor="#FFFFFF", edgecolor="#CCCCCC")

    ax.annotate(
        "Trade-off Space: Energy vs. Stack Memory Usage (Mean ± 95% CI)",
        xy=(0.5, 1.0),
        xycoords="axes fraction",
        xytext=(0, 6),
        textcoords="offset points",
        ha="center",
        va="bottom",
        fontsize=9.5,
        fontweight="bold",
        color="#1A1A1A",
        bbox=dict(boxstyle="square,pad=0.35", facecolor="#EFEFEF", edgecolor="#4D4D4D", linewidth=0.8),
    )

    fig.text(0.11, 0.93, "Energy vs. SRAM Memory Trade-off", fontsize=13.0, fontweight="bold", color="#111111")
    fig.text(
        0.11,
        0.025,
        "Source: CMP223 experimental pipeline. Error bars indicate 95% Confidence Intervals (Student's t).",
        fontsize=8.0,
        color="#555555",
        style="italic",
    )

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    fig.savefig(args.out, dpi=200)
    plt.close(fig)
    print(f"[figures] -> {args.out}")


if __name__ == "__main__":
    main()
