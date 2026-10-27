# analysis — Reproducible pipeline (Snakemake)

Automates collection and analysis, following the methodology flowchart
(`.kiro/specs/cmp223/draft.md`). Turns the factor matrix into statistically
processed data.

## Flow

```
config.yaml  ->  build (avr-gcc)  ->  flash (avrdude/UPDI)  ->  collect (scope + LA)
             ->  parse (E=INT V*i dt) ->  aggregate (mean, 95% CI) ->  figures
```

Factors: **algorithm x variant x clock x optimization x operation**. There are
6 binaries (3 algorithms x {ref, asm}); each is built, flashed and measured
separately, for every clock and optimization combination.

## Files

| File | Role | Status |
|------|------|--------|
| `config.yaml`  | Factor matrix and DoE parameters | ready |
| `Snakefile`    | Rule orchestration | skeleton (bench rules = TODO) |
| `parse.py`     | Per-iteration energy integration | **working / tested** |
| `aggregate.py` | Mean + 95% CI per factor combination | **working / tested** |
| `collect.py`   | Serial trigger + waveform capture | stub (depends on the bench) |
| `figures.py`   | Trade-off plot with error bars | working (needs data) |

## Usage

```bash
nix develop                 # brings snakemake + scientific python
cd src/analysis
snakemake -n -j1            # dry-run: inspect the DAG
snakemake -j1 all           # full pipeline (needs the bench for flash/collect)
```

## What's still missing (bench)

- `collect.py`: integrate the oscilloscope driver (pyvisa/vxi11) and
  `sigrok-cli` for the logic analyzer. It currently writes an empty CSV
  (placeholder).
- Calibration: create `calib.yaml` with the **measured** shunt value, instead
  of the nominal 1 ohm in `config.yaml`.
- Serial telemetry read (stack peak) and injection into `parse.py` via
  `--stack-peak`.

The pure stages (`parse`, `aggregate`, `figures`) already work offline — you
can validate the statistics with synthetic CSVs before having the hardware.
