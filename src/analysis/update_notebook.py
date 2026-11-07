import json
from pathlib import Path

nb_path = Path("/home/eduabdala/git/project-cspa-cmp223/src/analysis/analise.ipynb")
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

# Improved code for flash (cell with "fig.savefig(FIG / \"flash.pdf\")")
flash_code = [
    "fl = flash.copy()\n",
    "fl[\"alg_name\"] = fl.algorithm.map(LABEL)\n",
    "fl[\"cfg\"] = fl.alg_name + \"\\n\" + fl.variant\n",
    "order = [\"Kyber-512\\nasm\", \"Kyber-512\\nref\", \"CTRU-Light\\nasm\", \"CTRU-Light\\nref\", \"ECDH\\nasm\", \"ECDH\\nref\"]\n",
    "fig, ax = plt.subplots(figsize=(TEXTW, 2.3))\n",
    "palette = {\"-O3\": \"#0072B2\", \"-Os\": \"#E69F00\"}\n",
    "sns.barplot(data=fl, x=\"cfg\", y=\"flash_b\", hue=\"optimization\", ax=ax,\n",
    "            order=order, palette=palette, width=0.62, edgecolor=\"black\", linewidth=0.5, zorder=3)\n",
    "ax.axhline(49152, color=\"#c0392b\", ls=\"--\", lw=1.0, zorder=4)\n",
    "ax.text(5.45, 50200, \"Capacidade do MCU (48 KB)\", color=\"#c0392b\", fontsize=7.5, fontweight=\"bold\", va=\"bottom\", ha=\"right\", zorder=5)\n",
    "ax.set_xlabel(\"\"); ax.set_ylabel(\"Flash ocupada (KB)\")\n",
    "ax.set_yticks([k * 8192 for k in range(7)])\n",
    "ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f\"{v/1024:.0f}\"))\n",
    "ax.set_ylim(0, 58000)\n",
    "ax.grid(True, axis=\"y\", linestyle=\":\", alpha=0.6, zorder=0); ax.grid(False, axis=\"x\")\n",
    "handles, labels = ax.get_legend_handles_labels()\n",
    "ax.legend(handles, [\"Otimização -O3\", \"Otimização -Os\"], loc=\"upper center\", bbox_to_anchor=(0.5, 1.12), frameon=False, ncol=2, fontsize=7.5)\n",
    "sns.despine(fig)\n",
    "fig.savefig(FIG / \"flash.pdf\"); fig.savefig(FIG / \"flash.png\", dpi=300)\n"
]

# Improved code for latency (cell with "fig.savefig(FIG / \"latency.pdf\")")
latency_code = [
    "import matplotlib.ticker as ticker\n",
    "kem = df[df.operation != \"msgcrypt\"].copy()\n",
    "kem[\"cfg\"] = kem.variant + \" \" + kem.optimization\n",
    "cols = [\"asm -O3\", \"asm -Os\", \"ref -O3\", \"ref -Os\"]\n",
    "titles = [\"Assembly (-O3)\", \"Assembly (-Os)\", \"Referência (-O3)\", \"Referência (-Os)\"]\n",
    "op_map = {\"keygen\": \"KeyGen\", \"encaps\": \"Encaps\", \"decaps\": \"Decaps\"}\n",
    "kem[\"op_label\"] = kem.operation.map(op_map)\n",
    "op_order = [\"KeyGen\", \"Encaps\", \"Decaps\"]\n",
    "fig, axs = plt.subplots(1, 4, figsize=(TEXTW, 2.3), sharey=True)\n",
    "for i, (ax, cfg, title) in enumerate(zip(axs, cols, titles)):\n",
    "    sub_ = kem[kem.cfg == cfg]\n",
    "    sns.pointplot(data=sub_, x=\"op_label\", y=\"t_exec_ms\", hue=\"algorithm\", ax=ax,\n",
    "                  order=op_order, hue_order=[\"kyber512\", \"ctru-light\", \"ecdh\"],\n",
    "                  palette=PAL, errorbar=(\"ci\", 95), dodge=0.28, linestyles=\"--\",\n",
    "                  markers=[\"o\", \"s\", \"D\"], markersize=4, err_kws={\"linewidth\": 0.8}, legend=False)\n",
    "    ax.set_title(title, fontsize=7.5, fontweight=\"bold\", pad=4)\n",
    "    ax.set_xlabel(\"\"); ax.tick_params(axis=\"x\", rotation=25, labelsize=6.8)\n",
    "    for label in ax.get_xticklabels(): label.set_horizontalalignment('right')\n",
    "    ax.grid(True, axis=\"y\", linestyle=\":\", alpha=0.5); ax.grid(False, axis=\"x\")\n",
    "    if i > 0: ax.tick_params(axis=\"y\", left=False)\n",
    "axs[0].set_yscale(\"log\"); axs[0].set_ylim(60, 25000); axs[0].set_ylabel(\"Latência (escala log)\")\n",
    "axs[0].set_yticks([100, 1000, 10000])\n",
    "axs[0].yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: f\"{int(y):,} ms\" if y < 1000 else f\"{int(y/1000)} s\"))\n",
    "handles = [\n",
    "    plt.Line2D([0], [0], color=PAL[\"kyber512\"], marker=\"o\", linestyle=\"--\", lw=1.0, ms=4, label=\"Kyber-512\"),\n",
    "    plt.Line2D([0], [0], color=PAL[\"ctru-light\"], marker=\"s\", linestyle=\"--\", lw=1.0, ms=4, label=\"CTRU-Light\"),\n",
    "    plt.Line2D([0], [0], color=PAL[\"ecdh\"], marker=\"D\", linestyle=\"--\", lw=1.0, ms=4, label=\"ECDH\"),\n",
    "]\n",
    "fig.legend(handles=handles, loc=\"upper center\", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.08), fontsize=7.5)\n",
    "sns.despine(fig)\n",
    "fig.tight_layout(rect=[0, 0, 1, 0.93], w_pad=0.5)\n",
    "fig.savefig(FIG / \"latency.pdf\"); fig.savefig(FIG / \"latency.png\", dpi=300)\n"
]

