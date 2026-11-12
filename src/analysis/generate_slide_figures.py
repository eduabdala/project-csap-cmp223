#!/usr/bin/env python3
"""
generate_slide_figures.py
Author: eduabdala (CMP223 Presentation Figures - Perfect Legibility & Zero Overlap)

Generates clean, elegant, spacious figures tailored specifically for
presentation slides (Marp 16:9, viewing from distance, high contrast, ZERO overlapping text).
"""

import os
import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# High-legibility, clean styling
plt.rcParams.update({
    "font.sans-serif": ["Inter", "Liberation Sans", "DejaVu Sans", "Arial", "sans-serif"],
    "font.family": "sans-serif",
    "axes.edgecolor": "#333333",
    "axes.linewidth": 1.2,
    "grid.color": "#EDEDED",
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
EXP_DIR = os.path.abspath("data/experiments/exp_20261108_155653_bench_campanha_completa_la_nix_8289")


def decode_la_csv(path: str) -> list[dict]:
    with open(path) as f:
        first_line = f.readline()
        ch_name = "D0"
        for part in first_line.split(","):
            if "active_channel=" in part:
                ch_name = part.split("active_channel=")[1].strip()
        lines = [l for l in f if not l.startswith("#")]

    reader = csv.DictReader(lines)
    trans = [(float(r["t_s"]), int(r[ch_name])) for r in reader]

    pulses = []
    in_high = False
    start_t = 0
    for t, val in trans:
        if val == 1 and not in_high:
            in_high = True
            start_t = t
        elif val == 0 and in_high:
            in_high = False
            dur_ms = (t - start_t) * 1000.0
            pulses.append((start_t, dur_ms))

    events = []
    id_count = 0
    op_map = {1: "keygen", 2: "encaps", 3: "decaps", 4: "msgcrypt"}
    for t_start, dur_ms in pulses:
        if 2.0 <= dur_ms <= 5.5:
            id_count += 1
        elif id_count > 0 and dur_ms >= 0.01:
            events.append({
                "op": op_map.get(id_count, f"U{id_count}"),
                "t_start_s": t_start,
                "dur_ms": dur_ms,
                "id_count": id_count
            })
            id_count = 0
    return events


def load_all_la_data():
    la_data = {}
    combos = [
        ("ctru-light", "asm", "-O3"),
        ("ctru-light", "asm", "-Os"),
        ("ctru-light", "ref", "-O3"),
        ("ctru-light", "ref", "-Os"),
        ("ecdh",       "asm", "-O3"),
        ("ecdh",       "asm", "-Os"),
        ("ecdh",       "ref", "-O3"),
        ("ecdh",       "ref", "-Os"),
        ("kyber512",   "asm", "-O3"),
        ("kyber512",   "asm", "-Os"),
        ("kyber512",   "ref", "-O3"),
        ("kyber512",   "ref", "-Os"),
    ]
    for alg, var, opt in combos:
        opt_s = opt.replace("-", "")
        cf = os.path.join(EXP_DIR, "raw", f"la_{alg}_{var}_{opt_s}_20MHz.csv")
        if os.path.exists(cf):
            evs = decode_la_csv(cf)
            la_data[(alg, var, opt)] = {
                "keygen": np.array([e["dur_ms"] for e in evs if e["op"] == "keygen"]),
                "encaps": np.array([e["dur_ms"] for e in evs if e["op"] == "encaps"]),
                "decaps": np.array([e["dur_ms"] for e in evs if e["op"] == "decaps"]),
            }
    return la_data


def make_slide_tradeoff():
    """
    Slide 4: Trade-off Memória SRAM vs. Latência (PQC vs ECDH).
    Spacious scatter plot with absolutely ZERO overlapping elements.
    """
    fig, ax = plt.subplots(figsize=(8.5, 4.8), dpi=220)
    fig.subplots_adjust(left=0.11, right=0.96, top=0.90, bottom=0.14)

    # Coordenadas reais e posicionamentos cuidadosamente testados
    points = [
        # (sram, lat, label, alg, marker, offset, ha, va)
        (946,  239.4, "Kyber asm\n(239 ms)", "kyber512",   "o", (14, -14), "left",  "top"),
        (899,  471.3, "Kyber ref\n(471 ms)", "kyber512",   "s", (-14, 10), "right", "bottom"),
        (2464, 67.2,  "CTRU asm (67 ms)",    "ctru-light", "o", (14, 0),   "left",  "center"),
        (2472, 167.9, "CTRU ref (168 ms)",   "ctru-light", "s", (14, 8),   "left",  "bottom"),
        (777,  3179.6,"ECDH asm (3,2 s)",    "ecdh",       "o", (-14, -6), "right", "top"),
        (788,  6978.5,"ECDH ref (7,0 s)",    "ecdh",       "s", (-14, 8),  "right", "bottom"),
    ]

    for sram, lat, label, alg, marker, offset, ha, va in points:
        ax.scatter(
            sram, lat,
            color=PAL_ALG[alg],
            s=180,
            marker=marker,
            edgecolor="#111111",
            linewidth=1.4,
            zorder=5,
            alpha=0.95
        )
        ax.annotate(
            label,
            (sram, lat),
            xytext=offset,
            textcoords="offset points",
            fontsize=9.2,
            fontweight="bold",
            color=PAL_ALG[alg],
            ha=ha, va=va,
            bbox=dict(boxstyle="round,pad=0.25", facecolor="#FFFFFF", edgecolor="#D5D5D5", alpha=0.92, linewidth=0.8)
        )

    # Shaded SRAM regions com rótulos discretos na base do gráfico (longe dos pontos superiores)
    ax.axvspan(400, 1500, color="#2ECC71", alpha=0.07, zorder=1)
    ax.text(950, 48, ">75% SRAM LIVRE (Confortável)", ha="center", fontsize=8.5, color="#196F3D", fontweight="bold")

    ax.axvspan(1500, 3200, color="#F39C12", alpha=0.07, zorder=1)
    ax.text(2350, 48, "40%–75% SRAM LIVRE (Viável)", ha="center", fontsize=8.5, color="#B7950B", fontweight="bold")

    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: f"{int(y)} ms" if y < 1000 else f"{y/1000:.1f} s"))
    ax.set_ylim(35, 14000)  # Teto expandido para dar respiro ao ECDH ref
    ax.set_xlim(400, 3200)

    # Clean custom legend
    ax.scatter([], [], marker="o", color="#555555", s=90, label="Assembly (asm)")
    ax.scatter([], [], marker="s", color="#555555", s=90, label="Referência C (ref)")
    ax.legend(loc="upper right", framealpha=0.95, fontsize=8.8)

    ax.set_xlabel("Pico de Pilha na SRAM (Bytes) [Total do MCU: 6.144 B]", fontsize=11.0, fontweight="bold", labelpad=6)
    ax.set_ylabel("Tempo de Execução (KeyGen)", fontsize=11.0, fontweight="bold", labelpad=6)
    ax.set_title("Trade-off: Consumo de SRAM vs. Latência de CPU", fontsize=12.5, fontweight="bold", pad=10)
    ax.tick_params(axis="both", labelsize=10.0)

    out_path = os.path.join(OUT_DIR, "slide_tradeoff.png")
    plt.savefig(out_path, dpi=240)
    plt.close()
    print(f">> Saved {out_path}")


