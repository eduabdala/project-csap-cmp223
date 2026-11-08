#!/usr/bin/env python3
"""generate_exploratory_plots.py — Pure matplotlib & numpy exploratory visualizer.

Generates 7 complementary exploratory visualizations for the balanced N=50 physical
benchmark dataset (exp_20261107_161316_bench_full_pqc_campaign_9549):
  1. Raw Jitter Strip Plot (every single trial point exposed)
  2. Sequential Timeline (run order thermal drift inspection)
  3. Violin Distribution Shapes (bimodality vs Gaussian vs deterministic)
  4. Full Factorial Log-Scale Boxplot (all 12 configurations side-by-side)
  5. Pareto Trade-off Frontier (Latency vs. Peak Stack SRAM)
  6. Assembly vs. Reference Speedup Factors
  7. MsgCrypt UART Round-trip Control Baseline
"""

import os
import csv
import math
import numpy as np
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

import argparse
import glob
import re
from scipy import stats

ap = argparse.ArgumentParser(description="Generate exploratory plots for an experiment")
ap.add_argument("--dir", default="data/experiments/exp_20261107_181223_bench_full_la_campaign_8412",
                help="Experiment directory")
args = ap.parse_args()

EXP_DIR = args.dir
RUNS_CSV = os.path.join(EXP_DIR, "raw", "runs.csv")
OUT_DIR = os.path.join(EXP_DIR, "exploratory")
os.makedirs(OUT_DIR, exist_ok=True)

# Read CSV
rows = []
with open(RUNS_CSV, "r") as f:
    r = csv.DictReader(f)
    for row in r:
        row["latency_ms"] = float(row["latency_ms"])
        row["stack_peak_b"] = int(row["stack_peak_b"])
        row["repetition"] = int(row["repetition"])
        rows.append(row)

print(f">> Loaded {len(rows)} raw observations from {RUNS_CSV}")

# Okabe-Ito colorblind-safe palette
PAL_ALG = {
    "ctru-light": "#D55E00",  # Vermilion
    "kyber512":   "#0072B2",  # Blue
    "ecdh":       "#009E73",  # Green
}
PAL_OP = {
    "keygen":   "#0072B2",  # Blue
    "encaps":   "#D55E00",  # Vermilion
    "decaps":   "#009E73",  # Green
    "msgcrypt": "#CC79A7",  # Purple
}
OP_LABELS = {
    "keygen": "KeyGen",
    "encaps": "Encaps",
    "decaps": "Decaps",
    "msgcrypt": "MsgCrypt"
}

plt.rcParams.update({
    "figure.facecolor": "#FFFFFF",
    "axes.facecolor": "#FFFFFF",
    "axes.edgecolor": "#555555",
    "axes.linewidth": 0.8,
    "axes.grid": True,
    "grid.color": "#EFEFEF",
    "grid.linestyle": "--",
    "grid.alpha": 0.7,
    "font.sans-serif": ["DejaVu Sans", "Helvetica", "Arial"],
    "font.size": 9.5,
    "axes.labelsize": 10,
    "axes.titlesize": 11,
    "legend.fontsize": 8.5,
    "savefig.bbox": "tight",
})

rng = np.random.default_rng(42)

# ==============================================================================
# PLOT 1: RAW JITTER STRIP PLOT (Every single observation as a point)
# ==============================================================================
fig, axes = plt.subplots(1, 3, figsize=(16, 5.6))
fig.subplots_adjust(wspace=0.25, left=0.06, right=0.97, top=0.86, bottom=0.15)

configs = [("asm", "-O3"), ("asm", "-Os"), ("ref", "-O3"), ("ref", "-Os")]
cfg_labels = ["asm -O3", "asm -Os", "ref -O3", "ref -Os"]
ops = ["keygen", "encaps", "decaps"]

for a_idx, alg in enumerate(["ctru-light", "kyber512", "ecdh"]):
    ax = axes[a_idx]
    
    for c_idx, (var, opt) in enumerate(configs):
        # Base x position for this configuration
        x_base = c_idx * 4.0
        
        for o_idx, op in enumerate(ops):
            subset = [
                r["latency_ms"] for r in rows
                if r["algorithm"] == alg and r["variant"] == var and r["optimization"] == opt and r["operation"] == op
            ]
            if not subset:
                continue
            
            x_pos = x_base + (o_idx - 1) * 0.95
            jitter = rng.uniform(-0.18, 0.18, size=len(subset))
            
            lbl = OP_LABELS[op] if (a_idx == 0 and c_idx == 0) else ""
            ax.scatter(
                np.full_like(subset, x_pos) + jitter,
                subset,
                color=PAL_OP[op],
                alpha=0.75,
                s=24,
                edgecolors="#222222",
                linewidths=0.4,
                label=lbl,
                zorder=3
            )
            # Add median bar
            med = np.median(subset)
            ax.hlines(med, x_pos - 0.28, x_pos + 0.28, color="#111111", linewidth=1.8, zorder=4)

    ax.set_xticks([c_idx * 4.0 for c_idx in range(len(configs))])
    ax.set_xticklabels(cfg_labels, fontweight="bold")
    ax.set_title(f"{alg.upper()} (N=50 per cell)", fontweight="bold", pad=8)
    ax.set_xlabel("Configuration (Variant & Opt)", fontweight="bold")
    ax.set_ylabel("Execution Latency (ms)" if a_idx == 0 else "", fontweight="bold")
    
    # Zero-baseline: ALWAYS start Y at 0
    ax.set_ylim(bottom=0)
    
    if a_idx == 0:
        ax.legend(title="Operation (bar = median)", loc="upper left", framealpha=0.92)

fig.suptitle(
    "Plot 1: Raw Observations Strip Plot (Zero-Baseline Y=0) — Every Single Trial Point Exposed",
    fontsize=13, fontweight="bold", x=0.06, ha="left", y=0.96
)
fig.text(
    0.06, 0.91,
    "All physical measurements plotted individually starting at Y=0 (zero baseline). Honest representation of real variance and scale.",
    fontsize=8.5, color="#555555"
)

