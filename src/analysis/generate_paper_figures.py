import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
from pathlib import Path

OUT = Path("/home/eduabdala/git/project-cspa-cmp223/artigo/figures")
DATA = Path("/home/eduabdala/git/project-cspa-cmp223/data/processed")

sns.set_theme(style="ticks", context="paper")
TEXTW = 395.8225 / 72.27  # ~5.48 in

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Linux Libertine", "Libertinus Serif", "DejaVu Serif"],
    "font.size": 8,
    "axes.labelsize": 8,
    "axes.titlesize": 8,
    "legend.fontsize": 7,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "axes.linewidth": 0.6,
    "grid.linewidth": 0.4,
    "lines.linewidth": 1.0,
    "axes.grid": True,
    "grid.alpha": 0.4,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.03,
})

PAL = {"kyber512": "#0072B2", "ctru-light": "#D55E00", "ecdh": "#009E73"}
LABEL = {"kyber512": "Kyber-512", "ctru-light": "CTRU-Light", "ecdh": "ECDH"}

df = pd.read_csv(DATA / "bench_tidy.csv")
summ = pd.read_csv(DATA / "summary_bench.csv")
flash = pd.read_csv(DATA / "flash_sizes.csv")

# ==============================================================================
# 1. LATENCY PLOT
# ==============================================================================
def make_latency_plot():
    kem = df[df.operation != "msgcrypt"].copy()
    kem["cfg"] = kem.variant + " " + kem.optimization
    cols = ["asm -O3", "asm -Os", "ref -O3", "ref -Os"]
    titles = ["Assembly (-O3)", "Assembly (-Os)", "Referência (-O3)", "Referência (-Os)"]
    
    fig, axs = plt.subplots(1, 4, figsize=(TEXTW, 2.3), sharey=True)
    
    op_map = {"keygen": "KeyGen", "encaps": "Encaps", "decaps": "Decaps"}
    kem["op_label"] = kem.operation.map(op_map)
    op_order = ["KeyGen", "Encaps", "Decaps"]
    
    for i, (ax, cfg, title) in enumerate(zip(axs, cols, titles)):
        sub_ = kem[kem.cfg == cfg]
        
        sns.pointplot(
            data=sub_, x="op_label", y="t_exec_ms", hue="algorithm", ax=ax,
            order=op_order, hue_order=["kyber512", "ctru-light", "ecdh"],
            palette=PAL, errorbar=("ci", 95), dodge=0.28,
            linestyles="--", markers=["o", "s", "D"], markersize=4,
            err_kws={"linewidth": 0.8}, legend=False
        )
        ax.set_title(title, fontsize=7.5, fontweight="bold", pad=4)
        ax.set_xlabel("")
        ax.tick_params(axis="x", rotation=25, labelsize=6.8)
        # align tick labels nicely
        for label in ax.get_xticklabels():
            label.set_horizontalalignment('right')
        ax.grid(True, axis="y", linestyle=":", alpha=0.5)
        ax.grid(False, axis="x")
        if i > 0:
            ax.tick_params(axis="y", left=False)

    axs[0].set_yscale("log")
    axs[0].set_ylim(60, 25000)
    axs[0].set_ylabel("Latência (escala log)", fontsize=8)
    
    y_ticks = [100, 1000, 10000]
    axs[0].set_yticks(y_ticks)
    axs[0].yaxis.set_major_formatter(
        ticker.FuncFormatter(lambda y, _: f"{int(y):,} ms" if y < 1000 else f"{int(y/1000)} s")
    )
    
    handles = [
        plt.Line2D([0], [0], color=PAL["kyber512"], marker="o", linestyle="--", lw=1.0, ms=4, label="Kyber-512"),
        plt.Line2D([0], [0], color=PAL["ctru-light"], marker="s", linestyle="--", lw=1.0, ms=4, label="CTRU-Light"),
        plt.Line2D([0], [0], color=PAL["ecdh"], marker="D", linestyle="--", lw=1.0, ms=4, label="ECDH"),
    ]
    fig.legend(handles=handles, loc="upper center", ncol=3, frameon=False,
               bbox_to_anchor=(0.5, 1.08), fontsize=7.5)
    
    sns.despine(fig)
    fig.tight_layout(rect=[0, 0, 1, 0.93], w_pad=0.5)
    fig.savefig(OUT / "latency.png", dpi=300)
    fig.savefig(OUT / "latency.pdf")
    plt.close(fig)

