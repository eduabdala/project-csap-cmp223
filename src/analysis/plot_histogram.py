#!/usr/bin/env python3
"""plot_histogram.py — High-fidelity empirical distribution histogram for Experiment 0.

Follows the data visualization and analysis principles from:
  - Raj Jain, "The Art of Computer Systems Performance Analysis" (Ch. 10):
      * 10.1–10.4: Clear labeling, zero-baseline, no chartjunk, high data-ink ratio;
      * 10.3.3: Choice of cell (bin) size — using Freedman-Diaconis rule to balance bias and variance;
      * 10.5: Showing empirical distribution vs. central tendency (Mean, 95% CI, Median);
  - Tidyverse / ggplot2 design aesthetics:
      * ggplot2::theme_bw() styling (subtle gray borders, crisp white canvas, clean facets);
      * Okabe-Ito colorblind-safe palette (Wong 2011 / Claus Wilke standard);
      * Integrated kernel density estimate (KDE) and rug plot for individual sample visibility.

Usage:
  python3 src/analysis/plot_histogram.py --in data/raw/exp0_raw_runs.csv --out data/processed/figures/exp0_histogram
"""

import argparse
import csv
import math
import os
import numpy as np

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from scipy.stats import gaussian_kde

# Okabe-Ito Color Palette
OKABE_ITO = {
    "keygen":   "#0072B2",  # Blue
    "encaps":   "#D55E00",  # Vermilion
    "decaps":   "#009E73",  # Bluish Green
    "msgcrypt": "#CC79A7",  # Reddish Purple
}

OP_LABELS = {
    "keygen":   "KeyGen (K)",
    "encaps":   "Encaps (E)",
    "decaps":   "Decaps (D)",
    "msgcrypt": "MsgCrypt (M)",
}

def freedman_diaconis_bins(data):
    """Compute optimal bin width according to the Freedman-Diaconis rule (Jain Ch. 10.3)."""
    a = np.asarray(data)
    q75, q25 = np.percentile(a, [75, 25])
    iqr = q75 - q25
    if iqr == 0:
        return 10
    h = 2.0 * iqr * (len(a) ** (-1.0 / 3.0))
    if h == 0:
        return 10
    nbins = int(math.ceil((a.max() - a.min()) / h))
    return max(6, min(nbins, 25))

def plot_raw_timeseries(rows, out_path):
    """Plot every single raw observation across the execution timeline (Jain Ch. 11.4)."""
    fig, ax = plt.subplots(figsize=(11, 5.5))
    fig.subplots_adjust(left=0.08, right=0.96, top=0.88, bottom=0.12)

    variants = sorted(list({r.get("variant", "default") for r in rows}))
    marker_map = {"asm": "o", "ref": "s", "default": "^"}

    # Sort by run_order
    sorted_rows = sorted(rows, key=lambda x: int(x.get("run_order", 0)))

    for op in ["keygen", "encaps", "decaps", "msgcrypt"]:
        color = OKABE_ITO.get(op, "#333333")
        label_op = OP_LABELS.get(op, op)
        for var in variants:
            subset = [r for r in sorted_rows if r.get("operation") == op and r.get("variant", "default") == var]
            if not subset:
                continue
            x = [int(r["run_order"]) for r in subset]
            y = [float(r["latency_ms"]) for r in subset]
            marker = marker_map.get(var, "o")
            ax.plot(x, y, marker=marker, markersize=6, linestyle="-", linewidth=1.2,
                    alpha=0.85, color=color, label=f"{label_op} [{var.upper()}]")

    ax.set_title("Complete Raw Observations Across Trial Sequence (Run Order)", fontsize=11.5, fontweight="bold", pad=10)
    ax.set_xlabel("Execution Run Order (Sequential Trial Index)", fontsize=9.5, fontweight="medium")
    ax.set_ylabel("Execution Latency (ms)", fontsize=9.5, fontweight="medium")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), fontsize=8.2, framealpha=0.9, edgecolor="#CCCCCC")
    fig.subplots_adjust(right=0.78)

    fig.text(
        0.08, 0.02,
        "Note: Every single trial point is plotted. Zero aggregation; preserves temporal sequence and exposes thermal drift or outliers.",
        fontsize=7.8,
        color="#777777",
        ha="left"
    )

    png_path = f"{out_path}_timeseries.png"
    pdf_path = f"{out_path}_timeseries.pdf"
    plt.savefig(png_path, dpi=300)
    plt.savefig(pdf_path)
    plt.close()
    print(f"[plot_histogram] Time-series sequence plot saved to:\n  - {png_path}\n  - {pdf_path}")

