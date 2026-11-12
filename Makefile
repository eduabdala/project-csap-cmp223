# =============================================================================
# Makefile — Repositório Principal (CMP223)
# =============================================================================
SHELL := /bin/bash
VENV_DIR := $(shell [ -d ".venv" ] && echo ".venv" || echo "delivery/.venv")
LIB_PATH := $(VENV_DIR)/lib:$(LD_LIBRARY_PATH)

.PHONY: all venv analysis slides package firmware experiment clean clean-all

# Executa todo o pipeline do repositório e já gera o pacote delivery.tgz
all: venv analysis slides package
	@echo "=================================================================="
	@echo "[OK] Pipeline completo do repositório concluído!"
	@echo "  - Catálogo:       data/experiments/catalog.csv"
	@echo "  - Dados/Tabelas:  results/processed/ e results/tables/"
	@echo "  - Gráficos:       results/figures/ e slides/figures/"
	@echo "  - Notebook:       src/analysis/analise.ipynb"
	@echo "  - Slides:         results/slides/01-proposta.pdf e 02-parcial.pdf"
	@echo "  - Entregável:     delivery.tgz"
	@echo "=================================================================="

venv:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		python3 -m venv .venv; \
		.venv/bin/python -m pip install -q --upgrade pip; \
		.venv/bin/python -m pip install -q -r src/analysis/requirements-notebook.txt; \
	fi
	@mkdir -p "$(VENV_DIR)/lib"
	@for lib in libstdc++.so.6 libgcc_s.so.1 libz.so.1; do \
		if [ ! -e "$(VENV_DIR)/lib/$$lib" ]; then \
			p=$$(find /nix/store -maxdepth 3 -name "$$lib" 2>/dev/null | head -n 1); \
			[ -n "$$p" ] && cp -L "$$p" "$(VENV_DIR)/lib/$$lib" || true; \
		fi; \
	done

analysis: venv
	LD_LIBRARY_PATH="$(LIB_PATH)" "$(VENV_DIR)/bin/python" src/analysis/design.py --config src/analysis/config.yaml --out results/processed/design.csv
	LD_LIBRARY_PATH="$(LIB_PATH)" "$(VENV_DIR)/bin/python" src/analysis/catalog.py
	LD_LIBRARY_PATH="$(LIB_PATH)" "$(VENV_DIR)/bin/python" -m jupyter nbconvert --to notebook --execute --inplace src/analysis/analise.ipynb

slides:
	@if [ ! -d "node_modules" ]; then npm ci --no-audit --no-fund; fi
	npm run pdf
	npm run html

package:
	@python3 -c 'import os, pathlib, tarfile; ex_d={".venv","node_modules",".snakemake","__pycache__",".ipynb_checkpoints","build"}; ex_f={".env","delivery.tgz"}; f=lambda ti: None if (any(p in ex_d for p in pathlib.Path(ti.name).parts) or pathlib.Path(ti.name).parts[-1] in ex_f or pathlib.Path(ti.name).parts[-1].endswith(".pyc") or (len(pathlib.Path(ti.name).parts)>=3 and pathlib.Path(ti.name).parts[0]=="delivery" and pathlib.Path(ti.name).parts[1]=="results" and pathlib.Path(ti.name).parts[-1]!=".gitkeep" and not ti.isdir()) or (len(pathlib.Path(ti.name).parts)==4 and pathlib.Path(ti.name).parts[:3]==("delivery","slides","figures") and pathlib.Path(ti.name).parts[-1].endswith(".png"))) else ti; t=tarfile.open("delivery.tgz","w:gz"); t.add("delivery",arcname="delivery",filter=f); t.close(); print(f"[PACKAGE] delivery.tgz gerado ({os.path.getsize(\"delivery.tgz\")/1048576:.2f} MB)")'

firmware:
	$(MAKE) -C src/firmware/atmega4809 all

experiment: venv
	LD_LIBRARY_PATH="$(LIB_PATH)" "$(VENV_DIR)/bin/python" src/analysis/run_experiment.py \
		--mode bench --port /dev/ttyACM0 \
		--alg all --variants asm ref --opts O3 Os --clocks 20 \
		-n 30 --seed 42 --tag bench_campanha_completa_la_nix
	$(MAKE) analysis slides package

clean:
	@$(MAKE) -C delivery clean
	@rm -rf src/firmware/atmega4809/build
	@rm -rf results/processed/*.csv results/tables/*.tex results/figures/*.png results/figures/*.pdf results/slides/*
	@rm -f slides/figures/*.png delivery.tgz
	@python3 -c 'import json, pathlib; p = pathlib.Path("src/analysis/analise.ipynb"); nb = json.loads(p.read_text(encoding="utf-8")); [c.update({"outputs": [], "execution_count": None}) for c in nb["cells"] if c.get("cell_type") == "code"]; p.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")'
	@echo "[OK] Repositório principal e delivery/ limpos!"

clean-all: clean
	@$(MAKE) -C delivery clean-all
	@rm -rf .venv node_modules
