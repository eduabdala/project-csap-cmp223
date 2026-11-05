#!/usr/bin/env python3
"""plot_la.py — Scientific plots for logic analyzer captures.

Follows the data presentation guidelines from:
  - Raj Jain, "The Art of Computer Systems Performance Analysis" (Ch. 10):
      * Zero-baseline axes (no truncated scales);
      * High data-ink ratio (no chartjunk, clean white background, subtle grid);
      * Direct labeling on bars/series with mean latency and clock cycles;
      * Explicit representation of sample variability (individual points + 95% CI);
      * Explicit units on all axes and SUT metadata in the subtitle.
  - Tidyverse / ggplot2 (theme_bw + Okabe-Ito colorblind-safe palette):
      * Facet strip headers styled after ggplot2::theme_bw();
      * Clear typographic hierarchy (title, subtitle, caption);
      * Small multiples (faceting) to compare metrics without distorting scales.

Usage:
    # Single capture plot:
    python3 src/analysis/plot_la.py data/raw/kyber512_la.csv \
        --fcpu 20e6 --title "ATmega4809 (8-bit AVR) — Kyber-512 (asm, -O3)"

    python3 src/analysis/plot_la.py data/raw/rp2040_kyber512_la.csv \
        --fcpu 125e6 --title "RP2040 (32-bit Cortex-M0+) — Kyber-512 (ref, -O3)"

    # Side-by-side platform comparison (ATmega4809 vs. RP2040):
    python3 src/analysis/plot_la.py data/raw/kyber512_la.csv \
        --compare data/raw/rp2040_kyber512_la.csv \
        --fcpu 20e6 --compare-fcpu 125e6 \
        --label "ATmega4809 (8-bit AVR @ 20 MHz)" \
        --compare-label "RP2040 (32-bit Cortex-M0+ @ 125 MHz)" \
        --out data/processed/figures/comparacao_sut_kyber512
"""
import argparse
import csv
import math
import os
import statistics

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

# Okabe-Ito colorblind-safe palette (Tidyverse / Claus Wilke standard)
OKABE_ITO = {
    1: "#0072B2",  # K (KeyGen)   — Blue
    2: "#D55E00",  # E (Encaps)   — Vermilion
    3: "#009E73",  # D (Decaps)   — Bluish green
    4: "#CC79A7",  # M (MsgCrypt) — Reddish purple
    5: "#7F7F7F",  # Boot         — Grey
}

OPS = {
    1: "KeyGen (K)",
    2: "Encaps (E)",
    3: "Decaps (D)",
    4: "MsgCrypt (M)",
    5: "Boot",
}

# Two-sided Student's t critical values (95% CI) by degrees of freedom (df = n - 1)
T_CRIT_95 = {
    1: 12.706,
    2: 4.303,
    3: 3.182,
    4: 2.776,
    5: 2.571,
    6: 2.447,
    7: 2.365,
    8: 2.306,
    9: 2.262,
    10: 2.228,
    15: 2.131,
    20: 2.086,
    29: 2.045,
}

# Identification pulse width range (~2–4 ms)
ID_MIN_MS, ID_MAX_MS = 1.0, 6.0
# Max gap between ID pulses of the same operation (~4 ms nominal; >20 ms = new operation)
ID_GROUP_GAP_S = 0.020


def ci95_halfwidth(values: list[float]) -> float:
    """Half-width of the 95% Confidence Interval (Student's t)."""
    n = len(values)
    if n < 2:
        return 0.0
    sd = statistics.stdev(values)
    df = n - 1
    t_val = T_CRIT_95.get(df, 1.96)
    return t_val * sd / math.sqrt(n)


def apply_tidyverse_theme() -> None:
    """Configure matplotlib to reproduce the ggplot2::theme_bw() aesthetic."""
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
            "axes.titlesize": 10.5,
            "axes.titleweight": "bold",
            "axes.labelsize": 9.5,
            "axes.labelcolor": "#1A1A1A",
            "xtick.labelsize": 8.8,
            "ytick.labelsize": 8.8,
            "xtick.color": "#333333",
            "ytick.color": "#333333",
            "xtick.direction": "out",
            "ytick.direction": "out",
            "legend.frameon": True,
            "legend.facecolor": "#FFFFFF",
            "legend.edgecolor": "#CCCCCC",
            "legend.fontsize": 8.5,
        }
    )


