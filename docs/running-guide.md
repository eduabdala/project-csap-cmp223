---
created: 2026-10-27
status: how-to / running guide
---

# Running Guide — CMP223

End-to-end guide to run the experiment: environment setup, vendoring, build,
bench, collection and analysis. Marks clearly **what already works**, **what
still needs implementing**, and **what depends on you** (hardware / manual input).

Related docs:
- `docs/roadmap.md` — what to do and in what order (task breakdown).
- `docs/references.md` — external sources.
- `docs/decision-tooling.md` — why Snakemake + pyDOE3, not Omnibenchmark.
- `src/README.md`, `src/analysis/README.md` — per-directory details.

Legend: ✅ works now · 🟡 works but needs the bench/input · 🔧 not implemented yet

---

## 0. Prerequisites

- **Nix** with flakes enabled. Everything (AVR toolchain, programmer, analysis
  stack) comes from `flake.nix` — no manual `apt install`.
  - Enable flakes once:
    ```bash
    mkdir -p ~/.config/nix
    echo 'experimental-features = nix-command flakes' >> ~/.config/nix/nix.conf
    ```
- **Git** (for vendoring the algorithm sources).
- **Hardware** (only for the physical stages): Arduino Nano Every (ATmega4809),
  oscilloscope, logic analyzer, 1 ohm 1% shunt, bench power/battery.

---

## 1. One-time setup ✅ / 🔧

### 1.1 Fill in the pyDOE3 hash in `flake.nix` 🔧 (needs you, once)

pyDOE3 is not in nixpkgs, so the flake builds it from PyPI and needs the source
hash. It currently has a placeholder.

```bash
# Get the real hash for the pinned version (1.0.3):
nix-prefetch-url --unpack https://files.pythonhosted.org/packages/source/p/pyDOE3/pyDOE3-1.0.3.tar.gz
```

Copy the printed hash into `flake.nix` (the `hash = "sha256-...";` line under
`pyDOE3`). Alternatively, run `nix develop` once, let it fail, and paste the
`got: sha256-...` value it reports.

### 1.2 Enter the dev shell ✅

```bash
nix develop
```

You should see the banner and `avr-gcc --version`. This shell has: `avr-gcc`,
`avr-size`, `avr-objcopy`, `avrdude`, `sigrok-cli`, `picocom`, `snakemake`, and
Python with numpy/pandas/scipy/matplotlib/pyserial/pyDOE3.

### 1.3 Buy / calibrate the shunt 🔧 (needs you)

- Precision resistor **1 ohm 1%** in series with the MCU supply.
- Measure its real value with a 4.5-digit multimeter and put it in
  `src/analysis/config.yaml` under `shunt_ohms` (replace the nominal 1.0).

---

## 2. Vendor the algorithm sources 🟡 (needs network + path confirmation)

Downloads the reference + AVR-assembly implementations into `src/firmware/pqc/`.

```bash
cd src
scripts/vendor-pqc.sh all        # or: kyber512 | ctru-light | ecdh
```

This clones the CHES 2026 artifact (Kyber + CTRU-Light) and micro-ecc (ECDH),
and writes a `VENDOR.txt` (pinned commit) in each `pqc/<alg>/<variant>/`.

> **Needs you:** the exact `ref`/`asm` subfolder names inside the CHES artifact
> must be confirmed on the first clone — the script prints a `!! adjust ... path`
> warning if a path is wrong. Open the cloned tree, find the real folders (e.g.
> `crypto_kem/kyber/C-ref` vs `.../Montgomery`) and fix the `cp` paths in
> `scripts/vendor-pqc.sh`. Also check the symbol prefix in each vendored `api.h`
> and adjust the `kem_*.c` macros if it differs from `crypto_kem_*`.

---

## 3. Build the firmware ✅ (once vendored)

One binary per `ALG x VARIANT`, with clock and optimization as extra factors.

```bash
cd src/firmware

# single build:
make ALG=kyber512 VARIANT=asm OPT=-O3 F_CPU=20000000UL

# memory report (THE moment of truth for the 6 KB SRAM / 48 KB Flash):
make ALG=kyber512 VARIANT=asm size

make clean
```

Valid values: `ALG in {kyber512, ctru-light, ecdh}`, `VARIANT in {ref, asm}`,
`OPT in {-Os, -O3}`, `F_CPU in {20000000UL, 10000000UL, 5000000UL}`.

