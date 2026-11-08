import json
from pathlib import Path

nb_path = Path(__file__).resolve().parent / "analise.ipynb"
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

# 1. Update imports cell
cell1 = nb["cells"][1]["source"]
cell1_str = "".join(cell1)
if "import plotnine as p9" not in cell1_str:
    cell1_str = cell1_str.replace(
        "import matplotlib.pyplot as plt, seaborn as sns\n",
        "import matplotlib.pyplot as plt, seaborn as sns\nimport plotnine as p9\n"
    )
    nb["cells"][1]["source"] = [line + "\n" for line in cell1_str.split("\n")[:-1]]
    print("Updated imports cell with plotnine!")

# 2. Update drift cell (cell 10)
drift_code = [
    "# Deriva temporal ao longo da ordem de execução (Jain cap. 11): sem tendência\n",
    "# esperada. Gráfico ggplot2 para kyber512 asm -O3 (maior N).\n",
    "sub_drift = df[(df.algorithm == 'kyber512') & (df.variant == 'asm') & (df.optimization == '-O3')].copy()\n",
    "sub_drift['seq'] = sub_drift.groupby('operation').cumcount()\n",
    "p_drift = (\n",
    "    p9.ggplot(sub_drift, p9.aes(x='seq', y='t_exec_ms', color='operation'))\n",
    "    + p9.geom_point(size=1.2, alpha=0.75)\n",
    "    + p9.labs(\n",
    "        x='Ordem de execução (índice dentro da operação)',\n",
    "        y='Latência (ms)',\n",
    "        title='Kyber-512 asm -O3: latência por ordem de execução'\n",
    "    )\n",
    "    + p9.scale_color_brewer(type='qual', palette='Set1', name='Operação')\n",
    "    + p9.theme_bw(base_size=8)\n",
    "    + p9.theme(\n",
    "        legend_position='top',\n",
    "        figure_size=(7, 2.6)\n",
    "    )\n",
    ")\n",
    "fig_drift = p_drift.draw()\n",
    "fig_drift.savefig(FIG / 'drift_kyber_asm.png', dpi=200, bbox_inches='tight')\n",
    "fig_drift.savefig(FIG / 'drift_kyber_asm.pdf', bbox_inches='tight')\n",
    "plt.close(fig_drift)\n"
]

# 3. Flash plot code (ggplot2 / plotnine)
flash_code = [
    "fl = flash.copy()\n",
    "fl['alg_name'] = fl.algorithm.map(LABEL)\n",
    "fl['cfg'] = [f\"{a}\\n{v}\" for a, v in zip(fl.alg_name, fl.variant)]\n",
    "order = ['Kyber-512\\nasm', 'Kyber-512\\nref', 'CTRU-Light\\nasm', 'CTRU-Light\\nref', 'ECDH\\nasm', 'ECDH\\nref']\n",
    "fl['cfg'] = pd.Categorical(fl.cfg, categories=order, ordered=True)\n",
    "fl['flash_kb'] = fl.flash_b / 1024.0\n",
    "opt_map = {'-O3': 'Otimização -O3', '-Os': 'Otimização -Os'}\n",
    "fl['opt_label'] = pd.Categorical(fl.optimization.map(opt_map), categories=['Otimização -O3', 'Otimização -Os'], ordered=True)\n",
    "colors = {'Otimização -O3': '#0072B2', 'Otimização -Os': '#E69F00'}\n",
    "p_flash = (\n",
    "    p9.ggplot(fl, p9.aes(x='cfg', y='flash_kb', fill='opt_label'))\n",
    "    + p9.geom_col(position=p9.position_dodge(width=0.65), width=0.58, color='black', size=0.4)\n",
    "    + p9.geom_hline(yintercept=48, linetype='dashed', color='#B22222', size=0.8)\n",
    "    + p9.annotate('text', x=5.4, y=50.2, label='Capacidade do MCU (48 KB)',\n",
    "                  color='#B22222', size=7.5, fontweight='bold', ha='right', va='bottom')\n",
    "    + p9.scale_fill_manual(values=colors, name='')\n",
    "    + p9.scale_y_continuous(limits=(0, 56), breaks=[0, 8, 16, 24, 32, 40, 48], expand=(0, 0, 0.05, 0))\n",
    "    + p9.labs(x='', y='Flash ocupada (KB)')\n",
    "    + p9.theme_bw(base_size=8)\n",
    "    + p9.theme(\n",
    "        legend_position='top',\n",
    "        legend_direction='horizontal',\n",
    "        legend_title=p9.element_blank(),\n",
    "        legend_box_spacing=0.05,\n",
    "        panel_grid_minor=p9.element_blank(),\n",
    "        panel_grid_major_x=p9.element_blank(),\n",
    "        panel_grid_major_y=p9.element_line(color='#e0e0e0', size=0.4, linetype='dotted'),\n",
    "        figure_size=(TEXTW, 2.3)\n",
    "    )\n",
    ")\n",
    "fig_flash = p_flash.draw()\n",
    "fig_flash.savefig(FIG / 'flash.png', dpi=300, bbox_inches='tight')\n",
    "fig_flash.savefig(FIG / 'flash.pdf', bbox_inches='tight')\n",
    "plt.close(fig_flash)\n"
]