def plot_unified_real_scale_histogram(rows, out_path):
    """Plot unified comparative histogram where ALL operations and variants share the exact same
    physical zero-baseline scale and real trial counts (density=False).
    """
    algs = sorted(list({r.get("algorithm", "kyber512") for r in rows}))
    ordered_ops = ["keygen", "encaps", "decaps", "msgcrypt"]
    op_titles = {
        "keygen": "KeyGen (K)",
        "encaps": "Encaps (E)",
        "decaps": "Decaps (D)",
        "msgcrypt": "MsgCrypt (M)"
    }

    for alg in algs:
        alg_rows = [r for r in rows if r.get("algorithm", "kyber512") == alg]
        all_lats = [float(r["latency_ms"]) for r in alg_rows if "latency_ms" in r]
        max_lat = max(all_lats) if all_lats else 700.0
        x_max = int(math.ceil(max_lat / 50.0) * 50) + 20

        # Bin configuration on real millisecond scale
        bin_width = max(5.0, round(x_max / 70.0))
        bin_edges = np.arange(0, x_max + bin_width, bin_width)

        fig, axes = plt.subplots(4, 1, figsize=(12, 10.5), sharex=True, sharey=True)
        fig.subplots_adjust(left=0.08, right=0.96, top=0.91, bottom=0.07, hspace=0.36)

        max_count = 0
        for idx, op in enumerate(ordered_ops):
            ax = axes[idx]
            asm_vals = np.array([float(r["latency_ms"]) for r in alg_rows if r.get("operation") == op and r.get("variant") == "asm"])
            ref_vals = np.array([float(r["latency_ms"]) for r in alg_rows if r.get("operation") == op and r.get("variant") == "ref"])

            n_asm = len(asm_vals)
            n_ref = len(ref_vals)
            max_count = max(max_count, n_asm, n_ref)

            m_asm = np.mean(asm_vals) if n_asm > 0 else 0.0
            m_ref = np.mean(ref_vals) if n_ref > 0 else 0.0

            # Plot real integer counts (density=False)
            if n_asm > 0:
                ax.hist(
                    asm_vals, bins=bin_edges, color="#0072B2", alpha=0.85,
                    edgecolor="#003B66", linewidth=1.2,
                    label=f"ASM (Mean: {m_asm:.1f} ms, N={n_asm})"
                )
                # Rug ticks at baseline for individual observations
                ax.plot(asm_vals, np.full_like(asm_vals, 0.2), '|', color="#0072B2",
                        markersize=10, markeredgewidth=1.8, zorder=5)
                ax.axvline(m_asm, color="#0072B2", linestyle="--", linewidth=1.6, zorder=4)

            if n_ref > 0:
                ax.hist(
                    ref_vals, bins=bin_edges, color="#D55E00", alpha=0.85,
                    edgecolor="#7A3500", linewidth=1.2,
                    label=f"REF Pure C (Mean: {m_ref:.1f} ms, N={n_ref})"
                )
                ax.plot(ref_vals, np.full_like(ref_vals, 0.4), '|', color="#D55E00",
                        markersize=10, markeredgewidth=1.8, zorder=5)
                ax.axvline(m_ref, color="#D55E00", linestyle="--", linewidth=1.6, zorder=4)

            speedup_str = ""
            if m_asm > 0 and m_ref > 0:
                sp = m_ref / m_asm
                speedup_str = f" | Speedup: {sp:.2f}x faster in ASM" if sp > 1.05 else " | Equivalent baseline"

            ax.set_title(
                f"{op_titles[op]} — Real Execution Latency Distribution ({speedup_str.lstrip(' | ')})",
                fontsize=10.5,
                fontweight="bold",
                pad=6,
                bbox=dict(boxstyle="square,pad=0.3", facecolor="#F4F4F4", edgecolor="#D0D0D0", linewidth=0.7)
            )
            ax.set_ylabel("Observed Trials (Count)", fontsize=9.2, fontweight="medium")
            ax.grid(True, linestyle="--", alpha=0.45)
            ax.legend(loc="upper right", fontsize=8.5, framealpha=0.92, edgecolor="#CCCCCC")

        # Set common shared Y-axis (integer counts)
        y_top = max(5, max_count) + 1
        axes[0].set_ylim(0, y_top)
        axes[0].set_yticks(list(range(1, y_top)))

        # Set common shared X-axis (0 to x_max ms)
        axes[-1].set_xlim(0, x_max)
        axes[-1].set_xlabel("Physical Execution Latency (ms) [Shared Zero-Baseline Scale across All Operations]", fontsize=10.5, fontweight="bold")

        fig.suptitle(
            f"Unified Real-Scale Latency Histograms: {alg.upper()} (ASM vs. Pure C REF)",
            fontsize=12.5,
            fontweight="bold",
            x=0.08,
            ha="left",
            y=0.96
        )
        fig.text(
            0.08, 0.925,
            f"Zero-baseline shared scale [0 - {x_max} ms] and real integer trial counts (no density normalization). "
            "Directly visualizes the true physical time proportions between operations and variants.",
            fontsize=8.5,
            color="#555555",
            ha="left"
        )

        png_name = f"{out_path}_unified_{alg}.png" if len(algs) > 1 else f"{out_path}_unified_real_scale.png"
        pdf_name = f"{out_path}_unified_{alg}.pdf" if len(algs) > 1 else f"{out_path}_unified_real_scale.pdf"
        plt.savefig(png_name, dpi=300)
        plt.savefig(pdf_name)
        plt.close()
        print(f"[plot_histogram] Unified real-scale histogram for {alg} saved to:\n  - {png_name}\n  - {pdf_name}")

