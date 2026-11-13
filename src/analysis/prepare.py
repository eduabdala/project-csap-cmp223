"""Ingestão dos dados brutos para a análise em R (src/analysis/analise.qmd).

Lê apenas os arquivos brutos versionados em data/experiments/ e grava as bases
tidy em results/processed/. É a mesma lógica das células 3, 6 e 14 do
analise.ipynb, separada para que a estatística, as tabelas e as figuras fiquem
no caderno Quarto.

Saídas (results/processed/):
  bench_history_tidy.csv   todas as observações das campanhas de bancada
  campaigns_history.csv    uma linha por campanha (volume e instrumentação)
  bench_tidy.csv           campanha #17 (analisador lógico), base da análise
  la_vs_uart_overhead.csv  pulso no PA0 vs. tempo serial no host (asm -O3)
  flash_sizes.csv          Flash ocupada, lida dos .hex gravados

Uso (a partir da raiz do repositório):
  python src/analysis/prepare.py
"""

from __future__ import annotations

import glob
import json
import os
import re
from pathlib import Path

import numpy as np
import pandas as pd

LA_EXP = "exp_20261108_155653_bench_campanha_completa_la_nix_8289"
OPS = {"K": "keygen", "E": "encaps", "D": "decaps", "M": "msgcrypt"}
TELEMETRY = re.compile(
    r"telemetry_(?P<alg>kyber512|ctru-light|ecdh)_(?P<variant>asm|ref)"
    r"(?:_(?P<opt>O3|Os)_(?P<clk>[\d.]+)MHz)?\.json"
)
HEX = re.compile(
    r"firmware-(?P<alg>kyber512|ctru-light|ecdh)-(?P<variant>asm|ref)-[\d.]+MHz-(?P<opt>O3|Os)\.hex"
)
FLASH_TOTAL_B = 49152


def find_root(start: Path) -> Path:
    root = start.resolve()
    while not (root / "data" / "experiments").is_dir() and root != root.parent:
        root = root.parent
    return root


