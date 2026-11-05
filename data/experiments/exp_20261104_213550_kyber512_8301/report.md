# Experiment Report: exp_20261104_213550_kyber512_8301

- **Generated:** 2026-11-04 21:35:54
- **Execution Mode:** `sim`
- **Randomization Seed (Jain Ch. 11.4):** `123`
- **Replications per Cell ($N$):** `30`
- **Total Trials Executed:** `240`

## 1. Experimental Summary Table

| Algorithm | Variant | Opt | Clock | Operation | Mean Lat (ms) | 95% CI (ms) | Median (ms) | Mean Energy (uJ) | Stack Peak (B) |
| :--- | :---: | :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| kyber512 | asm | -O3 | 20.0 MHz | decaps | 287.260 | ±0.292 | 287.188 | 14732.4 | 809 |
| kyber512 | asm | -O3 | 20.0 MHz | encaps | 314.515 | ±0.315 | 314.463 | 16182.8 | 808 |
| kyber512 | asm | -O3 | 20.0 MHz | keygen | 239.049 | ±0.247 | 239.173 | 12184.4 | 676 |
| kyber512 | asm | -O3 | 20.0 MHz | msgcrypt | 38.489 | ±0.031 | 38.475 | 1952.8 | 68 |
| kyber512 | ref | -O3 | 20.0 MHz | decaps | 704.142 | ±0.723 | 704.786 | 36085.8 | 1092 |
| kyber512 | ref | -O3 | 20.0 MHz | encaps | 770.650 | ±0.740 | 770.620 | 39708.1 | 1090 |
| kyber512 | ref | -O3 | 20.0 MHz | keygen | 586.441 | ±0.474 | 586.314 | 29903.8 | 912 |
| kyber512 | ref | -O3 | 20.0 MHz | msgcrypt | 94.353 | ±0.091 | 94.316 | 4789.6 | 91 |

## 2. Visual Artifacts

- **Empirical Distribution Histograms (Freedman-Diaconis + 95% CI):**
  - PNG: `figures/histogram.png`
  - PDF: `figures/histogram.pdf`
- **Raw Trial Database:** `raw/runs.csv`
- **Summary Statistics:** `summary.csv`
