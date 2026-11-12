# =============================================================================
# Makefile — Pacote de Entrega Etapa 2 (CMP223)
# =============================================================================
SHELL := /bin/bash
VENV_DIR := .venv
LIB_PATH := $(VENV_DIR)/lib:$(LD_LIBRARY_PATH)

.PHONY: all venv analysis slides firmware experiment clean clean-all

# Reproduz toda a análise, tabelas, figuras e slides do zero (sem precisar do hardware)
all: venv analysis slides
	@echo "=================================================================="
	@echo "[OK] Pipeline completo concluído!"
	@echo "  - Catálogo:       data/experiments/catalog.csv"
	@echo "  - Dados/Tabelas:  results/processed/ e results/tables/"
	@echo "  - Gráficos:       results/figures/ e slides/figures/"
	@echo "  - Notebook:       src/analysis/analise.ipynb (com outputs)"
	@echo "  - Slides:         results/slides/01-proposta.pdf e 02-parcial.pdf"
	@echo "=================================================================="

# Garante o ambiente virtual Python (.venv) e bibliotecas C++ no NixOS/Nix
venv:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		python3 -m venv "$(VENV_DIR)"; \
		"$(VENV_DIR)/bin/python" -m pip install -q --upgrade pip; \
		"$(VENV_DIR)/bin/python" -m pip install -q -r src/analysis/requirements-notebook.txt; \
	fi
	@mkdir -p "$(VENV_DIR)/lib"
	@for lib in libstdc++.so.6 libgcc_s.so.1 libz.so.1; do \
		if [ ! -e "$(VENV_DIR)/lib/$$lib" ]; then \
			p=$$(find /nix/store -maxdepth 3 -name "$$lib" 2>/dev/null | head -n 1); \
			[ -n "$$p" ] && cp -L "$$p" "$(VENV_DIR)/lib/$$lib" || true; \
		fi; \
	done

# Atualiza o planejamento fatorial, o catálogo e executa o notebook analise.ipynb
analysis: venv
	LD_LIBRARY_PATH="$(LIB_PATH)" "$(VENV_DIR)/bin/python" src/analysis/design.py --config src/analysis/config.yaml --out results/processed/design.csv
	LD_LIBRARY_PATH="$(LIB_PATH)" "$(VENV_DIR)/bin/python" src/analysis/catalog.py
	LD_LIBRARY_PATH="$(LIB_PATH)" "$(VENV_DIR)/bin/python" -m jupyter nbconvert --to notebook --execute --inplace src/analysis/analise.ipynb

# Compila os slides Marp em PDF e HTML em results/slides/
slides:
	@if [ ! -d "node_modules" ]; then npm ci --no-audit --no-fund; fi
	npm run pdf
	npm run html

# Compila os firmwares bare-metal (.elf e .hex) do ATmega4809
firmware:
	$(MAKE) -C src/firmware/atmega4809 all

# Roda o experimento completo na bancada física + atualiza catálogo, notebook e slides
experiment: venv
	LD_LIBRARY_PATH="$(LIB_PATH)" "$(VENV_DIR)/bin/python" src/analysis/run_experiment.py \
		--mode bench --port /dev/ttyACM0 \
		--alg all --variants asm ref --opts O3 Os --clocks 20 \
		-n 30 --seed 42 --tag bench_campanha_completa_la_nix
	$(MAKE) analysis slides

# Limpa todos os artefatos gerados (mantém apenas dados brutos, código-fonte e bancada.jpg)
clean:
	@echo "[CLEAN] Removendo builds de firmware..."
	@rm -rf src/firmware/atmega4809/build
	@echo "[CLEAN] Removendo CSVs processados, tabelas LaTeX, figuras e slides compilados..."
	@rm -rf results/processed/*.csv results/tables/*.tex results/figures/*.png results/figures/*.pdf results/slides/*
	@rm -f slides/figures/*.png
	@echo "[CLEAN] Limpando saídas (outputs) do notebook src/analysis/analise.ipynb..."
	@python3 -c 'import json, pathlib; p = pathlib.Path("src/analysis/analise.ipynb"); nb = json.loads(p.read_text(encoding="utf-8")); [c.update({"outputs": [], "execution_count": None}) for c in nb["cells"] if c.get("cell_type") == "code"]; p.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")'
	@echo "[OK] Tudo limpo! Restaram apenas os dados brutos e o código-fonte."

# Limpeza profunda: remove também .venv e node_modules para testar instalação do zero
clean-all: clean
	@echo "[CLEAN-ALL] Removendo .venv e node_modules..."
	@rm -rf .venv node_modules
	@echo "[OK] Limpeza completa concluída."
