#!/usr/bin/env python3
"""catalog.py — Classify every folder under data/experiments by provenance.

Evidence-based (does not trust the folder name; e.g. a folder tagged
"complete_simulation_matrix" may actually hold bench telemetry):
  - bench : raw/telemetry_*.json exists (only trigger.py on the real board writes it)
  - bench_legacy : report.md says `bench` but only runs.csv survived (early runs)
  - sim   : report.md says "Execution Mode: `sim`" and there is no telemetry
            (a runs.csv without report/telemetry is also treated as sim)
  - empty : nothing usable (aborted before any observation)

Writes data/experiments/catalog.csv. Nothing is deleted.

Usage:
  python src/analysis/catalog.py [--root data/experiments]
"""
import argparse, csv, glob, json, os, re


def classify(exp_dir):
    tel = sorted(glob.glob(os.path.join(exp_dir, "raw", "telemetry_*.json")))
    report = os.path.join(exp_dir, "report.md")
    mode = None
    if os.path.exists(report):
        m = re.search(r"Execution Mode:\*\*\s*`(\w+)`", open(report, encoding="utf-8").read())
        mode = m.group(1) if m else None
    n_obs = sum(len(json.load(open(f))) for f in tel)
    runs = os.path.join(exp_dir, "raw", "runs.csv")
    n_runs = sum(1 for _ in open(runs)) - 1 if os.path.exists(runs) else 0
    if tel:
        source = "bench"
    elif mode == "bench" and n_runs:
        # Early bench runs: only runs.csv survived (no raw telemetry JSON).
        source, n_obs = "bench_legacy", n_runs
    elif mode == "sim" or (mode is None and n_runs):
        source, n_obs = "sim", n_runs
    else:
        source = "empty"
    return {
        "experiment": os.path.basename(exp_dir),
        "source": source,
        "n_observations": n_obs,
        "telemetry_files": len(tel),
        "has_report": os.path.exists(report),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="data/experiments")
    args = ap.parse_args()
    rows = [classify(d) for d in sorted(glob.glob(os.path.join(args.root, "exp_*"))) if os.path.isdir(d)]
    out = os.path.join(args.root, "catalog.csv")
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    for s in ("bench", "bench_legacy", "sim", "empty"):
        print(f"{s:6s}: {sum(r['source'] == s for r in rows)} experiments")
    print(f"-> {out}")


if __name__ == "__main__":
    main()
