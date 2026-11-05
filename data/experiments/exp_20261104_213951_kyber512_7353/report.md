# Experiment Report: exp_20261104_213951_kyber512_7353

- **Generated:** 2026-11-04 21:40:20
- **Execution Mode:** `bench`
- **Randomization Seed (Jain Ch. 11.4):** `42`
- **Replications per Cell ($N$):** `1`
- **Total Trials Executed:** `4`

## 1. Experimental Summary Table

| Algorithm | Variant | Opt | Clock | Operation | Mean Lat (ms) | 95% CI (ms) | Median (ms) | Mean Energy (uJ) | Stack Peak (B) |
| :--- | :---: | :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| kyber512 | asm | -O3 | 20.0 MHz | decaps | 316.580 | ±0.000 | 316.580 | 16145.6 | 1019 |
| kyber512 | asm | -O3 | 20.0 MHz | encaps | 343.490 | ±0.000 | 343.490 | 17518.0 | 1008 |
| kyber512 | asm | -O3 | 20.0 MHz | keygen | 261.350 | ±0.000 | 261.350 | 13328.9 | 935 |
| kyber512 | asm | -O3 | 20.0 MHz | msgcrypt | 38.450 | ±0.000 | 38.450 | 1961.0 | 68 |

## 2. Visual Artifacts

- **Empirical Distribution Histograms (Freedman-Diaconis + 95% CI):**
  - PNG: `figures/histogram.png`
  - PDF: `figures/histogram.pdf`
- **Raw Trial Database:** `raw/runs.csv`
- **Summary Statistics:** `summary.csv`
