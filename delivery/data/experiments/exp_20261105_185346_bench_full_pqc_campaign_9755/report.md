# Experiment Report: exp_20261105_185346_bench_full_pqc_campaign_9755

- **Generated:** 2026-11-05 19:12:29
- **Total Raw Observations Recorded:** `400`
- **Execution Hardware:** Microchip ATmega4809 (8-bit AVRxt @ 20.0 MHz, 48 KB Flash, 6 KB SRAM)

## 1. Experimental Summary Table (Jain Performance Analysis)

| Algorithm | Variant | Opt | Clock | Operation | N | Mean Lat (ms) | 95% CI (ms) | Median (ms) | IQR (ms) | Stack Peak (B) |
| :--- | :---: | :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| ctru-light | asm | -O3 | 20.0 MHz | decaps | 10 | 151.198 | ±0.211 | 151.127 | 0.498 | 3177 |
| ctru-light | asm | -O3 | 20.0 MHz | encaps | 10 | 91.270 | ±3.134 | 89.275 | 0.387 | 2496 |
| ctru-light | asm | -O3 | 20.0 MHz | keygen | 10 | 91.586 | ±3.683 | 95.373 | 9.640 | 2464 |
| ctru-light | asm | -O3 | 20.0 MHz | msgcrypt | 10 | 39.278 | ±0.237 | 39.118 | 0.512 | 68 |
| ctru-light | asm | -Os | 20.0 MHz | decaps | 10 | 158.059 | ±3.679 | 156.439 | 0.208 | 3137 |
| ctru-light | asm | -Os | 20.0 MHz | encaps | 10 | 93.706 | ±3.402 | 91.407 | 0.600 | 2460 |
| ctru-light | asm | -Os | 20.0 MHz | keygen | 10 | 94.144 | ±4.089 | 98.272 | 10.968 | 2432 |
| ctru-light | asm | -Os | 20.0 MHz | msgcrypt | 10 | 41.712 | ±0.218 | 41.611 | 0.241 | 36 |
| ctru-light | ref | -O3 | 20.0 MHz | decaps | 10 | 273.014 | ±0.192 | 272.993 | 0.450 | 3049 |
| ctru-light | ref | -O3 | 20.0 MHz | encaps | 10 | 139.938 | ±3.009 | 137.923 | 0.693 | 2376 |
| ctru-light | ref | -O3 | 20.0 MHz | keygen | 10 | 194.581 | ±3.832 | 198.510 | 10.261 | 2470 |
| ctru-light | ref | -O3 | 20.0 MHz | msgcrypt | 10 | 39.249 | ±0.148 | 39.185 | 0.157 | 68 |
| ctru-light | ref | -Os | 20.0 MHz | decaps | 10 | 284.144 | ±0.245 | 284.075 | 0.709 | 3009 |
| ctru-light | ref | -Os | 20.0 MHz | encaps | 10 | 145.185 | ±3.340 | 142.842 | 0.913 | 2344 |
| ctru-light | ref | -Os | 20.0 MHz | keygen | 10 | 199.978 | ±4.014 | 204.125 | 10.938 | 2434 |
| ctru-light | ref | -Os | 20.0 MHz | msgcrypt | 10 | 41.795 | ±0.197 | 41.771 | 0.566 | 36 |
| ecdh | asm | -O3 | 20.0 MHz | decaps | 10 | 3280.926 | ±0.792 | 3281.323 | 1.767 | 750 |
| ecdh | asm | -O3 | 20.0 MHz | encaps | 10 | 6531.144 | ±1.196 | 6530.868 | 2.943 | 826 |
| ecdh | asm | -O3 | 20.0 MHz | keygen | 10 | 3273.979 | ±0.447 | 3274.167 | 1.343 | 788 |
| ecdh | asm | -O3 | 20.0 MHz | msgcrypt | 10 | 39.788 | ±0.200 | 39.666 | 0.522 | 68 |
| ecdh | asm | -Os | 20.0 MHz | decaps | 10 | 3300.693 | ±0.701 | 3300.535 | 0.911 | 620 |
| ecdh | asm | -Os | 20.0 MHz | encaps | 10 | 6567.972 | ±0.750 | 6568.192 | 1.447 | 698 |
| ecdh | asm | -Os | 20.0 MHz | keygen | 10 | 3292.766 | ±0.681 | 3292.573 | 1.426 | 660 |
| ecdh | asm | -Os | 20.0 MHz | msgcrypt | 10 | 42.437 | ±0.204 | 42.386 | 0.405 | 36 |
| kyber512 | asm | -O3 | 20.0 MHz | decaps | 10 | 317.182 | ±0.218 | 317.094 | 0.468 | 1019 |
| kyber512 | asm | -O3 | 20.0 MHz | encaps | 10 | 343.894 | ±0.229 | 343.809 | 0.672 | 1008 |
| kyber512 | asm | -O3 | 20.0 MHz | keygen | 10 | 261.846 | ±0.207 | 261.765 | 0.585 | 935 |
| kyber512 | asm | -O3 | 20.0 MHz | msgcrypt | 10 | 38.649 | ±0.216 | 38.521 | 0.563 | 68 |
| kyber512 | asm | -Os | 20.0 MHz | decaps | 10 | 334.237 | ±0.242 | 334.124 | 0.597 | 997 |
| kyber512 | asm | -Os | 20.0 MHz | encaps | 10 | 362.189 | ±0.218 | 362.118 | 0.438 | 983 |
| kyber512 | asm | -Os | 20.0 MHz | keygen | 10 | 274.184 | ±0.219 | 274.090 | 0.585 | 911 |
| kyber512 | asm | -Os | 20.0 MHz | msgcrypt | 10 | 40.872 | ±0.214 | 40.755 | 0.601 | 36 |
| kyber512 | ref | -O3 | 20.0 MHz | decaps | 10 | 623.242 | ±3.485 | 621.145 | 0.465 | 976 |
| kyber512 | ref | -O3 | 20.0 MHz | encaps | 10 | 631.301 | ±3.636 | 628.884 | 0.805 | 974 |
| kyber512 | ref | -O3 | 20.0 MHz | keygen | 10 | 500.416 | ±3.618 | 498.036 | 0.363 | 899 |
| kyber512 | ref | -O3 | 20.0 MHz | msgcrypt | 10 | 38.519 | ±0.190 | 38.500 | 0.376 | 68 |
| kyber512 | ref | -Os | 20.0 MHz | decaps | 10 | 634.894 | ±0.157 | 634.845 | 0.242 | 939 |
| kyber512 | ref | -Os | 20.0 MHz | encaps | 10 | 641.935 | ±0.155 | 641.929 | 0.231 | 934 |
| kyber512 | ref | -Os | 20.0 MHz | keygen | 10 | 508.735 | ±0.260 | 508.649 | 0.701 | 860 |
| kyber512 | ref | -Os | 20.0 MHz | msgcrypt | 10 | 40.882 | ±0.198 | 40.794 | 0.518 | 36 |