def add_facet_strip(ax, text: str) -> None:
    """Draw a top facet strip header styled after ggplot2::theme_bw()."""
    ax.set_title("")
    ax.annotate(
        text,
        xy=(0.5, 1.0),
        xycoords="axes fraction",
        xytext=(0, 6),
        textcoords="offset points",
        ha="center",
        va="bottom",
        fontsize=9.5,
        fontweight="bold",
        color="#1A1A1A",
        bbox=dict(
            boxstyle="square,pad=0.35",
            facecolor="#EFEFEF",
            edgecolor="#4D4D4D",
            linewidth=0.8,
        ),
    )


def read_la_csv(path: str):
    """Return (samplerate, channel, total_samples, list of (t_s, level))."""
    meta = {}
    rows = []
    with open(path) as f:
        first = f.readline()
        if first.startswith("#"):
            for kv in first.lstrip("# ").strip().split(","):
                k, _, v = kv.strip().partition("=")
                meta[k] = v
        else:
            f.seek(0)
        reader = csv.reader(f)
        header = next(reader)
        for r in reader:
            rows.append((float(r[1]), int(r[2])))
    sr = int(meta.get("samplerate_hz", 0)) or 100000
    total = int(meta.get("total_samples", 0))
    channel = header[2] if len(header) > 2 else "D0"
    return sr, channel, total, rows


def extract_pulses(rows: list[tuple[float, int]]) -> list[tuple[float, float]]:
    """Return list of (t_start_s, width_ms) for HIGH logic pulses."""
    pulses, t_rise, prev = [], None, None
    for t, v in rows:
        if v == prev:
            continue
        if v == 1:
            t_rise = t
        elif t_rise is not None:
            pulses.append((t_rise, (t - t_rise) * 1000.0))
            t_rise = None
        prev = v
    return pulses


def decode_events(pulses: list[tuple[float, float]], samplerate: int = 100000) -> list[dict]:
    """Group ID pulses (separated by <20 ms) and pair them with the following MEASURE window."""
    events = []
    ids = 0
    id_start = None
    id_last_end = None
    min_res_ms = 1000.0 / samplerate

    for t, w in pulses:
        # If more than 20 ms elapsed since the last ID pulse without a captured window,
        # the previous window was sub-sample (< 1/samplerate, e.g., MsgCrypt on RP2040).
        if ids > 0 and id_last_end is not None and (t - id_last_end) > ID_GROUP_GAP_S:
            if ids == 4:
                events.append(
                    {
                        "ids": 4,
                        "op": OPS[4],
                        "id_start": id_start,
                        "t": id_last_end + 0.005,
                        "width_ms": min_res_ms,
                        "sub_sample": True,
                    }
                )
            ids = 0
            id_start = None
            id_last_end = None

        if ID_MIN_MS <= w <= ID_MAX_MS:
            if ids == 0:
                id_start = t
            ids += 1
            id_last_end = t + (w / 1000.0)
            continue

        if ids == 0:
            continue
        events.append(
            {
                "ids": ids,
                "op": OPS.get(ids, f"Op ({ids}p)"),
                "id_start": id_start,
                "t": t,
                "width_ms": w,
                "sub_sample": False,
            }
        )
        ids = 0
        id_start = None
        id_last_end = None

    # Close trailing 4-pulse group if capture ends right after a sub-sample MsgCrypt
    if ids == 4 and id_last_end is not None:
        events.append(
            {
                "ids": 4,
                "op": OPS[4],
                "id_start": id_start,
                "t": id_last_end + 0.005,
                "width_ms": min_res_ms,
                "sub_sample": True,
            }
        )
    return events


