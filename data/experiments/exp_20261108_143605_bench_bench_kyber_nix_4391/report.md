# Experiment Report: exp_20261108_143605_bench_bench_kyber_nix_4391

- **Generated:** 2026-11-08 14:37:37
- **Execution Mode:** `bench`
- **Randomization Seed (Jain Ch. 11.4):** `42`
- **Replications per Cell ($N$):** `5`
- **Total Raw Observations Recorded:** `40`

> Latency = host-side time until the first serial byte (includes UART/USB overhead). Energy = NA: shunt/battery not installed yet.

## 1. Experimental Summary Table

| Algorithm | Variant | Opt | Clock | Operation | N | Mean Lat (ms) | 95% CI (ms) | Median (ms) | IQR (ms) | Mean Energy (uJ) | Stack Peak (B) |
| :--- | :---: | :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| kyber512 | asm | -O3 | 20.0 MHz | decaps | 5 | 316.951 | ±0.102 | 316.937 | 0.141 | NA | 1029 |
| kyber512 | asm | -O3 | 20.0 MHz | encaps | 5 | 343.838 | ±0.099 | 343.844 | 0.098 | NA | 1018 |
| kyber512 | asm | -O3 | 20.0 MHz | keygen | 5 | 261.659 | ±0.130 | 261.642 | 0.105 | NA | 946 |
| kyber512 | asm | -O3 | 20.0 MHz | msgcrypt | 5 | 38.405 | ±0.143 | 38.405 | 0.136 | NA | 66 |
| kyber512 | ref | -O3 | 20.0 MHz | decaps | 5 | 625.283 | ±7.972 | 629.868 | 11.701 | NA | 975 |
| kyber512 | ref | -O3 | 20.0 MHz | encaps | 5 | 632.358 | ±8.008 | 636.898 | 11.655 | NA | 973 |
| kyber512 | ref | -O3 | 20.0 MHz | keygen | 5 | 502.662 | ±7.989 | 507.319 | 11.675 | NA | 899 |
| kyber512 | ref | -O3 | 20.0 MHz | msgcrypt | 5 | 38.354 | ±0.185 | 38.267 | 0.235 | NA | 66 |

## 2. Complete Raw Observations Log (All Individual Measurements)

