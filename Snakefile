# =============================================================================
# Snakefile — Pipeline Reprodutível do Repositório Principal (CMP223)
# =============================================================================
# Como usar (a partir da raiz do repositório):
#   snakemake -j1              # Roda TUDO sem a placa: compila os 12 firmwares + design + catálogo + notebook + slides + delivery.tgz
#   snakemake -j1 package      # Gera apenas o pacote compactado delivery.tgz limpo
#   snakemake -j1 experiment   # Roda o EXPERIMENTO COMPLETO na bancada (MCU + LA) + atualiza tudo + gera delivery.tgz
#   snakemake -j1 clean        # Limpa todos os artefatos gerados (firmwares, CSVs, figuras, tabelas, slides, outputs do .ipynb e .tgz)
#   snakemake -n               # Dry-run: exibe o grafo de tarefas pendentes sem executar
# =============================================================================

import glob
import json
import os
import pathlib
import shutil
import tarfile

configfile: "src/analysis/config.yaml"

# Caminhos relativos à raiz do projeto
PYTHON = ".venv/bin/python" if os.path.exists(".venv/bin/python") else ("delivery/.venv/bin/python" if os.path.exists("delivery/.venv/bin/python") else "python3")
ENV_PREFIX = (
    'LD_LIBRARY_PATH=".venv/lib:${LD_LIBRARY_PATH:-}"'
    if os.path.exists(".venv/lib")
    else ('LD_LIBRARY_PATH="delivery/.venv/lib:${LD_LIBRARY_PATH:-}"' if os.path.exists("delivery/.venv/lib") else "")
)

RAW_TELEMETRY = sorted(glob.glob("data/experiments/exp_*/raw/telemetry_*.json"))

ALGS = ["kyber512", "ctru-light", "ecdh"]
VARS = ["asm", "ref"]
OPTS = ["O3", "Os"]

FIRMWARE_HEX = [
    f"src/firmware/atmega4809/build/firmware-{alg}-{var}-20MHz-{opt}.hex"
    for alg in ALGS
    for var in VARS
    for opt in OPTS
]

PROCESSED_CSVS = [
    "results/processed/bench_history_tidy.csv",
    "results/processed/campaigns_history.csv",
    "results/processed/bench_tidy.csv",
    "results/processed/la_vs_uart_overhead.csv",
    "results/processed/summary_bench.csv",
    "results/processed/flash_sizes.csv",
    "results/processed/anova_latency.csv",
]

LATEX_TABLES = [
    "results/tables/results.tex",
    "results/tables/anova.tex",
]

FIGURES = [
    "results/figures/historico_todos_experimentos.png",
    "results/figures/historico_todos_experimentos.pdf",
    "results/figures/oscillogram.png",
    "results/figures/drift_kyber_asm.png",
    "results/figures/drift_kyber_asm.pdf",
    "results/figures/flash.png",
    "results/figures/flash.pdf",
    "results/figures/latency.png",
    "results/figures/latency.pdf",
    "results/figures/bimodality.png",
    "results/figures/bimodality.pdf",
    "results/figures/residuals.png",
    "results/figures/residuals.pdf",
    "results/figures/tradeoff.png",
    "results/figures/tradeoff.pdf",
]

SLIDE_FIGURES = [
    "slides/figures/historico_todos_experimentos.png",
    "slides/figures/slide_oscillogram.png",
    "slides/figures/slide_bancada_setup.png",
    "slides/figures/slide_flash.png",
    "slides/figures/slide_bimodality.png",
    "slides/figures/slide_tradeoff.png",
]

SLIDE_DECKS = [
    "results/slides/01-proposta.pdf",
    "results/slides/02-parcial.pdf",
    "results/slides/01-proposta.html",
    "results/slides/02-parcial.html",
]


def build_delivery_tgz(out_tgz="delivery.tgz"):
    """Empacota a pasta delivery/ em delivery.tgz ignorando caches, ambientes e artefatos derivados."""
    exclude_dirs = {".venv", "node_modules", ".snakemake", "__pycache__", ".ipynb_checkpoints", "build"}
    exclude_files = {".env", "delivery.tgz"}

    def _filter(tarinfo):
        parts = pathlib.Path(tarinfo.name).parts
        if any(p in exclude_dirs for p in parts):
            return None
        if parts[-1] in exclude_files or parts[-1].endswith(".pyc"):
            return None
        if len(parts) >= 3 and parts[0] == "delivery" and parts[1] == "results" and parts[-1] != ".gitkeep" and not tarinfo.isdir():
            return None
        if len(parts) == 4 and parts[:3] == ("delivery", "slides", "figures") and parts[-1].endswith(".png"):
            return None
        return tarinfo

    with tarfile.open(out_tgz, "w:gz") as tar:
        tar.add("delivery", arcname="delivery", filter=_filter)
    size_mb = os.path.getsize(out_tgz) / (1024 * 1024)
    print(f"[PACKAGE] Gerado {out_tgz} ({size_mb:.2f} MB)")


# ---- Meta padrão (sem placa): compila os 12 firmwares + design + catálogo + notebook + slides + delivery.tgz ----
rule all:
    input:
        FIRMWARE_HEX,
        "results/processed/design.csv",
        "data/experiments/catalog.csv",
        PROCESSED_CSVS,
        LATEX_TABLES,
        FIGURES,
        SLIDE_FIGURES,
        SLIDE_DECKS,
        "delivery.tgz"

