# Experiment Report: exp_20261104_221304_kyber512_4445

- **Generated:** 2026-11-04 22:14:48
- **Execution Mode:** `bench`
- **Randomization Seed (Jain Ch. 11.4):** `42`
- **Replications per Cell ($N$):** `10`
- **Total Trials Executed:** `80`

## 1. Experimental Summary Table

| Algorithm | Variant | Opt | Clock | Operation | Mean Lat (ms) | 95% CI (ms) | Median (ms) | Mean Energy (uJ) | Stack Peak (B) |
| :--- | :---: | :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| kyber512 | asm | -O3 | 20.0 MHz | decaps | 317.860 | ±0.000 | 317.860 | 16210.9 | 1019 |
| kyber512 | asm | -O3 | 20.0 MHz | encaps | 344.500 | ±0.000 | 344.500 | 17569.5 | 1008 |
| kyber512 | asm | -O3 | 20.0 MHz | keygen | 262.510 | ±0.000 | 262.510 | 13388.0 | 935 |
| kyber512 | asm | -O3 | 20.0 MHz | msgcrypt | 38.300 | ±0.000 | 38.300 | 1953.3 | 68 |
| kyber512 | ref | -O3 | 20.0 MHz | decaps | 611.290 | ±0.000 | 611.290 | 31175.8 | 985 |
| kyber512 | ref | -O3 | 20.0 MHz | encaps | 625.510 | ±0.000 | 625.510 | 31901.0 | 974 |
| kyber512 | ref | -O3 | 20.0 MHz | keygen | 497.570 | ±0.000 | 497.570 | 25376.1 | 899 |
| kyber512 | ref | -O3 | 20.0 MHz | msgcrypt | 38.400 | ±0.000 | 38.400 | 1958.4 | 68 |

## 2. Visual Artifacts

- **Empirical Distribution Histograms (Freedman-Diaconis + 95% CI):**
  - PNG: `figures/histogram.png`
  - PDF: `figures/histogram.pdf`
- **Raw Trial Database:** `raw/runs.csv`
- **Summary Statistics:** `summary.csv`