# ==============================================================================
# 2. TRADEOFF PLOT (Stack peak vs Latency)
# ==============================================================================
def make_tradeoff_plot():
    s = summ[summ.operation != "msgcrypt"].copy()
    
    fig, ax = plt.subplots(figsize=(TEXTW, 2.5))
    
    alg_order = ["kyber512", "ctru-light", "ecdh"]
    markers = {"asm": "o", "ref": "s"}
    
    for alg in alg_order:
        for var in ["asm", "ref"]:
            g = s[(s.algorithm == alg) & (s.variant == var)]
            if len(g) == 0:
                continue
            label = f"{LABEL[alg]} ({var})"
            ax.errorbar(
                g.stack_peak_b, g.mean_ms, yerr=g.ci95_ms,
                fmt=markers[var],
                color=PAL[alg],
                mfc=PAL[alg] if var == "asm" else "white",
                mec=PAL[alg],
                ms=4.8, mew=1.2, capsize=2, elinewidth=0.8,
                linestyle="none", label=label, zorder=4
            )
            
    ax.set_xlabel("Pico de pilha (bytes)", fontsize=8)
    ax.set_ylabel("Latência média (escala log)", fontsize=8)
    ax.set_yscale("log")
    ax.set_xlim(350, 3500)
    ax.set_ylim(60, 25000)
    
    y_ticks = [100, 1000, 10000]
    ax.set_yticks(y_ticks)
    ax.yaxis.set_major_formatter(
        ticker.FuncFormatter(lambda y, _: f"{int(y):,} ms" if y < 1000 else f"{int(y/1000)} s")
    )
    
    ax.set_xticks([500, 1000, 1500, 2000, 2500, 3000])
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,} B"))
    
    ax_top = ax.twiny()
    ax_top.set_xlim(ax.get_xlim())
    top_pcts = [10, 20, 30, 40, 50]
    top_ticks = [6144 * p / 100 for p in top_pcts]
    ax_top.set_xticks(top_ticks)
    ax_top.set_xticklabels([f"{p}%" for p in top_pcts], fontsize=7)
    ax_top.set_xlabel("Ocupação da SRAM do ATmega4809 (total 6 KB)", fontsize=7.5, labelpad=4)
    ax_top.grid(False)
    
    handles, labels = ax.get_legend_handles_labels()
    order_dict = {
        "Kyber-512 (asm)": 0, "Kyber-512 (ref)": 1,
        "CTRU-Light (asm)": 2, "CTRU-Light (ref)": 3,
        "ECDH (asm)": 4, "ECDH (ref)": 5
    }
    sorted_pairs = sorted(zip(handles, labels), key=lambda p: order_dict.get(p[1], 99))
    h_sorted = [p[0] for p in sorted_pairs]
    l_sorted = [p[1] for p in sorted_pairs]
    
    leg = ax.legend(
        h_sorted, l_sorted,
        frameon=True, facecolor="white", edgecolor="#d0d0d0", framealpha=0.95,
        loc="upper right", bbox_to_anchor=(0.98, 0.96), ncol=2, fontsize=7,
        handletextpad=0.3, columnspacing=0.8
    )
    leg.set_zorder(5)
    
    ax.grid(True, linestyle=":", alpha=0.5)
    sns.despine(fig, top=False)
    fig.tight_layout()
    fig.savefig(OUT / "tradeoff.png", dpi=300)
    fig.savefig(OUT / "tradeoff.pdf")
    plt.close(fig)

# ==============================================================================
# 3. FLASH SIZES PLOT
# ==============================================================================
def make_flash_plot():
    fl = flash.copy()
    fl["alg_name"] = fl.algorithm.map(LABEL)
    fl["cfg"] = fl.alg_name + "\n" + fl.variant
    
    order = [
        "Kyber-512\nasm", "Kyber-512\nref",
        "CTRU-Light\nasm", "CTRU-Light\nref",
        "ECDH\nasm", "ECDH\nref"
    ]
    
    fig, ax = plt.subplots(figsize=(TEXTW, 2.3))
    
    palette = {"-O3": "#0072B2", "-Os": "#E69F00"}
    sns.barplot(
        data=fl, x="cfg", y="flash_b", hue="optimization", ax=ax,
        order=order, palette=palette, width=0.62,
        edgecolor="black", linewidth=0.5, zorder=3
    )
    
    ax.axhline(49152, color="#c0392b", ls="--", lw=1.0, zorder=4)
    ax.text(5.45, 50200, "Capacidade do MCU (48 KB)", color="#c0392b",
            fontsize=7.5, fontweight="bold", va="bottom", ha="right", zorder=5)
    
    ax.set_xlabel("")
    ax.set_ylabel("Flash ocupada (KB)", fontsize=8)
    ax.set_yticks([k * 8192 for k in range(7)])
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v/1024:.0f}"))
    ax.set_ylim(0, 58000)
    
    ax.grid(True, axis="y", linestyle=":", alpha=0.6, zorder=0)
    ax.grid(False, axis="x")
    
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, ["Otimização -O3", "Otimização -Os"],
              loc="upper center", bbox_to_anchor=(0.5, 1.12),
              frameon=False, ncol=2, fontsize=7.5)
    
    sns.despine(fig)
    fig.tight_layout()
    fig.savefig(OUT / "flash.png", dpi=300)
    fig.savefig(OUT / "flash.pdf")
    plt.close(fig)

make_latency_plot()
make_tradeoff_plot()
make_flash_plot()
print("Direct export to artigo/figures complete!")
