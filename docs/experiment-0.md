# Experiment 0: Baseline Characterization & Reproducibility Protocol

**Author:** CMP223 Research Group  
**Target System Under Test (SUT):** Microchip ATmega4809 (Arduino Nano Every)  
**Algorithm:** Kyber-512 (ML-KEM-512, AVR Assembly Variant, `-O3`)  
**Methodological Framework:** Raj Jain, *The Art of Computer Systems Performance Analysis* (Chapters 2, 10, 11, 13)

---

## 1. System Definition, Goals & Metrics (Jain Ch. 2)

Following Jain's systematic approach (Section 2.2):

### 1.1 Goal of the Study
Establish the baseline empirical performance distribution, variance, measurement repeatability, and hardware ceiling for Post-Quantum Cryptography (ML-KEM-512) executed on an 8-bit constrained microcontroller before exploring the multi-factor parameter space ($2^k$ / full factorial design).

### 1.2 System Under Test (SUT) & Component Under Study (CUS)
- **SUT:** Arduino Nano Every board powered by an 8-bit Microchip ATmega4809 MCU.
  - Flash Memory: 48 KB (executable program storage)
  - SRAM: 6,144 Bytes (data, heap, and call stack)
  - Clock Frequency: $f_{\text{CPU}} = 20.00\text{ MHz}$ (internal calibrated oscillator via `OSCCFG` + `SIGROW` correction)
  - Supply Voltage: $V_{\text{DD}} = 5.0\text{ V}$
- **CUS:** Cryptographic core routines (`KeyGen`, `Encaps`, `Decaps`, and post-KEM message encryption `MsgCrypt`).

### 1.3 Selected Performance Metrics
1. **Execution Latency ($T$, ms):** Pulse width of the dedicated non-intrusive GPIO toggle (`VPORTA.OUT`, pin `PA0`/`D2`) measured via hardware logic analyzer at 100 kHz sampling rate.
2. **Clock Cycles ($C$, cycles):** $C = T \times f_{\text{CPU}}$, capturing exact algorithmic complexity independent of nominal clock dividers.
3. **Peak Stack Consumption ($S_{\text{peak}}$, Bytes):** Assessed via high-watermark painting (`0xAA` fill from `__heap_start` to current `SP`) scanned after execution.
4. **Energy Consumption ($E$, $\mu\text{J}$):** Estimated via $E = \int V_{\text{DD}} \cdot I_{\text{active}}(t)\, dt \approx V_{\text{DD}} \cdot \bar{I}_{\text{active}} \cdot T$.

---

## 2. Experimental Design & Reproducibility Protocol (Jain Ch. 11 & 13)

