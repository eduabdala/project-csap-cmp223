# Experiment Report: exp_20261104_234322_kyber512_3110

- **Generated:** 2026-11-04 23:45:11
- **Execution Mode:** `bench`
- **Randomization Seed (Jain Ch. 11.4):** `42`
- **Replications per Cell ($N$):** `10`
- **Total Raw Observations Recorded:** `80`

## 1. Experimental Summary Table

| Algorithm | Variant | Opt | Clock | Operation | N | Mean Lat (ms) | 95% CI (ms) | Median (ms) | IQR (ms) | Mean Energy (uJ) | Stack Peak (B) |
| :--- | :---: | :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| kyber512 | asm | -O3 | 20.0 MHz | decaps | 10 | 317.277 | ±1.546 | 316.622 | 0.083 | 16181.1 | 1019 |
| kyber512 | asm | -O3 | 20.0 MHz | encaps | 10 | 344.117 | ±1.512 | 343.373 | 0.536 | 17550.0 | 1008 |
| kyber512 | asm | -O3 | 20.0 MHz | keygen | 10 | 262.160 | ±1.640 | 261.438 | 0.600 | 13370.1 | 935 |
| kyber512 | asm | -O3 | 20.0 MHz | msgcrypt | 10 | 38.583 | ±0.205 | 38.458 | 0.237 | 1967.7 | 68 |
| kyber512 | ref | -O3 | 20.0 MHz | decaps | 10 | 619.943 | ±0.209 | 619.826 | 0.264 | 31617.1 | 976 |
| kyber512 | ref | -O3 | 20.0 MHz | encaps | 10 | 628.031 | ±0.186 | 627.949 | 0.119 | 32029.6 | 974 |
| kyber512 | ref | -O3 | 20.0 MHz | keygen | 10 | 497.342 | ±0.075 | 497.324 | 0.063 | 25364.4 | 899 |
| kyber512 | ref | -O3 | 20.0 MHz | msgcrypt | 10 | 38.364 | ±0.163 | 38.313 | 0.207 | 1956.5 | 68 |

## 2. Complete Raw Observations Log (All Individual Measurements)

