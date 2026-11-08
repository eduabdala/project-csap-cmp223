# Experiment Report: exp_20261108_143006_sim_nix_verification_9301

- **Generated:** 2026-11-08 14:30:13
- **Execution Mode:** `sim`
- **Randomization Seed (Jain Ch. 11.4):** `42`
- **Replications per Cell ($N$):** `10`
- **Total Raw Observations Recorded:** `80`

> **WARNING: SIMULATED DATA.** Every value in this report comes from a noise model (`simulate_trial`), not from the board. Do not report it as a measurement.

## 1. Experimental Summary Table

| Algorithm | Variant | Opt | Clock | Operation | N | Mean Lat (ms) | 95% CI (ms) | Median (ms) | IQR (ms) | Mean Energy (uJ) | Stack Peak (B) |
| :--- | :---: | :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| kyber512 | asm | -O3 | 20.0 MHz | decaps | 10 | 287.150 | ±0.470 | 287.023 | 0.776 | 14684.7 | 809 |
| kyber512 | asm | -O3 | 20.0 MHz | encaps | 10 | 314.060 | ±0.474 | 314.246 | 0.784 | 16153.8 | 808 |
| kyber512 | asm | -O3 | 20.0 MHz | keygen | 10 | 239.185 | ±0.465 | 239.089 | 1.032 | 12189.9 | 676 |
| kyber512 | asm | -O3 | 20.0 MHz | msgcrypt | 10 | 38.462 | ±0.084 | 38.486 | 0.120 | 1949.2 | 68 |
| kyber512 | ref | -O3 | 20.0 MHz | decaps | 10 | 704.128 | ±1.043 | 704.636 | 2.195 | 36119.7 | 1092 |
| kyber512 | ref | -O3 | 20.0 MHz | encaps | 10 | 770.088 | ±1.859 | 770.111 | 1.912 | 39607.2 | 1090 |
| kyber512 | ref | -O3 | 20.0 MHz | keygen | 10 | 585.385 | ±1.102 | 585.500 | 1.086 | 29867.6 | 912 |
| kyber512 | ref | -O3 | 20.0 MHz | msgcrypt | 10 | 94.230 | ±0.127 | 94.237 | 0.262 | 4789.4 | 91 |

## 2. Complete Raw Observations Log (All Individual Measurements)

