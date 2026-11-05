# Experiment Report: exp_20261104_213656_n50_study_5365

- **Generated:** 2026-11-04 21:36:59
- **Execution Mode:** `sim`
- **Randomization Seed (Jain Ch. 11.4):** `999`
- **Replications per Cell ($N$):** `50`
- **Total Trials Executed:** `400`

## 1. Experimental Summary Table

| Algorithm | Variant | Opt | Clock | Operation | Mean Lat (ms) | 95% CI (ms) | Median (ms) | Mean Energy (uJ) | Stack Peak (B) |
| :--- | :---: | :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| kyber512 | asm | -O3 | 20.0 MHz | decaps | 287.749 | ±0.229 | 287.774 | 14758.5 | 809 |
| kyber512 | asm | -O3 | 20.0 MHz | encaps | 315.053 | ±0.255 | 314.952 | 16227.8 | 808 |
| kyber512 | asm | -O3 | 20.0 MHz | keygen | 239.555 | ±0.213 | 239.571 | 12214.0 | 676 |
| kyber512 | asm | -O3 | 20.0 MHz | msgcrypt | 38.530 | ±0.031 | 38.540 | 1955.7 | 68 |
| kyber512 | ref | -O3 | 20.0 MHz | decaps | 705.275 | ±0.616 | 705.000 | 36173.0 | 1092 |
| kyber512 | ref | -O3 | 20.0 MHz | encaps | 772.287 | ±0.647 | 772.368 | 39759.4 | 1090 |
| kyber512 | ref | -O3 | 20.0 MHz | keygen | 587.696 | ±0.511 | 587.655 | 30029.8 | 912 |
| kyber512 | ref | -O3 | 20.0 MHz | msgcrypt | 94.373 | ±0.093 | 94.374 | 4792.9 | 91 |

## 2. Visual Artifacts

- **Empirical Distribution Histograms (Freedman-Diaconis + 95% CI):**
  - PNG: `figures/histogram.png`
  - PDF: `figures/histogram.pdf`
- **Raw Trial Database:** `raw/runs.csv`
- **Summary Statistics:** `summary.csv`
