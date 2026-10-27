#!/usr/bin/env python3
"""design.py — Build the experiment design (factor matrix) with pyDOE3.

Reads the factor levels from config.yaml and generates the design as an explicit
table (one row per build combination: algorithm x variant x clock x
optimization). Writes it to CSV so the design is a citable, inspectable
artifact of the experiment (not an implicit cartesian product in the Snakefile).

Design type:
  - "full"      : general full-factorial via pyDOE3.fullfact (default).
  - "fracfact"  : fractional factorial (requires a generator string in config,
                  key 'fraction_generator') — use only if the full matrix is
                  too long for the bench.

Usage:
  python design.py --config config.yaml --out data/design.csv
  python design.py --config config.yaml --print        # just print, no write
"""
import argparse, csv, os, sys
import yaml


# Factor order is fixed so level indices map back to labels deterministically.
FACTORS = ["algorithm", "variant", "clock_mhz", "optimization"]
CONFIG_KEYS = {
    "algorithm":    "algorithms",
    "variant":      "variants",
    "clock_mhz":    "clock_mhz",
    "optimization": "optimization",
}


def load_levels(config):
    """Return an ordered list of (factor_name, [levels...])."""
    levels = []
    for f in FACTORS:
        vals = config[CONFIG_KEYS[f]]
        levels.append((f, [str(v) for v in vals]))
    return levels


def build_design(levels, kind="full", generator=None):
    """Return a list of dict rows mapping factor name -> chosen level label.

    Uses pyDOE3 to produce the coded design (level indices), then decodes the
    indices back to the string labels from the config.
    """
    try:
        from pyDOE3 import fullfact, fracfact
    except ImportError:
        sys.exit("pyDOE3 not installed (enter the `nix develop` shell).")

    counts = [len(vals) for _, vals in levels]

    if kind == "full":
        coded = fullfact(counts)          # rows of level indices (floats)
    elif kind == "fracfact":
        if not generator:
            sys.exit("fracfact requires 'fraction_generator' in the config.")
        # fracfact handles 2-level factors; guard against multi-level here.
        if any(c != 2 for c in counts):
            sys.exit("fracfact only supports 2-level factors; use 'full'.")
        coded = fracfact(generator)
        coded = (coded + 1) / 2           # map {-1,+1} -> {0,1} indices
    else:
        sys.exit(f"unknown design kind: {kind}")

    rows = []
    for coded_row in coded:
        row = {}
        for (name, vals), idx in zip(levels, coded_row):
            row[name] = vals[int(round(idx))]
        rows.append(row)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--out", default=None, help="CSV output (omit with --print)")
    ap.add_argument("--print", dest="do_print", action="store_true")
    args = ap.parse_args()

    with open(args.config) as f:
        config = yaml.safe_load(f)

    levels = load_levels(config)
    kind = config.get("design", "full")
    rows = build_design(levels, kind=kind,
                        generator=config.get("fraction_generator"))

    if args.do_print or not args.out:
        for r in rows:
            print(", ".join(f"{k}={r[k]}" for k in FACTORS))
        print(f"# {len(rows)} combinations ({kind} design)")
        return

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FACTORS)
        w.writeheader()
        w.writerows(rows)
    print(f"[design] {len(rows)} combinations -> {args.out}")


if __name__ == "__main__":
    main()
