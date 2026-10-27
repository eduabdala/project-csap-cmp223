---
created: 2026-10-27
status: execution roadmap
---

# Execution Roadmap — CMP223

Actionable document of what still needs to be done and **how to do it**. Derived
from `docs/plan.md` (schedule and SUT) and `.kiro/specs/cmp223/draft.md`
(architecture, firmware and methodology diagrams).

Milestones: **Interim 2026-11-09** · **Final + Paper 2026-12-14**.

Status legend: ⬜ pending · 🟨 in progress · ✅ done

---

## Experiment overview

| Dimension | Definition |
|-----------|------------|
| SUT | Arduino Nano Every — ATmega4809 (8-bit AVRxt, 48 KB Flash / 6 KB SRAM / 256 B EEPROM) |
| Factors (independent) | Algorithm {ECDH, CTRU-Light, Kyber-512} · Variant {ref (C), asm (AVR)} · Clock {20, 10, 5 MHz} · Optimization {-Os, -O3} |
| Metrics (dependent) | Energy per operation `E_op = INT V*i dt` (uJ) · Latency/cycles · Peak stack (bytes) · CPU/SRAM headroom (%) |
| Measured operations | KeyGen · Encaps · Decaps (+ optional AES-CTR on the payload) |
| Instrumentation | Oscilloscope (1 ohm shunt) · Logic analyzer (GPIO window) · Stack watermarking (0xAA) |
| DoE | N = 30 iterations per combination · randomized order · 95% CI |
| Automation | Snakemake (build -> flash -> collect -> parse -> statistics) |

---

## Phase 0 — Preparation and setup (target: ~2026-10-22)

### 0.1 Repository organization ✅
Done: `docs/`, `artigo/`, `src/`, `slides/` and README created.

### 0.2 Purchases and bench ⬜
- [ ] Precision resistor **1 ohm 1%** (shunt) — *purchase item pending in the draft*.
- [ ] Confirm availability: oscilloscope, logic analyzer, Li-Ion 18650 battery.
- **How:** the shunt goes in series with the MCU supply; the voltage drop
  `v_shunt` gives the current (`i = v_shunt / 1 ohm`). Calibrate the resistor's
  real value with a 4.5-digit multimeter before using it as a constant in the parser.

### 0.3 AVR toolchain 🟨
Nix environment created (`flake.nix`): `nix develop` provides avr-gcc, binutils,
avrdude, sigrok-cli, picocom and the Python stack (snakemake + numpy/pandas/
scipy/matplotlib/pyserial). Still needs validation on the real machine (UPDI
programming + bench).

---

## Phase 1 — Port and base firmware (target: interim 2026-11-09)

> **Progress (scaffold created):** the base firmware, the ECDH baseline, the
> AVR cross build and the pipeline skeleton already exist under `src/`:
> - `src/firmware/` — measurement harness (`main.c`), `kem.h` interface,
>   adapters `kem_kyber512.c`, `kem_ctru.c` and `kem_ecdh.c`, a `Makefile`
>   parameterized by **ALG x VARIANT** (6 binaries: 3 algorithms x {ref, asm}).
> - `src/scripts/vendor-pqc.sh` — vendors CTRU-Light and Kyber (ref + AVR asm)
>   from the CHES 2026 artifact `whYBeKim/CTRU-Light-and-PQC-on-AVR` (MIT) and
>   micro-ecc (ECDH).
> - `src/analysis/` — `Snakefile`, `config.yaml` (variant as a factor) and the
>   pure stages (`parse.py`, `aggregate.py`), already tested offline.
>
> **Experimental protocol:** each combination is built, flashed to the board and
> measured **separately** — 6 binaries x clock x optimization x operation.
>
> **Still missing:** run `vendor-pqc.sh` (needs network), confirm the real
> ref/asm subfolder paths in the artifact, build with `avr-gcc` (`make size` =
> the SRAM/Flash moment of truth) and connect the bench.
>
> **Relevant finding (from the CHES artifact):** Kyber-512 in reference C takes
> ~79 KB of code — it **does not fit in the ATmega4809's 48 KB of Flash**. The
> asm variant (Montgomery) drops to ~22 KB. So for Kyber the asm variant may be
> **required to fit**, not just faster. This reinforces treating ref/asm as a
> first-class factor.

### 1.1 Define the base algorithm and baseline ⬜
- [ ] Pick the first algorithm to port (suggestion: **Kyber-512**, as the NIST
  ML-KEM standard with portable C references).
- [ ] Define the **classical baseline**: ECDH (same-purpose comparison — KEM/key
  exchange) and, optionally, AES-128 as a symmetric cost reference.
- **Open decision (from the draft):** comparing PQC vs. classical crypto adds
  value, but be careful not to compare algorithms of different purposes. Keep
  ECDH as the direct counterpart to the PQC KEM.

### 1.2 Port the crypto routine to the ATmega4809 ⬜
- [ ] Bring in the C reference implementation (e.g. PQClean / adapted pqm4).
- [ ] Adjust to AVR constraints: no FPU, no HW division, 6 KB SRAM. Prefer
  integer arithmetic, avoid `malloc`, control stack usage.
- [ ] Compile with `avr-gcc` and inspect size with `avr-size`
  (Flash/`.text` + `.data`, SRAM `.data` + `.bss`).