def make_slide_flash():
    """
    Slide 5: Ocupação de Memória Flash (ROM).
    Spacious bar chart with Y limit up to 60 KB to prevent label collisions with the 48 KB limit line.
    """
    flash_kb = {
        ("kyber512",   "asm", "-O3"): 22.7,
        ("kyber512",   "asm", "-Os"): 13.9,
        ("kyber512",   "ref", "-O3"): 44.5,
        ("kyber512",   "ref", "-Os"): 34.5,
        ("ctru-light", "asm", "-O3"): 27.4,
        ("ctru-light", "asm", "-Os"): 21.3,
        ("ctru-light", "ref", "-O3"): 47.0,
        ("ctru-light", "ref", "-Os"): 39.4,
        ("ecdh",       "asm", "-O3"): 12.8,
        ("ecdh",       "asm", "-Os"):  7.9,
        ("ecdh",       "ref", "-O3"): 25.5,
        ("ecdh",       "ref", "-Os"):  9.7,
    }

    combos = [
        ("kyber512", "asm", "Kyber-512\n(asm)"),
        ("kyber512", "ref", "Kyber-512\n(ref)"),
        ("ctru-light", "asm", "CTRU-Light\n(asm)"),
        ("ctru-light", "ref", "CTRU-Light\n(ref)"),
        ("ecdh", "asm", "ECDH\n(asm)"),
        ("ecdh", "ref", "ECDH\n(ref)"),
    ]

    x = np.arange(len(combos))
    w = 0.30

    fig, ax = plt.subplots(figsize=(8.8, 4.6), dpi=220)
    fig.subplots_adjust(left=0.08, right=0.96, top=0.88, bottom=0.16)

    o3_vals = [flash_kb.get((alg, var, "-O3"), 0.0) for alg, var, _ in combos]
    os_vals = [flash_kb.get((alg, var, "-Os"), 0.0) for alg, var, _ in combos]

    rects1 = ax.bar(x - w/2, o3_vals, w, label="-O3 (Velocidade)", color="#0072B2", alpha=0.90, edgecolor="#111111", linewidth=0.9)
    rects2 = ax.bar(x + w/2, os_vals, w, label="-Os (Tamanho)", color="#E69F00", alpha=0.90, edgecolor="#111111", linewidth=0.9)

    # Annotate bar values cleanly
    for r in rects1:
        h = r.get_height()
        ax.annotate(f"{h:.1f}k", xy=(r.get_x() + r.get_width()/2, h), xytext=(0, 3),
                    textcoords="offset points", ha="center", va="bottom", fontsize=8.2, fontweight="bold", color="#004D7A")
    for r in rects2:
        h = r.get_height()
        ax.annotate(f"{h:.1f}k", xy=(r.get_x() + r.get_width()/2, h), xytext=(0, 3),
                    textcoords="offset points", ha="center", va="bottom", fontsize=8.2, fontweight="bold", color="#935116")

    # 48 KB Flash limit line: Y-lim is 60 KB, so text sits cleanly above the line without colliding with bars
    ax.axhline(48.0, color="#C0392B", linestyle="--", linewidth=1.6, zorder=5)
    ax.text(5.3, 49.5, "Teto de 48 KB (MCU Flash)", color="#C0392B", fontweight="bold", fontsize=9.0, ha="right", va="bottom")

    ax.set_xticks(x)
    ax.set_xticklabels([lbl for _, _, lbl in combos], fontsize=9.5, fontweight="bold")
    ax.set_ylim(0, 60)  # Teto 60 KB para desobstruir a linha de 48 KB
    ax.set_ylabel("Ocupação de Flash (KB)", fontsize=11.0, fontweight="bold", labelpad=6)
    ax.set_title("Ocupação de Memória Flash ROM (Impacto de -Os e Assembly)", fontsize=12.5, fontweight="bold", pad=10)
    ax.tick_params(axis="both", labelsize=9.5)
    ax.legend(loc="upper left", framealpha=0.95, fontsize=9.2)

    out_path = os.path.join(OUT_DIR, "slide_flash.png")
    plt.savefig(out_path, dpi=240)
    plt.close()
    print(f">> Saved {out_path}")


