#!/usr/bin/env python3
"""run_experiment.py — Automated end-to-end experiment executor (CMP223).

Adheres to Raj Jain's "The Art of Computer Systems Performance Analysis":
  - Ch. 11.4: Randomization of execution sequence to prevent systematic error & thermal drift.
  - Ch. 12 & 13: Full factorial design (Algorithms x Variants x Clocks x Optimizations).
  - Ch. 10: High data-ink, zero-baseline, Freedman-Diaconis empirical distribution histograms.

Workflow for each generated experiment:
  1. Generates a self-contained folder under `data/experiments/exp_<timestamp>_<id>/`.
  2. Creates a randomized execution plan using the specified seed.
  3. Iterates through combinations:
       a. Builds the target firmware (avr-gcc / make) for the combination factors.
       b. Flashes the MCU (/dev/ttyACM0 via avrdude UPDI) if in hardware mode.
       c. Triggers measurement & telemetry collection (trigger.py / serial).
       d. Saves raw logs and trial CSVs into the experiment folder.
  4. Computes descriptive statistics (Mean, Median, Std Dev, 95% CI, IQR).
  5. Renders publication-ready Freedman-Diaconis distribution histograms and trade-off plots.
  6. Emits a structured Markdown report (`report.md`) documenting all parameters and findings.

Usage:
  # Dry-run / Simulation mode (deterministic physical emulation when bench is offline):
  python3 src/analysis/run_experiment.py --mode sim --seed 42 -n 30

  # Hardware bench mode (flashes ATmega4809 and triggers physical logic analyzer):
  python3 src/analysis/run_experiment.py --mode bench --port /dev/ttyACM0 --seed 42 -n 30
"""

import argparse
import csv
import datetime
import json
import math
import os
import random
import subprocess
import sys
import time
import yaml

# Statistical critical values for Student's t (two-sided, 95% confidence)
T_CRIT_95 = {
    1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571,
    6: 2.447,  7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
    15: 2.131, 20: 2.086, 25: 2.060, 29: 2.045, 30: 2.042,
    40: 2.021, 50: 2.009, 60: 2.000, 100: 1.984, 1000: 1.962
}

def get_t_crit(df):
    for k in sorted(T_CRIT_95.keys(), reverse=True):
        if df >= k:
            return T_CRIT_95[k]
    return 12.706

# Physical baseline profiles on 8-bit ATmega4809 (20 MHz, -O3, asm)
ALGO_PROFILES = {
    "kyber512": {
        "keygen":   {"cycles": 4778000, "stack": 676, "i_ma": 10.2},
        "encaps":   {"cycles": 6283467, "stack": 808, "i_ma": 10.3},
        "decaps":   {"cycles": 5736867, "stack": 809, "i_ma": 10.25},
        "msgcrypt": {"cycles": 768400,  "stack": 68,  "i_ma": 10.15},
    },
    "ctru-light": {
        "keygen":   {"cycles": 3210000, "stack": 540, "i_ma": 10.1},
        "encaps":   {"cycles": 4150000, "stack": 612, "i_ma": 10.15},
        "decaps":   {"cycles": 3890000, "stack": 620, "i_ma": 10.12},
        "msgcrypt": {"cycles": 768400,  "stack": 68,  "i_ma": 10.15},
    },
    "ecdh": {
        "keygen":   {"cycles": 28500000, "stack": 280, "i_ma": 9.9},
        "encaps":   {"cycles": 29800000, "stack": 310, "i_ma": 9.92},
        "decaps":   {"cycles": 29800000, "stack": 310, "i_ma": 9.92},
        "msgcrypt": {"cycles": 768400,   "stack": 68,  "i_ma": 10.15},
    }
}

VARIANT_MULTIPLIER = {"asm": 1.0, "ref": 2.45}
OPT_MULTIPLIER = {"-O3": 1.0, "-Os": 1.28, "O3": 1.0, "Os": 1.28}

