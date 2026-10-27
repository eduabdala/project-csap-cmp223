# References

Consolidated external references for the CMP223 project. Grouped by topic.
Content was rephrased for compliance with licensing restrictions.

## Experiment management & reproducible benchmarking

- **Omnibenchmark** — reproducible, extensible orchestration of benchmarks,
  built on top of Snakemake (declarative YAML plan, dynamic workflow generation,
  S3-compatible storage, Conda/Apptainer environments).
  <https://arxiv.org/pdf/2409.17038v3>
- **Experiments as Code** — paradigm of versioning the whole experiment
  (provisioning/execution/analysis code), for auditability and reproducibility.
  <https://arxiv.org/pdf/2202.12050>
- **Does Systems Research Measure Up?** — guidelines for structuring systems
  experiments so results are comparable across researchers.
  <https://www.researchgate.net/publication/2828591_Does_Systems_Research_Measure_Up>

## Design of Experiments (DoE)

- **pyDOE3** — DoE package for Python (BSD-3, actively maintained). Provides
  general full-factorial (`fullfact`), fractional factorial, Plackett-Burman,
  Latin-Hypercube, Taguchi, etc. Candidate to generate the factor matrix.
  <https://pypi.org/project/pyDOE3/> · <https://github.com/relf/pyDOE3>
- **Current State and Prospects of R-Packages for the Design of Experiments**
  (R Journal, 2024) — survey of R DoE packages (`DoE.base`, `FrF2`, ...).
  <https://journal.r-project.org/articles/RJ-2024-013/>
- **ADEMP framework** (Morris et al. 2019) — methodology for statistical
  benchmark studies (Aims, Data-generating, Estimands, Methods, Performance),
  with R/tidyverse implementations.
  <https://skillsmp.com/ja/creators/slds-lmu/ai-scaffolding/skills-setup-benchmark>

## Energy / power measurement on microcontrollers

- **An Open-Source Power Measurement Platform for System-Level Semiconductor
  Testing** (Univ. Stuttgart / Advantest, 2026) — Raspberry Pi controller +
  precision current measurement + MCU DUT, with automated firmware deployment,
  synchronized execution and high-resolution current acquisition across firmware
  variants. Closely matches this project's bench.
  <https://arxiv.org/html/2608.05888>
- **BEEBS** (Embecosm) — benchmark suite for measuring energy on embedded
  systems with no OS / no output stream.
  <https://github.com/embecosm/riscv-beebs>
- **InstMeter** — instruction/clock-cycle-level predictor of energy and latency
  for inference on MCUs.
  <https://arxiv.org/pdf/2603.04134>

## Post-quantum crypto on AVR (project sources)

- **CTRU-Light-and-PQC-on-AVR** (CHES 2026 artifact, MIT) — CTRU-Light, Kyber
  and Saber in reference C and optimized AVR assembly; benchmarked on
  ATmega4808/1284p. Source for the `kyber512` and `ctru-light` ports.
  <https://github.com/whYBeKim/CTRU-Light-and-PQC-on-AVR>
- **Highly Efficient and Light NTRU-Based KEMs with Small Moduli** (MDPI
  Mathematics 13-21-3388) — CTRU-Light scheme (pk/ct = 1206 bytes).
  <https://www.mdpi.com/2227-7390/13/21/3388>
- **Lightweight PQ KEM and Hybrid MQTT Protocol for 8-bit AVR Sensor Nodes**
  (IACR ePrint 2026/248) — the CTRU-Light paper.
  <https://eprint.iacr.org/2026/248>
- **PQClean** — clean, portable, tested PQC reference implementations
  (alternative source for Kyber). <https://github.com/PQClean/PQClean>
- **micro-ecc (uECC)** — small, portable ECDH/ECDSA for microcontrollers, with
  AVR assembly routines. Source for the ECDH baseline.
  <https://github.com/kmackay/micro-ecc>

## Tooling

- **Snakemake** — workflow management system (current pipeline orchestrator).
  <https://snakemake.readthedocs.io>
- **sigrok / sigrok-cli** — logic analyzer capture.
  <https://sigrok.org>
