# src — Source code

Experiment code: firmware for the SUT (Arduino Nano Every / ATmega4809), PQC
algorithm ports, and the instrumentation, collection and data-processing
scripts.

## Layout

```
src/
├── firmware/            # embedded code
│   ├── main.c           # measurement harness (state machine)
│   ├── kem.h            # algorithm-agnostic KEM interface
│   ├── kem_kyber512.c   # Kyber-512 adapter  -> kem.h
│   ├── kem_ctru.c       # CTRU-Light adapter -> kem.h
│   ├── kem_ecdh.c       # ECDH adapter (baseline) -> kem.h
│   ├── Makefile         # AVR cross build, parameterized by ALG x VARIANT
│   └── pqc/<alg>/<var>/ # vendored sources: <alg> in {kyber512,ctru-light,ecdh}
│                        #                    <var> in {ref, asm}
├── scripts/
│   └── vendor-pqc.sh    # vendors the 3 algorithms (ref + asm)
├── measure/             # oscilloscope / logic-analyzer capture [TODO]
└── analysis/            # Snakemake + Python (parser, statistics)
```

## The 6 binaries (3 algorithms x 2 variants)

Each combination is a distinct binary, **built, flashed and measured
separately**:

| ALG          | VARIANT=ref        | VARIANT=asm                 |
|--------------|--------------------|-----------------------------|
| `kyber512`   | reference C        | Montgomery + AVR assembly   |
| `ctru-light` | reference C        | Kred-ascon + AVR assembly   |
| `ecdh`       | micro-ecc C        | micro-ecc + AVR assembly    |

`ref` = portability / implementation baseline; `asm` = assembly-optimized
version (a first-class factor in the experiment).

## Build

Prerequisite: the Nix environment (see `flake.nix` at the repo root).

```bash
nix develop                                   # devShell (avr-gcc, avrdude, snakemake...)

src/scripts/vendor-pqc.sh all                 # 1. vendor the 3 algorithms (ref+asm)

# 2. build one combination (ALG x VARIANT x OPT x F_CPU):
make -C src/firmware ALG=kyber512 VARIANT=asm OPT=-O3 F_CPU=20000000UL
make -C src/firmware ALG=kyber512 VARIANT=asm size      # Flash/SRAM usage
make -C src/firmware ALG=ctru-light VARIANT=ref         # reference C
make -C src/firmware flash PORT=/dev/ttyACM0            # program via UPDI
```

## Sources

- **Kyber-512 and CTRU-Light** (ref + **AVR assembly**): CHES 2026 artifact
  [`whYBeKim/CTRU-Light-and-PQC-on-AVR`](https://github.com/whYBeKim/CTRU-Light-and-PQC-on-AVR)
  (MIT), benchmarked on ATmega4808/1284p — very close to our ATmega4809.
- **ECDH** (classical baseline): [micro-ecc](https://github.com/kmackay/micro-ecc),
  with built-in AVR assembly routines.

No algorithm is reimplemented by hand. `vendor-pqc.sh` pins the commits and
writes a `VENDOR.txt` in each folder for reproducibility.

> **Flash caveat:** Kyber-512 in reference C takes ~79 KB — it does not fit in
> the ATmega4809's 48 KB of Flash. The asm variant (~22 KB) fits. Confirm with
> `make size` right after vendoring.

## Target metrics

- Energy per operation (keygen, encaps, decaps)
- Stack usage (0xAA watermarking -> `RAMEND - lowest_address`)
- Execution time / cycles (GPIO window measured by the logic analyzer)
- Generated binary size (`avr-size`)
- System operating headroom (Flash/SRAM)

SUT details, metrics and plan in `../docs/plan.md` and `../docs/roadmap.md`.