def make_slide_bimodality(la_data):
    """
    Slide 6: Diagnóstico Limpo de Bimodalidade (KeyGen: CTRU vs Kyber).
    Spacious 2-panel figure with clear, uncluttered labels.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.0, 4.2), dpi=220)
    fig.subplots_adjust(left=0.07, right=0.96, top=0.84, bottom=0.18, wspace=0.22)

    c_k = la_data.get(("ctru-light", "asm", "-O3"), {}).get("keygen", np.array([]))
    k_k = la_data.get(("kyber512", "asm", "-O3"), {}).get("keygen", np.array([]))

    # Panel 1: CTRU-Light KeyGen (Bimodal)
    bins_ctru = np.arange(56, 76, 1.6)
    ax1.hist(c_k, bins=bins_ctru, color=PAL_ALG["ctru-light"], alpha=0.85, edgecolor="#111111", linewidth=1.0)

    m1 = c_k[c_k < 65]
    m2 = c_k[c_k >= 65]
    m1_val, m2_val = np.mean(m1), np.mean(m2)

    ax1.axvline(m1_val, color="#C0392B", linestyle="--", linewidth=1.6)
    ax1.axvline(m2_val, color="#C0392B", linestyle="--", linewidth=1.6)

    ax1.text(m1_val, 22, f"Modo 1\n{m1_val:.1f} ms", ha="center", fontsize=9.2, fontweight="bold", color="#111111",
             bbox=dict(boxstyle="round,pad=0.2", facecolor="#FDEDEC", edgecolor="#C0392B", alpha=0.9))
    ax1.text(m2_val, 22, f"Modo 2\n{m2_val:.1f} ms", ha="center", fontsize=9.2, fontweight="bold", color="#111111",
             bbox=dict(boxstyle="round,pad=0.2", facecolor="#FDEDEC", edgecolor="#C0392B", alpha=0.9))

    # Seta entre os modos posicionada mais alta para não colidir com o topo das barras
    ax1.annotate(
        "", xy=(m2_val, 15), xytext=(m1_val, 15),
        arrowprops=dict(arrowstyle="<->", color="#C0392B", lw=1.6)
    )
    delta_ms = m2_val - m1_val
    ax1.text((m1_val + m2_val)/2, 16.5, f"Δt ≈ +{delta_ms:.1f} ms\n(Retry)", ha="center", fontsize=8.8, fontweight="bold", color="#922B21")

    ax1.set_xlim(54, 76)
    ax1.set_ylim(0, 28)
    ax1.set_xlabel("Tempo no Analisador Lógico (ms)", fontsize=10.5, fontweight="bold", labelpad=6)
    ax1.set_ylabel("Pulsos Capturados (N=30)", fontsize=10.5, fontweight="bold")
    ax1.set_title("CTRU-Light: ESTRITAMENTE BIMODAL\n(Amostragem com Rejeição)", fontsize=11.5, fontweight="bold", color="#0072B2", pad=8)
    ax1.tick_params(axis="both", labelsize=9.5)

    # Panel 2: Kyber-512 KeyGen (Unimodal)
    bins_kyber = np.arange(234, 248, 1.4)
    ax2.hist(k_k, bins=bins_kyber, color=PAL_ALG["kyber512"], alpha=0.85, edgecolor="#111111", linewidth=1.0)

    k_med = np.median(k_k)
    ax2.axvline(k_med, color="#27AE60", linestyle="--", linewidth=1.6)
    ax2.text(k_med, 22, f"Pico Único Determinístico\n{k_med:.1f} ms (Tempo Constante)",
             ha="center", fontsize=9.2, fontweight="bold", color="#111111",
             bbox=dict(boxstyle="round,pad=0.25", facecolor="#E8F8F5", edgecolor="#27AE60", alpha=0.9))

    ax2.set_xlim(232, 248)
    ax2.set_ylim(0, 28)
    ax2.set_xlabel("Tempo no Analisador Lógico (ms)", fontsize=10.5, fontweight="bold", labelpad=6)
    ax2.set_title("Kyber-512: ESTRITAMENTE UNIMODAL\n(Sem Rejeição / Tempo Constante)", fontsize=11.5, fontweight="bold", color="#D55E00", pad=8)
    ax2.tick_params(axis="both", labelsize=9.5)

    out_path = os.path.join(OUT_DIR, "slide_bimodality.png")
    plt.savefig(out_path, dpi=240)
    plt.close()
    print(f">> Saved {out_path}")


def main():
    la_data = load_all_la_data()
    print(f">> Loaded LA data from: {EXP_DIR}")
    make_slide_tradeoff()
    make_slide_bimodality(la_data)
    make_slide_flash()
    print(">> [SUCCESS] Clean, perfectly legible slide figures generated!")


if __name__ == "__main__":
    main()