def generate_experiment_dir(base_dir="data/experiments", tag=""):
    now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    rnd_suffix = f"{random.randint(1000, 9999)}"
    dir_name = f"exp_{now_str}_{tag}_{rnd_suffix}" if tag else f"exp_{now_str}_{rnd_suffix}"
    exp_dir = os.path.join(base_dir, dir_name)
    os.makedirs(os.path.join(exp_dir, "raw"), exist_ok=True)
    os.makedirs(os.path.join(exp_dir, "figures"), exist_ok=True)
    os.makedirs(os.path.join(exp_dir, "bin"), exist_ok=True)
    return exp_dir

def build_firmware(alg, variant, opt, clock_mhz, exp_dir):
    """Build the target firmware using the AVR Makefile."""
    fcpu = f"{int(clock_mhz * 1e6)}UL"
    cmd = [
        "make", "-C", "src/firmware/atmega4809",
        "clean", "all", "size",
        f"ALG={alg}",
        f"VARIANT={variant}",
        f"OPT={opt}",
        f"F_CPU={fcpu}"
    ]
    print(f">> [BUILD] Compiling firmware: ALG={alg} VARIANT={variant} OPT={opt} F_CPU={fcpu}")
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print(f"!! Build failed:\n{res.stderr}", file=sys.stderr)
        return False, None
    
    # Copy build artifacts to experiment folder
    hex_src = f"src/firmware/atmega4809/build/firmware-{alg}-{variant}.hex"
    hex_dst = os.path.join(exp_dir, "bin", f"firmware-{alg}-{variant}-{clock_mhz}MHz-{opt.lstrip('-')}.hex")
    if os.path.exists(hex_src):
        import shutil
        shutil.copyfile(hex_src, hex_dst)
    return True, hex_dst

def flash_firmware(hex_path, port="/dev/ttyACM0", max_retries=3):
    """Flash firmware to ATmega4809 using avrdude over jtag2updi with 1200bps touch and timeout."""
    print(f">> [FLASH] Programming {hex_path} to {port} via avrdude (1200 bps touch)...")
    for attempt in range(1, max_retries + 1):
        time.sleep(0.5)
        touch_cmd = f"stty -F {port} 1200 hupcl && sleep 0.5"
        subprocess.run(touch_cmd, shell=True)
        flash_cmd = [
            "avrdude", "-c", "jtag2updi", "-p", "atmega4809",
            "-P", port, "-b", "115200", "-e", "-D",
            "-U", "fuse2:w:0x02:m",
            "-U", f"flash:w:{hex_path}:i"
        ]
        try:
            res = subprocess.run(flash_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60)
            if res.returncode == 0:
                print(f">> [FLASH] Flashed successfully on attempt {attempt}.")
                time.sleep(1.0)
                return True
            else:
                print(f"!! Flash attempt {attempt} failed: {res.stderr.strip()}", file=sys.stderr)
        except subprocess.TimeoutExpired:
            print(f"!! Flash attempt {attempt} timed out after 60s", file=sys.stderr)
        time.sleep(1.0)
    return False

def run_hardware_collection(port, repeats, exp_dir, combo, use_la=False):
    """Call trigger.py to execute battery BM and record timing and telemetry from the board."""
    prefix = f"{combo['alg']}_{combo['variant']}_{combo['opt'].lstrip('-')}_{int(combo['clock_mhz'])}MHz"
    json_path = os.path.join(exp_dir, "raw", f"telemetry_{prefix}.json")
    log_path = os.path.join(exp_dir, "raw", f"console_{prefix}.log")
    la_csv = os.path.join(exp_dir, "raw", f"la_{prefix}.csv")

    # Dynamic timeout: ECDH pure C requires ~14s for Encaps (2x 256-bit scalar mult on 8-bit AVR)
    timeout_sec = 35.0 if (combo["alg"] == "ecdh" and combo["variant"] == "ref") else 15.0

    cmd = [
        sys.executable, "src/scripts/trigger.py",
        "BM", port,
        "-n", str(repeats),
        "--msg", "Sensor Temp: 24.8C",
        "--alg", combo["alg"],
        "--timeout", str(timeout_sec),
        "--json-out", json_path
    ]
    if use_la:
        cmd.extend(["--la-out", la_csv])

    print(f">> [COLLECT] Running hardware collection on {port}: {' '.join(cmd)}")
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print(res.stdout)

    # Save complete console log for raw telemetry preservation
    with open(log_path, "w") as f_log:
        f_log.write(res.stdout)
        if res.stderr:
            f_log.write("\n--- STDERR ---\n" + res.stderr)

    if res.returncode != 0:
        print(f"!! Trigger error:\n{res.stderr}", file=sys.stderr)
        return False, []

    if not os.path.exists(json_path):
        print(f"!! Expected telemetry file not found: {json_path}", file=sys.stderr)
        return False, []

    with open(json_path, "r") as f_json:
        parsed_runs = json.load(f_json)

    return True, parsed_runs