### 2.1 Sample Size & Statistical Power
- Following Jain Chapter 13.2, each operation is replicated $N = 30$ times ($N \ge 30$ satisfies the Central Limit Theorem while allowing robust Student's $t$ confidence interval estimation).
- Total trials in Experiment 0: $4 \text{ operations} \times 30 \text{ replications} = 120 \text{ trials}$.

### 2.2 Randomization of Execution Order (Jain Ch. 11.4)
To avoid systematic errors, drift due to thermal effects, or memory fragmentation artifacts:
- The 120 trials are pseudo-randomly shuffled using a fixed seed (`seed = 42`).
- The execution schedule maps each trial to a sequential `run_order` ($1 \dots 120$), ensuring independent and identically distributed (i.i.d.) observations.

```
Execution Schedule Generation:
  [keygen x 30, encaps x 30, decaps x 30, msgcrypt x 30] 
     -- (PRNG shuffle with seed=42) --> 
  Trial 1: encaps (rep 1)
  Trial 2: decaps (rep 1)
  Trial 3: keygen (rep 1)
  ...
  Trial 120: msgcrypt (rep 30)
```

### 2.3 Eliminating Measurement Overhead
- Interrupts are disabled (`cli`) during the execution window.
- The measurement window is initiated and terminated with single-cycle bit-manipulation instructions (`cbi`/`sbi` on virtual port `VPORTA.OUT`).
- All logging, verification, and telemetry transfers occur strictly outside the measurement window over UART at 115,200 bps.

---

## 3. Empirical Results & Statistical Summary (Jain Ch. 10 & 12)

Table 1 compiles the statistical metrics across $N = 30$ trials per operation ($f_{\text{CPU}} = 20\text{ MHz}$, $V_{\text{DD}} = 5.0\text{ V}$, `seed = 42`).

### Table 1: Experiment 0 Summary Statistics ($N = 30$, 95% Confidence Intervals)

| Cryptographic Operation | Sample Size ($N$) | Mean Latency (ms) | 95% CI (ms) | Std Dev ($s$, ms) | Median Latency (ms) | IQR (ms) | Mean Energy ($\mu\text{J}$) | Peak Stack (Bytes) | SRAM Margin (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **KeyGen (K)** | 30 | 239.312 | $\pm$ 0.195 | 0.521 | 239.323 | 0.697 | 12,216.1 | 676 B | 89.0% |
| **Encaps (E)** | 30 | 314.622 | $\pm$ 0.213 | 0.569 | 314.579 | 0.771 | 16,077.8 | 808 B | 86.8% |
| **Decaps (D)** | 30 | 287.193 | $\pm$ 0.216 | 0.578 | 287.230 | 0.793 | 14,644.7 | 809 B | 86.8% |
| **MsgCrypt (M)**| 30 | 38.470 | $\pm$ 0.040 | 0.108 | 38.465 | 0.147 | 1,962.7 | 68 B | 98.9% |

*Note:* $95\%\text{ CI} = \bar{x} \pm t_{0.975, 29} \cdot \frac{s}{\sqrt{N}}$, where $t_{0.975, 29} = 2.045$. SRAM Margin calculated relative to the total 6,144-byte physical SRAM boundary.

---

## 4. Empirical Distribution Analysis (Histogram)

The latency distribution across all 120 trials was analyzed according to Jain Chapter 10.3:
- **Binning Rule:** Bin widths are chosen using the **Freedman-Diaconis rule** ($h = 2 \cdot \text{IQR} \cdot N^{-1/3}$) to minimize mean integrated squared error without subjective bin count bias.
- **Aesthetics & Palette:** Rendered adhering to Tidyverse `ggplot2::theme_bw()` principles with Okabe-Ito colorblind-safe palettes (Blue, Vermilion, Bluish Green, Reddish Purple).
- **Artifacts:**
  - High-resolution Vector Graphics: `data/processed/figures/exp0_histogram.pdf`
  - High-DPI Bitmap: `data/processed/figures/exp0_histogram.png`

### Visual Insights
1. **Tight Gaussian Dispersion:** The empirical distributions for all four cryptographic operations exhibit near-normal behavior with very narrow dispersion ($\text{CV} = s / \bar{x} < 0.3\%$). This validates that deterministic instruction execution on the AVRxt architecture has near-zero OS jitter.
2. **Mean vs. Median Coincidence:** The mean and median values match within $< 0.02\%$, confirming the absence of severe outliers or asymmetric tail skewness.
3. **Separation of Operational Workloads:** The four latency clusters are distinctly isolated:
   $$\text{MsgCrypt (38.5 ms)} \ll \text{KeyGen (239.3 ms)} < \text{Decaps (287.2 ms)} < \text{Encaps (314.6 ms)}$$

---

## 5. Artifact Lineage & Reproducibility Guide

All steps are 100% reproducible through the automated scripts:

```bash
# 1. Generate Experiment 0 randomized design and run simulation / bench collection
python3 src/analysis/experiment_zero.py --config src/analysis/config.yaml --iterations 30 --seed 42

# 2. Generate publication-quality Freedman-Diaconis histograms with 95% CI and KDE
python3 src/analysis/plot_histogram.py --in data/raw/exp0_raw_runs.csv --out data/processed/figures/exp0_histogram

# 3. Inspect raw trial data and aggregated summary
cat data/processed/exp0_summary.csv
```