# ---- 0. Compilação bare-metal dos 12 firmwares AVR (ATmega4809 @ 20 MHz) ----
rule build_firmware:
    output:
        hex="src/firmware/atmega4809/build/firmware-{alg}-{var}-20MHz-{opt}.hex"
    shell:
        r"""
        rm -f src/firmware/atmega4809/build/*.o src/firmware/atmega4809/build/*.elf
        make -C src/firmware/atmega4809 ALG={wildcards.alg} VARIANT={wildcards.var} OPT=-{wildcards.opt} F_CPU=20000000UL
        cp src/firmware/atmega4809/build/firmware-{wildcards.alg}-{wildcards.var}.hex {output.hex}
        """

rule firmware:
    input:
        FIRMWARE_HEX

# ---- 1. Matriz de planejamento experimental fatorial (pyDOE3) ----
rule design:
    input:
        "src/analysis/config.yaml"
    output:
        "results/processed/design.csv"
    shell:
        "{ENV_PREFIX} {PYTHON} src/analysis/design.py --config {input} --out {output}"

# ---- 2. Auditoria dos dados brutos e geração do catálogo de campanhas ----
rule catalog:
    input:
        RAW_TELEMETRY
    output:
        "data/experiments/catalog.csv"
    shell:
        "{ENV_PREFIX} {PYTHON} src/analysis/catalog.py"

# ---- 3. Execução completa do caderno analise.ipynb (estatística, tabelas e figuras) ----
rule analysis_notebook:
    input:
        catalog="data/experiments/catalog.csv",
        nb="src/analysis/analise.ipynb",
        photo="slides/figures/bancada.jpg"
    output:
        PROCESSED_CSVS,
        LATEX_TABLES,
        FIGURES,
        SLIDE_FIGURES
    shell:
        "{ENV_PREFIX} {PYTHON} -m jupyter nbconvert --to notebook --execute --inplace {input.nb}"

# ---- 4. Renderização das apresentações Marp (PDF e HTML) ----
rule slides:
    input:
        md1="slides/01-proposta.md",
        md2="slides/02-parcial.md",
        figs=SLIDE_FIGURES
    output:
        SLIDE_DECKS
    shell:
        r"""
        if [ ! -d "node_modules" ]; then npm ci --no-audit --no-fund; fi
        npm run pdf
        npm run html
        """

# ---- 5. Empacotamento do entregável delivery.tgz ----
rule package:
    input:
        "delivery/README.md",
        "delivery/Snakefile",
        "delivery/Makefile",
        "delivery/flake.nix",
        "delivery/data/experiments/catalog.csv",
        "delivery/src/analysis/analise.ipynb"
    output:
        "delivery.tgz"
    run:
        build_delivery_tgz(output[0])

# ---- 6. Experimento completo de ponta a ponta (Bancada + Catálogo + Notebook + Slides + delivery.tgz) ----
rule experiment:
    params:
        mode=config.get("mode", "bench"),
        port=config.get("port", config.get("serial_port", "/dev/ttyACM0")),
        n=config.get("iterations", 30),
        seed=config.get("seed", 42),
        tag=config.get("tag", "bench_campanha_completa_la_nix")
    shell:
        r"""
        {ENV_PREFIX} {PYTHON} src/analysis/run_experiment.py \
            --mode {params.mode} --port {params.port} \
            --alg all --variants asm ref --opts O3 Os --clocks 20 \
            -n {params.n} --seed {params.seed} \
            --tag {params.tag}
        {ENV_PREFIX} {PYTHON} src/analysis/design.py --config src/analysis/config.yaml --out results/processed/design.csv
        {ENV_PREFIX} {PYTHON} src/analysis/catalog.py
        cp data/experiments/catalog.csv delivery/data/experiments/catalog.csv
        {ENV_PREFIX} {PYTHON} -m jupyter nbconvert --to notebook --execute --inplace src/analysis/analise.ipynb
        if [ ! -d "node_modules" ]; then npm ci --no-audit --no-fund; fi
        npm run pdf
        npm run html
        snakemake -j1 --forcerun package
        """

# ---- 7. Apenas coleta física na bancada (ATmega4809 + Analisador Lógico 24 MHz) ----
rule bench:
    params:
        port=config.get("port", config.get("serial_port", "/dev/ttyACM0")),
        n=config.get("iterations", 30),
        seed=config.get("seed", 42),
        tag=config.get("tag", "bench_campanha_completa_la_nix")
    shell:
        r"""
        {ENV_PREFIX} {PYTHON} src/analysis/run_experiment.py \
            --mode bench --port {params.port} \
            --alg all --variants asm ref --opts O3 Os --clocks 20 \
            -n {params.n} --seed {params.seed} \
            --tag {params.tag}
        {ENV_PREFIX} {PYTHON} src/analysis/catalog.py
        """

# ---- 8. Limpeza de todos os artefatos derivados para testar ou commitar do zero ----
rule clean:
    run:
        for base in [pathlib.Path("."), pathlib.Path("delivery")]:
            shutil.rmtree(base / "src/firmware/atmega4809/build", ignore_errors=True)
            for pattern in [
                "results/processed/*.csv",
                "results/tables/*.tex",
                "results/figures/*.png",
                "results/figures/*.pdf",
                "results/slides/*",
                "slides/figures/*.png",
            ]:
                for f in glob.glob(str(base / pattern)):
                    if os.path.isfile(f):
                        os.remove(f)
            nb_path = base / "src/analysis/analise.ipynb"
            if nb_path.exists():
                nb = json.loads(nb_path.read_text(encoding="utf-8"))
                for c in nb.get("cells", []):
                    if c.get("cell_type") == "code":
                        c["outputs"] = []
                        c["execution_count"] = None
                nb_path.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        if os.path.exists("delivery.tgz"):
            os.remove("delivery.tgz")
        print("[OK] Repositório e delivery/ limpos! Todos os resultados gerados e outputs do notebook foram removidos.")
