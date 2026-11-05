# Experiment Report: exp_20261104_224531_test_raw_4783

- **Generated:** 2026-11-04 22:45:36
- **Execution Mode:** `sim`
- **Randomization Seed (Jain Ch. 11.4):** `42`
- **Replications per Cell ($N$):** `5`
- **Total Raw Observations Recorded:** `40`

## 1. Experimental Summary Table

| Algorithm | Variant | Opt | Clock | Operation | N | Mean Lat (ms) | 95% CI (ms) | Median (ms) | IQR (ms) | Mean Energy (uJ) | Stack Peak (B) |
| :--- | :---: | :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| kyber512 | asm | -O3 | 20.0 MHz | decaps | 5 | 286.481 | ±0.374 | 286.373 | 0.176 | 14689.9 | 809 |
| kyber512 | asm | -O3 | 20.0 MHz | encaps | 5 | 314.001 | ±0.695 | 313.722 | 0.313 | 16194.5 | 808 |
| kyber512 | asm | -O3 | 20.0 MHz | keygen | 5 | 239.177 | ±0.739 | 239.045 | 0.443 | 12173.2 | 676 |
| kyber512 | asm | -O3 | 20.0 MHz | msgcrypt | 5 | 38.518 | ±0.094 | 38.538 | 0.109 | 1954.7 | 68 |
| kyber512 | ref | -O3 | 20.0 MHz | decaps | 5 | 703.935 | ±1.892 | 703.077 | 0.994 | 36097.0 | 1092 |
| kyber512 | ref | -O3 | 20.0 MHz | encaps | 5 | 770.123 | ±1.025 | 770.529 | 1.385 | 39746.3 | 1090 |
| kyber512 | ref | -O3 | 20.0 MHz | keygen | 5 | 585.499 | ±2.517 | 585.992 | 2.076 | 29809.1 | 912 |
| kyber512 | ref | -O3 | 20.0 MHz | msgcrypt | 5 | 94.012 | ±0.249 | 94.086 | 0.338 | 4772.3 | 91 |

## 2. Complete Raw Observations Log (All Individual Measurements)

