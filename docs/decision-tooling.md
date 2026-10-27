---
created: 2026-10-27
status: decision record
---

# Decision: Omnibenchmark and pyDOE3

Evaluation of whether to adopt **Omnibenchmark** (orchestration) and/or
**pyDOE3** (design of experiments) in the CMP223 project.

TL;DR:
- **pyDOE3 — adopt (low effort, real gain).**
- **Omnibenchmark — do not adopt now (overkill; revisit only if the project grows).**

---

## Context (what the project actually needs)

- Factor matrix: 3 algorithms x 2 variants x 3 clocks x 2 optimizations
  = **36 combinations** x 3 operations x 30 iterations.
- Current DoE: `itertools.product` + `random.shuffle(seed=42)` in the `Snakefile`.
- Scale: **single bench, single researcher, one-semester** project.
- Committed stack: Snakemake + Python (already in `flake.nix`).

The hard parts of this project are physical (shunt calibration, GPIO window,
oscilloscope capture) and the SRAM/Flash fit — not workflow orchestration.

---

## pyDOE3 — ADOPT

BSD-3, actively maintained (Production/Stable, release Jan 2026), pure Python,
already compatible with the existing stack.

### Why it helps

The current factor generation is a manual cartesian product + shuffle. That
works, but:
- It gives no statistical structure beyond "run everything in random order".
- If the full matrix (36 combos x 30 = 1080 runs x 3 ops) becomes too long on
  the bench, there is no principled way to **reduce** it.

pyDOE3 addresses both:
- `fullfact([3,2,3,2])` generates the full factorial design explicitly, as data
  (easy to export to CSV, cite, and attach to the paper as the experiment plan).
- If the bench time is too long, `fracfact` / Plackett-Burman give a
  **statistically justified fractional design** instead of an ad-hoc cut.
- Makes the DoE a **named, citable method** in the article ("full factorial
  design generated with pyDOE3"), which strengthens the methodology section.

### Cost

Minimal: add `pyDOE3` to the Python packages in `flake.nix`, and replace the
`itertools.product` block in the `Snakefile` with a small helper that builds the
design (and optionally writes `data/design.csv`). The randomized execution order
stays (still valuable for the thermal/ordering confound).

### Caveat

pyDOE3 numbers factor **levels** (0,1,2...). We still map those indices back to
the string labels (`kyber512`, `-Os`, ...). It is a thin mapping layer, not a
rewrite.

---

## Omnibenchmark — DO NOT ADOPT (now)

Built on Snakemake; adds declarative YAML benchmark plans, dynamic workflow
generation, S3-compatible storage and Conda/Apptainer environments.

### Why not now

- **It solves problems we do not have.** Its value is in *collaborative,
  multi-method, multi-dataset* benchmarks with shared storage and community
  contributions. This is a single-bench, single-author course project.
- **Redundant with what we already have.** Reproducible environments are already
  covered by the Nix `flake.nix`; orchestration by the existing `Snakefile`;
  provenance by vendoring with pinned commits + git hashes.
- **The bottleneck is physical, not orchestration.** No orchestration framework
  helps with shunt calibration, the GPIO measurement window, or the 6 KB SRAM
  fit. Adding it now is effort spent away from the real risks.
- **Extra moving parts** (S3, environment modules/Apptainer) increase setup and
  failure surface for no concrete benefit at this scale.

### When to revisit

Adopt Omnibenchmark only if the project later becomes a **shared, extensible
benchmark** (e.g. other students/labs contributing algorithms, or publishing a
reusable PQC-on-AVR benchmark suite). At that point its plan syntax and storage
model pay off.

---

## Recommendation

1. **Now:** add pyDOE3 and refactor the factor generation in the `Snakefile`
   (keep the randomized order). Export `data/design.csv` as the experiment plan.
2. **Keep:** Snakemake + Nix + pinned vendoring (already the right choice).
3. **Later / optional:** reconsider Omnibenchmark only if the scope shifts to a
   shared, community benchmark.

Full citations in `docs/references.md`.