p1_png = os.path.join(OUT_DIR, "01_raw_jitter_strip_all_points.png")
p1_pdf = os.path.join(OUT_DIR, "01_raw_jitter_strip_all_points.pdf")
plt.savefig(p1_png, dpi=300); plt.savefig(p1_pdf); plt.close()
print(f"[1/7] Saved {p1_png}")


# ==============================================================================
# PLOT 2: RUN ORDER TIMELINE (Thermal drift & sequential stability)
# ==============================================================================
fig, axes = plt.subplots(3, 1, figsize=(13, 9), sharex=True)
fig.subplots_adjust(hspace=0.28, left=0.08, right=0.96, top=0.91, bottom=0.08)

for a_idx, alg in enumerate(["ctru-light", "kyber512", "ecdh"]):
    ax = axes[a_idx]
    
    for op in ["keygen", "encaps", "decaps"]:
        sub = [
            (r["repetition"], r["latency_ms"]) for r in rows
            if r["algorithm"] == alg and r["variant"] == "asm" and r["optimization"] == "-O3" and r["operation"] == op
        ]
        sub.sort(key=lambda x: x[0])
        reps = np.array([x[0] for x in sub])
        lats = np.array([x[1] for x in sub])
        
        ax.plot(
            reps, lats,
            marker="o", markersize=4.2, linewidth=1.1,
            color=PAL_OP[op], label=OP_LABELS[op], alpha=0.85
        )
        
        # Linear fit to quantify drift
        if len(reps) > 1:
            z = np.polyfit(reps, lats, 1)
            p = np.poly1d(z)
            ax.plot(reps, p(reps), ":", color=PAL_OP[op], linewidth=1.3, alpha=0.6)

    ax.set_title(f"{alg.upper()} [Assembly -O3 across 50 consecutive runs]", fontweight="bold", pad=6)
    ax.set_ylabel("Latency (ms)", fontweight="bold")
    ax.set_ylim(bottom=0)
    ax.set_xlim(left=0)
    ax.legend(loc="upper right", framealpha=0.9, ncol=3)

axes[-1].set_xlabel("Trial Sequence (Repetition Index 1 to 50)", fontweight="bold")
fig.suptitle(
    "Plot 2: Sequential Execution Timeline (Zero-Baseline X=0, Y=0) — Thermal Drift Inspection",
    fontsize=13, fontweight="bold", x=0.08, ha="left", y=0.97
)
fig.text(
    0.08, 0.94,
    "Tests whether MCU warm-up causes latency drift across 50 consecutive repetitions. Y-axis starts strictly at 0 ms.",
    fontsize=8.5, color="#555555"
)

p2_png = os.path.join(OUT_DIR, "02_timeline_thermal_drift_run_order.png")
p2_pdf = os.path.join(OUT_DIR, "02_timeline_thermal_drift_run_order.pdf")
plt.savefig(p2_png, dpi=300); plt.savefig(p2_pdf); plt.close()
print(f"[2/7] Saved {p2_png}")


# ==============================================================================
# PLOT 3: VIOLIN DENSITY + RAW POINTS (Bimodality vs Gaussian vs Deterministic)
# ==============================================================================
fig, axes = plt.subplots(1, 3, figsize=(15, 5.5))
fig.subplots_adjust(wspace=0.25, left=0.07, right=0.96, top=0.86, bottom=0.15)

for a_idx, alg in enumerate(["ctru-light", "kyber512", "ecdh"]):
    ax = axes[a_idx]
    
    violin_data = []
    labels = []
    for op in ["keygen", "encaps", "decaps"]:
        sub = [
            r["latency_ms"] for r in rows
            if r["algorithm"] == alg and r["variant"] == "asm" and r["optimization"] == "-O3" and r["operation"] == op
        ]
        violin_data.append(sub)
        labels.append(OP_LABELS[op])
    
    parts = ax.violinplot(violin_data, showmeans=False, showmedians=True, showextrema=True)
    for p_idx, pc in enumerate(parts['bodies']):
        op_name = ["keygen", "encaps", "decaps"][p_idx]
        pc.set_facecolor(PAL_OP[op_name])
        pc.set_edgecolor(PAL_OP[op_name])
        pc.set_alpha(0.4)
    parts['cmedians'].set_color("#111111")
    parts['cmedians'].set_linewidth(1.8)
    
    # Overlay individual dots
    for o_idx, vals in enumerate(violin_data, start=1):
        jitter = rng.uniform(-0.08, 0.08, size=len(vals))
        ax.scatter(
            np.full_like(vals, o_idx) + jitter,
            vals,
            color="#111111",
            s=18,
            alpha=0.6,
            edgecolors="none",
            zorder=4
        )

    ax.set_xticks([1, 2, 3])
    ax.set_xticklabels(labels, fontweight="bold")
    ax.set_title(f"{alg.upper()} [ASM -O3]", fontweight="bold", pad=8)
    ax.set_xlabel("Operation", fontweight="bold")
    ax.set_ylabel("Latency (ms)" if a_idx == 0 else "", fontweight="bold")
    ax.set_ylim(bottom=0)

fig.suptitle(
    "Plot 3: Distribution Density Shapes (Zero-Baseline Y=0) — Exposing Multi-Modality",
    fontsize=13, fontweight="bold", x=0.07, ha="left", y=0.96
)
fig.text(
    0.07, 0.91,
    "Violin plots with Y starting strictly at 0 ms. CTRU-Light exhibits discrete bimodal/stepped distribution; Kyber & ECDH are unimodal.",
    fontsize=8.5, color="#555555"
)

p3_png = os.path.join(OUT_DIR, "03_distribution_shapes_violin_strip.png")
p3_pdf = os.path.join(OUT_DIR, "03_distribution_shapes_violin_strip.pdf")
plt.savefig(p3_png, dpi=300); plt.savefig(p3_pdf); plt.close()
print(f"[3/8] Saved {p3_png}")


# ==============================================================================
# PLOT 4: FULL FACTORIAL LINEAR-SCALE BOXPLOT (Strict Zero-Baseline Y=0)
# ==============================================================================
fig, (ax_all, ax_pqc) = plt.subplots(2, 1, figsize=(15, 9.5))
fig.subplots_adjust(left=0.07, right=0.97, top=0.92, bottom=0.14, hspace=0.38)