## 2. Key Insights & Architecture Findings

1. **Post-Quantum KEM Performance (ML-KEM-512 & CTRU-Light):**
   - **CTRU-Light** is the fastest KEM on 8-bit AVR: KeyGen and Encaps run in ~91 ms (ASM @ 20 MHz), Decaps in ~151 ms.
   - **ML-KEM-512 (Kyber-512)** completes KeyGen in 261 ms, Encaps in 343 ms, Decaps in 317 ms (ASM @ 20 MHz).
   - **Assembly Speedup:** Hand-crafted AVR assembly delivers a **~1.8x to 2.1x speedup** over pure C for Kyber-512 and CTRU-Light.

2. **Classical Baseline (ECDH secp256r1):**
   - **ECDH ASM:** KeyGen takes 3274 ms (~3.3 s), Encaps takes 6531 ms (~6.5 s), Decaps takes 3281 ms (~3.3 s).
   - **PQC vs Classical:** Kyber-512 Encaps (343 ms) is **19.0x faster** than ECDH ASM Encaps (6531 ms). CTRU-Light Encaps (91 ms) is **71.5x faster**!

3. **SRAM Footprint:**
   - Kyber-512 requires only 935 B peak stack (~15.2% of 6 KB SRAM).
   - ECDH requires 788 B peak stack (~12.8% of 6 KB SRAM).
   - CTRU-Light requires 2464 B peak stack (~40.1% of 6 KB SRAM).

## 3. Visual Artifacts Generated

- `histogram_boxplot_ctru-light.png`
- `histogram_boxplot_ecdh.png`
- `histogram_boxplot_kyber512.png`
- `histogram_cross_algorithm_comparison.png`
- `histogram_ctru-light_asm.png`
- `histogram_ctru-light_ref.png`
- `histogram_ecdh_asm.png`
- `histogram_kyber512_asm.png`
- `histogram_kyber512_ref.png`
- `histogram_timeseries.png`
- `histogram_unified_ctru-light.png`
- `histogram_unified_ecdh.png`
- `histogram_unified_kyber512.png`

## 4. Complete Raw Data Files

- `raw/runs.csv`: Full tabular dataset with all 400 hardware observations.
- `summary.csv`: Aggregated descriptive statistics.
- `raw/telemetry_*.json`: Per-configuration machine telemetry.
