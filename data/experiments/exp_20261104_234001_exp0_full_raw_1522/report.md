
# Experiment Report: exp_20261104_234001_exp0_full_raw_1522

- **Generated:** 2026-11-04 23:41:33
- **Execution Mode:** `bench`
- **Randomization Seed (Jain Ch. 11.4):** `42`
- **Replications per Cell ($N$):** `5`
- **Total Raw Observations Recorded:** `40`

## 1. Experimental Summary Table

| Algorithm | Variant | Opt | Clock | Operation | N | Mean Lat (ms) | 95% CI (ms) | Median (ms) | IQR (ms) | Mean Energy (uJ) | Stack Peak (B) |
| :--- | :---: | :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| kyber512 | asm | -O3 | 20.0 MHz | decaps | 5 | 316.394 | ±0.110 | 316.363 | 0.116 | 16136.1 | 1019 |
| kyber512 | asm | -O3 | 20.0 MHz | encaps | 5 | 343.178 | ±0.132 | 343.161 | 0.033 | 17502.1 | 1008 |
| kyber512 | asm | -O3 | 20.0 MHz | keygen | 5 | 261.138 | ±0.060 | 261.149 | 0.053 | 13318.1 | 935 |
| kyber512 | asm | -O3 | 20.0 MHz | msgcrypt | 5 | 38.323 | ±0.174 | 38.336 | 0.171 | 1954.5 | 68 |
| kyber512 | ref | -O3 | 20.0 MHz | decaps | 5 | 622.631 | ±6.527 | 620.397 | 0.198 | 31754.2 | 976 |
| kyber512 | ref | -O3 | 20.0 MHz | encaps | 5 | 630.756 | ±6.426 | 628.341 | 0.603 | 32168.6 | 974 |
| kyber512 | ref | -O3 | 20.0 MHz | keygen | 5 | 500.076 | ±6.521 | 497.747 | 0.351 | 25503.9 | 899 |
| kyber512 | ref | -O3 | 20.0 MHz | msgcrypt | 5 | 38.418 | ±0.418 | 38.279 | 0.226 | 1959.3 | 68 |

## 2. Complete Raw Observations Log (All Individual Measurements)