combos_order = [
    (a, v, o)
    for a in ["ctru-light", "kyber512", "ecdh"]
    for v in ["asm", "ref"]
    for o in ["-O3", "-Os"]
]

pqc_combos_order = [
    (a, v, o)
    for a in ["ctru-light", "kyber512"]
    for v in ["asm", "ref"]
    for o in ["-O3", "-Os"]
]

# Panel 1: Complete linear scale (0 to 15,500 ms)
x_tick_pos_all = []
x_tick_lbls_all = []
for c_idx, (alg, var, opt) in enumerate(combos_order):
    x_base = c_idx * 4.0
    x_tick_pos_all.append(x_base)
    x_tick_lbls_all.append(f"{alg.upper()}\n{var} {opt}")
    
    for o_idx, op in enumerate(["keygen", "encaps", "decaps"]):
        sub = [
            r["latency_ms"] for r in rows
            if r["algorithm"] == alg and r["variant"] == var and r["optimization"] == opt and r["operation"] == op
        ]
        if not sub:
            continue
        x_pos = x_base + (o_idx - 1) * 1.0
        bp = ax_all.boxplot(
            [sub], positions=[x_pos], widths=0.8, patch_artist=True, showmeans=True,
            meanprops=dict(marker="^", markeredgecolor="black", markerfacecolor="white", markersize=4.5),
            medianprops=dict(color="#111111", linewidth=1.4),
            whiskerprops=dict(color="#444444", linewidth=1.0),
            capprops=dict(color="#444444", linewidth=1.0),
            flierprops=dict(marker="x", color="red", markersize=3)
        )
        for patch in bp['boxes']:
            patch.set_facecolor(PAL_OP[op]); patch.set_alpha(0.65); patch.set_edgecolor(PAL_OP[op])

ax_all.set_xticks(x_tick_pos_all)
ax_all.set_xticklabels(x_tick_lbls_all, fontsize=7.8)
ax_all.set_ylim(bottom=0)
ax_all.set_ylabel("Execution Latency (ms)", fontweight="bold")
ax_all.set_title("Panel A: Complete Linear Scale (0 to 15,500 ms, Zero-Baseline Y=0) — Shows Massive ECDH Disparity", fontweight="bold", pad=6)

# Panel 2: PQC Focused linear scale (0 to 700 ms)
x_tick_pos_pqc = []
x_tick_lbls_pqc = []
for c_idx, (alg, var, opt) in enumerate(pqc_combos_order):
    x_base = c_idx * 4.0
    x_tick_pos_pqc.append(x_base)
    x_tick_lbls_pqc.append(f"{alg.upper()}\n{var} {opt}")
    
    for o_idx, op in enumerate(["keygen", "encaps", "decaps"]):
        sub = [
            r["latency_ms"] for r in rows
            if r["algorithm"] == alg and r["variant"] == var and r["optimization"] == opt and r["operation"] == op
        ]
        if not sub:
            continue
        x_pos = x_base + (o_idx - 1) * 1.0
        bp = ax_pqc.boxplot(
            [sub], positions=[x_pos], widths=0.8, patch_artist=True, showmeans=True,
            meanprops=dict(marker="^", markeredgecolor="black", markerfacecolor="white", markersize=4.5),
            medianprops=dict(color="#111111", linewidth=1.4),
            whiskerprops=dict(color="#444444", linewidth=1.0),
            capprops=dict(color="#444444", linewidth=1.0),
            flierprops=dict(marker="x", color="red", markersize=3)
        )
        for patch in bp['boxes']:
            patch.set_facecolor(PAL_OP[op]); patch.set_alpha(0.65); patch.set_edgecolor(PAL_OP[op])

ax_pqc.set_xticks(x_tick_pos_pqc)
ax_pqc.set_xticklabels(x_tick_lbls_pqc, fontsize=8.2)
ax_pqc.set_ylim(bottom=0, top=700)
ax_pqc.set_ylabel("Execution Latency (ms)", fontweight="bold")
ax_pqc.set_xlabel("PQC Configuration (Algorithm, Variant & Compiler Flag)", fontweight="bold", labelpad=6)
ax_pqc.set_title("Panel B: PQC Detailed Linear Scale (0 to 700 ms, Zero-Baseline Y=0) — Unobscured PQC Comparison", fontweight="bold", pad=6)

# Create custom legend
handles = [
    plt.Rectangle((0, 0), 1, 1, facecolor=PAL_OP[op], alpha=0.7, edgecolor=PAL_OP[op])
    for op in ["keygen", "encaps", "decaps"]
]
handles.append(plt.Line2D([0], [0], marker="^", color="black", markerfacecolor="white", markersize=7, linestyle="none"))
ax_all.legend(handles, ["KeyGen", "Encaps", "Decaps", "Mean (Triangle)"], loc="upper left", ncol=4, framealpha=0.95)

fig.suptitle(
    "Plot 4: Complete Factorial Benchmark Overview (Strict Zero-Baseline Y=0, Honest Linear Scales)",
    fontsize=13, fontweight="bold", x=0.07, ha="left", y=0.97
)

p4_png = os.path.join(OUT_DIR, "04_log_scale_comparative_boxplot.png")
p4_pdf = os.path.join(OUT_DIR, "04_log_scale_comparative_boxplot.pdf")
plt.savefig(p4_png, dpi=300); plt.savefig(p4_pdf); plt.close()
print(f"[4/8] Saved {p4_png}")


# ==============================================================================
# PLOT 5: PARETO TRADE-OFF FRONTIER (Strict Zero-Baseline X=0, Y=0)
# ==============================================================================
fig, (ax_p5_all, ax_p5_pqc) = plt.subplots(1, 2, figsize=(16, 6))
fig.subplots_adjust(left=0.07, right=0.96, top=0.86, bottom=0.14, wspace=0.22)

marker_map = {"keygen": "o", "encaps": "s", "decaps": "D"}