def plot_boxplot_with_raw_points(rows, out_path):
    """Plot boxplots with all individual raw data points overlaid as a jittered strip plot."""
    variants = sorted(list({r.get("variant", "default") for r in rows}))
    ordered_ops = ["keygen", "encaps", "decaps", "msgcrypt"]

    fig, axes = plt.subplots(1, 4, figsize=(13.5, 4.8))
    fig.subplots_adjust(left=0.06, right=0.97, top=0.84, bottom=0.14, wspace=0.32)

    rng = np.random.default_rng(42)

    for idx, op in enumerate(ordered_ops):
        ax = axes[idx]
        color = OKABE_ITO.get(op, "#333333")
        label = OP_LABELS.get(op, op)

        box_data = []
        labels = []
        for var in variants:
            vals = [float(r["latency_ms"]) for r in rows if r.get("operation") == op and r.get("variant", "default") == var]
            box_data.append(vals)
            labels.append(var.upper())

        # Render boxplot
        bp = ax.boxplot(
            box_data,
            labels=labels,
            patch_artist=True,
            showmeans=True,
            meanline=True,
            medianprops=dict(color="#111111", linewidth=1.8),
            meanprops=dict(color="#D55E00", linewidth=1.5, linestyle="--"),
            whiskerprops=dict(color="#555555", linewidth=1.2),
            capprops=dict(color="#555555", linewidth=1.2),
            flierprops=dict(marker='x', color='red', markersize=6)
        )

        for patch in bp['boxes']:
            patch.set_facecolor(color)
            patch.set_alpha(0.35)
            patch.set_edgecolor(color)
            patch.set_linewidth(1.3)

        # Overlay ALL individual raw observation points with jitter
        for var_idx, vals in enumerate(box_data, start=1):
            if not vals:
                continue
            jitter = rng.uniform(-0.12, 0.12, size=len(vals))
            ax.scatter(
                np.full_like(vals, var_idx) + jitter,
                vals,
                color=color,
                edgecolors="#222222",
                linewidths=0.7,
                s=36,
                alpha=0.9,
                zorder=4,
                label="Raw Observation" if var_idx == 1 and idx == 0 else ""
            )

        ax.set_title(label, fontsize=10, fontweight="bold", pad=8,
                     bbox=dict(boxstyle="square,pad=0.3", facecolor="#F5F5F5", edgecolor="#DDDDDD", linewidth=0.6))
        ax.set_ylabel("Latency (ms)" if idx == 0 else "", fontsize=9, fontweight="medium")
        ax.grid(True, linestyle="--", alpha=0.4, axis="y")

    fig.suptitle(
        "Individual Raw Observations & Distribution Spread by Operation (Boxplot + Strip Points)",
        fontsize=12,
        fontweight="bold",
        x=0.06,
        ha="left",
        y=0.96
    )
    fig.text(
        0.06, 0.90,
        "Every single measurement is plotted as a distinct point over the boxplot (Median: solid black, Mean: dashed vermilion).",
        fontsize=8.5,
        color="#555555",
        ha="left"
    )

    png_path = f"{out_path}_boxplot_points.png"
    pdf_path = f"{out_path}_boxplot_points.pdf"
    plt.savefig(png_path, dpi=300)
    plt.savefig(pdf_path)
    plt.close()
    print(f"[plot_histogram] Boxplot with raw individual points saved to:\n  - {png_path}\n  - {pdf_path}")

