# Experiment Report: exp_20261105_000627_test_all_matrix_2686

- **Generated:** 2026-11-05 00:06:43
- **Execution Mode:** `sim`
- **Randomization Seed (Jain Ch. 11.4):** `42`
- **Replications per Cell ($N$):** `2`
- **Total Raw Observations Recorded:** `96`

## 1. Experimental Summary Table

| Algorithm | Variant | Opt | Clock | Operation | N | Mean Lat (ms) | 95% CI (ms) | Median (ms) | IQR (ms) | Mean Energy (uJ) | Stack Peak (B) |
| :--- | :---: | :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| ctru-light | asm | -O3 | 20.0 MHz | decaps | 2 | 194.773 | ±11.721 | 194.773 | 1.845 | 9852.8 | 620 |
| ctru-light | asm | -O3 | 20.0 MHz | encaps | 2 | 208.648 | ±11.073 | 208.648 | 1.743 | 10580.3 | 612 |
| ctru-light | asm | -O3 | 20.0 MHz | keygen | 2 | 160.435 | ±0.623 | 160.435 | 0.098 | 8144.3 | 540 |
| ctru-light | asm | -O3 | 20.0 MHz | msgcrypt | 2 | 38.528 | ±0.699 | 38.528 | 0.110 | 1952.1 | 68 |
| ctru-light | asm | -Os | 20.0 MHz | decaps | 2 | 249.910 | ±2.668 | 249.910 | 0.420 | 12630.9 | 620 |
| ctru-light | asm | -Os | 20.0 MHz | encaps | 2 | 267.053 | ±3.799 | 267.053 | 0.598 | 13561.9 | 612 |
| ctru-light | asm | -Os | 20.0 MHz | keygen | 2 | 205.207 | ±2.687 | 205.207 | 0.423 | 10411.2 | 540 |
| ctru-light | asm | -Os | 20.0 MHz | msgcrypt | 2 | 49.322 | ±1.188 | 49.322 | 0.187 | 2495.9 | 68 |
| ctru-light | ref | -O3 | 20.0 MHz | decaps | 2 | 479.257 | ±19.866 | 479.257 | 3.127 | 24220.9 | 837 |
| ctru-light | ref | -O3 | 20.0 MHz | encaps | 2 | 509.017 | ±24.840 | 509.017 | 3.910 | 25822.1 | 826 |
| ctru-light | ref | -O3 | 20.0 MHz | keygen | 2 | 392.851 | ±0.419 | 392.851 | 0.066 | 19802.2 | 729 |
| ctru-light | ref | -O3 | 20.0 MHz | msgcrypt | 2 | 94.337 | ±0.597 | 94.337 | 0.094 | 4775.5 | 91 |
| ctru-light | ref | -Os | 20.0 MHz | decaps | 2 | 610.482 | ±0.515 | 610.482 | 0.081 | 31076.2 | 837 |
| ctru-light | ref | -Os | 20.0 MHz | encaps | 2 | 651.347 | ±5.089 | 651.347 | 0.801 | 32885.6 | 826 |
| ctru-light | ref | -Os | 20.0 MHz | keygen | 2 | 504.467 | ±10.330 | 504.467 | 1.626 | 25623.8 | 729 |
| ctru-light | ref | -Os | 20.0 MHz | msgcrypt | 2 | 120.576 | ±3.246 | 120.576 | 0.511 | 6120.2 | 91 |
| ecdh | asm | -O3 | 20.0 MHz | decaps | 2 | 1485.692 | ±30.139 | 1485.692 | 4.744 | 73705.9 | 310 |
| ecdh | asm | -O3 | 20.0 MHz | encaps | 2 | 1492.699 | ±22.293 | 1492.699 | 3.509 | 73920.1 | 310 |
| ecdh | asm | -O3 | 20.0 MHz | keygen | 2 | 1429.703 | ±17.636 | 1429.703 | 2.776 | 70976.6 | 280 |
| ecdh | asm | -O3 | 20.0 MHz | msgcrypt | 2 | 38.521 | ±0.851 | 38.521 | 0.134 | 1957.1 | 68 |
| ecdh | asm | -Os | 20.0 MHz | decaps | 2 | 1909.845 | ±60.068 | 1909.845 | 9.455 | 94686.3 | 310 |
| ecdh | asm | -Os | 20.0 MHz | encaps | 2 | 1908.792 | ±59.210 | 1908.792 | 9.320 | 94483.8 | 310 |
| ecdh | asm | -Os | 20.0 MHz | keygen | 2 | 1828.099 | ±80.797 | 1828.099 | 12.718 | 90488.4 | 280 |
| ecdh | asm | -Os | 20.0 MHz | msgcrypt | 2 | 49.206 | ±0.267 | 49.206 | 0.042 | 2508.3 | 68 |
| ecdh | ref | -O3 | 20.0 MHz | decaps | 2 | 3657.961 | ±26.765 | 3657.961 | 4.213 | 182637.2 | 418 |
| ecdh | ref | -O3 | 20.0 MHz | encaps | 2 | 3654.073 | ±41.898 | 3654.073 | 6.595 | 181939.6 | 418 |
| ecdh | ref | -O3 | 20.0 MHz | keygen | 2 | 3499.055 | ±132.028 | 3499.055 | 20.782 | 172430.5 | 378 |
| ecdh | ref | -O3 | 20.0 MHz | msgcrypt | 2 | 94.120 | ±3.037 | 94.120 | 0.478 | 4788.1 | 91 |
| ecdh | ref | -Os | 20.0 MHz | decaps | 2 | 4658.406 | ±69.578 | 4658.406 | 10.952 | 231730.0 | 418 |
| ecdh | ref | -Os | 20.0 MHz | encaps | 2 | 4671.506 | ±71.115 | 4671.506 | 11.194 | 231170.1 | 418 |
| ecdh | ref | -Os | 20.0 MHz | keygen | 2 | 4469.936 | ±225.379 | 4469.936 | 35.476 | 221713.4 | 378 |
| ecdh | ref | -Os | 20.0 MHz | msgcrypt | 2 | 120.353 | ±2.687 | 120.353 | 0.423 | 6093.5 | 91 |
| kyber512 | asm | -O3 | 20.0 MHz | decaps | 2 | 286.896 | ±4.295 | 286.896 | 0.676 | 14740.2 | 809 |
| kyber512 | asm | -O3 | 20.0 MHz | encaps | 2 | 315.229 | ±1.588 | 315.229 | 0.250 | 16226.2 | 808 |
| kyber512 | asm | -O3 | 20.0 MHz | keygen | 2 | 238.401 | ±7.325 | 238.401 | 1.153 | 12132.4 | 676 |
| kyber512 | asm | -O3 | 20.0 MHz | msgcrypt | 2 | 38.488 | ±0.165 | 38.488 | 0.026 | 1960.8 | 68 |
| kyber512 | asm | -Os | 20.0 MHz | decaps | 2 | 367.262 | ±5.762 | 367.262 | 0.907 | 18882.9 | 809 |
| kyber512 | asm | -Os | 20.0 MHz | encaps | 2 | 401.993 | ±6.315 | 401.993 | 0.994 | 20684.1 | 808 |
| kyber512 | asm | -Os | 20.0 MHz | keygen | 2 | 306.567 | ±0.375 | 306.567 | 0.059 | 15613.4 | 676 |
| kyber512 | asm | -Os | 20.0 MHz | msgcrypt | 2 | 49.276 | ±0.705 | 49.276 | 0.111 | 2514.9 | 68 |
| kyber512 | ref | -O3 | 20.0 MHz | decaps | 2 | 703.186 | ±11.658 | 703.186 | 1.835 | 36133.1 | 1092 |
| kyber512 | ref | -O3 | 20.0 MHz | encaps | 2 | 770.545 | ±8.532 | 770.545 | 1.343 | 39720.8 | 1090 |
| kyber512 | ref | -O3 | 20.0 MHz | keygen | 2 | 584.372 | ±14.472 | 584.372 | 2.278 | 29770.3 | 912 |
| kyber512 | ref | -O3 | 20.0 MHz | msgcrypt | 2 | 94.109 | ±1.747 | 94.109 | 0.275 | 4791.9 | 91 |
| kyber512 | ref | -Os | 20.0 MHz | decaps | 2 | 897.726 | ±19.370 | 897.726 | 3.049 | 46176.2 | 1092 |
| kyber512 | ref | -Os | 20.0 MHz | encaps | 2 | 986.716 | ±40.176 | 986.716 | 6.324 | 51042.9 | 1090 |
| kyber512 | ref | -Os | 20.0 MHz | keygen | 2 | 750.799 | ±1.518 | 750.799 | 0.239 | 38351.6 | 912 |
| kyber512 | ref | -Os | 20.0 MHz | msgcrypt | 2 | 120.378 | ±7.280 | 120.378 | 1.146 | 6127.2 | 91 |