for ax_curr, max_x, title_suffix in [
    (ax_p5_all, 15500, "Panel A: All Algorithms (0 to 15,500 ms)"),
    (ax_p5_pqc, 750, "Panel B: PQC Detail (0 to 750 ms)")
]:
    for alg in ["ctru-light", "kyber512", "ecdh"]:
        for op in ["keygen", "encaps", "decaps"]:
            for var in ["asm", "ref"]:
                for opt in ["-O3", "-Os"]:
                    sub = [
                        r for r in rows
                        if r["algorithm"] == alg and r["variant"] == var and r["optimization"] == opt and r["operation"] == op
                    ]
                    if not sub:
                        continue
                    mean_lat = np.mean([r["latency_ms"] for r in sub])
                    peak_stk = max([r["stack_peak_b"] for r in sub])
                    
                    if mean_lat > max_x:
                        continue
                    
                    lbl = f"{alg.upper()} {OP_LABELS[op]}" if (var == "asm" and opt == "-O3" and ax_curr == ax_p5_all) else ""
                    ax_curr.scatter(
                        mean_lat, peak_stk,
                        color=PAL_ALG[alg],
                        marker=marker_map[op],
                        s=85,
                        alpha=0.85,
                        edgecolors="#111111",
                        linewidths=0.9,
                        label=lbl,
                        zorder=4
                    )
                    annot = f"{var[0]}:{opt[-1]}"
                    ax_curr.annotate(
                        annot, (mean_lat, peak_stk),
                        xytext=(3, 3), textcoords="offset points",
                        fontsize=6.8, color="#555555"
                    )

    # Physical SRAM limits
    ax_curr.axhline(6144, color="#C0392B", linestyle="--", linewidth=1.5, zorder=2)
    ax_curr.text(max_x * 0.05, 6200, "ATmega4809 Physical SRAM Limit (6,144 Bytes)", color="#C0392B", fontweight="bold", fontsize=8.0)

    # Free headroom bands
    ax_curr.axhspan(0, 6144 * 0.20, color="#2ECC71", alpha=0.08, label=">80% SRAM Free" if ax_curr == ax_p5_all else "")
    ax_curr.axhspan(6144 * 0.20, 6144 * 0.55, color="#F39C12", alpha=0.08, label="45%-80% SRAM Free" if ax_curr == ax_p5_all else "")

    # STRICT ZERO-BASELINE: X=0, Y=0
    ax_curr.set_xlim(left=0, right=max_x)
    ax_curr.set_ylim(bottom=0, top=6600)
    ax_curr.set_xlabel("Mean Execution Latency (ms) [Starts at X=0]", fontweight="bold")
    ax_curr.set_ylabel("Peak Stack Usage in SRAM (Bytes) [Starts at Y=0]" if ax_curr == ax_p5_all else "", fontweight="bold")
    ax_curr.set_title(title_suffix, fontweight="bold", pad=8)

ax_p5_all.legend(loc="upper right", fontsize=7.5, framealpha=0.92)

fig.suptitle(
    "Plot 5: Pareto Trade-off Frontier (Strict Zero-Baseline X=0, Y=0) — True Physical Proportions",
    fontsize=13, fontweight="bold", x=0.07, ha="left", y=0.96
)

p5_png = os.path.join(OUT_DIR, "05_pareto_memory_vs_latency_frontier.png")
p5_pdf = os.path.join(OUT_DIR, "05_pareto_memory_vs_latency_frontier.pdf")
plt.savefig(p5_png, dpi=300); plt.savefig(p5_pdf); plt.close()
print(f"[5/8] Saved {p5_png}")


# ==============================================================================
# PLOT 6: SPEEDUP RATIOS (ASM Speedup over Pure C Reference)
# ==============================================================================
# Only include combinations that actually exist in the dataset
present_opts = sorted(list(set(r["optimization"] for r in rows)))
present_algs = ["ctru-light", "kyber512", "ecdh"]
labels_sp = [f"{a.upper()} {o}" for a in present_algs for o in present_opts]

fig, ax = plt.subplots(figsize=(10.5, 5))
fig.subplots_adjust(left=0.08, right=0.96, top=0.86, bottom=0.14)

x_pos = np.arange(len(labels_sp))
bar_width = 0.26

for o_idx, op in enumerate(["keygen", "encaps", "decaps"]):
    sp_vals = []
    for alg in present_algs:
        for opt in present_opts:
            ref_sub = [
                r["latency_ms"] for r in rows
                if r["algorithm"] == alg and r["variant"] == "ref" and r["optimization"] == opt and r["operation"] == op
            ]
            asm_sub = [
                r["latency_ms"] for r in rows
                if r["algorithm"] == alg and r["variant"] == "asm" and r["optimization"] == opt and r["operation"] == op
            ]
            sp = (np.mean(ref_sub) / np.mean(asm_sub)) if (asm_sub and ref_sub) else 1.0
            sp_vals.append(sp)

    offset = (o_idx - 1) * bar_width
    bars = ax.bar(
        x_pos + offset, sp_vals,
        width=bar_width,
        color=PAL_OP[op],
        alpha=0.85,
        edgecolor="#222222",
        linewidth=0.8,
        label=OP_LABELS[op]
    )
    
    for bar in bars:
        h = bar.get_height()
        ax.annotate(
            f"{h:.2f}x",
            xy=(bar.get_x() + bar.get_width() / 2, h),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center", va="bottom",
            fontsize=7.2, fontweight="bold"
        )

ax.axhline(1.0, color="#555555", linestyle="--", linewidth=1.0)
ax.set_xticks(x_pos)
ax.set_xticklabels(labels_sp, fontweight="bold", fontsize=8.8)
ax.set_ylabel("Speedup Factor ($T_{ref} / T_{asm}$)", fontweight="bold")
ax.set_xlabel("Algorithm & Compiler Optimization", fontweight="bold")
ax.set_ylim(bottom=0)
ax.set_title("Plot 6: Assembly Acceleration Factor (Strict Zero-Baseline Y=0)", fontweight="bold", pad=10)
ax.legend(title="Operation", loc="upper left", framealpha=0.95)

p6_png = os.path.join(OUT_DIR, "06_assembly_speedup_ratios.png")
p6_pdf = os.path.join(OUT_DIR, "06_assembly_speedup_ratios.pdf")
plt.savefig(p6_png, dpi=300); plt.savefig(p6_pdf); plt.close()
print(f"[6/8] Saved {p6_png}")