| Run # | Rep | Variant | Operation | Latency (ms) | Total UART (ms) | Cycles (@20MHz) | Stack Peak (B) | SRAM Margin | KEM Valid | Msg Valid | Status |
| :---: | :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 5 | asm | encaps | 313.72 | 383.17 | 6,274,439 | 808 | 86.8% | - | - | OK |
| 2 | 4 | asm | keygen | 238.89 | 308.33 | 4,777,819 | 676 | 89.0% | - | - | OK |
| 3 | 1 | asm | decaps | 286.50 | 290.50 | 5,729,958 | 809 | 86.8% | OK | - | OK |
| 4 | 2 | ref | msgcrypt | 94.22 | 98.22 | 1,884,377 | 91 | 98.5% | - | OK | OK |
| 5 | 1 | ref | encaps | 769.06 | 838.50 | 15,381,131 | 1090 | 82.3% | - | - | OK |
| 6 | 5 | ref | keygen | 586.40 | 655.85 | 11,728,006 | 912 | 85.2% | - | - | OK |
| 7 | 1 | ref | decaps | 703.08 | 707.08 | 14,061,533 | 1092 | 82.2% | OK | - | OK |
| 8 | 2 | asm | decaps | 286.22 | 290.22 | 5,724,484 | 809 | 86.8% | OK | - | OK |
| 9 | 5 | asm | keygen | 240.10 | 309.55 | 4,802,035 | 676 | 89.0% | - | - | OK |
| 10 | 3 | ref | decaps | 704.02 | 708.02 | 14,080,401 | 1092 | 82.2% | OK | - | OK |
| 11 | 2 | ref | keygen | 582.75 | 652.19 | 11,654,911 | 912 | 85.2% | - | - | OK |
| 12 | 4 | ref | encaps | 770.80 | 840.25 | 15,416,080 | 1090 | 82.3% | - | - | OK |
| 13 | 4 | ref | keygen | 584.32 | 653.77 | 11,686,489 | 912 | 85.2% | - | - | OK |
| 14 | 4 | asm | msgcrypt | 38.41 | 42.41 | 768,261 | 68 | 98.9% | - | OK | OK |
| 15 | 3 | asm | decaps | 286.32 | 290.32 | 5,726,430 | 809 | 86.8% | OK | - | OK |
| 16 | 5 | ref | decaps | 703.00 | 707.00 | 14,059,974 | 1092 | 82.2% | OK | - | OK |
| 17 | 1 | ref | msgcrypt | 94.09 | 98.09 | 1,881,719 | 91 | 98.5% | - | OK | OK |
| 18 | 2 | ref | encaps | 769.42 | 838.86 | 15,388,380 | 1090 | 82.3% | - | - | OK |
| 19 | 4 | asm | decaps | 286.37 | 290.37 | 5,727,462 | 809 | 86.8% | OK | - | OK |
| 20 | 3 | ref | keygen | 588.03 | 657.48 | 11,760,660 | 912 | 85.2% | - | - | OK |
| 21 | 1 | ref | keygen | 585.99 | 655.44 | 11,719,838 | 912 | 85.2% | - | - | OK |
| 22 | 2 | ref | decaps | 706.55 | 710.55 | 14,131,042 | 1092 | 82.2% | OK | - | OK |
| 23 | 3 | ref | msgcrypt | 93.82 | 97.82 | 1,876,397 | 91 | 98.5% | - | OK | OK |
| 24 | 5 | ref | encaps | 770.53 | 839.97 | 15,410,572 | 1090 | 82.3% | - | - | OK |
| 25 | 5 | asm | msgcrypt | 38.54 | 42.54 | 770,753 | 68 | 98.9% | - | OK | OK |
| 26 | 2 | asm | msgcrypt | 38.47 | 42.47 | 769,357 | 68 | 98.9% | - | OK | OK |
| 27 | 5 | ref | msgcrypt | 94.16 | 98.16 | 1,883,158 | 91 | 98.5% | - | OK | OK |
| 28 | 4 | ref | decaps | 703.03 | 707.03 | 14,060,530 | 1092 | 82.2% | OK | - | OK |
| 29 | 3 | asm | keygen | 238.51 | 307.96 | 4,770,274 | 676 | 89.0% | - | - | OK |
| 30 | 1 | asm | keygen | 239.33 | 308.78 | 4,786,670 | 676 | 89.0% | - | - | OK |
| 31 | 4 | ref | msgcrypt | 93.78 | 97.78 | 1,875,556 | 91 | 98.5% | - | OK | OK |
| 32 | 3 | ref | encaps | 770.81 | 840.25 | 15,416,138 | 1090 | 82.3% | - | - | OK |
| 33 | 1 | asm | encaps | 314.96 | 384.41 | 6,299,301 | 808 | 86.8% | - | - | OK |
| 34 | 2 | asm | encaps | 313.70 | 383.14 | 6,273,937 | 808 | 86.8% | - | - | OK |
| 35 | 4 | asm | encaps | 313.61 | 383.06 | 6,272,216 | 808 | 86.8% | - | - | OK |
| 36 | 5 | asm | decaps | 286.99 | 290.99 | 5,739,803 | 809 | 86.8% | OK | - | OK |
| 37 | 1 | asm | msgcrypt | 38.58 | 42.58 | 771,541 | 68 | 98.9% | - | OK | OK |
| 38 | 3 | asm | msgcrypt | 38.59 | 42.59 | 771,843 | 68 | 98.9% | - | OK | OK |
| 39 | 2 | asm | keygen | 239.04 | 308.49 | 4,780,908 | 676 | 89.0% | - | - | OK |
| 40 | 3 | asm | encaps | 314.01 | 383.45 | 6,280,204 | 808 | 86.8% | - | - | OK |

## 3. Visual Artifacts

- **Empirical Distribution Histograms (Freedman-Diaconis + KDE + Rug Plot):**
  - `figures/histogram_asm.png` (PDF: `figures/histogram_asm.pdf`)
  - `figures/histogram_ref.png` (PDF: `figures/histogram_ref.pdf`)
- **Sequential Observation Timeline (Run-Order Time Series):**
  - `figures/histogram_timeseries.png` (Every single observation plotted across sequence)
- **Boxplot with All Individual Observations Overlaid (Strip Scatter):**
  - `figures/histogram_boxplot_points.png` (Boxplot showing full spread & every measured dot)

## 4. Complete Raw Data & Telemetry Files

- `raw/runs.csv`: Full tabular dataset with all observations and parameters.
- `raw/telemetry_*.json`: Full machine telemetry per firmware build.
- `raw/console_*.log`: Verbatim UART execution logs.
- `summary.csv`: Aggregated descriptive statistics.
- `schedule.json`: Randomized trial execution schedule.
