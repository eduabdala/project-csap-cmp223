# Experiment Report: exp_20261104_220508_kyber512_3751

- **Generated:** 2026-11-04 22:06:52
- **Execution Mode:** `bench`
- **Randomization Seed (Jain Ch. 11.4):** `42`
- **Replications per Cell ($N$):** `10`
- **Total Trials Executed:** `80`

## 1. Experimental Summary Table

| Algorithm | Variant | Opt | Clock | Operation | Mean Lat (ms) | 95% CI (ms) | Median (ms) | Mean Energy (uJ) | Stack Peak (B) |
| :--- | :---: | :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| kyber512 | asm | -O3 | 20.0 MHz | decaps | 316.590 | ±0.000 | 316.590 | 16146.1 | 1019 |
| kyber512 | asm | -O3 | 20.0 MHz | encaps | 343.370 | ±0.000 | 343.370 | 17511.9 | 1008 |
| kyber512 | asm | -O3 | 20.0 MHz | keygen | 261.300 | ±0.000 | 261.300 | 13326.3 | 935 |
| kyber512 | asm | -O3 | 20.0 MHz | msgcrypt | 38.360 | ±0.000 | 38.360 | 1956.4 | 68 |
| kyber512 | ref | -O3 | 20.0 MHz | decaps | 597.140 | ±0.000 | 597.140 | 30454.1 | 985 |
| kyber512 | ref | -O3 | 20.0 MHz | encaps | 615.100 | ±0.000 | 615.100 | 31370.1 | 974 |
| kyber512 | ref | -O3 | 20.0 MHz | keygen | 484.930 | ±0.000 | 484.930 | 24731.4 | 899 |
| kyber512 | ref | -O3 | 20.0 MHz | msgcrypt | 38.350 | ±0.000 | 38.350 | 1955.8 | 68 |

## 2. Visual Artifacts

- **Empirical Distribution Histograms (Freedman-Diaconis + 95% CI):**
  - PNG: `figures/histogram.png`
  - PDF: `figures/histogram.pdf`
- **Raw Trial Database:** `raw/runs.csv`
- **Summary Statistics:** `summary.csv`