def simulate_trial(task, trial_order, rng):
    """Simulate a single trial measurement with realistic Gaussian noise & thermal drift."""
    alg = task["alg"]
    variant = task["variant"]
    opt = task["opt"]
    clock_mhz = task["clock_mhz"]
    op = task["op"]
    
    prof = ALGO_PROFILES[alg][op]
    base_cycles = prof["cycles"]
    v_mult = VARIANT_MULTIPLIER[variant]
    o_mult = OPT_MULTIPLIER[opt]

    # Thermal drift modeled as slight increase over trial order (Jain Ch. 11.4)
    thermal_drift = 1.0 + (trial_order * 0.000015)
    noise_factor = rng.gauss(1.0, 0.0025)
    
    total_cycles = int(round(base_cycles * v_mult * o_mult * noise_factor * thermal_drift))
    fcpu_hz = clock_mhz * 1e6
    latency_ms = (total_cycles / fcpu_hz) * 1000.0
    
    # Active current model at 5.0V
    i_ma = prof["i_ma"] * (0.85 + 0.15 * (clock_mhz / 20.0)) + rng.gauss(0, 0.05)
    energy_uj = (5.0 * (i_ma / 1000.0)) * (latency_ms / 1000.0) * 1e6
    stack_peak = prof["stack"] if variant == "asm" else int(prof["stack"] * 1.35)
    total_time_ms = latency_ms + (800 * 10.0 / 115.2 if op in ("keygen", "encaps") else 4.0)

    return {
        "run_order": trial_order,
        "repetition": task["rep"],
        "timestamp": datetime.datetime.now().isoformat(),
        "algorithm": alg,
        "variant": variant,
        "optimization": opt,
        "clock_mhz": clock_mhz,
        "operation": op,
        "latency_ms": round(latency_ms, 3),
        "total_time_ms": round(total_time_ms, 3),
        "cycles": total_cycles,
        "stack_peak_b": stack_peak,
        "sram_total_b": 6144,
        "sram_headroom_pct": round((6144 - stack_peak) / 6144 * 100.0, 2),
        "payload_bytes": 800 if op in ("keygen", "encaps") else (32 if op == "decaps" else 18),
        "current_ma": round(i_ma, 3),
        "energy_uj": round(energy_uj, 2),
        "kem_validated": True if op == "decaps" else None,
        "msg_validated": True if op == "msgcrypt" else None,
        "status": "OK",
        # Provenance: every value above comes from a MODEL, not a measurement.
        "data_source": "sim",
        "latency_method": "model",
        "energy_method": "model",
    }

def generate_histograms(raw_csv_path, output_prefix):
    """Render Freedman-Diaconis distribution histograms via plot_histogram.py."""
    cmd = [
        sys.executable, "src/analysis/plot_histogram.py",
        "--in", raw_csv_path,
        "--out", output_prefix
    ]
    subprocess.run(cmd, check=True)