> **Expected finding:** Kyber-512 `ref` likely does NOT fit in Flash (~79 KB vs
> 48 KB). That is a valid result (applicability limit) — record it. The `asm`
> variant (~22 KB) should fit.

---

## 4. Flash and bench 🟡 / 🔧 (needs hardware)

### 4.1 Program the board 🟡

```bash
cd src/firmware
make ALG=kyber512 VARIANT=asm flash PORT=/dev/ttyACM0   # adjust PORT
```

### 4.2 Wire the bench 🔧 (needs you)

- Shunt (1 ohm) in series with the MCU supply; oscilloscope probes across it.
- Measurement-window GPIO (PA0) to the logic analyzer and the scope trigger.
- Serial (USB) to the host for the trigger protocol.

The firmware state machine is already implemented (`src/firmware/main.c`):
serial commands `K`/`E`/`D`, 1-cycle GPIO window, interrupts off during the
window, 0xAA stack watermarking, identifier pulses, UART telemetry.

---

## 5. Analysis pipeline

### 5.1 Experiment design (pyDOE3) ✅

```bash
cd src/analysis
python design.py --config config.yaml --print            # preview 36 combos
python design.py --config config.yaml --out data/processed/design.csv
```

Switch `design: full` -> `design: fracfact` (+ `fraction_generator`) in
`config.yaml` only if the full matrix is too long for the bench.

### 5.2 Full pipeline (Snakemake) 🟡

```bash
cd src/analysis
snakemake -n -j1                 # dry-run: inspect the DAG (no hardware needed)
snakemake -j1 all                # full run (needs the bench for flash/collect)
```

Pipeline stages and status:

| Stage | Rule | Status |
|-------|------|--------|
| Design matrix | `design`    | ✅ works offline |
| Build         | `build`     | ✅ needs vendored sources |
| Flash         | `flash`     | 🟡 needs the board |
| Collect       | `collect`   | 🔧 **stub** — needs scope/LA driver |
| Parse (energy)| `parse`     | ✅ works offline |
| Aggregate     | `aggregate` | ✅ works offline |
| Figures       | `figures`   | ✅ works (needs data) |

### 5.3 Validate the offline stages now ✅ (no hardware)

You can exercise parse + aggregate with synthetic data today:

```bash
cd src/analysis
mkdir -p /tmp/t
printf 't_s,v_shunt_v\n0.0,0.0\n0.001,0.1\n0.002,0.0\n' > /tmp/t/run.csv
python parse.py --in /tmp/t/run.csv --shunt 1.0 --stack-peak 2351 \
    --out /tmp/t/kyber512-asm-20MHz-O3-keygen-0.json
python aggregate.py --in /tmp/t/*.json --out /tmp/t/summary.csv
cat /tmp/t/summary.csv
```

---

## 6. What still needs implementing (🔧 summary)

1. **`collect.py`** — the only real code gap. Integrate the oscilloscope driver
   (pyvisa/vxi11) and `sigrok-cli` to capture `v_shunt(t)` and the GPIO pulse
   width, and read the stack-peak telemetry back over serial. Today it writes an
   empty CSV placeholder.
   - Shortcut: the open-source Stuttgart power-measurement platform
     (`docs/references.md`) is a ready blueprint for this.
2. **Vendor paths** — confirm the CHES artifact subfolders (section 2).
3. **pyDOE3 hash** — fill it in `flake.nix` (section 1.1).
4. **Shunt calibration** — real value into `config.yaml` (section 1.3).
5. **Thermal cool-down** — add an inter-run delay in the `collect` rule for
   isolation (roadmap 2.1).

Everything else — firmware harness, build matrix, DoE, energy integration,
statistics, plotting — is implemented and verified offline.

---

## 7. Deliverables (slides and paper)

Independent of the experiment; run from the repo root (needs Node + LaTeX):

```bash
npm ci
npm run pdf                      # slides -> dist/slides/*.pdf
cd artigo && latexmk -pdf main.tex
```

---

## Quick reference

```bash
nix develop                                   # enter the environment
src/scripts/vendor-pqc.sh all                 # get the algorithm sources
make -C src/firmware ALG=kyber512 VARIANT=asm OPT=-O3 size   # build + size
cd src/analysis && snakemake -n -j1           # inspect the pipeline DAG
```