## 2. Complete Raw Observations Log (All Individual Measurements)

| Run # | Rep | Variant | Operation | Latency (ms) | Total UART (ms) | Cycles (@20MHz) | Stack Peak (B) | SRAM Margin | KEM Valid | Msg Valid | Status |
| :---: | :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 1 | ref | decaps | 3655.86 | 3659.86 | 73,117,104 | 418 | 93.2% | OK | - | OK |
| 2 | 2 | ref | encaps | 651.75 | 721.19 | 13,034,962 | 826 | 86.6% | - | - | OK |
| 3 | 1 | ref | msgcrypt | 120.32 | 124.32 | 2,406,426 | 91 | 98.5% | - | OK | OK |
| 4 | 2 | asm | keygen | 306.54 | 375.98 | 6,130,768 | 676 | 89.0% | - | - | OK |
| 5 | 2 | asm | keygen | 160.48 | 229.93 | 3,209,677 | 540 | 91.2% | - | - | OK |
| 6 | 1 | ref | encaps | 983.55 | 1053.00 | 19,671,083 | 1090 | 82.3% | - | - | OK |
| 7 | 2 | asm | keygen | 237.82 | 307.27 | 4,756,505 | 676 | 89.0% | - | - | OK |
| 8 | 1 | asm | decaps | 1488.06 | 1492.06 | 29,761,275 | 310 | 95.0% | OK | - | OK |
| 9 | 2 | asm | msgcrypt | 49.33 | 53.33 | 986,620 | 68 | 98.9% | - | OK | OK |
| 10 | 1 | ref | decaps | 610.44 | 614.44 | 12,208,842 | 837 | 86.4% | OK | - | OK |
| 11 | 2 | ref | msgcrypt | 120.83 | 124.83 | 2,416,636 | 91 | 98.5% | - | OK | OK |
| 12 | 1 | asm | encaps | 402.49 | 471.93 | 8,049,790 | 808 | 86.8% | - | - | OK |
| 13 | 1 | ref | decaps | 477.69 | 481.69 | 9,553,887 | 837 | 86.4% | OK | - | OK |
| 14 | 1 | asm | encaps | 1913.45 | 1982.90 | 38,269,036 | 310 | 95.0% | - | - | OK |
| 15 | 2 | ref | encaps | 510.97 | 580.42 | 10,219,444 | 826 | 86.6% | - | - | OK |
| 16 | 2 | ref | keygen | 4487.67 | 4557.12 | 89,753,489 | 378 | 93.8% | - | - | OK |
| 17 | 2 | ref | keygen | 392.82 | 462.26 | 7,856,352 | 729 | 88.1% | - | - | OK |
| 18 | 2 | asm | keygen | 205.42 | 274.86 | 4,108,358 | 540 | 91.2% | - | - | OK |
| 19 | 2 | asm | keygen | 1428.32 | 1497.76 | 28,566,306 | 280 | 95.4% | - | - | OK |
| 20 | 1 | ref | msgcrypt | 119.81 | 123.81 | 2,396,108 | 91 | 98.5% | - | OK | OK |
| 21 | 2 | ref | msgcrypt | 94.29 | 98.29 | 1,885,790 | 91 | 98.5% | - | OK | OK |
| 22 | 1 | asm | keygen | 1821.74 | 1891.18 | 36,434,802 | 280 | 95.4% | - | - | OK |
| 23 | 2 | asm | decaps | 250.12 | 254.12 | 5,002,396 | 620 | 89.9% | OK | - | OK |
| 24 | 1 | asm | keygen | 160.39 | 229.83 | 3,207,721 | 540 | 91.2% | - | - | OK |
| 25 | 1 | ref | keygen | 3488.66 | 3558.11 | 69,773,274 | 378 | 93.8% | - | - | OK |
| 26 | 2 | asm | encaps | 1490.94 | 1560.39 | 29,818,909 | 310 | 95.0% | - | - | OK |
| 27 | 2 | ref | encaps | 4677.10 | 4746.55 | 93,542,055 | 418 | 93.2% | - | - | OK |
| 28 | 1 | asm | keygen | 306.60 | 376.04 | 6,131,949 | 676 | 89.0% | - | - | OK |
| 29 | 2 | asm | decaps | 195.69 | 199.69 | 3,913,908 | 620 | 89.9% | OK | - | OK |
| 30 | 1 | asm | decaps | 1914.57 | 1918.57 | 38,291,456 | 310 | 95.0% | OK | - | OK |
| 31 | 2 | asm | msgcrypt | 49.19 | 53.19 | 983,709 | 68 | 98.9% | - | OK | OK |
| 32 | 2 | asm | msgcrypt | 49.42 | 53.42 | 988,319 | 68 | 98.9% | - | OK | OK |
| 33 | 1 | asm | decaps | 249.70 | 253.70 | 4,994,002 | 620 | 89.9% | OK | - | OK |
| 34 | 1 | asm | encaps | 266.75 | 336.20 | 5,335,085 | 612 | 90.0% | - | - | OK |
| 35 | 1 | ref | msgcrypt | 120.56 | 124.56 | 2,411,281 | 91 | 98.5% | - | OK | OK |
| 36 | 1 | ref | encaps | 507.06 | 576.51 | 10,141,246 | 826 | 86.6% | - | - | OK |
| 37 | 1 | ref | encaps | 3650.78 | 3720.22 | 73,015,512 | 418 | 93.2% | - | - | OK |
| 38 | 1 | asm | decaps | 366.81 | 370.81 | 7,336,152 | 809 | 86.8% | OK | - | OK |
| 39 | 1 | asm | decaps | 193.85 | 197.85 | 3,877,008 | 620 | 89.9% | OK | - | OK |
| 40 | 2 | ref | msgcrypt | 94.25 | 98.25 | 1,884,939 | 91 | 98.5% | - | OK | OK |
| 41 | 2 | asm | msgcrypt | 38.58 | 42.58 | 771,656 | 68 | 98.9% | - | OK | OK |
| 42 | 1 | asm | keygen | 205.00 | 274.44 | 4,099,905 | 540 | 91.2% | - | - | OK |
| 43 | 1 | ref | encaps | 771.22 | 840.66 | 15,424,333 | 1090 | 82.3% | - | - | OK |
| 44 | 2 | asm | decaps | 1905.12 | 1909.12 | 38,102,352 | 310 | 95.0% | OK | - | OK |
| 45 | 1 | asm | msgcrypt | 38.45 | 42.45 | 769,088 | 68 | 98.9% | - | OK | OK |
| 46 | 1 | ref | keygen | 505.28 | 574.72 | 10,105,592 | 729 | 88.1% | - | - | OK |
| 47 | 2 | asm | msgcrypt | 38.48 | 42.48 | 769,493 | 68 | 98.9% | - | OK | OK |
| 48 | 1 | asm | encaps | 207.78 | 277.22 | 4,155,518 | 612 | 90.0% | - | - | OK |
| 49 | 1 | asm | msgcrypt | 49.23 | 53.23 | 984,550 | 68 | 98.9% | - | OK | OK |
| 50 | 1 | asm | msgcrypt | 49.23 | 53.23 | 984,582 | 68 | 98.9% | - | OK | OK |
| 51 | 1 | asm | encaps | 315.35 | 384.80 | 6,307,072 | 808 | 86.8% | - | - | OK |
| 52 | 1 | ref | keygen | 583.23 | 652.68 | 11,664,663 | 912 | 85.2% | - | - | OK |
| 53 | 1 | asm | msgcrypt | 38.47 | 42.47 | 769,453 | 68 | 98.9% | - | OK | OK |
| 54 | 1 | asm | encaps | 1494.45 | 1563.90 | 29,889,087 | 310 | 95.0% | - | - | OK |
| 55 | 1 | ref | msgcrypt | 93.97 | 97.97 | 1,879,446 | 91 | 98.5% | - | OK | OK |
| 56 | 1 | ref | encaps | 650.95 | 720.39 | 13,018,946 | 826 | 86.6% | - | - | OK |
| 57 | 1 | ref | keygen | 750.68 | 820.12 | 15,013,601 | 912 | 85.2% | - | - | OK |
| 58 | 2 | asm | decaps | 286.56 | 290.56 | 5,731,160 | 809 | 86.8% | OK | - | OK |
| 59 | 1 | asm | msgcrypt | 38.50 | 42.50 | 770,018 | 68 | 98.9% | - | OK | OK |
| 60 | 2 | ref | decaps | 704.10 | 708.10 | 14,082,054 | 1092 | 82.2% | OK | - | OK |
| 61 | 1 | ref | keygen | 392.88 | 462.33 | 7,857,671 | 729 | 88.1% | - | - | OK |
| 62 | 2 | ref | decaps | 610.52 | 614.52 | 12,210,469 | 837 | 86.4% | OK | - | OK |
| 63 | 1 | ref | keygen | 4452.20 | 4521.64 | 89,043,954 | 378 | 93.8% | - | - | OK |
| 64 | 2 | ref | encaps | 769.87 | 839.32 | 15,397,475 | 1090 | 82.3% | - | - | OK |
| 65 | 2 | asm | keygen | 1834.46 | 1903.90 | 36,689,162 | 280 | 95.4% | - | - | OK |
| 66 | 2 | asm | encaps | 267.35 | 336.80 | 5,347,048 | 612 | 90.0% | - | - | OK |
| 67 | 2 | ref | encaps | 3657.37 | 3726.82 | 73,147,417 | 418 | 93.2% | - | - | OK |
| 68 | 1 | ref | decaps | 702.27 | 706.27 | 14,045,366 | 1092 | 82.2% | OK | - | OK |
| 69 | 1 | asm | keygen | 238.98 | 308.42 | 4,779,566 | 676 | 89.0% | - | - | OK |
| 70 | 1 | ref | decaps | 4652.93 | 4656.93 | 93,058,607 | 418 | 93.2% | OK | - | OK |
| 71 | 2 | ref | keygen | 503.65 | 573.10 | 10,073,074 | 729 | 88.1% | - | - | OK |
| 72 | 1 | ref | encaps | 4665.91 | 4735.35 | 93,318,181 | 418 | 93.2% | - | - | OK |
| 73 | 2 | ref | decaps | 480.82 | 484.82 | 9,616,427 | 837 | 86.4% | OK | - | OK |
| 74 | 2 | ref | msgcrypt | 93.88 | 97.88 | 1,877,624 | 91 | 98.5% | - | OK | OK |
| 75 | 2 | ref | keygen | 750.92 | 820.36 | 15,018,384 | 912 | 85.2% | - | - | OK |
| 76 | 2 | asm | msgcrypt | 38.59 | 42.59 | 771,758 | 68 | 98.9% | - | OK | OK |
| 77 | 2 | ref | msgcrypt | 120.14 | 124.14 | 2,402,822 | 91 | 98.5% | - | OK | OK |
| 78 | 1 | asm | keygen | 1431.09 | 1500.54 | 28,621,814 | 280 | 95.4% | - | - | OK |
| 79 | 2 | ref | decaps | 896.20 | 900.20 | 17,924,012 | 1092 | 82.2% | OK | - | OK |
| 80 | 2 | ref | encaps | 989.88 | 1059.32 | 19,797,558 | 1090 | 82.3% | - | - | OK |
| 81 | 2 | ref | decaps | 3660.07 | 3664.07 | 73,201,354 | 418 | 93.2% | OK | - | OK |
| 82 | 2 | ref | decaps | 4663.88 | 4667.88 | 93,277,639 | 418 | 93.2% | OK | - | OK |
| 83 | 1 | asm | decaps | 287.23 | 291.23 | 5,744,683 | 809 | 86.8% | OK | - | OK |
| 84 | 1 | ref | msgcrypt | 94.38 | 98.38 | 1,887,686 | 91 | 98.5% | - | OK | OK |
| 85 | 2 | asm | encaps | 1904.13 | 1973.58 | 38,082,644 | 310 | 95.0% | - | - | OK |
| 86 | 2 | asm | encaps | 401.50 | 470.94 | 8,029,920 | 808 | 86.8% | - | - | OK |
| 87 | 2 | asm | decaps | 1483.32 | 1487.32 | 29,666,399 | 310 | 95.0% | OK | - | OK |
| 88 | 1 | ref | msgcrypt | 94.36 | 98.36 | 1,887,185 | 91 | 98.5% | - | OK | OK |
| 89 | 2 | asm | decaps | 367.71 | 371.71 | 7,354,304 | 809 | 86.8% | OK | - | OK |
| 90 | 2 | ref | keygen | 585.51 | 654.96 | 11,710,211 | 912 | 85.2% | - | - | OK |
| 91 | 1 | ref | decaps | 899.25 | 903.25 | 17,984,999 | 1092 | 82.2% | OK | - | OK |
| 92 | 2 | ref | msgcrypt | 120.95 | 124.95 | 2,419,025 | 91 | 98.5% | - | OK | OK |
| 93 | 2 | asm | encaps | 209.52 | 278.96 | 4,190,389 | 612 | 90.0% | - | - | OK |
| 94 | 2 | asm | encaps | 315.10 | 384.55 | 6,302,085 | 808 | 86.8% | - | - | OK |
| 95 | 1 | asm | msgcrypt | 49.22 | 53.22 | 984,407 | 68 | 98.9% | - | OK | OK |
| 96 | 2 | ref | keygen | 3509.45 | 3578.89 | 70,188,923 | 378 | 93.8% | - | - | OK |

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