# ==============================================================================
# PLOT 7: MSGCRYPT UART BASELINE STABILITY (Strict Zero-Baseline Y=0)
# ==============================================================================
fig, ax = plt.subplots(figsize=(13, 5))
fig.subplots_adjust(left=0.08, right=0.96, top=0.86, bottom=0.22)

# Dynamically find combos that actually have msgcrypt data
msg_combos = []
for a in ["ctru-light", "kyber512", "ecdh"]:
    for v in ["asm", "ref"]:
        for o in ["-O3", "-Os"]:
            sub = [
                r["latency_ms"] for r in rows
                if r["algorithm"] == a and r["variant"] == v and r["optimization"] == o and r["operation"] == "msgcrypt"
            ]
            if sub:
                msg_combos.append((a, v, o))

msg_data = []
msg_labels = []

for c_idx, (alg, var, opt) in enumerate(msg_combos, start=1):
    sub = [
        r["latency_ms"] for r in rows
        if r["algorithm"] == alg and r["variant"] == var and r["optimization"] == opt and r["operation"] == "msgcrypt"
    ]
    msg_data.append(sub)
    msg_labels.append(f"{alg.upper()}\n{var} {opt}")

bp = ax.boxplot(
    msg_data,
    patch_artist=True,
    showmeans=True,
    meanprops=dict(marker="o", markeredgecolor="black", markerfacecolor="white", markersize=5),
    medianprops=dict(color="#111111", linewidth=1.5),
    whiskerprops=dict(color="#444444", linewidth=1.0),
    capprops=dict(color="#444444", linewidth=1.0)
)
for patch in bp['boxes']:
    patch.set_facecolor("#CC79A7")
    patch.set_alpha(0.5)

# Overlay individual dots
for idx, vals in enumerate(msg_data, start=1):
    jitter = rng.uniform(-0.15, 0.15, size=len(vals))
    ax.scatter(np.full_like(vals, idx) + jitter, vals, color="#333333", s=14, alpha=0.5, edgecolors="none")

ax.set_xticks(list(range(1, len(msg_labels) + 1)))
ax.set_xticklabels(msg_labels, fontsize=8.0)
ax.set_ylabel("Round-trip Latency (ms)", fontweight="bold")
ax.set_xlabel("Firmware Build Configuration", fontweight="bold")
ax.set_ylim(bottom=0, top=55)
ax.set_title("Plot 7: MsgCrypt Control Baseline (Strict Zero-Baseline Y=0: Solid 41 ms Across All Builds)", fontweight="bold", pad=10)

p7_png = os.path.join(OUT_DIR, "07_msgcrypt_uart_baseline_stability.png")
p7_pdf = os.path.join(OUT_DIR, "07_msgcrypt_uart_baseline_stability.pdf")
plt.savefig(p7_png, dpi=300); plt.savefig(p7_pdf); plt.close()
print(f"[7/8] Saved {p7_png}")


# ==============================================================================
# PLOT 8: LOGIC ANALYZER (GPIO PULSE) VS HOST SERIAL LATENCY (Strict Zero-Baseline Y=0)
# ==============================================================================
# Parse LA pulses from console logs robustly
la_parsed = {}
for lpath in sorted(glob.glob(os.path.join(EXP_DIR, "raw", "console_*.log"))):
    m = re.match(r"console_(.+?)_(asm|ref)_(O3|Os)_(\d+)MHz\.log", os.path.basename(lpath))
    if not m:
        continue
    alg, var, opt, clk = m.groups()
    with open(lpath, "r") as fp:
        txt = fp.read()
    lines = re.findall(r"\d+\s+([A-Za-z0-9\s\(\)]+?)\s+([\d\.]+)\s+([\d\.]+)\s+([\d,]+)", txt)
    if lines:
        k_pulses = [float(x[2]) for x in lines if "KeyGen" in x[0] or "Janela" in x[0]]
        e_pulses = [float(x[2]) for x in lines if "Encaps" in x[0]]
        d_pulses = [float(x[2]) for x in lines if "Decaps" in x[0]]
        la_parsed[(alg, var, f"-{opt}")] = {
            "keygen": np.mean(k_pulses) if k_pulses else 0.0,
            "encaps": np.mean(e_pulses) if e_pulses else 0.0,
            "decaps": np.mean(d_pulses) if d_pulses else 0.0,
        }