| Run # | Rep | Variant | Operation | Latency (ms) | Total UART (ms) | Cycles (@20MHz) | Stack Peak (B) | SRAM Margin | KEM Valid | Msg Valid | Status |
| :---: | :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 1 | asm | keygen | 261.15 | 331.20 | 5,222,980 | 935 | 84.8% | - | - | OK |
| 2 | 1 | asm | encaps | 343.16 | 413.23 | 6,863,220 | 1008 | 83.6% | - | - | OK |
| 3 | 1 | asm | decaps | 316.34 | 320.02 | 6,326,760 | 1019 | 83.4% | OK | - | OK |
| 4 | 1 | asm | msgcrypt | 38.12 | 41.23 | 762,400 | 68 | 98.9% | - | OK | OK |
| 5 | 2 | asm | keygen | 261.16 | 331.14 | 5,223,260 | 935 | 84.8% | - | - | OK |
| 6 | 2 | asm | encaps | 343.06 | 413.07 | 6,861,160 | 1008 | 83.6% | - | - | OK |
| 7 | 2 | asm | decaps | 316.30 | 319.94 | 6,326,000 | 1019 | 83.4% | OK | - | OK |
| 8 | 2 | asm | msgcrypt | 38.43 | 41.17 | 768,560 | 68 | 98.9% | - | OK | OK |
| 9 | 3 | asm | keygen | 261.20 | 331.21 | 5,223,960 | 935 | 84.8% | - | - | OK |
| 10 | 3 | asm | encaps | 343.35 | 413.22 | 6,866,980 | 1008 | 83.6% | - | - | OK |
| 11 | 3 | asm | decaps | 316.52 | 320.06 | 6,330,320 | 1019 | 83.4% | OK | - | OK |
| 12 | 3 | asm | msgcrypt | 38.26 | 41.19 | 765,140 | 68 | 98.9% | - | OK | OK |
| 13 | 4 | asm | keygen | 261.11 | 331.26 | 5,222,200 | 935 | 84.8% | - | - | OK |
| 14 | 4 | asm | encaps | 343.18 | 413.24 | 6,863,560 | 1008 | 83.6% | - | - | OK |
| 15 | 4 | asm | decaps | 316.45 | 320.03 | 6,329,080 | 1019 | 83.4% | OK | - | OK |
| 16 | 4 | asm | msgcrypt | 38.34 | 41.18 | 766,720 | 68 | 98.9% | - | OK | OK |
| 17 | 5 | asm | keygen | 261.07 | 331.15 | 5,221,440 | 935 | 84.8% | - | - | OK |
| 18 | 5 | asm | encaps | 343.14 | 413.19 | 6,862,900 | 1008 | 83.6% | - | - | OK |
| 19 | 5 | asm | decaps | 316.36 | 319.96 | 6,327,260 | 1019 | 83.4% | OK | - | OK |
| 20 | 5 | asm | msgcrypt | 38.47 | 41.19 | 769,440 | 68 | 98.9% | - | OK | OK |
| 21 | 1 | ref | keygen | 497.61 | 567.63 | 9,952,280 | 899 | 85.4% | - | - | OK |
| 22 | 1 | ref | encaps | 628.34 | 698.32 | 12,566,820 | 974 | 84.2% | - | - | OK |
| 23 | 1 | ref | decaps | 620.40 | 623.70 | 12,407,940 | 976 | 84.1% | OK | - | OK |
| 24 | 1 | ref | msgcrypt | 38.44 | 41.19 | 768,780 | 68 | 98.9% | - | OK | OK |
| 25 | 2 | ref | keygen | 497.75 | 567.68 | 9,954,940 | 899 | 85.4% | - | - | OK |
| 26 | 2 | ref | encaps | 628.91 | 698.28 | 12,578,280 | 974 | 84.2% | - | - | OK |
| 27 | 2 | ref | decaps | 620.48 | 623.73 | 12,409,540 | 976 | 84.1% | OK | - | OK |
| 28 | 2 | ref | msgcrypt | 38.99 | 41.30 | 779,840 | 68 | 98.9% | - | OK | OK |
| 29 | 3 | ref | keygen | 497.96 | 567.65 | 9,959,300 | 899 | 85.4% | - | - | OK |
| 30 | 3 | ref | encaps | 628.31 | 698.29 | 12,566,220 | 974 | 84.2% | - | - | OK |
| 31 | 3 | ref | decaps | 620.28 | 623.74 | 12,405,580 | 976 | 84.1% | OK | - | OK |
| 32 | 3 | ref | msgcrypt | 38.21 | 41.19 | 764,260 | 68 | 98.9% | - | OK | OK |
| 33 | 4 | ref | keygen | 509.47 | 579.56 | 10,189,360 | 899 | 85.4% | - | - | OK |
| 34 | 4 | ref | encaps | 640.00 | 710.12 | 12,800,040 | 974 | 84.2% | - | - | OK |
| 35 | 4 | ref | decaps | 632.03 | 635.57 | 12,640,600 | 976 | 84.1% | OK | - | OK |
| 36 | 4 | ref | msgcrypt | 38.17 | 41.17 | 763,360 | 68 | 98.9% | - | OK | OK |
| 37 | 5 | ref | keygen | 497.58 | 567.57 | 9,951,680 | 899 | 85.4% | - | - | OK |
| 38 | 5 | ref | encaps | 628.21 | 698.18 | 12,564,260 | 974 | 84.2% | - | - | OK |
| 39 | 5 | ref | decaps | 619.97 | 623.52 | 12,399,420 | 976 | 84.1% | OK | - | OK |
| 40 | 5 | ref | msgcrypt | 38.28 | 41.21 | 765,580 | 68 | 98.9% | - | OK | OK |

## 3. Visual Artifacts

- **Unified Real-Scale Latency Histograms (Shared Zero-Baseline 0-700 ms, Real Trial Counts):**
  - `figures/histogram_unified_real_scale.png` (PDF: `figures/histogram_unified_real_scale.pdf`)
  - Primary view: `figures/histogram.png` (Presents both `asm` and `ref` side-by-side on the exact same physical scale)
- **Sequential Observation Timeline (Run-Order Time Series):**
  - `figures/histogram_timeseries.png` (Every single observation plotted across sequence to verify stability)
- **Boxplot with All Individual Observations Overlaid (Strip Scatter):**
  - `figures/histogram_boxplot_points.png` (Boxplot showing full spread & every measured dot)
- **Variant-Specific Detailed Real-Count Histograms:**
  - `figures/histogram_asm.png` (PDF: `figures/histogram_asm.pdf`)
  - `figures/histogram_ref.png` (PDF: `figures/histogram_ref.pdf`)

## 4. Complete Raw Data & Telemetry Files

- `raw/runs.csv`: Full tabular dataset with all observations and parameters.
- `raw/telemetry_*.json`: Full machine telemetry per firmware build.
- `raw/console_*.log`: Verbatim UART execution logs.
- `summary.csv`: Aggregated descriptive statistics.
- `schedule.json`: Randomized trial execution schedule.
