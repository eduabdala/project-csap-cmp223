# Experiment Report: exp_20261104_223733_compare_asm_ref_1944

- **Generated:** 2026-11-04 22:39:01
- **Execution Mode:** `bench`
- **Randomization Seed (Jain Ch. 11.4):** `42`
- **Replications per Cell ($N$):** `5`
- **Total Trials Executed:** `40`

## 1. Experimental Summary Table

| Algorithm | Variant | Opt | Clock | Operation | Mean Lat (ms) | 95% CI (ms) | Median (ms) | Mean Energy (uJ) | Stack Peak (B) |
| :--- | :---: | :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| kyber512 | asm | -O3 | 20.0 MHz | decaps | 316.784 | ±0.345 | 316.650 | 16156.0 | 1019 |
| kyber512 | asm | -O3 | 20.0 MHz | encaps | 343.540 | ±0.142 | 343.580 | 17520.5 | 1008 |
| kyber512 | asm | -O3 | 20.0 MHz | keygen | 261.360 | ±0.125 | 261.360 | 13329.4 | 935 |
| kyber512 | asm | -O3 | 20.0 MHz | msgcrypt | 38.414 | ±0.117 | 38.420 | 1959.1 | 68 |
| kyber512 | ref | -O3 | 20.0 MHz | decaps | 620.246 | ±0.177 | 620.290 | 31632.5 | 976 |
| kyber512 | ref | -O3 | 20.0 MHz | encaps | 628.640 | ±0.464 | 628.570 | 32060.6 | 974 |
| kyber512 | ref | -O3 | 20.0 MHz | keygen | 497.846 | ±0.273 | 497.840 | 25390.2 | 899 |
| kyber512 | ref | -O3 | 20.0 MHz | msgcrypt | 38.542 | ±0.121 | 38.560 | 1965.6 | 68 |

## 2. Visual Artifacts

- **Empirical Distribution Histograms (Freedman-Diaconis + 95% CI):**
  - PNG: `figures/histogram.png`
  - PDF: `figures/histogram.pdf`
- **Raw Trial Database:** `raw/runs.csv`
- **Summary Statistics:** `summary.csv`