| Run # | Rep | Variant | Operation | Latency (ms) | Total UART (ms) | Cycles (@20MHz) | Stack Peak (B) | SRAM Margin | KEM Valid | Msg Valid | Status |
| :---: | :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 1 | asm | keygen | 261.38 | 331.19 | 5,227,500 | 935 | 84.8% | - | - | OK |
| 2 | 1 | asm | encaps | 343.92 | 413.21 | 6,878,460 | 1008 | 83.6% | - | - | OK |
| 3 | 1 | asm | decaps | 316.62 | 320.09 | 6,332,460 | 1019 | 83.4% | OK | - | OK |
| 4 | 1 | asm | msgcrypt | 38.34 | 41.20 | 766,900 | 68 | 98.9% | - | OK | OK |
| 5 | 2 | asm | keygen | 261.51 | 331.18 | 5,230,260 | 935 | 84.8% | - | - | OK |
| 6 | 2 | asm | encaps | 343.15 | 413.19 | 6,863,020 | 1008 | 83.6% | - | - | OK |
| 7 | 2 | asm | decaps | 316.67 | 319.96 | 6,333,360 | 1019 | 83.4% | OK | - | OK |
| 8 | 2 | asm | msgcrypt | 38.41 | 41.20 | 768,140 | 68 | 98.9% | - | OK | OK |
| 9 | 3 | asm | keygen | 261.49 | 331.17 | 5,229,720 | 935 | 84.8% | - | - | OK |
| 10 | 3 | asm | encaps | 343.37 | 413.18 | 6,867,420 | 1008 | 83.6% | - | - | OK |
| 11 | 3 | asm | decaps | 316.62 | 320.01 | 6,332,400 | 1019 | 83.4% | OK | - | OK |
| 12 | 3 | asm | msgcrypt | 38.36 | 41.19 | 767,140 | 68 | 98.9% | - | OK | OK |
| 13 | 4 | asm | keygen | 261.09 | 331.20 | 5,221,860 | 935 | 84.8% | - | - | OK |
| 14 | 4 | asm | encaps | 343.86 | 413.20 | 6,877,120 | 1008 | 83.6% | - | - | OK |
| 15 | 4 | asm | decaps | 316.73 | 320.07 | 6,334,500 | 1019 | 83.4% | OK | - | OK |
| 16 | 4 | asm | msgcrypt | 38.64 | 41.35 | 772,740 | 67 | 98.9% | - | OK | OK |
| 17 | 5 | asm | keygen | 261.84 | 331.10 | 5,236,800 | 935 | 84.8% | - | - | OK |
| 18 | 5 | asm | encaps | 343.38 | 413.12 | 6,867,520 | 1008 | 83.6% | - | - | OK |
| 19 | 5 | asm | decaps | 316.58 | 319.90 | 6,331,700 | 1019 | 83.4% | OK | - | OK |
| 20 | 5 | asm | msgcrypt | 38.46 | 41.30 | 769,240 | 68 | 98.9% | - | OK | OK |
| 21 | 6 | asm | keygen | 261.39 | 331.11 | 5,227,780 | 935 | 84.8% | - | - | OK |
| 22 | 6 | asm | encaps | 343.55 | 413.14 | 6,870,960 | 1008 | 83.6% | - | - | OK |
| 23 | 6 | asm | decaps | 316.46 | 319.96 | 6,329,280 | 1019 | 83.4% | OK | - | OK |
| 24 | 6 | asm | msgcrypt | 38.60 | 41.16 | 772,020 | 68 | 98.9% | - | OK | OK |
| 25 | 7 | asm | keygen | 268.65 | 337.99 | 5,372,940 | 935 | 84.8% | - | - | OK |
| 26 | 7 | asm | encaps | 350.09 | 419.95 | 7,001,760 | 1008 | 83.6% | - | - | OK |
| 27 | 7 | asm | decaps | 323.42 | 326.83 | 6,468,400 | 1019 | 83.4% | OK | - | OK |
| 28 | 7 | asm | msgcrypt | 38.96 | 41.20 | 779,240 | 68 | 98.9% | - | OK | OK |
| 29 | 8 | asm | keygen | 261.84 | 331.08 | 5,236,820 | 935 | 84.8% | - | - | OK |
| 30 | 8 | asm | encaps | 343.36 | 413.01 | 6,867,280 | 1008 | 83.6% | - | - | OK |
| 31 | 8 | asm | decaps | 316.61 | 319.94 | 6,332,200 | 1019 | 83.4% | OK | - | OK |
| 32 | 8 | asm | msgcrypt | 38.45 | 41.30 | 769,080 | 68 | 98.9% | - | OK | OK |
| 33 | 9 | asm | keygen | 261.17 | 331.10 | 5,223,480 | 935 | 84.8% | - | - | OK |
| 34 | 9 | asm | encaps | 343.32 | 413.23 | 6,866,400 | 1008 | 83.6% | - | - | OK |
| 35 | 9 | asm | decaps | 316.39 | 319.92 | 6,327,860 | 1019 | 83.4% | OK | - | OK |
| 36 | 9 | asm | msgcrypt | 38.40 | 41.16 | 768,000 | 68 | 98.9% | - | OK | OK |
| 37 | 10 | asm | keygen | 261.24 | 331.06 | 5,224,800 | 935 | 84.8% | - | - | OK |
| 38 | 10 | asm | encaps | 343.17 | 413.07 | 6,863,400 | 1008 | 83.6% | - | - | OK |
| 39 | 10 | asm | decaps | 316.66 | 319.88 | 6,333,220 | 1019 | 83.4% | OK | - | OK |
| 40 | 10 | asm | msgcrypt | 39.21 | 41.28 | 784,120 | 68 | 98.9% | - | OK | OK |
| 41 | 1 | ref | keygen | 497.30 | 567.39 | 9,946,060 | 899 | 85.4% | - | - | OK |
| 42 | 1 | ref | encaps | 628.01 | 697.90 | 12,560,260 | 974 | 84.2% | - | - | OK |
| 43 | 1 | ref | decaps | 619.79 | 623.36 | 12,395,760 | 976 | 84.1% | OK | - | OK |
| 44 | 1 | ref | msgcrypt | 38.31 | 41.18 | 766,180 | 68 | 98.9% | - | OK | OK |
| 45 | 2 | ref | keygen | 497.49 | 567.36 | 9,949,780 | 899 | 85.4% | - | - | OK |
| 46 | 2 | ref | encaps | 627.89 | 706.71 | 12,557,880 | 974 | 84.2% | - | - | OK |
| 47 | 2 | ref | decaps | 619.84 | 623.38 | 12,396,860 | 976 | 84.1% | OK | - | OK |
| 48 | 2 | ref | msgcrypt | 38.16 | 41.16 | 763,220 | 68 | 98.9% | - | OK | OK |
| 49 | 3 | ref | keygen | 497.54 | 567.42 | 9,950,880 | 899 | 85.4% | - | - | OK |
| 50 | 3 | ref | encaps | 628.01 | 697.79 | 12,560,260 | 974 | 84.2% | - | - | OK |
| 51 | 3 | ref | decaps | 619.79 | 623.39 | 12,395,780 | 976 | 84.1% | OK | - | OK |
| 52 | 3 | ref | msgcrypt | 38.28 | 41.14 | 765,540 | 68 | 98.9% | - | OK | OK |
| 53 | 4 | ref | keygen | 497.35 | 567.34 | 9,946,920 | 899 | 85.4% | - | - | OK |
| 54 | 4 | ref | encaps | 627.96 | 697.88 | 12,559,180 | 974 | 84.2% | - | - | OK |
| 55 | 4 | ref | decaps | 619.77 | 623.44 | 12,395,360 | 976 | 84.1% | OK | - | OK |
| 56 | 4 | ref | msgcrypt | 38.18 | 41.15 | 763,600 | 68 | 98.9% | - | OK | OK |
| 57 | 5 | ref | keygen | 497.20 | 567.26 | 9,944,100 | 899 | 85.4% | - | - | OK |
| 58 | 5 | ref | encaps | 627.94 | 697.78 | 12,558,780 | 974 | 84.2% | - | - | OK |
| 59 | 5 | ref | decaps | 619.92 | 623.32 | 12,398,460 | 976 | 84.1% | OK | - | OK |
| 60 | 5 | ref | msgcrypt | 38.16 | 41.13 | 763,200 | 68 | 98.9% | - | OK | OK |
| 61 | 6 | ref | keygen | 497.23 | 567.12 | 9,944,500 | 899 | 85.4% | - | - | OK |
| 62 | 6 | ref | encaps | 627.91 | 697.82 | 12,558,180 | 974 | 84.2% | - | - | OK |
| 63 | 6 | ref | decaps | 619.81 | 623.32 | 12,396,160 | 976 | 84.1% | OK | - | OK |
| 64 | 6 | ref | msgcrypt | 38.32 | 41.19 | 766,340 | 68 | 98.9% | - | OK | OK |
| 65 | 7 | ref | keygen | 497.34 | 567.33 | 9,946,780 | 899 | 85.4% | - | - | OK |
| 66 | 7 | ref | encaps | 628.04 | 698.00 | 12,560,900 | 974 | 84.2% | - | - | OK |
| 67 | 7 | ref | decaps | 620.05 | 623.45 | 12,401,040 | 976 | 84.1% | OK | - | OK |
| 68 | 7 | ref | msgcrypt | 38.39 | 41.21 | 767,740 | 68 | 98.9% | - | OK | OK |
| 69 | 8 | ref | keygen | 497.30 | 567.24 | 9,945,940 | 899 | 85.4% | - | - | OK |
| 70 | 8 | ref | encaps | 627.89 | 697.87 | 12,557,820 | 974 | 84.2% | - | - | OK |
| 71 | 8 | ref | decaps | 620.06 | 623.28 | 12,401,160 | 976 | 84.1% | OK | - | OK |
| 72 | 8 | ref | msgcrypt | 38.32 | 41.22 | 766,380 | 68 | 98.9% | - | OK | OK |
| 73 | 9 | ref | keygen | 497.36 | 567.22 | 9,947,200 | 899 | 85.4% | - | - | OK |
| 74 | 9 | ref | encaps | 627.89 | 697.76 | 12,557,820 | 974 | 84.2% | - | - | OK |
| 75 | 9 | ref | decaps | 619.70 | 623.16 | 12,394,020 | 976 | 84.1% | - | - | OK |
| 76 | 9 | ref | msgcrypt | 38.67 | 41.38 | 773,460 | 68 | 98.9% | - | OK | OK |
| 77 | 10 | ref | keygen | 497.31 | 567.26 | 9,946,160 | 899 | 85.4% | - | - | OK |
| 78 | 10 | ref | encaps | 628.75 | 697.98 | 12,575,040 | 974 | 84.2% | - | - | OK |
| 79 | 10 | ref | decaps | 620.70 | 623.46 | 12,414,060 | 976 | 84.1% | OK | - | OK |
| 80 | 10 | ref | msgcrypt | 38.85 | 41.19 | 777,080 | 68 | 98.9% | - | OK | OK |

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
