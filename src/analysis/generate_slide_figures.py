#!/usr/bin/env python3
"""
generate_slide_figures.py
Author: eduabdala (CMP223 Presentation Figures)

Generates clean, bold, highly legible figures tailored specifically for
presentation slides (Marp 16:9, viewing from distance, 10-minute presentation).
Eliminates microtext, excessive legends, and academic paper sizing.
"""

import os
import re
import glob
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

plt.rcParams.update({
    "font.sans-serif": ["Inter", "Liberation Sans", "DejaVu Sans", "Arial"],
    "font.family": "sans-serif",
    "axes.edgecolor": "#444444",
    "axes.linewidth": 1.2,
    "grid.color": "#EAEAEA",
    "grid.linestyle": "--",
    "grid.linewidth": 0.8,
    "axes.grid": True,
})

PAL_ALG = {
    "ctru-light": "#0072B2",  # Okabe-Ito Blue
    "kyber512":   "#D55E00",  # Okabe-Ito Vermilion / Orange
    "ecdh":       "#009E73",  # Okabe-Ito Green
}

OUT_DIR = os.path.abspath("slides/figures")
os.makedirs(OUT_DIR, exist_ok=True)
EXP_DIR = os.path.abspath("data/experiments/exp_20261107_181223_bench_full_la_campaign_8412")


def parse_la_pulses():
    la_data = {}
    for lpath in sorted(glob.glob(os.path.join(EXP_DIR, "raw", "console_*.log"))):
        m = re.match(r"console_(.+?)_(asm|ref)_(O3|Os)_(\d+)MHz\.log", os.path.basename(lpath))
        if not m:
            continue
        alg, var, opt, clk = m.groups()
        with open(lpath, "r", encoding="utf-8") as fp:
            txt = fp.read()
        if "RESUMO DA BATERIA" in txt:
            txt = txt.split("RESUMO DA BATERIA")[0]
        lines = re.findall(
            r"^\s*(\d+)\s+([A-Za-z0-9\s\(\)]+?)\s+([\d\.]+)\s+([\d\.]+)\s+([\d,]+)",
            txt,
            re.MULTILINE
        )
        la_data[(alg, var, f"-{opt}")] = {
            "keygen": np.array([float(x[3]) for x in lines if "KeyGen" in x[1] or "Janela" in x[1]]),
            "encaps": np.array([float(x[3]) for x in lines if "Encaps" in x[1]]),
            "decaps": np.array([float(x[3]) for x in lines if "Decaps" in x[1]]),
        }
    return la_data