def aggregate_experiment(raw_records, summary_csv_path):
    """Compute Jain-standard statistics (Mean, Std Dev, 95% CI, Median, IQR)."""
    grouped = {}
    for r in raw_records:
        key = (r["algorithm"], r["variant"], r["optimization"], r["clock_mhz"], r["operation"])
        grouped.setdefault(key, []).append(r)

    summary_rows = []
    for (alg, var, opt, clk, op), records in sorted(grouped.items()):
        n = len(records)
        lats = [x["latency_ms"] for x in records]
        energies = [x["energy_uj"] for x in records]
        stacks = [x["stack_peak_b"] for x in records]

        mean_lat = sum(lats) / n
        std_lat = math.sqrt(sum((x - mean_lat)**2 for x in lats) / (n - 1)) if n > 1 else 0.0
        t_crit = get_t_crit(n - 1)
        ci_lat = t_crit * (std_lat / math.sqrt(n)) if n > 1 else 0.0

        sorted_lats = sorted(lats)
        median_lat = sorted_lats[n // 2] if n % 2 != 0 else (sorted_lats[n // 2 - 1] + sorted_lats[n // 2]) / 2.0
        iqr_lat = sorted_lats[(3 * n) // 4] - sorted_lats[n // 4]

        # Energy may be missing (bench without shunt): report NA, never a guess.
        en_vals = [x for x in energies if x is not None]
        n_en = len(en_vals)
        if n_en:
            mean_raw = sum(en_vals) / n_en
            std_en = math.sqrt(sum((x - mean_raw)**2 for x in en_vals) / (n_en - 1)) if n_en > 1 else 0.0
            mean_en = round(mean_raw, 2)
            ci_en = round(get_t_crit(n_en - 1) * (std_en / math.sqrt(n_en)), 2) if n_en > 1 else 0.0
        else:
            mean_en = ci_en = None

        summary_rows.append({
            "algorithm": alg,
            "variant": var,
            "optimization": opt,
            "clock_mhz": clk,
            "operation": op,
            "sample_size": n,
            "latency_ms_mean": round(mean_lat, 4),
            "latency_ms_std": round(std_lat, 4),
            "latency_ms_ci95": round(ci_lat, 4),
            "latency_ms_median": round(median_lat, 4),
            "latency_ms_iqr": round(iqr_lat, 4),
            "energy_uj_mean": mean_en,
            "energy_uj_ci95": ci_en,
            "stack_peak_bytes": stacks[0]
        })

    with open(summary_csv_path, "w", newline="") as f:
        fieldnames = [
            "algorithm", "variant", "optimization", "clock_mhz", "operation", "sample_size",
            "latency_ms_mean", "latency_ms_std", "latency_ms_ci95",
            "latency_ms_median", "latency_ms_iqr",
            "energy_uj_mean", "energy_uj_ci95", "stack_peak_bytes"
        ]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(summary_rows)

    return summary_rows

def write_markdown_report(exp_dir, args, summary_rows, raw_records, total_trials):
    """Write comprehensive experiment report adhering to Jain Chapter 10 & 13."""
    report_path = os.path.join(exp_dir, "report.md")
    with open(report_path, "w") as f:
        f.write(f"# Experiment Report: {os.path.basename(exp_dir)}\n\n")
        f.write(f"- **Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"- **Execution Mode:** `{args.mode}`\n")
        f.write(f"- **Randomization Seed (Jain Ch. 11.4):** `{args.seed}`\n")
        f.write(f"- **Replications per Cell ($N$):** `{args.n}`\n")
        f.write(f"- **Total Raw Observations Recorded:** `{len(raw_records)}`\n\n")
        if args.mode == "sim":
            f.write("> **WARNING: SIMULATED DATA.** Every value in this report comes from a "
                    "noise model (`simulate_trial`), not from the board. Do not report it as a measurement.\n\n")
        else:
            f.write("> Latency = host-side time until the first serial byte (includes UART/USB overhead). "
                    "Energy = NA: shunt/battery not installed yet.\n\n")

        f.write("## 1. Experimental Summary Table\n\n")
        f.write("| Algorithm | Variant | Opt | Clock | Operation | N | Mean Lat (ms) | 95% CI (ms) | Median (ms) | IQR (ms) | Mean Energy (uJ) | Stack Peak (B) |\n")
        f.write("| :--- | :---: | :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for s in summary_rows:
            en_str = "NA" if s["energy_uj_mean"] is None else f"{s['energy_uj_mean']:.1f}"
            f.write(f"| {s['algorithm']} | {s['variant']} | {s['optimization']} | {s['clock_mhz']} MHz | "
                    f"{s['operation']} | {s['sample_size']} | {s['latency_ms_mean']:.3f} | ±{s['latency_ms_ci95']:.3f} | "
                    f"{s['latency_ms_median']:.3f} | {s['latency_ms_iqr']:.3f} | {en_str} | {s['stack_peak_bytes']} |\n")

        f.write("\n## 2. Complete Raw Observations Log (All Individual Measurements)\n\n")
        f.write("| Run # | Rep | Variant | Operation | Latency (ms) | Total UART (ms) | Cycles (@20MHz) | Stack Peak (B) | SRAM Margin | KEM Valid | Msg Valid | Status |\n")
        f.write("| :---: | :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for r in raw_records:
            kem_val = r.get("kem_validated")
            kem_str = "OK" if kem_val is True else ("FAIL" if kem_val is False else "-")
            msg_val = r.get("msg_validated")
            msg_str = "OK" if msg_val is True else ("FAIL" if msg_val is False else "-")
            f.write(f"| {r['run_order']} | {r['repetition']} | {r['variant']} | {r['operation']} | "
                    f"{r['latency_ms']:.2f} | {r.get('total_time_ms', r['latency_ms']):.2f} | {r['cycles']:,} | "
                    f"{r['stack_peak_b']} | {r.get('sram_headroom_pct', 0.0):.1f}% | {kem_str} | {msg_str} | {r['status']} |\n")

        f.write("\n## 3. Visual Artifacts\n\n")
        f.write("- **Unified Real-Scale Latency Histograms (Shared Zero-Baseline 0-700 ms, Real Counts):**\n")
        f.write("  - `figures/histogram_unified_real_scale.png` (PDF: `figures/histogram_unified_real_scale.pdf`)\n")
        f.write("  - `figures/histogram.png` (Direct side-by-side comparison of ASM vs Pure C REF on identical scale)\n")
        f.write("- **Sequential Observation Timeline (Run-Order Time Series):**\n")
        f.write("  - `figures/histogram_timeseries.png` (Every single observation plotted across sequence)\n")
        f.write("- **Boxplot with All Individual Observations Overlaid (Strip Scatter):**\n")
        f.write("  - `figures/histogram_boxplot_points.png` (Boxplot showing full spread & every measured dot)\n")
        f.write("- **Variant-Specific Detailed Real-Count Histograms:**\n")
        for var in sorted(list({r.get('variant', 'asm') for r in raw_records})):
            f.write(f"  - `figures/histogram_{var}.png` (PDF: `figures/histogram_{var}.pdf`)\n")

        f.write("## 4. Complete Raw Data & Telemetry Files\n\n")
        f.write("- `raw/runs.csv`: Full tabular dataset with all observations and parameters.\n")
        f.write("- `raw/telemetry_*.json`: Full machine telemetry per firmware build.\n")
        f.write("- `raw/console_*.log`: Verbatim UART execution logs.\n")
        f.write("- `summary.csv`: Aggregated descriptive statistics.\n")
        f.write("- `schedule.json`: Randomized trial execution schedule.\n")

    print(f">> [REPORT] Markdown summary written to: {report_path}")

def main():
    ap = argparse.ArgumentParser(description="Automated Experiment Runner & Directory Generator")
    ap.add_argument("--mode", choices=["sim", "bench"], default="sim",
                    help="Execution mode: 'sim' for deterministic emulation, 'bench' for physical board")
    ap.add_argument("--port", default="/dev/ttyACM0", help="Serial port for hardware flashing & trigger")
    ap.add_argument("-n", "--iterations", dest="n", type=int, default=30,
                    help="Replications per combination (default: 30)")
    ap.add_argument("--seed", type=int, default=42, help="PRNG seed for randomized sequence")
    ap.add_argument("--tag", default="", help="Optional label to append to experiment folder")
    ap.add_argument("--alg", choices=["all", "kyber512", "ctru-light", "ecdh"], default="kyber512",
                    help="Algorithm filter (default: kyber512)")
    ap.add_argument("--use-la", dest="use_la", action="store_true", default=True,
                    help="Enable hardware logic analyzer capture via sigrok-cli (DEFAULT: True)")
    ap.add_argument("--no-la", dest="use_la", action="store_false",
                    help="Disable hardware logic analyzer capture")
    ap.add_argument("--variants", nargs="+", default=["asm", "ref"],
                    help="Variants to evaluate (default: asm ref)")
    ap.add_argument("--opts", nargs="+", default=["O3"],
                    help="Optimization levels: O3, Os (default: O3)")
    ap.add_argument("--clocks", nargs="+", type=float, default=[20.0],
                    help="Clock frequencies in MHz (default: 20.0)")
    args = ap.parse_args()

    if args.mode == "bench" and not os.path.exists(args.port):
        print(f"!! [ERRO] Porta serial {args.port} não encontrada (Arduino Nano Every desconectado?).")
        print(f"!! Conecte a placa USB (ou passe --port /dev/ttyACM1) para rodar em modo bench,")
        print(f"!! ou rode 'snakemake -j1' (sem 'experiment') para reproduzir a análise a partir dos dados já coletados.")
        sys.exit(1)

    # 1. Generate unique directory for this experiment
    # Mode goes into the folder name so simulated runs can never be mistaken for bench data.
    exp_dir = generate_experiment_dir(tag=f"{args.mode}_{args.tag or args.alg}")
    print(f"\n{'='*75}")
    print(f">> [EXPERIMENT] Initialized isolated experiment workspace:")
    print(f">> Directory: {exp_dir}")
    print(f">> Mode:      {args.mode}")
    print(f">> Seed:      {args.seed}")
    print(f">> N (reps):  {args.n}")
    print(f"{'='*75}\n")

    # 2. Build factor combinations
    algs = ["kyber512", "ctru-light", "ecdh"] if args.alg == "all" else [args.alg]
    variants = args.variants
    opts = [o if o.startswith("-") else f"-{o}" for o in args.opts]
    clocks = args.clocks
    ops = ["keygen", "encaps", "decaps", "msgcrypt"]

    combos = []
    for a in algs:
        for v in variants:
            for o in opts:
                for c in clocks:
                    combos.append({"alg": a, "variant": v, "opt": o, "clock_mhz": c})

    # 3. Create full randomized trial task list (Jain Ch. 11.4)
    tasks = []
    for combo in combos:
        for op in ops:
            for rep in range(1, args.n + 1):
                tasks.append({
                    "alg": combo["alg"],
                    "variant": combo["variant"],
                    "opt": combo["opt"],
                    "clock_mhz": combo["clock_mhz"],
                    "op": op,
                    "rep": rep
                })

    rng = random.Random(args.seed)
    rng.shuffle(tasks)

    # 4. Save randomized trial schedule
    schedule_path = os.path.join(exp_dir, "schedule.json")
    with open(schedule_path, "w") as f:
        json.dump(tasks, f, indent=2)
    print(f">> [SCHEDULE] Generated randomized schedule with {len(tasks)} trials -> {schedule_path}")

    # 5. Execute builds and measurements
    raw_records = []
    if args.mode == "sim":
        print(f">> [SIMULATION] Executing {len(tasks)} trials with physical noise modeling...")
        # Still compile the actual ELF/HEX into the folder to guarantee code integrity
        for combo in combos:
            build_firmware(combo["alg"], combo["variant"], combo["opt"], combo["clock_mhz"], exp_dir)

        for trial_order, task in enumerate(tasks, start=1):
            rec = simulate_trial(task, trial_order, rng)
            raw_records.append(rec)
    else:
        # Hardware bench mode
        print(f">> [BENCH] Running live hardware execution on {args.port}...")
        for combo in combos:
            ok, hex_file = build_firmware(combo["alg"], combo["variant"], combo["opt"], combo["clock_mhz"], exp_dir)
            if not ok:
                sys.exit(1)
            if not flash_firmware(hex_file, port=args.port):
                sys.exit(1)
            ok_coll, parsed_runs = run_hardware_collection(args.port, args.n, exp_dir, combo, use_la=args.use_la)
            if not ok_coll:
                sys.exit(1)
            # Create detailed observation records
            op_map = {"K": "keygen", "E": "encaps", "D": "decaps", "M": "msgcrypt"}
            rep_counter = {}
            for item in parsed_runs:
                op_code = item.get("cmd", "")
                op_name = op_map.get(op_code, item.get("op_name", "").lower())
                rep_counter[op_name] = rep_counter.get(op_name, 0) + 1
                has_la = item.get("t_la_ms") is not None
                lat_ms = item["t_la_ms"] if has_la else item["t_exec_ms"]
                tot_ms = item.get("t_total_ms", lat_ms)
                clk = combo["clock_mhz"]
                cycles = item["cycles_la"] if has_la else int(round(lat_ms * clk * 1000))
                lat_method = "saleae_logic_analyzer_gpio" if has_la else "host_serial_first_byte"
                raw_records.append({
                    "run_order": len(raw_records) + 1,
                    "repetition": rep_counter[op_name],
                    "timestamp": item.get("timestamp", datetime.datetime.now().isoformat()),
                    "algorithm": combo["alg"],
                    "variant": combo["variant"],
                    "optimization": combo["opt"],
                    "clock_mhz": combo["clock_mhz"],
                    "operation": op_name,
                    "latency_ms": lat_ms,
                    "latency_host_serial_ms": item["t_exec_ms"],
                    "latency_la_gpio_ms": item.get("t_la_ms"),
                    "total_time_ms": tot_ms,
                    "cycles": cycles,
                    "stack_peak_b": item["stack_peak"],
                    "sram_total_b": item.get("sram_total", 6144),
                    "sram_headroom_pct": item.get("sram_headroom", round((6144 - item["stack_peak"]) / 6144 * 100.0, 2)),
                    "payload_bytes": item.get("payload_bytes", 0),
                    "current_ma": None,
                    "energy_uj": None,
                    "kem_validated": item.get("kem_validated"),
                    "msg_validated": item.get("msg_validated"),
                    "status": item.get("status", "OK"),
                    "data_source": "bench",
                    "latency_method": lat_method,
                    "energy_method": "not_measured",
                })

    if not raw_records:
        sys.exit("!! No observations collected; nothing to aggregate.")

    # 6. Write raw runs CSV
    raw_csv_path = os.path.join(exp_dir, "raw", "runs.csv")
    if raw_records:
        raw_records.sort(key=lambda x: x["run_order"])
        with open(raw_csv_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(raw_records[0].keys()))
            w.writeheader()
            w.writerows(raw_records)
        print(f">> [DATA] Saved raw trial observations -> {raw_csv_path}")

    # 7. Aggregate statistics
    summary_csv_path = os.path.join(exp_dir, "summary.csv")
    summary_rows = aggregate_experiment(raw_records, summary_csv_path)
    print(f">> [DATA] Saved aggregated summary statistics -> {summary_csv_path}")

    # 8. Render Freedman-Diaconis distribution histogram & raw timeseries plots
    hist_prefix = os.path.join(exp_dir, "figures", "histogram")
    generate_histograms(raw_csv_path, hist_prefix)
    import shutil
    uni_png = f"{hist_prefix}_unified_real_scale.png"
    if os.path.exists(uni_png):
        shutil.copyfile(uni_png, f"{hist_prefix}.png")

    # 9. Write final markdown report
    write_markdown_report(exp_dir, args, summary_rows, raw_records, len(tasks))

    print(f"\n{'='*75}")
    print(f">> [SUCCESS] Experiment finished completely!")
    print(f">> All artifacts stored under: {exp_dir}")
    print(f"{'='*75}\n")

if __name__ == "__main__":
    main()