# 4. Latency plot code (ggplot2 / plotnine)
latency_code = [
    "kem = df[df.operation != 'msgcrypt'].copy()\n",
    "s = summ[summ.operation != 'msgcrypt'].copy()\n",
    "op_map = {'keygen': 'KeyGen', 'encaps': 'Encaps', 'decaps': 'Decaps'}\n",
    "alg_map = {'kyber512': 'Kyber-512', 'ctru-light': 'CTRU-Light', 'ecdh': 'ECDH'}\n",
    "panel_map = {\n",
    "    ('asm', '-O3'): 'Assembly (-O3)',\n",
    "    ('asm', '-Os'): 'Assembly (-Os)',\n",
    "    ('ref', '-O3'): 'Referência (-O3)',\n",
    "    ('ref', '-Os'): 'Referência (-Os)',\n",
    "}\n",
    "s['op_label'] = pd.Categorical(s.operation.map(op_map), categories=['KeyGen', 'Encaps', 'Decaps'], ordered=True)\n",
    "s['alg_label'] = pd.Categorical(s.algorithm.map(alg_map), categories=['Kyber-512', 'CTRU-Light', 'ECDH'], ordered=True)\n",
    "s['panel'] = pd.Categorical(\n",
    "    [panel_map[(v, o)] for v, o in zip(s.variant, s.optimization)],\n",
    "    categories=['Assembly (-O3)', 'Assembly (-Os)', 'Referência (-O3)', 'Referência (-Os)'],\n",
    "    ordered=True\n",
    ")\n",
    "s['ymin'] = s.mean_ms - s.ci95_ms\n",
    "s['ymax'] = s.mean_ms + s.ci95_ms\n",
    "dodge = p9.position_dodge(width=0.35)\n",
    "p_lat = (\n",
    "    p9.ggplot(s, p9.aes(x='op_label', y='mean_ms', color='alg_label', group='alg_label'))\n",
    "    + p9.geom_line(position=dodge, linetype='dashed', size=0.6, alpha=0.85)\n",
    "    + p9.geom_errorbar(p9.aes(ymin='ymin', ymax='ymax'), position=dodge, width=0.18, size=0.5)\n",
    "    + p9.geom_point(p9.aes(shape='alg_label'), position=dodge, size=2.2)\n",
    "    + p9.facet_wrap('~ panel', nrow=1)\n",
    "    + p9.scale_y_log10(breaks=[100, 1000, 10000], labels=['100 ms', '1 s', '10 s'], limits=(60, 25000))\n",
    "    + p9.scale_color_manual(values={'Kyber-512': '#0072B2', 'CTRU-Light': '#D55E00', 'ECDH': '#009E73'}, name=' ')\n",
    "    + p9.scale_shape_manual(values={'Kyber-512': 'o', 'CTRU-Light': 's', 'ECDH': '^'}, name=' ')\n",
    "    + p9.labs(x='', y='Latência (escala log)')\n",
    "    + p9.theme_bw(base_size=8)\n",
    "    + p9.theme(\n",
    "        legend_position='top',\n",
    "        legend_direction='horizontal',\n",
    "        legend_box_spacing=0.05,\n",
    "        legend_margin=0,\n",
    "        axis_text_x=p9.element_text(rotation=25, ha='right', size=7),\n",
    "        strip_background=p9.element_rect(fill='#f0f0f0', color='#cccccc', size=0.5),\n",
    "        strip_text=p9.element_text(weight='bold', size=7.5),\n",
    "        panel_grid_minor=p9.element_blank(),\n",
    "        panel_grid_major_x=p9.element_blank(),\n",
    "        panel_grid_major_y=p9.element_line(color='#e0e0e0', size=0.4, linetype='dotted'),\n",
    "        figure_size=(TEXTW, 2.5)\n",
    "    )\n",
    ")\n",
    "fig_lat = p_lat.draw()\n",
    "fig_lat.savefig(FIG / 'latency.png', dpi=300, bbox_inches='tight')\n",
    "fig_lat.savefig(FIG / 'latency.pdf', bbox_inches='tight')\n",
    "plt.close(fig_lat)\n"
]