def load_history(exp_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    cat = pd.read_csv(exp_dir / "catalog.csv")
    bench_exps = cat.loc[cat.source == "bench", "experiment"].tolist()

    rows, campaigns = [], []
    for idx, e in enumerate(bench_exps, start=1):
        obs_csv = exp_dir / e / "raw" / "observations.csv"
        files = sorted(glob.glob(str(exp_dir / e / "raw" / "telemetry_*.json")))
        la_files = sorted(glob.glob(str(exp_dir / e / "raw" / "la_*.csv")))
        algs_e, opts_e, n_e, has_t_la = set(), set(), 0, False

        if obs_csv.is_file():
            obs_df = pd.read_csv(obs_csv)
            n_e = len(obs_df)
            algs_e.update(obs_df["algorithm"].astype(str).unique())
            opts_e.update(obs_df["optimization"].astype(str).unique())
            has_t_la = obs_df["t_pa0_ms"].notna().any()
            for i, r in enumerate(obs_df.to_dict(orient="records")):
                t_exec = float(r["t_uart_ms"]) if pd.notna(r.get("t_uart_ms")) else np.nan
                t_la = float(r["t_pa0_ms"]) if pd.notna(r.get("t_pa0_ms")) else np.nan
                rows.append({
                    **r, "experiment": e, "campaign_idx": idx, "seq": i,
                    "t_exec_ms": t_exec, "t_la_ms": t_la,
                    "latency_ms": t_la if not np.isnan(t_la) else t_exec,
                })
            n_configs = int(obs_df[["algorithm", "variant", "optimization"]].drop_duplicates().shape[0])
        else:
            for f in files:
                m = TELEMETRY.match(os.path.basename(f)).groupdict()
                algs_e.add(m["alg"])
                opt = "-" + (m["opt"] or "O3")
                opts_e.add(opt)
                with open(f, encoding="utf-8") as fh:
                    data = json.load(fh)
                n_e += len(data)
                for i, r in enumerate(data):
                    t_exec = float(r["t_exec_ms"])
                    t_la = float(r["t_la_ms"]) if r.get("t_la_ms") is not None else np.nan
                    if not np.isnan(t_la):
                        has_t_la = True
                    rows.append({
                        **r, "experiment": e, "campaign_idx": idx, "seq": i,
                        "algorithm": m["alg"], "variant": m["variant"],
                        "optimization": opt, "clock_mhz": float(m["clk"] or 20),
                        "operation": OPS[r["cmd"]], "t_exec_ms": t_exec, "t_la_ms": t_la,
                        "latency_ms": t_la if not np.isnan(t_la) else t_exec,
                    })
            n_configs = len(files)

        m_dt = re.match(r"exp_(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})\d{2}_(.+)_\d{4}", e)
        dt_str = f"{m_dt.group(3)}/{m_dt.group(2)} {m_dt.group(4)}:{m_dt.group(5)}" if m_dt else e
        if has_t_la:
            metodo = "LA 24MHz (PA0) + UART"
        elif la_files:
            metodo = "LA CSV parcial + UART"
        else:
            metodo = "UART (host)"
        campaigns.append({
            "campanha": f"#{idx:02d}", "experiment": e, "data_hora": dt_str,
            "configs": n_configs, "algoritmos": ", ".join(sorted(algs_e)),
            "flags": ", ".join(sorted(opts_e)), "observacoes": n_e, "instrumentacao": metodo,
        })
    return pd.DataFrame(rows), pd.DataFrame(campaigns)


def hex_bytes(path: str) -> int:
    """Soma os bytes dos registros de dados (tipo 00) de um Intel HEX."""
    n = 0
    with open(path, encoding="ascii") as fh:
        for line in fh:
            if line.startswith(":") and line[7:9] == "00":
                n += int(line[1:3], 16)
    return n


def load_flash(exp_dir: Path) -> pd.DataFrame:
    hx = []
    for f in sorted(glob.glob(str(exp_dir / "exp_*" / "bin" / "*.hex"))):
        m = HEX.match(os.path.basename(f))
        if m:
            hx.append({**m.groupdict(), "flash_b": hex_bytes(f), "src": Path(f).parts[-3]})
    flash = (pd.DataFrame(hx).groupby(["alg", "variant", "opt"]).last().reset_index()
             .rename(columns={"alg": "algorithm", "opt": "optimization"}))
    flash["optimization"] = "-" + flash.optimization
    flash["flash_kb"] = (flash.flash_b / 1024.0).round(2)
    flash["flash_free_pct"] = (100 * (FLASH_TOTAL_B - flash.flash_b) / FLASH_TOTAL_B).round(2)
    return flash


def main() -> None:
    root = find_root(Path(__file__).parent)
    exp_dir = root / "data" / "experiments"
    out = root / "results" / "processed"
    out.mkdir(parents=True, exist_ok=True)

    hist, campaigns = load_history(exp_dir)
    hist.to_csv(out / "bench_history_tidy.csv", index=False)
    campaigns.to_csv(out / "campaigns_history.csv", index=False)

    # Campanha #17: a largura do pulso no PA0 (t_la_ms) é a latência principal.
    df = hist[hist.experiment == LA_EXP].copy()
    df["t_exec_ms"] = df["t_la_ms"]
    df.to_csv(out / "bench_tidy.csv", index=False)

    sub = hist[(hist.experiment == LA_EXP) & (hist.variant == "asm") & (hist.optimization == "-O3")]
    overhead = sub.groupby(["algorithm", "operation"]).agg(
        la_gpio_ms=("t_la_ms", "mean"),
        uart_host_ms=("t_exec_ms", "mean"),
        payload_bytes=("payload_bytes", "first"),
    ).reset_index()
    overhead["overhead_uart_ms"] = overhead.uart_host_ms - overhead.la_gpio_ms
    overhead.round(2).to_csv(out / "la_vs_uart_overhead.csv", index=False)

    load_flash(exp_dir).to_csv(out / "flash_sizes.csv", index=False)

    print(f"[prepare] {len(campaigns)} campanhas, {len(hist)} observações; "
          f"campanha LA: {len(df)} observações -> {out}")


if __name__ == "__main__":
    main()