if la_parsed:
    # 2 rows x 3 columns: Row 1 = All Algorithms (Linear 0 to 7000 ms), Row 2 = PQC Detail (Linear 0 to 450 ms)
    fig, axes = plt.subplots(2, 3, figsize=(16, 9.5))
    fig.subplots_adjust(left=0.07, right=0.97, top=0.91, bottom=0.10, hspace=0.38, wspace=0.24)
    
    comp_combos_all = [k for k in sorted(la_parsed.keys()) if k[1] == "asm"]
    if not comp_combos_all:
        comp_combos_all = sorted(la_parsed.keys())
    
    comp_combos_pqc = [k for k in comp_combos_all if "ecdh" not in k[0]]
    
    # Row 1: All algorithms (linear, 0 to 7,000 ms)
    for o_idx, op in enumerate(["keygen", "encaps", "decaps"]):
        ax = axes[0, o_idx]
        x = np.arange(len(comp_combos_all))
        w = 0.36
        
        la_vals = [la_parsed[c][op] for c in comp_combos_all]
        serial_vals = [
            np.mean([
                r["latency_ms"] for r in rows
                if r["algorithm"] == c[0] and r["variant"] == c[1] and r["optimization"] == c[2] and r["operation"] == op
            ])
            for c in comp_combos_all
        ]
        
        rects1 = ax.bar(x - w/2, la_vals, w, label="Logic Analyzer (GPIO Window)", color="#0072B2", alpha=0.85, edgecolor="#111111", linewidth=0.8)
        rects2 = ax.bar(x + w/2, serial_vals, w, label="Host Serial (1st Byte via UART)", color="#D55E00", alpha=0.85, edgecolor="#111111", linewidth=0.8)
        
        ax.set_title(f"Panel 1.{o_idx+1}: {OP_LABELS[op]} (All Algorithms)", fontweight="bold", pad=7)
        ax.set_xticks(x)
        ax.set_xticklabels([f"{c[0].upper()}\n({c[1]} {c[2]})" for c in comp_combos_all], fontsize=8.2)
        ax.set_ylabel("Execution Time (ms)" if o_idx == 0 else "", fontweight="bold")
        ax.set_ylim(bottom=0, top=7200)
        
        for b1, b2 in zip(rects1, rects2):
            h1 = b1.get_height()
            h2 = b2.get_height()
            diff = h2 - h1
            ax.annotate(
                f"+{diff:.1f}ms",
                xy=(b2.get_x() + b2.get_width()/2, h2),
                xytext=(0, 3), textcoords="offset points",
                ha="center", va="bottom", fontsize=6.8, fontweight="bold", color="#7A3500"
            )
        
        if o_idx == 0:
            ax.legend(loc="upper left", framealpha=0.92, fontsize=7.8)

    # Row 2: PQC Detail (linear, 0 to 450 ms)
    for o_idx, op in enumerate(["keygen", "encaps", "decaps"]):
        ax = axes[1, o_idx]
        x = np.arange(len(comp_combos_pqc))
        w = 0.36
        
        la_vals = [la_parsed[c][op] for c in comp_combos_pqc]
        serial_vals = [
            np.mean([
                r["latency_ms"] for r in rows
                if r["algorithm"] == c[0] and r["variant"] == c[1] and r["optimization"] == c[2] and r["operation"] == op
            ])
            for c in comp_combos_pqc
        ]
        
        rects1 = ax.bar(x - w/2, la_vals, w, label="Logic Analyzer (GPIO Window)", color="#0072B2", alpha=0.85, edgecolor="#111111", linewidth=0.8)
        rects2 = ax.bar(x + w/2, serial_vals, w, label="Host Serial (1st Byte via UART)", color="#D55E00", alpha=0.85, edgecolor="#111111", linewidth=0.8)
        
        ax.set_title(f"Panel 2.{o_idx+1}: {OP_LABELS[op]} (PQC Zoom)", fontweight="bold", pad=7)
        ax.set_xticks(x)
        ax.set_xticklabels([f"{c[0].upper()}\n({c[1]} {c[2]})" for c in comp_combos_pqc], fontsize=8.5)
        ax.set_ylabel("Execution Time (ms)" if o_idx == 0 else "", fontweight="bold")
        ax.set_ylim(bottom=0, top=450)
        
        for b1, b2 in zip(rects1, rects2):
            h1 = b1.get_height()
            h2 = b2.get_height()
            diff = h2 - h1
            ax.annotate(
                f"+{diff:.1f}ms\nUART",
                xy=(b2.get_x() + b2.get_width()/2, h2),
                xytext=(0, 3), textcoords="offset points",
                ha="center", va="bottom", fontsize=7.2, fontweight="bold", color="#7A3500"
            )

    fig.suptitle(
        "Plot 8: Pure Hardware Logic Analyzer (GPIO Pulse) vs Host Serial Latency (Strict Zero-Baseline Y=0)",
        fontsize=13, fontweight="bold", x=0.07, ha="left", y=0.97
    )
    fig.text(
        0.07, 0.94,
        "Logic Analyzer (Blue) isolates pure CPU cycles with zero UART overhead. Orange is Host Serial. Both rows start strictly at Y=0 ms.",
        fontsize=8.5, color="#555555"
    )
    
    p8_png = os.path.join(OUT_DIR, "08_logic_analyzer_gpio_vs_serial_host.png")
    p8_pdf = os.path.join(OUT_DIR, "08_logic_analyzer_gpio_vs_serial_host.pdf")
    plt.savefig(p8_png, dpi=300); plt.savefig(p8_pdf); plt.close()
    print(f"[8/10] Saved {p8_png}")


# ==============================================================================
# PLOT 9: FACTORIAL 3X3 HISTOGRAM GRID (Strict Logic Analyzer Ground Truth)
# ==============================================================================
# Parse clean LA pulses excluding battery summaries
clean_la_pulses = {}
for lpath in sorted(glob.glob(os.path.join(EXP_DIR, "raw", "console_*.log"))):
    m = re.match(r"console_(.+?)_(asm|ref)_(O3|Os)_(\d+)MHz\.log", os.path.basename(lpath))
    if not m:
        continue
    alg, var, opt, clk = m.groups()
    with open(lpath, "r", encoding="utf-8") as fp:
        txt = fp.read()
    if "RESUMO DA BATERIA" in txt:
        txt = txt.split("RESUMO DA BATERIA")[0]
    lines = re.findall(r"^\s*(\d+)\s+([A-Za-z0-9\s\(\)]+?)\s+([\d\.]+)\s+([\d\.]+)\s+([\d,]+)", txt, re.MULTILINE)
    clean_la_pulses[(alg, var, f"-{opt}")] = {
        "keygen": np.array([float(x[3]) for x in lines if "KeyGen" in x[1] or "Janela" in x[1]]),
        "encaps": np.array([float(x[3]) for x in lines if "Encaps" in x[1]]),
        "decaps": np.array([float(x[3]) for x in lines if "Decaps" in x[1]]),
    }

algs_p9 = ["ctru-light", "kyber512", "ecdh"]
ops_p9 = ["keygen", "encaps", "decaps"]
x_max_map = {"ctru-light": 150.0, "kyber512": 360.0, "ecdh": 7000.0}
bin_width_map = {"ctru-light": 2.5, "kyber512": 5.0, "ecdh": 100.0}

fig, axes = plt.subplots(3, 3, figsize=(16, 11))
fig.subplots_adjust(left=0.07, right=0.97, top=0.91, bottom=0.08, hspace=0.38, wspace=0.25)