# 5. Tradeoff plot code (ggplot2 / plotnine)
tradeoff_code = [
    "s = summ[summ.operation != 'msgcrypt'].copy()\n",
    "alg_map = {'kyber512': 'Kyber-512', 'ctru-light': 'CTRU-Light', 'ecdh': 'ECDH'}\n",
    "s['cfg_label'] = [f\"{alg_map[a]} ({v})\" for a, v in zip(s.algorithm, s.variant)]\n",
    "cfg_order = ['Kyber-512 (asm)', 'Kyber-512 (ref)', 'CTRU-Light (asm)', 'CTRU-Light (ref)', 'ECDH (asm)', 'ECDH (ref)']\n",
    "s['cfg_label'] = pd.Categorical(s.cfg_label, categories=cfg_order, ordered=True)\n",
    "s['ymin'] = s.mean_ms - s.ci95_ms\n",
    "s['ymax'] = s.mean_ms + s.ci95_ms\n",
    "colors = {\n",
    "    'Kyber-512 (asm)': '#0072B2', 'Kyber-512 (ref)': '#0072B2',\n",
    "    'CTRU-Light (asm)': '#D55E00', 'CTRU-Light (ref)': '#D55E00',\n",
    "    'ECDH (asm)': '#009E73', 'ECDH (ref)': '#009E73'\n",
    "}\n",
    "fills = {\n",
    "    'Kyber-512 (asm)': '#0072B2', 'Kyber-512 (ref)': 'white',\n",
    "    'CTRU-Light (asm)': '#D55E00', 'CTRU-Light (ref)': 'white',\n",
    "    'ECDH (asm)': '#009E73', 'ECDH (ref)': 'white'\n",
    "}\n",
    "shapes = {\n",
    "    'Kyber-512 (asm)': 'o', 'Kyber-512 (ref)': 's',\n",
    "    'CTRU-Light (asm)': 'o', 'CTRU-Light (ref)': 's',\n",
    "    'ECDH (asm)': 'o', 'ECDH (ref)': 's'\n",
    "}\n",
    "p_trade = (\n",
    "    p9.ggplot(s, p9.aes(x='stack_peak_b', y='mean_ms', color='cfg_label', fill='cfg_label', shape='cfg_label'))\n",
    "    + p9.geom_errorbar(p9.aes(ymin='ymin', ymax='ymax'), width=25, size=0.5, alpha=0.8)\n",
    "    + p9.geom_point(size=2.8, stroke=1.1)\n",
    "    + p9.scale_x_continuous(\n",
    "        limits=(350, 3500),\n",
    "        breaks=[500, 1000, 1500, 2000, 2500, 3000],\n",
    "        labels=['500 B', '1.000 B', '1.500 B', '2.000 B', '2.500 B', '3.000 B']\n",
    "    )\n",
    "    + p9.scale_y_log10(limits=(60, 25000), breaks=[100, 1000, 10000], labels=['100 ms', '1 s', '10 s'])\n",
    "    + p9.scale_color_manual(values=colors, name='Configuração')\n",
    "    + p9.scale_fill_manual(values=fills, name='Configuração')\n",
    "    + p9.scale_shape_manual(values=shapes, name='Configuração')\n",
    "    + p9.guides(color=p9.guide_legend(ncol=2), fill=p9.guide_legend(ncol=2), shape=p9.guide_legend(ncol=2))\n",
    "    + p9.labs(x='Pico de pilha (bytes)', y='Latência média (escala log)')\n",
    "    + p9.theme_bw(base_size=8)\n",
    "    + p9.theme(\n",
    "        legend_position=(0.77, 0.77),\n",
    "        legend_background=p9.element_rect(fill='white', color='#d0d0d0', size=0.5),\n",
    "        legend_title=p9.element_blank(),\n",
    "        legend_text=p9.element_text(size=7),\n",
    "        legend_key=p9.element_blank(),\n",
    "        legend_box_margin=2,\n",
    "        panel_grid_minor=p9.element_blank(),\n",
    "        panel_grid_major=p9.element_line(color='#e5e5e5', size=0.4, linetype='dotted'),\n",
    "        figure_size=(TEXTW, 2.5)\n",
    "    )\n",
    ")\n",
    "fig_trade = p_trade.draw()\n",
    "ax_tr = fig_trade.axes[0]\n",
    "ax_top = ax_tr.twiny()\n",
    "ax_top.set_xlim(ax_tr.get_xlim())\n",
    "top_pcts = [10, 20, 30, 40, 50]\n",
    "top_ticks = [6144 * p_val / 100 for p_val in top_pcts]\n",
    "ax_top.set_xticks(top_ticks)\n",
    "ax_top.set_xticklabels([f\"{p_val}%\" for p_val in top_pcts], fontsize=7)\n",
    "ax_top.set_xlabel('Ocupação da SRAM do ATmega4809 (total 6 KB)', fontsize=7.5, labelpad=4)\n",
    "ax_top.grid(False)\n",
    "fig_trade.savefig(FIG / 'tradeoff.png', dpi=300, bbox_inches='tight')\n",
    "fig_trade.savefig(FIG / 'tradeoff.pdf', bbox_inches='tight')\n",
    "plt.close(fig_trade)\n"
]

for cell in nb["cells"]:
    src = "".join(cell.get("source", []))
    if 'drift_kyber_asm' in src:
        cell["source"] = drift_code
        print("Updated drift cell!")
    elif 'fig.savefig(FIG / "flash.pdf")' in src or 'fig_flash.savefig' in src or 'flash.pdf' in src:
        cell["source"] = flash_code
        print("Updated flash cell!")
    elif 'fig.savefig(FIG / "latency.pdf")' in src or 'fig_lat.savefig' in src or 'latency.pdf' in src:
        cell["source"] = latency_code
        print("Updated latency cell!")
    elif 'fig.savefig(FIG / "tradeoff.pdf")' in src or 'fig_trade.savefig' in src or 'tradeoff.pdf' in src:
        cell["source"] = tradeoff_code
        print("Updated tradeoff cell!")

with open(nb_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1)

print("Notebook successfully updated with ggplot2 (plotnine) figures!")