def make_slide_tradeoff():
    """
    Slide 4: Trade-off Memória SRAM vs. Latência (PQC vs ECDH).
    Clean, bold scatter plot specifically designed for slides.
    """
    fig, ax = plt.subplots(figsize=(6.2, 5.0), dpi=200)
    fig.subplots_adjust(left=0.15, right=0.92, top=0.90, bottom=0.14)

    # Data points: (SRAM_bytes, Latency_ms, Label, Alg, Marker, Offset)
    points = [
        # Kyber-512
        (935, 239.3, "Kyber-512 (asm)", "kyber512", "o", (-15, 12)),
        (976, 475.0, "Kyber-512 (ref)", "kyber512", "s", (12, -8)),
        # CTRU-Light
        (2464, 67.4, "CTRU-Light (asm)", "ctru-light", "o", (12, -12)),
        (3049, 170.4, "CTRU-Light (ref)", "ctru-light", "s", (12, 10)),
        # ECDH
        (788, 3248.1, "ECDH (asm)", "ecdh", "o", (12, -10)),
        (893, 6957.1, "ECDH (ref)", "ecdh", "s", (12, 10)),
    ]

    for sram, lat, label, alg, marker, offset in points:
        ax.scatter(
            sram, lat,
            color=PAL_ALG[alg],
            s=160,
            marker=marker,
            edgecolor="#111111",
            linewidth=1.5,
            zorder=5,
            alpha=0.9
        )
        ax.annotate(
            label,
            (sram, lat),
            xytext=offset,
            textcoords="offset points",
            fontsize=9.5,
            fontweight="bold",
            color="#222222",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="#D0D0D0", alpha=0.85)
        )

    # Shaded SRAM regions
    ax.axvspan(0, 1500, color="#2ECC71", alpha=0.08)
    ax.text(750, 85, "> 75% SRAM Livre\n(Margem Segura IoT)", ha="center", fontsize=8.5, color="#1E8449", fontweight="bold")

    ax.axvspan(1500, 3500, color="#F39C12", alpha=0.08)
    ax.text(2500, 85, "40% - 75% SRAM Livre\n(Viável com cuido)", ha="center", fontsize=8.5, color="#B7950B", fontweight="bold")

    # Physical SRAM boundary (6,144 Bytes)
    ax.axvline(6144, color="#C0392B", linestyle="--", linewidth=1.5)

    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: f"{int(y)} ms" if y < 1000 else f"{y/1000:.1f} s"))
    ax.set_ylim(40, 11000)
    ax.set_xlim(400, 3600)

    ax.set_xlabel("Pico de Pilha na SRAM (Bytes)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Tempo de Execução (KeyGen)", fontsize=11, fontweight="bold")
    ax.set_title("Trade-off: Memória SRAM vs. Latência de CPU", fontsize=12.5, fontweight="bold", pad=10)

    out_path = os.path.join(OUT_DIR, "slide_tradeoff.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f">> Saved {out_path}")


def make_slide_bimodality(la_data):
    """
    Slide 5: Diagnóstico Limpo de Bimodalidade (KeyGen: CTRU vs Kyber).
    Clean, bold 2-panel figure specifically designed for slides.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.2, 3.6), dpi=200)
    fig.subplots_adjust(left=0.08, right=0.96, top=0.84, bottom=0.18, wspace=0.25)

    c_k = la_data.get(("ctru-light", "asm", "-O3"), {}).get("keygen", np.array([]))
    k_k = la_data.get(("kyber512", "asm", "-O3"), {}).get("keygen", np.array([]))

    # Panel 1: CTRU-Light KeyGen (Bimodal)
    bins_ctru = np.arange(56, 80, 1.8)
    ax1.hist(c_k, bins=bins_ctru, color=PAL_ALG["ctru-light"], alpha=0.80, edgecolor="#111111", linewidth=1.0)
    
    # Mode highlights
    m1 = c_k[c_k < 68]
    m2 = c_k[c_k >= 68]
    m1_val, m2_val = np.mean(m1), np.mean(m2)
    
    ax1.axvline(m1_val, color="#C0392B", linestyle="--", linewidth=1.5)
    ax1.axvline(m2_val, color="#C0392B", linestyle="--", linewidth=1.5)
    
    ax1.text(m1_val, 28, f"Modo 1\n{m1_val:.1f} ms\n(48%)", ha="center", fontsize=8.5, fontweight="bold", color="#111111")
    ax1.text(m2_val, 28, f"Modo 2\n{m2_val:.1f} ms\n(52%)", ha="center", fontsize=8.5, fontweight="bold", color="#111111")

    # Arrow between modes
    ax1.annotate(
        "", xy=(m2_val, 15), xytext=(m1_val, 15),
        arrowprops=dict(arrowstyle="<->", color="#C0392B", lw=1.8)
    )
    ax1.text((m1_val + m2_val)/2, 17, "+10,2 ms\n(204k ciclos)", ha="center", fontsize=8.0, fontweight="bold", color="#C0392B")

    ax1.set_xlim(55, 78)
    ax1.set_ylim(0, 36)
    ax1.set_xlabel("Tempo no Analisador Lógico (ms)", fontsize=9.5, fontweight="bold")
    ax1.set_ylabel("Pulsos Capturados", fontsize=9.5, fontweight="bold")
    ax1.set_title("CTRU-Light: ESTRITAMENTE BIMODAL\n(Retry de Amostragem por Rejeição)", fontsize=10.0, fontweight="bold", color="#0072B2", pad=6)

    # Panel 2: Kyber-512 KeyGen (Unimodal)
    bins_kyber = np.arange(232, 260, 2.0)
    ax2.hist(k_k, bins=bins_kyber, color=PAL_ALG["kyber512"], alpha=0.80, edgecolor="#111111", linewidth=1.0)
    
    k_med = np.median(k_k)
    ax2.axvline(k_med, color="#27AE60", linestyle="--", linewidth=1.5)
    ax2.text(k_med, 44, f"Pico Único\n{k_med:.1f} ms\n(100% dos ensaios)", ha="center", fontsize=9.0, fontweight="bold", color="#111111")

    ax2.set_xlim(230, 258)
    ax2.set_ylim(0, 54)
    ax2.set_xlabel("Tempo no Analisador Lógico (ms)", fontsize=9.5, fontweight="bold")
    ax2.set_title("Kyber-512: ESTRITAMENTE UNIMODAL\n(Tempo Constante Determinístico)", fontsize=10.0, fontweight="bold", color="#D55E00", pad=6)

    out_path = os.path.join(OUT_DIR, "slide_bimodality.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f">> Saved {out_path}")


def make_slide_flash():
    """
    Slide: Ocupação de Memória Flash (ROM) em todas as configurações.
    Compara -O3 vs -Os e destaca o limite físico de 48 KB do ATmega4809.
    """
    import csv
    flash_csv = os.path.abspath("data/processed/flash_sizes.csv")
    if not os.path.isfile(flash_csv):
        print(f"!! Flash file not found: {flash_csv}")
        return

    flash_data = {}
    with open(flash_csv, "r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            key = (r["algorithm"], r["variant"], r["optimization"])
            flash_data[key] = float(r["flash_b"]) / 1024.0

    combos = [
        ("kyber512", "asm", "Kyber-512\n(asm)"),
        ("kyber512", "ref", "Kyber-512\n(ref)"),
        ("ctru-light", "asm", "CTRU-Light\n(asm)"),
        ("ctru-light", "ref", "CTRU-Light\n(ref)"),
        ("ecdh", "asm", "ECDH\n(asm)"),
        ("ecdh", "ref", "ECDH\n(ref)"),
    ]

    x = np.arange(len(combos))
    w = 0.36

    fig, ax = plt.subplots(figsize=(7.2, 4.4), dpi=200)
    fig.subplots_adjust(left=0.10, right=0.95, top=0.86, bottom=0.16)

    o3_vals = [flash_data.get((alg, var, "-O3"), 0.0) for alg, var, _ in combos]
    os_vals = [flash_data.get((alg, var, "-Os"), 0.0) for alg, var, _ in combos]

    rects1 = ax.bar(x - w/2, o3_vals, w, label="Otimização -O3 (Velocidade)", color="#0072B2", alpha=0.85, edgecolor="#111111", linewidth=0.9)
    rects2 = ax.bar(x + w/2, os_vals, w, label="Otimização -Os (Tamanho)", color="#E69F00", alpha=0.85, edgecolor="#111111", linewidth=0.9)

    # Annotate bar values
    for r in rects1:
        h = r.get_height()
        ax.annotate(f"{h:.1f}k", xy=(r.get_x() + r.get_width()/2, h), xytext=(0, 3),
                    textcoords="offset points", ha="center", va="bottom", fontsize=7.8, fontweight="bold")
    for r in rects2:
        h = r.get_height()
        ax.annotate(f"{h:.1f}k", xy=(r.get_x() + r.get_width()/2, h), xytext=(0, 3),
                    textcoords="offset points", ha="center", va="bottom", fontsize=7.8, fontweight="bold", color="#A04000")

    # 48 KB Flash physical limit line
    ax.axhline(48.0, color="#C0392B", linestyle="--", linewidth=1.6, zorder=4)
    ax.text(2.5, 49.0, "Capacidade Máxima de Flash do MCU (48 KB)", color="#C0392B", fontweight="bold", fontsize=9.0, ha="center")

    # Safe headroom zone (< 32 KB)
    ax.axhspan(0, 32.0, color="#2ECC71", alpha=0.06, zorder=1)
    ax.text(0.1, 4.0, "Margem Segura (>16 KB Livres para Aplicação)", color="#1E8449", fontsize=8.0, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels([lbl for _, _, lbl in combos], fontsize=9.2, fontweight="bold")
    ax.set_ylim(0, 54)
    ax.set_ylabel("Ocupação de Flash ROM (KB)", fontsize=10.5, fontweight="bold")
    ax.set_title("Custo de Memória Flash (ROM) por Implementação e Compilador", fontsize=11.5, fontweight="bold", pad=10)
    ax.legend(loc="upper left", framealpha=0.95, fontsize=8.8)

    out_path = os.path.join(OUT_DIR, "slide_flash.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f">> Saved {out_path}")


def main():
    la_data = parse_la_pulses()
    make_slide_tradeoff()
    make_slide_bimodality(la_data)
    make_slide_flash()
    print(">> [DONE] Custom slide figures generated successfully!")


if __name__ == "__main__":
    main()
