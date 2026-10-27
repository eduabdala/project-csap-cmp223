# analysis — Pipeline reprodutível (Snakemake)

Automação da coleta e análise, conforme o flowchart de metodologia
(`.kiro/specs/cmp223/draft.md`). Transforma a matriz de fatores em dados
tratados com estatística.

## Fluxo

```
config.yaml  →  build (avr-gcc)  →  flash (avrdude/UPDI)  →  collect (osc + LA)
             →  parse (E=∫V·i dt) →  aggregate (média, IC 95%) →  figures
```

Fatores: **algoritmo × variante × clock × otimização × operação**. São 6
binários (3 algoritmos × {ref, asm}); cada um é buildado, gravado e medido
separadamente, para todas as combinações de clock e otimização.

## Arquivos

| Arquivo | Papel | Estado |
|---------|-------|--------|
| `config.yaml`  | Matriz de fatores e parâmetros do DoE | pronto |
| `Snakefile`    | Orquestração das regras | esqueleto (regras de bancada = TODO) |
| `parse.py`     | Integração numérica da energia por iteração | **funcional / testado** |
| `aggregate.py` | Média + IC 95% por combinação de fatores | **funcional / testado** |
| `collect.py`   | Disparo serial + captura de forma de onda | stub (depende da bancada) |
| `figures.py`   | Gráfico de trade-off com barras de erro | funcional (precisa de dados) |

## Uso

```bash
nix develop                 # traz snakemake + python científico
cd src/analysis
snakemake -n -j1            # dry-run: inspeciona o DAG
snakemake -j1 all           # pipeline completo (requer bancada p/ flash/collect)
```

## O que ainda falta (bancada)

- `collect.py`: integrar o driver do osciloscópio (pyvisa/vxi11) e o
  `sigrok-cli` para o analisador lógico. Hoje grava um CSV vazio (placeholder).
- Calibração: criar `calib.yaml` com o valor **real** do shunt (medido), em vez
  do nominal de 1 Ω em `config.yaml`.
- Leitura da telemetria serial (stack peak) e injeção em `parse.py` via
  `--stack-peak`.

As etapas puras (`parse`, `aggregate`, `figures`) já funcionam offline — dá para
validar a estatística com CSVs sintéticos antes de ter o hardware.