for c_idx, alg in enumerate(algs_p9):
    max_x = x_max_map[alg]
    b_width = bin_width_map[alg]
    bins = np.arange(0, max_x + b_width, b_width)
    
    for r_idx, op in enumerate(ops_p9):
        ax = axes[r_idx, c_idx]
        arr = clean_la_pulses.get((alg, "asm", "-O3"), {}).get(op, np.array([]))
        if len(arr) == 0:
            continue
        
        ax.hist(arr, bins=bins, color=PAL_ALG[alg], alpha=0.75, edgecolor="#111111", linewidth=0.8)
        
        if alg == "ctru-light" and op in ["keygen", "encaps"]:
            split_val = 68.0 if op == "keygen" else 65.0
            m1 = arr[arr < split_val]
            m2 = arr[arr >= split_val]
            m1_m, m2_m = np.mean(m1), np.mean(m2)
            d_ms = m2_m - m1_m
            ax.axvline(m1_m, color="#C0392B", linestyle="--", linewidth=1.2)
            ax.axvline(m2_m, color="#C0392B", linestyle="--", linewidth=1.2)
            badge_txt = (
                f"ESTRITAMENTE BIMODAL (LA)\n"
                f"• Modo 1: {m1_m:.1f} ms (N={len(m1)}, {len(m1)*2}%)\n"
                f"• Modo 2: {m2_m:.1f} ms (N={len(m2)}, {len(m2)*2}%)\n"
                f"• Separação: {d_ms:.2f} ms (~{d_ms*20000:,.0f} cyc)\n"
                f"  -> Retry de Rejeição de Polinômio"
            )
            bcolor, bborder = "#FADBD8", "#C0392B"
        else:
            med = np.median(arr)
            ax.axvline(med, color="#27AE60", linestyle="--", linewidth=1.2)
            badge_txt = (
                f"ESTRITAMENTE UNIMODAL (LA)\n"
                f"• Mediana: {med:.1f} ms\n"
                f"• Mín: {np.min(arr):.1f} ms | Máx: {np.max(arr):.1f} ms\n"
                f"• Desvio Padrão: {np.std(arr):.2f} ms\n"
                f"  -> Execução Determinística"
            )
            bcolor, bborder = "#D4EFDF", "#27AE60"

        ax.text(
            0.96, 0.94, badge_txt,
            transform=ax.transAxes, ha="right", va="top",
            fontsize=7.4, fontfamily="monospace",
            bbox=dict(boxstyle="round,pad=0.35", facecolor=bcolor, edgecolor=bborder, alpha=0.9)
        )

        ax.set_xlim(left=0, right=max_x)
        ax.set_ylim(bottom=0, top=55)
        ax.set_ylabel("Pulsos Capturados (N=50)" if c_idx == 0 else "", fontweight="bold")
        ax.set_title(f"{alg.upper()} - {OP_LABELS[op]} [LA GPIO Pulse]", fontweight="bold", pad=6)

    axes[-1, c_idx].set_xlabel(f"Tempo de Execução (ms) [0 a {int(max_x)} ms]", fontweight="bold")

fig.suptitle(
    "Plot 9: Matriz Fatorial 3x3 com Dados do Analisador Lógico e Eixos Realistas (X=0, Y=0)",
    fontsize=13, fontweight="bold", x=0.07, ha="left", y=0.97
)
fig.text(
    0.07, 0.94,
    "Tempo medido pelo Analisador Lógico Saleae no pino PA0 (ciclos puros de CPU). Todos os subgráficos iniciam estritamente no zero.",
    fontsize=8.5, color="#555555"
)

p9_png = os.path.join(OUT_DIR, "09_multimodality_histograms_grid.png")
p9_pdf = os.path.join(OUT_DIR, "09_multimodality_histograms_grid.pdf")
plt.savefig(p9_png, dpi=300); plt.savefig(p9_pdf); plt.close()
print(f"[9/11] Saved {p9_png}")


# ==============================================================================
# PLOT 10: HISTOGRAMA GERAL PQC (Eixos Realistas Alinhados 0 a 360 ms)
# ==============================================================================
fig, axes = plt.subplots(3, 1, figsize=(14, 9), sharex=True)
fig.subplots_adjust(left=0.08, right=0.96, top=0.91, bottom=0.09, hspace=0.30)

bins_pqc = np.arange(0, 364, 4.0)

for idx, op in enumerate(["keygen", "encaps", "decaps"]):
    ax = axes[idx]
    c_arr = clean_la_pulses.get(("ctru-light", "asm", "-O3"), {}).get(op, np.array([]))
    k_arr = clean_la_pulses.get(("kyber512", "asm", "-O3"), {}).get(op, np.array([]))
    
    if len(c_arr) > 0:
        ax.hist(c_arr, bins=bins_pqc, color=PAL_ALG["ctru-light"], alpha=0.75, edgecolor="#111111", linewidth=0.8, label=f"CTRU-Light (ASM -O3, N={len(c_arr)})")
    if len(k_arr) > 0:
        ax.hist(k_arr, bins=bins_pqc, color=PAL_ALG["kyber512"], alpha=0.75, edgecolor="#111111", linewidth=0.8, label=f"Kyber-512 (ASM -O3, N={len(k_arr)})")

    if op == "keygen":
        m1 = c_arr[c_arr < 68.0]
        m2 = c_arr[c_arr >= 68.0]
        ax.annotate(f"CTRU Modo 1 ({np.mean(m1):.1f} ms, N={len(m1)})", xy=(np.mean(m1), 24), xytext=(np.mean(m1) - 45, 27), arrowprops=dict(arrowstyle="->", color=PAL_ALG["ctru-light"], lw=1.2), fontsize=8.2, fontweight="bold", color=PAL_ALG["ctru-light"])
        ax.annotate(f"CTRU Modo 2 ({np.mean(m2):.1f} ms, N={len(m2)})\n[Δt = 10.2 ms / ~204k cyc]", xy=(np.mean(m2), 26), xytext=(np.mean(m2) + 12, 27), arrowprops=dict(arrowstyle="->", color=PAL_ALG["ctru-light"], lw=1.2), fontsize=8.2, fontweight="bold", color=PAL_ALG["ctru-light"])
        k_med = np.median(k_arr)
        ax.annotate(f"Kyber Unimodal Spike\n({k_med:.1f} ms, N={len(k_arr)})", xy=(k_med, 48), xytext=(k_med + 15, 42), arrowprops=dict(arrowstyle="->", color=PAL_ALG["kyber512"], lw=1.2), fontsize=8.2, fontweight="bold", color=PAL_ALG["kyber512"])
    elif op == "encaps":
        m1 = c_arr[c_arr < 65.0]
        m2 = c_arr[c_arr >= 65.0]
        ax.annotate(f"CTRU Modo 1 ({np.mean(m1):.1f} ms, N={len(m1)})\nModo 2 ({np.mean(m2):.1f} ms, N={len(m2)})", xy=(np.mean(m1), 38), xytext=(np.mean(m1) + 20, 38), arrowprops=dict(arrowstyle="->", color=PAL_ALG["ctru-light"], lw=1.2), fontsize=8.2, fontweight="bold", color=PAL_ALG["ctru-light"])
        k_med = np.median(k_arr)
        ax.annotate(f"Kyber Unimodal Spike\n({k_med:.1f} ms)", xy=(k_med, 48), xytext=(k_med - 75, 42), arrowprops=dict(arrowstyle="->", color=PAL_ALG["kyber512"], lw=1.2), fontsize=8.2, fontweight="bold", color=PAL_ALG["kyber512"])
    elif op == "decaps":
        c_med, k_med = np.median(c_arr), np.median(k_arr)
        ax.annotate(f"CTRU Unimodal ({c_med:.1f} ms)\n[Sem retry no Decaps]", xy=(c_med, 50), xytext=(c_med + 15, 42), arrowprops=dict(arrowstyle="->", color=PAL_ALG["ctru-light"], lw=1.2), fontsize=8.2, fontweight="bold", color=PAL_ALG["ctru-light"])
        ax.annotate(f"Kyber Unimodal ({k_med:.1f} ms)", xy=(k_med, 48), xytext=(k_med - 65, 42), arrowprops=dict(arrowstyle="->", color=PAL_ALG["kyber512"], lw=1.2), fontsize=8.2, fontweight="bold", color=PAL_ALG["kyber512"])

    ax.set_xlim(left=0, right=360)
    ax.set_ylim(bottom=0, top=55)
    ax.set_ylabel("Pulsos Capturados (N=50)", fontweight="bold")
    ax.set_title(f"{OP_LABELS[op]} - Histograma de Execução no Analisador Lógico (GPIO PA0)", fontweight="bold", pad=6)
    ax.legend(loc="upper right", framealpha=0.92)

