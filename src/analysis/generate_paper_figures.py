#!/usr/bin/env python3
"""
Geração de figuras do artigo utilizando plotnine (implementação do ggplot2 para Python).
Mantém compatibilidade total com o pipeline do repositório.
"""

from pathlib import Path
import pandas as pd
import plotnine as p9
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent.parent.parent / "artigo" / "figures"
DATA = Path(__file__).resolve().parent.parent.parent / "data" / "processed"

OUT.mkdir(parents=True, exist_ok=True)

TEXTW = 395.8225 / 72.27  # ~5.48 polegadas (largura exata de acmsmall)

summ = pd.read_csv(DATA / "summary_bench.csv")
flash = pd.read_csv(DATA / "flash_sizes.csv")

# ==============================================================================
# 1. LATENCY PLOT (ggplot2 / plotnine)
# ==============================================================================
def make_latency_plot():
    s = summ[summ.operation != "msgcrypt"].copy()
    
    op_map = {"keygen": "KeyGen", "encaps": "Encaps", "decaps": "Decaps"}
    alg_map = {"kyber512": "Kyber-512", "ctru-light": "CTRU-Light", "ecdh": "ECDH"}
    panel_map = {
        ("asm", "-O3"): "Assembly (-O3)",
        ("asm", "-Os"): "Assembly (-Os)",
        ("ref", "-O3"): "Referência (-O3)",
        ("ref", "-Os"): "Referência (-Os)",
    }
    
    s["op_label"] = pd.Categorical(s.operation.map(op_map), categories=["KeyGen", "Encaps", "Decaps"], ordered=True)
    s["alg_label"] = pd.Categorical(s.algorithm.map(alg_map), categories=["Kyber-512", "CTRU-Light", "ECDH"], ordered=True)
    s["panel"] = pd.Categorical(
        [panel_map[(v, o)] for v, o in zip(s.variant, s.optimization)],
        categories=["Assembly (-O3)", "Assembly (-Os)", "Referência (-O3)", "Referência (-Os)"],
        ordered=True
    )
    
    s["ymin"] = s.mean_ms - s.ci95_ms
    s["ymax"] = s.mean_ms + s.ci95_ms
    
    dodge = p9.position_dodge(width=0.35)
    
    p = (
        p9.ggplot(s, p9.aes(x="op_label", y="mean_ms", color="alg_label", group="alg_label"))
        + p9.geom_line(position=dodge, linetype="dashed", size=0.6, alpha=0.85)
        + p9.geom_errorbar(p9.aes(ymin="ymin", ymax="ymax"), position=dodge, width=0.18, size=0.5)
        + p9.geom_point(p9.aes(shape="alg_label"), position=dodge, size=2.2)
        + p9.facet_wrap("~ panel", nrow=1)
        + p9.scale_y_log10(breaks=[100, 1000, 10000], labels=["100 ms", "1 s", "10 s"], limits=(60, 25000))
        + p9.scale_color_manual(values={"Kyber-512": "#0072B2", "CTRU-Light": "#D55E00", "ECDH": "#009E73"}, name=" ")
        + p9.scale_shape_manual(values={"Kyber-512": "o", "CTRU-Light": "s", "ECDH": "^"}, name=" ")
        + p9.labs(x="", y="Latência (escala log)")
        + p9.theme_bw(base_size=8)
        + p9.theme(
            legend_position="top",
            legend_direction="horizontal",
            legend_box_spacing=0.05,
            legend_margin=0,
            axis_text_x=p9.element_text(rotation=25, ha="right", size=7),
            strip_background=p9.element_rect(fill="#f0f0f0", color="#cccccc", size=0.5),
            strip_text=p9.element_text(weight="bold", size=7.5),
            panel_grid_minor=p9.element_blank(),
            panel_grid_major_x=p9.element_blank(),
            panel_grid_major_y=p9.element_line(color="#e0e0e0", size=0.4, linetype="dotted"),
            figure_size=(TEXTW, 2.5)
        )
    )
    
    fig = p.draw()
    fig.savefig(OUT / "latency.png", dpi=300, bbox_inches="tight")
    fig.savefig(OUT / "latency.pdf", bbox_inches="tight")
    plt.close(fig)
    print("Latency figure saved!")