- **Critical risk:** 6 KB of SRAM is the biggest limiter. If the algorithm does
  not fit, record that as a result (one of the goals is precisely to find the
  applicability limit).
- **Suggested `src/` layout:**
  ```
  src/firmware/    # measurement harness + PQC port
  src/baseline/    # ECDH / AES-128
  src/measure/     # oscilloscope / logic-analyzer capture
  src/analysis/    # parser + statistics (Snakemake rules + Python)
  ```

### 1.3 Firmware measurement harness ⬜
Implement the state machine from the draft (see `stateDiagram-v2` diagrams):
- [ ] Serial trigger protocol: `CMD_KEYGEN`, `CMD_ENCAPS`, `CMD_DECAPS`
  (and `CMD_START_DOWNLINK` / `CMD_START_UPLINK` for the full flow).
- [ ] Measurement window with a **1-cycle** GPIO via `VPORTx.OUT` (HIGH before
  the operation, LOW after). No serial I/O inside the window.
- [ ] Disable interrupts (`cli()`) during the window for deterministic measurement.
- [ ] **Stack watermarking:** fill the free SRAM with `0xAA` before the operation;
  then scan to find the lowest touched address -> `Stack Peak = RAMEND - min_addr`.
- [ ] Identifier pulses (1/2/3 pulses) before the window so the parser knows
  which operation is being measured.
- [ ] Report over UART, **outside the window**: Stack Peak + artifacts (pk/ct).

### 1.4 Acquisition bench ⬜
- [ ] Oscilloscope: trigger on the GPIO rising edge; sample `v_shunt(t)`.
- [ ] Logic analyzer (`sigrok-cli`): measure the GPIO pulse width -> latency.
- [ ] Convert latency into cycles: `K_cycles = T_exec * F_clock`.
- [ ] Set an oscilloscope sampling rate suitable for the shortest operation.

### 1.5 Preliminary collection + interim slides ⬜
- [ ] Run a reduced collection (trends, not exhaustive) of KeyGen/Encaps/Decaps.
- [ ] Preliminary plots and bottleneck survey.
- [ ] Update `slides/02-parcial.md` with initial results and rehearse.

---

## Phase 2 — Final run and paper (target: 2026-12-14)

### 2.1 Automation with Snakemake ⬜
Reproducible pipeline (see the "Automation & Factorial Execution" flowchart in
the draft):
- [ ] `config.yaml` with the **factor matrix** (algorithm x variant x clock x optimization).
- [ ] **Parameterized build** rule (`avr-gcc` with per-combination flags + `avr-size` dump).
- [ ] **Automatic flash** rule (`avrdude` via UPDI).
- [ ] **Collection** rule (triggers the run, captures oscilloscope + LA + stack dump).
- [ ] **DoE:** 30 iterations per combination, **randomized order**, with a
  cool-down interval between runs (thermal isolation).
- [ ] Store raw data with **git hash + metadata** (traceability/reproducibility).

### 2.2 Post-processing and statistics ⬜
- [ ] Parser for the oscilloscope and logic-analyzer CSVs.
- [ ] **Numerical integration:** `E_op = INT V*i dt` (trapezoidal rule over `v_shunt`).
- [ ] Compute latency, cycles and peak stack.
- [ ] **Headroom:** `SRAM_free% = (6144 - Stack Peak)/6144`; `Flash_free% = (49152 - .text)/49152`.
- [ ] Statistics: mean, 95% CI, outlier detection and auditing.
- [ ] Outputs: `summary_table.csv` + plots with error bars (vector PDF).

### 2.3 LaTeX paper ⬜
- [ ] Fill in `artigo/main.tex` (skeleton already created): Introduction,
  Background, Methodology, Results, Conclusion.
- [ ] Reference the diagrams from `diagrams/out/` (see `diagrams/README.md`).
- [ ] **Organize references** (pending item in the draft) — create
  `artigo/referencias.bib` and enable `\bibliography` in `main.tex`.
- [ ] Review and finalize the text.

### 2.4 Final slides ⬜
- [ ] Update `slides/03-final.md` with consolidated results; rehearse.

---

## Cross-cutting items / open decisions

Extracted from the open questions in `plan.md` that still need answers:

- [ ] **Configurable variables** — confirm the final set: compiler optimization,
  ciphertext data size, amount of received/decrypted data.
- [ ] **Workloads** — define explicitly (the draft left it open: "The workloads
  will be: ?").
- [ ] **Reproducibility** — ensure that Snakemake + git hash + `config.yaml`
  allow full re-execution by third parties. Document the step-by-step in the README.
- [ ] **Per-algorithm metrics table** — build the final comparison table
  (energy, cycles, stack, headroom per algorithm x factor).

---

## Critical path (suggested order of attack)

1. **Toolchain + bench validated** (0.3) — nothing proceeds without this.
2. **Base algorithm fits in SRAM** (1.2) — biggest technical risk.
3. **Reliable measurement harness** (1.3/1.4) — defines the quality of all data.
4. **Snakemake automation** (2.1) — turns manual measurement into reproducible collection.
5. **Statistics + paper** (2.2/2.3) — depends on clean data.

The real bottleneck is the **6 KB SRAM**. Validate early whether Kyber-512 fits;
if it doesn't, that is a publishable result (applicability limit) and should
redirect the choice of algorithms.