| Run # | Rep | Variant | Operation | Latency (ms) | Total UART (ms) | Cycles (@20MHz) | Stack Peak (B) | SRAM Margin | KEM Valid | Msg Valid | Status |
| :---: | :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 10 | ref | keygen | 584.24 | 653.69 | 11,684,847 | 912 | 85.2% | - | - | OK |
| 2 | 4 | ref | decaps | 701.43 | 705.43 | 14,028,651 | 1092 | 82.2% | OK | - | OK |
| 3 | 4 | asm | decaps | 287.83 | 291.83 | 5,756,659 | 809 | 86.8% | OK | - | OK |
| 4 | 1 | ref | encaps | 770.09 | 839.54 | 15,401,884 | 1090 | 82.3% | - | - | OK |
| 5 | 1 | asm | msgcrypt | 38.43 | 42.43 | 768,532 | 68 | 98.9% | - | OK | OK |
| 6 | 6 | ref | encaps | 771.31 | 840.76 | 15,426,226 | 1090 | 82.3% | - | - | OK |
| 7 | 9 | asm | keygen | 238.75 | 308.19 | 4,774,906 | 676 | 89.0% | - | - | OK |
| 8 | 7 | ref | keygen | 586.99 | 656.44 | 11,739,880 | 912 | 85.2% | - | - | OK |
| 9 | 8 | ref | encaps | 769.56 | 839.01 | 15,391,243 | 1090 | 82.3% | - | - | OK |
| 10 | 10 | asm | msgcrypt | 38.23 | 42.23 | 764,522 | 68 | 98.9% | - | OK | OK |
| 11 | 6 | asm | encaps | 313.95 | 383.40 | 6,279,064 | 808 | 86.8% | - | - | OK |
| 12 | 3 | ref | msgcrypt | 94.39 | 98.39 | 1,887,893 | 91 | 98.5% | - | OK | OK |
| 13 | 10 | ref | encaps | 766.78 | 836.22 | 15,335,579 | 1090 | 82.3% | - | - | OK |
| 14 | 9 | asm | msgcrypt | 38.31 | 42.31 | 766,271 | 68 | 98.9% | - | OK | OK |
| 15 | 3 | ref | keygen | 582.18 | 651.62 | 11,643,540 | 912 | 85.2% | - | - | OK |
| 16 | 3 | ref | decaps | 704.26 | 708.26 | 14,085,159 | 1092 | 82.2% | OK | - | OK |
| 17 | 6 | asm | decaps | 286.97 | 290.97 | 5,739,365 | 809 | 86.8% | OK | - | OK |
| 18 | 7 | ref | encaps | 770.58 | 840.03 | 15,411,681 | 1090 | 82.3% | - | - | OK |
| 19 | 7 | ref | msgcrypt | 94.02 | 98.02 | 1,880,434 | 91 | 98.5% | - | OK | OK |
| 20 | 2 | asm | keygen | 238.37 | 307.81 | 4,767,384 | 676 | 89.0% | - | - | OK |
| 21 | 1 | ref | msgcrypt | 93.98 | 97.98 | 1,879,662 | 91 | 98.5% | - | OK | OK |
| 22 | 4 | ref | encaps | 765.63 | 835.08 | 15,312,679 | 1090 | 82.3% | - | - | OK |
| 23 | 9 | asm | encaps | 314.12 | 383.56 | 6,282,347 | 808 | 86.8% | - | - | OK |
| 24 | 8 | ref | decaps | 705.22 | 709.22 | 14,104,292 | 1092 | 82.2% | OK | - | OK |
| 25 | 10 | asm | encaps | 314.38 | 383.82 | 6,287,494 | 808 | 86.8% | - | - | OK |
| 26 | 1 | asm | decaps | 286.84 | 290.84 | 5,736,832 | 809 | 86.8% | OK | - | OK |
| 27 | 4 | ref | keygen | 587.88 | 657.33 | 11,757,683 | 912 | 85.2% | - | - | OK |
| 28 | 8 | ref | keygen | 584.81 | 654.25 | 11,696,200 | 912 | 85.2% | - | - | OK |
| 29 | 4 | asm | msgcrypt | 38.45 | 42.45 | 768,906 | 68 | 98.9% | - | OK | OK |
| 30 | 2 | ref | decaps | 705.01 | 709.01 | 14,100,300 | 1092 | 82.2% | OK | - | OK |
| 31 | 3 | asm | msgcrypt | 38.50 | 42.50 | 770,003 | 68 | 98.9% | - | OK | OK |
| 32 | 8 | asm | keygen | 239.20 | 308.64 | 4,783,942 | 676 | 89.0% | - | - | OK |
| 33 | 6 | ref | decaps | 705.41 | 709.41 | 14,108,228 | 1092 | 82.2% | OK | - | OK |
| 34 | 3 | asm | keygen | 240.20 | 309.65 | 4,804,082 | 676 | 89.0% | - | - | OK |
| 35 | 7 | asm | encaps | 313.60 | 383.04 | 6,271,969 | 808 | 86.8% | - | - | OK |
| 36 | 7 | asm | msgcrypt | 38.51 | 42.51 | 770,208 | 68 | 98.9% | - | OK | OK |
| 37 | 3 | asm | decaps | 288.30 | 292.30 | 5,765,960 | 809 | 86.8% | OK | - | OK |
| 38 | 1 | ref | keygen | 585.71 | 655.15 | 11,714,212 | 912 | 85.2% | - | - | OK |
| 39 | 5 | asm | decaps | 286.75 | 290.75 | 5,734,923 | 809 | 86.8% | OK | - | OK |
| 40 | 6 | asm | keygen | 238.92 | 308.36 | 4,778,372 | 676 | 89.0% | - | - | OK |
| 41 | 7 | asm | keygen | 239.78 | 309.22 | 4,795,541 | 676 | 89.0% | - | - | OK |
| 42 | 1 | ref | decaps | 705.03 | 709.03 | 14,100,511 | 1092 | 82.2% | OK | - | OK |
| 43 | 4 | ref | msgcrypt | 94.32 | 98.32 | 1,886,467 | 91 | 98.5% | - | OK | OK |
| 44 | 10 | asm | keygen | 238.25 | 307.70 | 4,765,073 | 676 | 89.0% | - | - | OK |
| 45 | 3 | ref | encaps | 774.56 | 844.01 | 15,491,234 | 1090 | 82.3% | - | - | OK |
| 46 | 2 | asm | decaps | 287.08 | 291.08 | 5,741,552 | 809 | 86.8% | OK | - | OK |
| 47 | 7 | ref | decaps | 702.85 | 706.85 | 14,057,047 | 1092 | 82.2% | OK | - | OK |
| 48 | 9 | ref | encaps | 769.40 | 838.84 | 15,387,984 | 1090 | 82.3% | - | - | OK |
| 49 | 1 | asm | encaps | 315.10 | 384.54 | 6,301,999 | 808 | 86.8% | - | - | OK |
| 50 | 9 | ref | keygen | 585.75 | 655.20 | 11,715,020 | 912 | 85.2% | - | - | OK |
| 51 | 1 | asm | keygen | 239.84 | 309.28 | 4,796,712 | 676 | 89.0% | - | - | OK |
| 52 | 2 | ref | encaps | 770.13 | 839.57 | 15,402,571 | 1090 | 82.3% | - | - | OK |
| 53 | 5 | ref | msgcrypt | 94.18 | 98.18 | 1,883,647 | 91 | 98.5% | - | OK | OK |
| 54 | 8 | asm | msgcrypt | 38.47 | 42.47 | 769,465 | 68 | 98.9% | - | OK | OK |
| 55 | 6 | ref | msgcrypt | 94.07 | 98.07 | 1,881,393 | 91 | 98.5% | - | OK | OK |
| 56 | 10 | ref | msgcrypt | 94.16 | 98.16 | 1,883,195 | 91 | 98.5% | - | OK | OK |
| 57 | 7 | asm | decaps | 285.97 | 289.97 | 5,719,456 | 809 | 86.8% | OK | - | OK |
| 58 | 5 | asm | msgcrypt | 38.55 | 42.55 | 770,931 | 68 | 98.9% | - | OK | OK |
| 59 | 5 | ref | keygen | 585.90 | 655.34 | 11,717,918 | 912 | 85.2% | - | - | OK |
| 60 | 2 | ref | keygen | 585.29 | 654.73 | 11,705,757 | 912 | 85.2% | - | - | OK |
| 61 | 6 | ref | keygen | 585.10 | 654.54 | 11,701,983 | 912 | 85.2% | - | - | OK |
| 62 | 3 | asm | encaps | 313.13 | 382.58 | 6,262,684 | 808 | 86.8% | - | - | OK |
| 63 | 8 | ref | msgcrypt | 94.54 | 98.54 | 1,890,824 | 91 | 98.5% | - | OK | OK |
| 64 | 9 | ref | decaps | 703.06 | 707.06 | 14,061,267 | 1092 | 82.2% | OK | - | OK |
| 65 | 5 | ref | decaps | 703.02 | 707.02 | 14,060,409 | 1092 | 82.2% | OK | - | OK |
| 66 | 10 | asm | decaps | 287.49 | 291.49 | 5,749,788 | 809 | 86.8% | OK | - | OK |
| 67 | 8 | asm | decaps | 286.75 | 290.75 | 5,734,946 | 809 | 86.8% | OK | - | OK |
| 68 | 2 | ref | msgcrypt | 94.33 | 98.33 | 1,886,631 | 91 | 98.5% | - | OK | OK |
| 69 | 9 | ref | msgcrypt | 94.29 | 98.29 | 1,885,843 | 91 | 98.5% | - | OK | OK |
| 70 | 5 | asm | keygen | 239.57 | 309.01 | 4,791,410 | 676 | 89.0% | - | - | OK |
| 71 | 5 | ref | encaps | 772.83 | 842.27 | 15,456,614 | 1090 | 82.3% | - | - | OK |
| 72 | 2 | asm | encaps | 314.38 | 383.83 | 6,287,629 | 808 | 86.8% | - | - | OK |
| 73 | 10 | ref | decaps | 705.99 | 709.99 | 14,119,768 | 1092 | 82.2% | OK | - | OK |
| 74 | 4 | asm | encaps | 314.59 | 384.04 | 6,291,815 | 808 | 86.8% | - | - | OK |
| 75 | 8 | asm | encaps | 312.96 | 382.41 | 6,259,300 | 808 | 86.8% | - | - | OK |
| 76 | 9 | asm | decaps | 287.52 | 291.52 | 5,750,452 | 809 | 86.8% | OK | - | OK |
| 77 | 2 | asm | msgcrypt | 38.56 | 42.56 | 771,201 | 68 | 98.9% | - | OK | OK |
| 78 | 6 | asm | msgcrypt | 38.62 | 42.62 | 772,319 | 68 | 98.9% | - | OK | OK |
| 79 | 4 | asm | keygen | 238.98 | 308.43 | 4,779,605 | 676 | 89.0% | - | - | OK |
| 80 | 5 | asm | encaps | 314.38 | 383.83 | 6,287,646 | 808 | 86.8% | - | - | OK |

## 3. Visual Artifacts

- **Unified Real-Scale Latency Histograms (Shared Zero-Baseline 0-700 ms, Real Counts):**
  - `figures/histogram_unified_real_scale.png` (PDF: `figures/histogram_unified_real_scale.pdf`)
  - `figures/histogram.png` (Direct side-by-side comparison of ASM vs Pure C REF on identical scale)
- **Sequential Observation Timeline (Run-Order Time Series):**
  - `figures/histogram_timeseries.png` (Every single observation plotted across sequence)
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