# ==============================================================================
# 2. TRADEOFF PLOT (ggplot2 / plotnine com eixo secundário)
# ==============================================================================
def make_tradeoff_plot():
    s = summ[summ.operation != "msgcrypt"].copy()
    
    alg_map = {"kyber512": "Kyber-512", "ctru-light": "CTRU-Light", "ecdh": "ECDH"}
    s["cfg_label"] = [f"{alg_map[a]} ({v})" for a, v in zip(s.algorithm, s.variant)]
    cfg_order = [
        "Kyber-512 (asm)", "Kyber-512 (ref)",
        "CTRU-Light (asm)", "CTRU-Light (ref)",
        "ECDH (asm)", "ECDH (ref)"
    ]
    s["cfg_label"] = pd.Categorical(s.cfg_label, categories=cfg_order, ordered=True)
    
    s["ymin"] = s.mean_ms - s.ci95_ms
    s["ymax"] = s.mean_ms + s.ci95_ms
    
    colors = {
        "Kyber-512 (asm)": "#0072B2", "Kyber-512 (ref)": "#0072B2",
        "CTRU-Light (asm)": "#D55E00", "CTRU-Light (ref)": "#D55E00",
        "ECDH (asm)": "#009E73", "ECDH (ref)": "#009E73"
    }
    fills = {
        "Kyber-512 (asm)": "#0072B2", "Kyber-512 (ref)": "white",
        "CTRU-Light (asm)": "#D55E00", "CTRU-Light (ref)": "white",
        "ECDH (asm)": "#009E73", "ECDH (ref)": "white"
    }
    shapes = {
        "Kyber-512 (asm)": "o", "Kyber-512 (ref)": "s",
        "CTRU-Light (asm)": "o", "CTRU-Light (ref)": "s",
        "ECDH (asm)": "o", "ECDH (ref)": "s"
    }
    
    p = (
        p9.ggplot(s, p9.aes(x="stack_peak_b", y="mean_ms", color="cfg_label", fill="cfg_label", shape="cfg_label"))
        + p9.geom_errorbar(p9.aes(ymin="ymin", ymax="ymax"), width=25, size=0.5, alpha=0.8)
        + p9.geom_point(size=2.8, stroke=1.1)
        + p9.scale_x_continuous(
            limits=(350, 3500),
            breaks=[500, 1000, 1500, 2000, 2500, 3000],
            labels=["500 B", "1.000 B", "1.500 B", "2.000 B", "2.500 B", "3.000 B"]
        )
        + p9.scale_y_log10(
            limits=(60, 25000),
            breaks=[100, 1000, 10000],
            labels=["100 ms", "1 s", "10 s"]
        )
        + p9.scale_color_manual(values=colors, name="Configuração")
        + p9.scale_fill_manual(values=fills, name="Configuração")
        + p9.scale_shape_manual(values=shapes, name="Configuração")
        + p9.guides(
            color=p9.guide_legend(ncol=2),
            fill=p9.guide_legend(ncol=2),
            shape=p9.guide_legend(ncol=2)
        )
        + p9.labs(x="Pico de pilha (bytes)", y="Latência média (escala log)")
        + p9.theme_bw(base_size=8)
        + p9.theme(
            legend_position=(0.77, 0.77),
            legend_background=p9.element_rect(fill="white", color="#d0d0d0", size=0.5),
            legend_title=p9.element_blank(),
            legend_text=p9.element_text(size=7),
            legend_key=p9.element_blank(),
            legend_box_margin=2,
            panel_grid_minor=p9.element_blank(),
            panel_grid_major=p9.element_line(color="#e5e5e5", size=0.4, linetype="dotted"),
            figure_size=(TEXTW, 2.5)
        )
    )
    
    fig = p.draw()
    ax = fig.axes[0]
    ax_top = ax.twiny()
    ax_top.set_xlim(ax.get_xlim())
    top_pcts = [10, 20, 30, 40, 50]
    top_ticks = [6144 * p_val / 100 for p_val in top_pcts]
    ax_top.set_xticks(top_ticks)
    ax_top.set_xticklabels([f"{p_val}%" for p_val in top_pcts], fontsize=7)
    ax_top.set_xlabel("Ocupação da SRAM do ATmega4809 (total 6 KB)", fontsize=7.5, labelpad=4)
    ax_top.grid(False)
    
    fig.savefig(OUT / "tradeoff.png", dpi=300, bbox_inches="tight")
    fig.savefig(OUT / "tradeoff.pdf", bbox_inches="tight")
    plt.close(fig)
    print("Tradeoff figure saved!")

