#!/usr/bin/env python3
"""pipeline.py — Master orchestrator for experimental workflows (CMP223).

Coordinates the complete end-to-end experimental pipeline following Raj Jain's
methodology (system goals -> DoE factor design -> automated execution -> 
statistical aggregation -> publication figures).

Stages:
  1. design   : Generate factor combination matrix (full or fractional factorial).
  2. exp0     : Execute Experiment 0 (baseline calibration, randomized replications).
  3. hist     : Generate empirical distribution histograms (Freedman-Diaconis + 95% CI).
  4. exp1     : Generate Experiment 1 (full factorial 2^k / multi-factor matrix).
  5. report   : Compile summary tables and LaTeX/Markdown report.
  6. all      : Run all stages sequentially.

Usage:
  python3 src/analysis/pipeline.py all
  python3 src/analysis/pipeline.py exp0 --iterations 30 --seed 42
  python3 src/analysis/pipeline.py exp1 --mode sim
"""

import argparse
import os
import subprocess
import sys

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPTS_DIR, "../.."))

def run_step(cmd, desc):
    print(f"\n{'='*75}")
    print(f">> [PIPELINE] {desc}")
    print(f">> Command: {' '.join(cmd)}")
    print(f"{'='*75}")
    res = subprocess.run(cmd, cwd=PROJECT_ROOT)
    if res.returncode != 0:
        print(f"!! Error executing: {desc} (Exit code {res.returncode})", file=sys.stderr)
        sys.exit(res.returncode)

def stage_design():
    run_step(
        [sys.executable, "src/analysis/design.py",
         "--config", "src/analysis/config.yaml",
         "--out", "data/processed/design.csv"],
        "Stage 1: Generate Factor Matrix (Design of Experiments)"
    )

def stage_exp0(iterations=30, seed=42, mode="sim"):
    run_step(
        [sys.executable, "src/analysis/experiment_zero.py",
         "--config", "src/analysis/config.yaml",
         "--mode", mode,
         "--iterations", str(iterations),
         "--seed", str(seed),
         "--out-raw", "data/raw/exp0_raw_runs.csv",
         "--out-summary", "data/processed/exp0_summary.csv"],
        f"Stage 2: Run Experiment 0 (N={iterations}, seed={seed}, mode={mode})"
    )

def stage_hist():
    run_step(
        [sys.executable, "src/analysis/plot_histogram.py",
         "--in", "data/raw/exp0_raw_runs.csv",
         "--out", "data/processed/figures/exp0_histogram"],
        "Stage 3: Generate Empirical Distribution Histogram (Freedman-Diaconis + 95% CI)"
    )

def stage_exp1(mode="sim", seed=42):
    run_step(
        [sys.executable, "src/analysis/experiment_one.py",
         "--config", "src/analysis/config.yaml",
         "--mode", mode,
         "--seed", str(seed),
         "--out-summary", "data/processed/summary_table.csv"],
        "Stage 4: Run Experiment 1 (Factorial Matrix Evaluation)"
    )
    run_step(
        [sys.executable, "src/analysis/figures.py",
         "--in", "data/processed/summary_table.csv",
         "--out", "data/processed/figures/trade_off.pdf"],
        "Stage 5: Generate Trade-off Figures (Energy vs. SRAM Peak)"
    )

def main():
    ap = argparse.ArgumentParser(description="Master Experimental Pipeline Orchestrator")
    ap.add_argument("stage", choices=["all", "design", "exp0", "hist", "exp1"],
                    default="all", nargs="?", help="Pipeline stage to execute (default: all)")
    ap.add_argument("--mode", choices=["sim", "bench"], default="sim",
                    help="Execution mode (sim for emulation, bench for hardware board)")
    ap.add_argument("--iterations", type=int, default=30, help="Replication count N (default: 30)")
    ap.add_argument("--seed", type=int, default=42, help="PRNG seed for randomized trial schedules")
    args = ap.parse_args()

    if args.stage in ("all", "design"):
        stage_design()
    if args.stage in ("all", "exp0"):
        stage_exp0(iterations=args.iterations, seed=args.seed, mode=args.mode)
    if args.stage in ("all", "hist"):
        stage_hist()
    if args.stage in ("all", "exp1"):
        stage_exp1(mode=args.mode, seed=args.seed)

    print(f"\n{'='*75}")
    print(">> [PIPELINE COMPLETED SUCCESSFULLY]")
    print(">> Generated artifacts:")
    print("   - Factor design:    data/processed/design.csv")
    print("   - Exp 0 Raw:        data/raw/exp0_raw_runs.csv")
    print("   - Exp 0 Summary:    data/processed/exp0_summary.csv")
    print("   - Exp 0 Histogram:  data/processed/figures/exp0_histogram.png & .pdf")
    print("   - Exp 1 Summary:    data/processed/summary_table.csv")
    print("   - Exp 1 Trade-off:  data/processed/figures/trade_off.pdf")
    print(f"{'='*75}\n")

if __name__ == "__main__":
    main()