# Improved code for tradeoff (cell with "fig.savefig(FIG / \"tradeoff.pdf\")")
tradeoff_code = [
    "import matplotlib.ticker as ticker\n",
    "s = summ[summ.operation != \"msgcrypt\"].copy()\n",
    "fig, ax = plt.subplots(figsize=(TEXTW, 2.5))\n",
    "alg_order = [\"kyber512\", \"ctru-light\", \"ecdh\"]\n",
    "markers = {\"asm\": \"o\", \"ref\": \"s\"}\n",
    "for alg in alg_order:\n",
    "    for var in [\"asm\", \"ref\"]:\n",
    "        g = s[(s.algorithm == alg) & (s.variant == var)]\n",
    "        if len(g) == 0: continue\n",
    "        label = f\"{LABEL[alg]} ({var})\"\n",
    "        ax.errorbar(g.stack_peak_b, g.mean_ms, yerr=g.ci95_ms, fmt=markers[var],\n",
    "                    color=PAL[alg], mfc=PAL[alg] if var == \"asm\" else \"white\", mec=PAL[alg],\n",
    "                    ms=4.8, mew=1.2, capsize=2, elinewidth=0.8, linestyle=\"none\", label=label, zorder=4)\n",
    "ax.set_xlabel(\"Pico de pilha (bytes)\"); ax.set_ylabel(\"Latência média (escala log)\")\n",
    "ax.set_yscale(\"log\"); ax.set_xlim(350, 3500); ax.set_ylim(60, 25000)\n",
    "ax.set_yticks([100, 1000, 10000])\n",
    "ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: f\"{int(y):,} ms\" if y < 1000 else f\"{int(y/1000)} s\"))\n",
    "ax.set_xticks([500, 1000, 1500, 2000, 2500, 3000])\n",
    "ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f\"{int(x):,} B\"))\n",
    "ax_top = ax.twiny(); ax_top.set_xlim(ax.get_xlim())\n",
    "top_pcts = [10, 20, 30, 40, 50]\n",
    "top_ticks = [6144 * p / 100 for p in top_pcts]\n",
    "ax_top.set_xticks(top_ticks); ax_top.set_xticklabels([f\"{p}%\" for p in top_pcts], fontsize=7)\n",
    "ax_top.set_xlabel(\"Ocupação da SRAM do ATmega4809 (total 6 KB)\", fontsize=7.5, labelpad=4); ax_top.grid(False)\n",
    "handles, labels = ax.get_legend_handles_labels()\n",
    "order_dict = {\"Kyber-512 (asm)\": 0, \"Kyber-512 (ref)\": 1, \"CTRU-Light (asm)\": 2, \"CTRU-Light (ref)\": 3, \"ECDH (asm)\": 4, \"ECDH (ref)\": 5}\n",
    "sorted_pairs = sorted(zip(handles, labels), key=lambda p: order_dict.get(p[1], 99))\n",
    "leg = ax.legend([p[0] for p in sorted_pairs], [p[1] for p in sorted_pairs],\n",
    "                frameon=True, facecolor=\"white\", edgecolor=\"#d0d0d0\", framealpha=0.95,\n",
    "                loc=\"upper right\", bbox_to_anchor=(0.98, 0.96), ncol=2, fontsize=7, handletextpad=0.3, columnspacing=0.8)\n",
    "leg.set_zorder(5); ax.grid(True, linestyle=\":\", alpha=0.5)\n",
    "sns.despine(fig, top=False); fig.tight_layout()\n",
    "fig.savefig(FIG / \"tradeoff.pdf\"); fig.savefig(FIG / \"tradeoff.png\", dpi=300)\n"
]

for cell in nb["cells"]:
    if cell.get("cell_type") == "code":
        src = "".join(cell.get("source", []))
        if "fig.savefig(FIG / \"flash.pdf\")" in src:
            cell["source"] = flash_code
            print("Updated flash cell!")
        elif "fig.savefig(FIG / \"latency.pdf\")" in src:
            cell["source"] = latency_code
            print("Updated latency cell!")
        elif "fig.savefig(FIG / \"tradeoff.pdf\")" in src:
            cell["source"] = tradeoff_code
            print("Updated tradeoff cell!")

with open(nb_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)
print("Notebook JSON successfully updated!")