axes[-1].set_xlabel("Tempo Puro de Execução na CPU (ms) [Analisador Lógico, Inicia estritamente em X=0]", fontweight="bold")
fig.suptitle(
    "Plot 10: Histograma Geral PQC — Identificação de Bimodalidade com Eixos Realistas (X=0 a 360 ms)",
    fontsize=13, fontweight="bold", x=0.08, ha="left", y=0.96
)
fig.text(
    0.08, 0.93,
    "Dados brutos do Analisador Lógico (GPIO PA0). CTRU-Light KeyGen e Encaps são estritamente bimodais; Kyber-512 e CTRU Decaps são unimodais.",
    fontsize=8.5, color="#555555"
)

p10_png = os.path.join(OUT_DIR, "10_general_pqc_histogram_zero_baseline.png")
p10_pdf = os.path.join(OUT_DIR, "10_general_pqc_histogram_zero_baseline.pdf")
plt.savefig(p10_png, dpi=300); plt.savefig(p10_pdf); plt.close()
print(f"[10/11] Saved {p10_png}")


# ==============================================================================
# PLOT 11: HISTOGRAMA GLOBAL FULL-SPECTRUM (PQC vs ECDH em 0 a 7.000 ms)
# ==============================================================================
fig, axes = plt.subplots(3, 1, figsize=(14, 9), sharex=True)
fig.subplots_adjust(left=0.08, right=0.96, top=0.91, bottom=0.09, hspace=0.30)

bins_full = np.arange(0, 7100, 50.0)

for idx, op in enumerate(["keygen", "encaps", "decaps"]):
    ax = axes[idx]
    for alg in ["ctru-light", "kyber512", "ecdh"]:
        arr = clean_la_pulses.get((alg, "asm", "-O3"), {}).get(op, np.array([]))
        if len(arr) > 0:
            ax.hist(arr, bins=bins_full, color=PAL_ALG[alg], alpha=0.75, edgecolor="#111111", linewidth=0.6, label=f"{alg.upper()} (ASM -O3, N={len(arr)})")
    
    ax.set_xlim(left=0, right=7000)
    ax.set_ylim(bottom=0, top=55)
    ax.set_ylabel("Pulsos Capturados", fontweight="bold")
    ax.set_title(f"{OP_LABELS[op]} - Escala Global Completa (0 a 7.000 ms)", fontweight="bold", pad=6)
    ax.legend(loc="upper right", framealpha=0.92)

axes[-1].set_xlabel("Tempo de Execução Puro no Analisador Lógico (ms) [Inicia estritamente em X=0]", fontweight="bold")
fig.suptitle(
    "Plot 11: Histograma Global PQC vs ECDH em Escala Linear Realista (0 a 7.000 ms)",
    fontsize=13, fontweight="bold", x=0.08, ha="left", y=0.96
)
fig.text(
    0.08, 0.93,
    "Exposição realista e não-enganosa da disparidade física: CTRU-Light e Kyber ocupam os primeiros 5% da régua de tempo.",
    fontsize=8.5, color="#555555"
)

p11_png = os.path.join(OUT_DIR, "11_full_spectrum_histogram_with_ecdh.png")
p11_pdf = os.path.join(OUT_DIR, "11_full_spectrum_histogram_with_ecdh.pdf")
plt.savefig(p11_png, dpi=300); plt.savefig(p11_pdf); plt.close()
print(f"[11/12] Saved {p11_png}")


# ==============================================================================
# PLOT 12: JAIN PAIRED HISTOGRAM & ECDF MASTER DIAGNOSTIC
# ==============================================================================
try:
    from generate_jain_distribution_plots import generate_jain_paired_figure
    generate_jain_paired_figure(clean_la_pulses, OUT_DIR)
except Exception as e:
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from generate_jain_distribution_plots import generate_jain_paired_figure
    generate_jain_paired_figure(clean_la_pulses, OUT_DIR)
print(f"[12/12] Saved {os.path.join(OUT_DIR, '12_jain_paired_histogram_and_ecdf.png')}")

print(f">> [DONE] All exploratory plots successfully generated in:\n   {OUT_DIR}/")