# ==============================================================================
# 3. FLASH SIZES PLOT (ggplot2 / plotnine)
# ==============================================================================
def make_flash_plot():
    fl = flash.copy()
    
    alg_map = {"kyber512": "Kyber-512", "ctru-light": "CTRU-Light", "ecdh": "ECDH"}
    fl["alg_name"] = fl.algorithm.map(alg_map)
    fl["cfg"] = [f"{a}\n{v}" for a, v in zip(fl.alg_name, fl.variant)]
    
    order = [
        "Kyber-512\nasm", "Kyber-512\nref",
        "CTRU-Light\nasm", "CTRU-Light\nref",
        "ECDH\nasm", "ECDH\nref"
    ]
    fl["cfg"] = pd.Categorical(fl.cfg, categories=order, ordered=True)
    fl["flash_kb"] = fl.flash_b / 1024.0
    
    opt_map = {"-O3": "Otimização -O3", "-Os": "Otimização -Os"}
    fl["opt_label"] = pd.Categorical(fl.optimization.map(opt_map), categories=["Otimização -O3", "Otimização -Os"], ordered=True)
    
    colors = {"Otimização -O3": "#0072B2", "Otimização -Os": "#E69F00"}
    
    p = (
        p9.ggplot(fl, p9.aes(x="cfg", y="flash_kb", fill="opt_label"))
        + p9.geom_col(position=p9.position_dodge(width=0.65), width=0.58, color="black", size=0.4)
        + p9.geom_hline(yintercept=48, linetype="dashed", color="#B22222", size=0.8)
        + p9.annotate("text", x=5.4, y=50.2, label="Capacidade do MCU (48 KB)",
                      color="#B22222", size=7.5, fontweight="bold", ha="right", va="bottom")
        + p9.scale_fill_manual(values=colors, name="")
        + p9.scale_y_continuous(
            limits=(0, 56),
            breaks=[0, 8, 16, 24, 32, 40, 48],
            expand=(0, 0, 0.05, 0)
        )
        + p9.labs(x="", y="Flash ocupada (KB)")
        + p9.theme_bw(base_size=8)
        + p9.theme(
            legend_position="top",
            legend_direction="horizontal",
            legend_title=p9.element_blank(),
            legend_box_spacing=0.05,
            panel_grid_minor=p9.element_blank(),
            panel_grid_major_x=p9.element_blank(),
            panel_grid_major_y=p9.element_line(color="#e0e0e0", size=0.4, linetype="dotted"),
            figure_size=(TEXTW, 2.3)
        )
    )
    
    fig = p.draw()
    fig.savefig(OUT / "flash.png", dpi=300, bbox_inches="tight")
    fig.savefig(OUT / "flash.pdf", bbox_inches="tight")
    plt.close(fig)
    print("Flash figure saved!")

if __name__ == "__main__":
    make_latency_plot()
    make_tradeoff_plot()
    make_flash_plot()
    print("Direct export to artigo/figures complete via ggplot2 (plotnine)!")