def main():
    ap = argparse.ArgumentParser(description="Generate distribution histograms for Experiment 0")
    ap.add_argument("--in", dest="inp", default="data/raw/exp0_raw_runs.csv", help="Input raw CSV")
    ap.add_argument("--out", default="data/processed/figures/exp0_histogram", help="Output prefix (without extension)")
    args = ap.parse_args()

    # Read data
    rows = []
    with open(args.inp, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    variants = sorted(list({r.get("variant", "default") for r in rows}))

    # Tidyverse / ggplot2 theme_bw parameters
    plt.rcParams.update({
        "figure.facecolor": "#FFFFFF",
        "axes.facecolor": "#FFFFFF",
        "axes.edgecolor": "#555555",
        "axes.linewidth": 0.8,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": "#EFEFEF",
        "grid.linestyle": "-",
        "grid.linewidth": 0.6,
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Helvetica", "Arial"],
        "font.size": 9.0,
        "xtick.color": "#333333",
        "ytick.color": "#333333",
    })

    ordered_ops = ["keygen", "encaps", "decaps", "msgcrypt"]

    for var in variants:
        var_rows = [r for r in rows if r.get("variant", "default") == var]
        by_op = {}
        for r in var_rows:
            by_op.setdefault(r["operation"], []).append(float(r["latency_ms"]))

        fig, axes = plt.subplots(2, 2, figsize=(10, 7.5))
        fig.subplots_adjust(left=0.08, right=0.96, top=0.88, bottom=0.09, hspace=0.36, wspace=0.22)

        for idx, op in enumerate(ordered_ops):
            ax = axes[idx // 2, idx % 2]
            data = np.array(by_op.get(op, []))
            if len(data) == 0:
                continue
            color = OKABE_ITO[op]
            label = OP_LABELS[op]

            n = len(data)
            mean_val = np.mean(data)
            std_val = np.std(data, ddof=1) if n > 1 else 0.0
            median_val = np.median(data)
            t_crit = 2.045 if n == 30 else (2.262 if n == 10 else 1.96)
            ci95 = t_crit * (std_val / math.sqrt(n)) if n > 1 else 0.0

            # 1. Real Trial Counts (density=False, no probability density)
            bins = max(5, freedman_diaconis_bins(data)) if std_val > 0 else 5
            counts, bin_edges, patches = ax.hist(
                data,
                bins=bins,
                density=False,
                color=color,
                alpha=0.65,
                edgecolor=color,
                linewidth=1.2,
                zorder=2
            )

            # 2. Rug plot on x-axis (individual observations)
            max_c = max(counts) if len(counts) > 0 and max(counts) > 0 else 1.0
            ax.plot(data, np.zeros_like(data) + 0.1, '|', color="#222222",
                    markersize=10, markeredgewidth=1.4, zorder=4)

            # 3. Central tendency markers: Mean with 95% CI & Median
            ax.axvline(mean_val, color="#000000", linestyle="--", linewidth=1.4, zorder=5, label=f"Mean: {mean_val:.2f} ms")
            if ci95 > 0:
                ax.axvspan(mean_val - ci95, mean_val + ci95, color="#555555", alpha=0.18, zorder=1, label=f"95% CI [±{ci95:.3f}]")
            ax.axvline(median_val, color="#D55E00" if color != "#D55E00" else "#0072B2",
                       linestyle=":", linewidth=1.5, zorder=5, label=f"Median: {median_val:.2f} ms")

            ax.set_title(
                f"{label}  (N = {n}, $\\bar{{x}} = {mean_val:.2f}$ ms, $s = {std_val:.3f}$ ms)",
                fontsize=10,
                fontweight="bold",
                pad=8,
                bbox=dict(boxstyle="square,pad=0.35", facecolor="#F2F2F2", edgecolor="#CCCCCC", linewidth=0.7)
            )

            ax.set_xlabel("Execution Latency (ms)", fontsize=9.2, fontweight="medium")
            ax.set_ylabel("Observed Trials (Count)", fontsize=9.2, fontweight="medium")
            y_max_int = max(4, int(max_c)) + 1
            ax.set_ylim(bottom=0, top=y_max_int)
            ax.set_yticks(list(range(1, y_max_int + 1)))
            ax.legend(loc="upper right", fontsize=7.5, framealpha=0.9, edgecolor="#CCCCCC")

        # Global Jain / Tidyverse Typography
        fig.suptitle(
            f"Empirical Execution Latency Distributions: ML-KEM-512 ({var.upper()} variant)",
            fontsize=12.5,
            fontweight="bold",
            x=0.08,
            ha="left",
            y=0.97
        )
        fig.text(
            0.08, 0.93,
            f"System Under Test (SUT): Microchip ATmega4809 (8-bit AVRxt @ 20.0 MHz, -O3, {var} variant) | Jain DoE: N={len(var_rows)//4} replications",
            fontsize=8.5,
            color="#555555",
            ha="left"
        )
        fig.text(
            0.08, 0.02,
            "Note: Y-axis represents real trial counts (density=False). Shaded regions depict 95% Student's t Confidence Intervals. Rug plot at baseline indicates individual observations.",
            fontsize=7.8,
            color="#777777",
            ha="left"
        )

        out_suffix = f"_{var}" if len(variants) > 1 else ""
        out_png = f"{args.out}{out_suffix}.png"
        out_pdf = f"{args.out}{out_suffix}.pdf"
        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
        plt.savefig(out_png, dpi=300)
        plt.savefig(out_pdf)
        plt.close()
        print(f"[plot_histogram] Plots successfully saved to:\n  - {out_png}\n  - {out_pdf}")

    # Generate unified real-scale comparative histogram
    plot_unified_real_scale_histogram(rows, args.out)

    # Generate additional visualizations exposing every single raw observation:
    plot_raw_timeseries(rows, args.out)
    plot_boxplot_with_raw_points(rows, args.out)

if __name__ == "__main__":
    main()