def plot_single_capture(args) -> None:
    apply_tidyverse_theme()
    sr, channel, total, rows = read_la_csv(args.csv)
    if not rows or total == 0:
        raise SystemExit(f"{args.csv}: empty capture (total_samples=0).")

    fcpu = args.fcpu
    if fcpu is None:
        fcpu = 125e6 if "rp2040" in os.path.basename(args.csv).lower() else 20e6

    pulses = extract_pulses(rows)
    events = decode_events(pulses, samplerate=sr)
    if not events:
        raise SystemExit("No MEASURE windows decoded.")

    base = os.path.splitext(os.path.basename(args.csv))[0]
    out = args.out or os.path.join("data", "processed", "figures", base)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)

    default_title = (
        "RP2040 (32-bit ARM Cortex-M0+) — Kyber-512 (ref, -O3)"
        if "rp2040" in base.lower()
        else "ATmega4809 (8-bit AVRxt) — Kyber-512 (asm, -O3)"
    )
    title = args.title or default_title
    duration = total / sr if sr else rows[-1][0]

    kem_keys = [k for k in (1, 2, 3) if any(e["ids"] == k for e in events)]
    all_keys = [k for k in (1, 2, 3, 4) if any(e["ids"] == k for e in events)]
    n_reps = max(len([e for e in events if e["ids"] == k]) for k in kem_keys)

    fig = plt.figure(figsize=(12.5, 8.4))
    gs = fig.add_gridspec(
        2,
        2,
        height_ratios=[1.05, 1.25],
        width_ratios=[1.05, 1.15],
        hspace=0.42,
        wspace=0.25,
        left=0.07,
        right=0.91,
        top=0.86,
        bottom=0.11,
    )
    ax_tl = fig.add_subplot(gs[0, :])
    ax_zoom = fig.add_subplot(gs[1, 0])
    ax_lat = fig.add_subplot(gs[1, 1])

    # ggplot2-style title and subtitle
    fig.text(0.07, 0.945, title, fontsize=13.5, fontweight="bold", color="#111111")
    fig.text(
        0.07,
        0.915,
        f"CPU Clock: {fcpu / 1e6:.0f} MHz  |  LA Sampling Rate: {sr / 1e3:.0f} kHz (channel {channel})  |  Repetitions (n): {n_reps} runs",
        fontsize=9.5,
        color="#4D4D4D",
    )

    # ------------------------------------------------------------------
    # Panel (a): Full capture timeline (Logic Signal + MEASURE Windows)
    # ------------------------------------------------------------------
    ts = [t for t, _ in rows] + [duration]
    vs = [v for _, v in rows] + [rows[-1][1]]
    ax_tl.step(ts, vs, where="post", color="#222222", lw=0.75, zorder=3)
    for ev in events:
        if ev["ids"] not in OKABE_ITO:
            continue
        c = OKABE_ITO[ev["ids"]]
        w_s = ev["width_ms"] / 1000.0
        span_w = max(w_s, duration * 0.004)
        ax_tl.axvspan(ev["t"], ev["t"] + span_w, color=c, alpha=0.28, zorder=2)
        short_lbl = ev["op"].split()[0]
        if ev["ids"] in (1, 2, 3):
            ax_tl.text(
                ev["t"] + span_w / 2,
                1.04,
                f"{short_lbl}\n({ev['width_ms']:.1f} ms)",
                ha="center",
                va="bottom",
                fontsize=7.4,
                color=c,
                fontweight="bold",
            )
    ax_tl.set_ylim(-0.12, 1.56)
    ax_tl.set_yticks([0, 1], ["0 (LOW)", "1 (HIGH)"])
    ax_tl.set_xlim(0, duration)
    ax_tl.set_xlabel("Capture Time (s)")
    ax_tl.set_ylabel("Logic Level (GPIO)")
    ax_tl.grid(axis="x", alpha=0.4)
    ax_tl.grid(axis="y", visible=False)
    handles = [Rectangle((0, 0), 1, 1, facecolor=OKABE_ITO[k], edgecolor="none", alpha=0.55) for k in all_keys]
    ax_tl.legend(
        handles,
        [OPS[k] for k in all_keys],
        loc="upper right",
        ncol=len(all_keys),
        title="Cryptographic Operation",
        title_fontsize=8.0,
    )
    add_facet_strip(ax_tl, "(a) Instrumentation Pin Time Series (Identification Pulses + MEASURE Windows)")

    # ------------------------------------------------------------------
    # Panel (b): Zoom on Pulse Encoding (Decaps = 3 ID pulses + window)
    # ------------------------------------------------------------------
    dec_events = [e for e in events if e["ids"] == 3]
    zev = dec_events[0] if dec_events else events[0]
    z0 = max(0.0, zev["id_start"] - 0.004)
    win_preview_s = min(zev["width_ms"] / 1000.0, 0.012)
    z1 = zev["t"] + win_preview_s + 0.004
    zt = [z0] + [t for t, _ in rows if z0 < t < z1] + [z1]
    zv = []
    for t in zt:
        lvl = 0
        for tt, vv in rows:
            if tt > t:
                break
            lvl = vv
        zv.append(lvl)
    ax_zoom.step([(t - z0) * 1000 for t in zt], zv, where="post", color="#111111", lw=1.1, zorder=3)
    ax_zoom.axvspan(
        (zev["id_start"] - z0) * 1000,
        (zev["t"] - 0.005 - z0) * 1000,
        color="#888888",
        alpha=0.18,
        label=f"{zev['ids']} ID pulses (~2 ms each)",
    )
    ax_zoom.axvspan(
        (zev["t"] - z0) * 1000,
        (min(zev["t"] + zev["width_ms"] / 1000.0, z1) - z0) * 1000,
        color=OKABE_ITO[zev["ids"]],
        alpha=0.30,
        label=f"{zev['op']} window start ({zev['width_ms']:.2f} ms)",
    )
    ax_zoom.set_ylim(-0.12, 1.25)
    ax_zoom.set_yticks([0, 1], ["0 (LOW)", "1 (HIGH)"])
    ax_zoom.set_xlim(0, (z1 - z0) * 1000)
    ax_zoom.set_xlabel("Time Relative to Pulse Group (ms)")
    ax_zoom.set_ylabel("Logic Level (GPIO)")
    ax_zoom.legend(loc="upper right", fontsize=8.0)
    add_facet_strip(ax_zoom, f"(b) Physical Protocol Detail: {zev['ids']} ID Pulses + Guard (5 ms) → {zev['op']}")

    # ------------------------------------------------------------------
    # Panel (c): KEM Latency & Clock Cycles by Operation (Jain Ch. 10: zero-baseline + 95% CI + points)
    # ------------------------------------------------------------------
    summary = []
    for k in all_keys:
        ws = [e["width_ms"] for e in events if e["ids"] == k]
        m = statistics.mean(ws)
        sd = statistics.stdev(ws) if len(ws) > 1 else 0.0
        ci = ci95_halfwidth(ws)
        summary.append((k, OPS[k], len(ws), m, sd, ci, min(ws), max(ws)))

    # Plot KEM operations (K, E, D) on primary axis starting strictly at zero
    kem_rows = [s for s in summary if s[0] in (1, 2, 3)]
    x_pos = list(range(len(kem_rows)))
    max_y = max(s[3] + s[5] for s in kem_rows)

    for idx, (k, op_label, n, m, sd, ci, mn, mx) in enumerate(kem_rows):
        c = OKABE_ITO[k]
        ax_lat.bar(
            idx,
            m,
            width=0.52,
            facecolor=c,
            edgecolor="#222222",
            linewidth=0.8,
            alpha=0.78,
            zorder=2,
        )
        ax_lat.errorbar(
            idx,
            m,
            yerr=ci,
            fmt="none",
            ecolor="#111111",
            elinewidth=1.3,
            capsize=5,
            capthick=1.2,
            zorder=4,
        )
        # Individual raw observations
        ws = [e["width_ms"] for e in events if e["ids"] == k]
        jitter = [idx + (j - (len(ws) - 1) / 2) * 0.06 for j in range(len(ws))]
        ax_lat.scatter(
            jitter,
            ws,
            color="#FFFFFF",
            edgecolor="#111111",
            s=28,
            linewidth=1.1,
            zorder=5,
            label="Samples ($n$)" if idx == 0 else None,
        )

        # Direct labeling (Jain Ch. 10)
        cyc = m / 1000.0 * fcpu
        cyc_str = f"{cyc / 1e6:.2f}M cycles" if cyc >= 1e6 else f"{cyc / 1e3:.1f}k cycles"
        ax_lat.text(
            idx,
            m + ci + max_y * 0.025,
            f"{m:.2f} ± {ci:.2f} ms\n({cyc_str})",
            ha="center",
            va="bottom",
            fontsize=8.2,
            fontweight="bold",
            color="#1A1A1A",
        )

    ax_lat.set_xticks(x_pos, [s[1] for s in kem_rows])
    ax_lat.set_ylabel("Execution Latency (ms)")
    ax_lat.set_ylim(0, max_y * 1.40)  # Jain: always start at 0 + headroom for note
    ax_lat.grid(axis="x", visible=False)

    # Secondary right axis in millions of clock cycles
    ax_cyc = ax_lat.twinx()
    ax_cyc.set_ylim(0, (max_y * 1.40) / 1000.0 * fcpu / 1e6)
    ax_cyc.set_ylabel(f"Clock Cycles (×10⁶ @ {fcpu / 1e6:.0f} MHz)")
    ax_cyc.grid(False)

    # Callout note for MsgCrypt (symmetric cost ~4 orders of magnitude smaller)
    msg_rows = [s for s in summary if s[0] == 4]
    if msg_rows:
        _, _, n_m, m_m, _, _, _, _ = msg_rows[0]
        cyc_m = m_m / 1000.0 * fcpu
        note = f"Note — MsgCrypt (M, 18 B symmetric): {m_m * 1000:.0f} µs (~{cyc_m:,.0f} cycles, ~{kem_rows[1][3] / m_m:,.0f}× faster than Encaps)"
        ax_lat.text(
            0.03,
            0.95,
            note,
            transform=ax_lat.transAxes,
            ha="left",
            va="top",
            fontsize=7.6,
            color="#222222",
            bbox=dict(boxstyle="round,pad=0.30", facecolor="#F8F8F8", edgecolor="#CCCCCC", lw=0.8),
        )

    add_facet_strip(ax_lat, f"(c) KEM Latency by Operation (Mean ± 95% CI, n = {n_reps})")

    # Methodological footer (ggplot2 caption style)
    fig.text(
        0.07,
        0.02,
        "Source: Physical measurement via logic analyzer (single-cycle GPIO trigger with interrupts disabled).\n"
        "Error bars represent 95% Confidence Intervals (Student's t); white circles indicate individual runs.",
        fontsize=8.0,
        color="#555555",
        style="italic",
    )

    for ext in ("png", "pdf"):
        fig.savefig(f"{out}.{ext}", dpi=200)
    plt.close(fig)

    # Save summary CSV with standard deviation and 95% CI
    with open(f"{out}_summary.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["operation", "n", "mean_ms", "sd_ms", "ci95_ms", "min_ms", "max_ms", "mean_cycles"])
        for _, op, n, m, sd, ci, mn, mx in summary:
            w.writerow([op, n, f"{m:.4f}", f"{sd:.4f}", f"{ci:.4f}", f"{mn:.4f}", f"{mx:.4f}", round(m / 1000 * fcpu)])

    print(f"{'Operation':<14} {'n':>3} {'mean (ms)':>11} {'95% CI':>9} {'cycles':>12}")
    for _, op, n, m, sd, ci, mn, mx in summary:
        print(f"{op:<14} {n:>3} {m:>11.3f} {ci:>9.3f} {round(m / 1000 * fcpu):>12,}")
    print(f"\nFigures: {out}.png / {out}.pdf\nSummary: {out}_summary.csv")


def plot_comparison(args) -> None:
    """Faceted comparison plot (Tidyverse small multiples + Jain Ch. 10) across two platforms."""
    apply_tidyverse_theme()

    sr_a, _, _, rows_a = read_la_csv(args.csv)
    sr_b, _, _, rows_b = read_la_csv(args.compare)
    fcpu_a = args.fcpu or 20e6
    fcpu_b = args.compare_fcpu or 125e6

    ev_a = decode_events(extract_pulses(rows_a), samplerate=sr_a)
    ev_b = decode_events(extract_pulses(rows_b), samplerate=sr_b)

    lbl_a = args.label or f"ATmega4809 (8-bit AVR @ {fcpu_a / 1e6:.0f} MHz)"
    lbl_b = args.compare_label or f"RP2040 (32-bit Cortex-M0+ @ {fcpu_b / 1e6:.0f} MHz)"

    ops_kem = [1, 2, 3]
    stats_a, stats_b = {}, {}
    for k in ops_kem:
        wa = [e["width_ms"] for e in ev_a if e["ids"] == k]
        wb = [e["width_ms"] for e in ev_b if e["ids"] == k]
        stats_a[k] = (statistics.mean(wa), ci95_halfwidth(wa), wa)
        stats_b[k] = (statistics.mean(wb), ci95_halfwidth(wb), wb)

    fig = plt.figure(figsize=(12.5, 5.6))
    gs = fig.add_gridspec(1, 2, wspace=0.22, left=0.07, right=0.97, top=0.80, bottom=0.16)
    ax_time = fig.add_subplot(gs[0, 0])
    ax_cyc = fig.add_subplot(gs[0, 1])

    fig.text(
        0.07,
        0.93,
        "Architectural Comparison on Kyber-512: ATmega4809 (8-bit AVR) vs. RP2040 (32-bit Cortex-M0+)",
        fontsize=13.0,
        fontweight="bold",
        color="#111111",
    )
    fig.text(
        0.07,
        0.885,
        f"{lbl_a} (asm variant, -O3)  vs.  {lbl_b} (ref variant, -O3)  |  Logic Analyzer Measurement (n = 3)",
        fontsize=9.5,
        color="#4D4D4D",
    )

    color_a = "#D55E00"  # Okabe-Ito Vermilion (ATmega4809)
    color_b = "#0072B2"  # Okabe-Ito Blue (RP2040)
    width = 0.35
    x = list(range(len(ops_kem)))

    # ------------------------------------------------------------------
    # Facet (a): Absolute Execution Latency in Milliseconds (ms)
    # ------------------------------------------------------------------
    max_t = max(stats_a[k][0] + stats_a[k][1] for k in ops_kem)
    for i, k in enumerate(ops_kem):
        ma, cia, wa = stats_a[k]
        mb, cib, wb = stats_b[k]
        speedup_t = ma / mb

        ax_time.bar(i - width / 2, ma, width=width, facecolor=color_a, edgecolor="#222222", lw=0.8, alpha=0.82,
                    label=lbl_a if i == 0 else None)
        ax_time.bar(i + width / 2, mb, width=width, facecolor=color_b, edgecolor="#222222", lw=0.8, alpha=0.82,
                    label=lbl_b if i == 0 else None)
        ax_time.errorbar(i - width / 2, ma, yerr=cia, fmt="none", ecolor="#111111", elinewidth=1.2, capsize=4)
        ax_time.errorbar(i + width / 2, mb, yerr=cib, fmt="none", ecolor="#111111", elinewidth=1.2, capsize=4)

        ax_time.text(i - width / 2, ma + cia + max_t * 0.02, f"{ma:.1f} ms", ha="center", va="bottom",
                     fontsize=8.2, fontweight="bold", color="#111111")
        ax_time.text(i + width / 2 + 0.04, mb + cib + max_t * 0.02, f"{mb:.1f} ms\n({speedup_t:.1f}× faster)",
                     ha="center", va="bottom", fontsize=7.8, fontweight="bold", color=color_b)

    ax_time.set_xticks(x, [OPS[k] for k in ops_kem])
    ax_time.set_ylabel("Execution Latency (ms)")
    ax_time.set_ylim(0, max_t * 1.24)
    ax_time.grid(axis="x", visible=False)
    ax_time.legend(loc="upper left", fontsize=8.2)
    add_facet_strip(ax_time, "(a) Execution Time by Operation (ms) — Linear Scale (Zero Baseline)")

    # ------------------------------------------------------------------
    # Facet (b): Clock Cycle Cost (×10⁶ cycles — frequency-independent)
    # ------------------------------------------------------------------
    max_c = max((stats_a[k][0] / 1000.0 * fcpu_a) / 1e6 for k in ops_kem)
    for i, k in enumerate(ops_kem):
        ma, cia, _ = stats_a[k]
        mb, cib, _ = stats_b[k]
        ca = (ma / 1000.0 * fcpu_a) / 1e6
        cb = (mb / 1000.0 * fcpu_b) / 1e6
        ea = (cia / 1000.0 * fcpu_a) / 1e6
        eb = (cib / 1000.0 * fcpu_b) / 1e6
        ratio_c = ca / cb

        ax_cyc.bar(i - width / 2, ca, width=width, facecolor=color_a, edgecolor="#222222", lw=0.8, alpha=0.82,
                   label=lbl_a if i == 0 else None)
        ax_cyc.bar(i + width / 2, cb, width=width, facecolor=color_b, edgecolor="#222222", lw=0.8, alpha=0.82,
                   label=lbl_b if i == 0 else None)
        ax_cyc.errorbar(i - width / 2, ca, yerr=ea, fmt="none", ecolor="#111111", elinewidth=1.2, capsize=4)
        ax_cyc.errorbar(i + width / 2, cb, yerr=eb, fmt="none", ecolor="#111111", elinewidth=1.2, capsize=4)

        ax_cyc.text(i - width / 2, ca + ea + max_c * 0.02, f"{ca:.2f}M", ha="center", va="bottom",
                    fontsize=8.2, fontweight="bold", color="#111111")
        ax_cyc.text(i + width / 2 + 0.04, cb + eb + max_c * 0.02, f"{cb:.2f}M\n({ratio_c:.1f}× fewer cycles)",
                    ha="center", va="bottom", fontsize=7.8, fontweight="bold", color=color_b)

    ax_cyc.set_xticks(x, [OPS[k] for k in ops_kem])
    ax_cyc.set_ylabel("Clock Cycles (×10⁶ cycles)")
    ax_cyc.set_ylim(0, max_c * 1.24)
    ax_cyc.grid(axis="x", visible=False)
    ax_cyc.legend(loc="upper left", fontsize=8.2)
    add_facet_strip(ax_cyc, "(b) Architectural Efficiency: Clock Cycles by Operation (×10⁶ cycles)")

    fig.text(
        0.07,
        0.025,
        "Source: Physical measurement via logic analyzer (100 kHz). Panel (b) isolates the architectural speedup (32-bit vs. 8-bit)\n"
        "from the clock frequency ratio (125 MHz vs. 20 MHz). Error bars indicate 95% Confidence Intervals.",
        fontsize=8.0,
        color="#555555",
        style="italic",
    )

    out = args.out or os.path.join("data", "processed", "figures", "comparacao_sut_kyber512")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(f"{out}.{ext}", dpi=200)
    plt.close(fig)
    print(f"Comparison plot saved to: {out}.png / {out}.pdf")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", help="CSV from trigger.py --la-out")
    ap.add_argument("--fcpu", type=float, default=None, help="MCU clock in Hz (auto: 125e6 for rp2040, 20e6 for avr)")
    ap.add_argument("--out", default=None, help="output prefix (without extension)")
    ap.add_argument("--title", default=None)
    ap.add_argument("--compare", default=None, help="second CSV to generate a cross-platform comparison plot")
    ap.add_argument("--compare-fcpu", type=float, default=125e6, help="second MCU clock in Hz (default: 125e6)")
    ap.add_argument("--label", default=None, help="first platform label")
    ap.add_argument("--compare-label", default=None, help="second platform label")
    args = ap.parse_args()

    if args.compare:
        plot_comparison(args)
    else:
        plot_single_capture(args)


if __name__ == "__main__":
    main()