| Run # | Rep | Variant | Operation | Latency (ms) | Total UART (ms) | Cycles (@20MHz) | Stack Peak (B) | SRAM Margin | KEM Valid | Msg Valid | Status |
| :---: | :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 1 | asm | keygen | 261.62 | 331.63 | 5,232,400 | 946 | 84.6% | - | - | OK |
| 2 | 1 | asm | encaps | 343.84 | 413.92 | 6,876,880 | 1018 | 83.4% | - | - | OK |
| 3 | 1 | asm | decaps | 317.02 | 320.44 | 6,340,460 | 1029 | 83.2% | OK | - | OK |
| 4 | 1 | asm | msgcrypt | 38.55 | 41.20 | 770,980 | 66 | 98.9% | - | OK | OK |
| 5 | 2 | asm | keygen | 261.73 | 331.66 | 5,234,500 | 946 | 84.6% | - | - | OK |
| 6 | 2 | asm | encaps | 343.88 | 413.83 | 6,877,680 | 1018 | 83.4% | - | - | OK |
| 7 | 2 | asm | decaps | 317.05 | 320.41 | 6,340,960 | 1029 | 83.2% | OK | - | OK |
| 8 | 2 | asm | msgcrypt | 38.25 | 41.13 | 765,040 | 66 | 98.9% | - | OK | OK |
| 9 | 3 | asm | keygen | 261.52 | 331.53 | 5,230,320 | 946 | 84.6% | - | - | OK |
| 10 | 3 | asm | encaps | 343.74 | 413.73 | 6,874,760 | 1018 | 83.4% | - | - | OK |
| 11 | 3 | asm | decaps | 316.94 | 320.39 | 6,338,740 | 1029 | 83.2% | OK | - | OK |
| 12 | 3 | asm | msgcrypt | 38.48 | 41.18 | 769,560 | 66 | 98.9% | - | OK | OK |
| 13 | 4 | asm | keygen | 261.79 | 331.64 | 5,235,800 | 946 | 84.6% | - | - | OK |
| 14 | 4 | asm | encaps | 343.94 | 413.78 | 6,878,800 | 1018 | 83.4% | - | - | OK |
| 15 | 4 | asm | decaps | 316.88 | 320.42 | 6,337,640 | 1029 | 83.2% | OK | - | OK |
| 16 | 4 | asm | msgcrypt | 38.41 | 41.13 | 768,100 | 66 | 98.9% | - | OK | OK |
| 17 | 5 | asm | keygen | 261.64 | 331.62 | 5,232,840 | 946 | 84.6% | - | - | OK |
| 18 | 5 | asm | encaps | 343.79 | 413.84 | 6,875,720 | 1018 | 83.4% | - | - | OK |
| 19 | 5 | asm | decaps | 316.87 | 320.58 | 6,337,320 | 1029 | 83.2% | OK | - | OK |
| 20 | 5 | asm | msgcrypt | 38.34 | 41.15 | 766,840 | 66 | 98.9% | - | OK | OK |
| 21 | 1 | ref | keygen | 495.66 | 565.65 | 9,913,180 | 899 | 85.4% | - | - | OK |
| 22 | 1 | ref | encaps | 625.32 | 695.19 | 12,506,360 | 973 | 84.2% | - | - | OK |
| 23 | 1 | ref | decaps | 618.21 | 621.64 | 12,364,180 | 975 | 84.1% | OK | - | OK |
| 24 | 1 | ref | msgcrypt | 38.24 | 41.16 | 764,740 | 66 | 98.9% | - | OK | OK |
| 25 | 2 | ref | keygen | 495.57 | 565.57 | 9,911,340 | 899 | 85.4% | - | - | OK |
| 26 | 2 | ref | encaps | 625.27 | 695.15 | 12,505,420 | 973 | 84.2% | - | - | OK |
| 27 | 2 | ref | decaps | 618.29 | 621.72 | 12,365,780 | 975 | 84.1% | OK | - | OK |
| 28 | 2 | ref | msgcrypt | 38.27 | 41.13 | 765,340 | 66 | 98.9% | - | OK | OK |
| 29 | 3 | ref | keygen | 507.32 | 577.37 | 10,146,380 | 899 | 85.4% | - | - | OK |
| 30 | 3 | ref | encaps | 636.90 | 707.08 | 12,737,960 | 973 | 84.2% | - | - | OK |
| 31 | 3 | ref | decaps | 629.99 | 633.49 | 12,599,800 | 975 | 84.1% | OK | - | OK |
| 32 | 3 | ref | msgcrypt | 38.55 | 41.15 | 771,080 | 66 | 98.9% | - | OK | OK |
| 33 | 4 | ref | keygen | 507.43 | 577.39 | 10,148,600 | 899 | 85.4% | - | - | OK |
| 34 | 4 | ref | encaps | 636.97 | 706.97 | 12,739,460 | 973 | 84.2% | - | - | OK |
| 35 | 4 | ref | decaps | 629.87 | 633.48 | 12,597,360 | 975 | 84.1% | OK | - | OK |
| 36 | 4 | ref | msgcrypt | 38.24 | 41.15 | 764,780 | 66 | 98.9% | - | OK | OK |
| 37 | 5 | ref | keygen | 507.33 | 577.48 | 10,146,680 | 899 | 85.4% | - | - | OK |
| 38 | 5 | ref | encaps | 637.33 | 707.19 | 12,746,620 | 973 | 84.2% | - | - | OK |
| 39 | 5 | ref | decaps | 630.06 | 633.63 | 12,601,200 | 975 | 84.1% | OK | - | OK |
| 40 | 5 | ref | msgcrypt | 38.47 | 41.13 | 769,480 | 66 | 98.9% | - | OK | OK |

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
