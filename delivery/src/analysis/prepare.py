"""Ingestão dos dados brutos para a análise em R (src/analysis/analise.qmd).

Lê apenas os arquivos brutos versionados em data/experiments/ e grava as bases
tidy em results/processed/. É a mesma lógica das células 3, 6 e 14 do
analise.ipynb, separada para que a estatística, as tabelas e as figuras fiquem
no caderno Quarto.

Saídas (results/processed/):
  bench_history_tidy.csv   todas as observações das campanhas de bancada, com
                           run_order, block, block_order e repetition
                           (reconstruídos dos timestamps nas campanhas antigas)
  campaigns_history.csv    uma linha por campanha (volume e instrumentação)
  bench_tidy.csv           campanha #17 (analisador lógico), base da análise
  la_vs_uart_overhead.csv  pulso no PA0 vs. tempo serial no host (asm -O3)
  flash_sizes.csv          Flash ocupada, lida dos .hex gravados (todas as otimizações)
  bench_O0_tidy.csv        campanha complementar sem otimização (-O0 + controles -O3)
  build_failures.csv       configurações que não compilaram (ex.: -O0 estoura a Flash)

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
    r"(?:_(?P<opt>O[0-3sgz])_(?P<clk>[\d.]+)MHz)?(?:_b(?P<block>\d+))?\.json"
)
CONFIG = ["algorithm", "variant", "optimization", "clock_mhz"]
HEX = re.compile(
    r"firmware-(?P<alg>kyber512|ctru-light|ecdh)-(?P<variant>asm|ref)-[\d.]+MHz-(?P<opt>O[0-3sgz])\.hex"
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
                    "stack_peak": r.get("stack_peak_b"),
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
                        "block": int(m["block"]) if m["block"] else 1,
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
    return add_execution_order(pd.DataFrame(rows)), pd.DataFrame(campaigns)


def add_execution_order(hist: pd.DataFrame) -> pd.DataFrame:
    """Garante run_order, block, block_order e repetition em todas as campanhas.

    Campanhas com observations.csv já trazem essas colunas. Nas que só têm
    telemetry_*.json, elas são reconstruídas a partir dos timestamps:
      run_order    ordem global de execução dentro da campanha
      block        bloco da configuração (sufixo _bNN do arquivo; 1 se não houver)
      block_order  posição do bloco na campanha (ordem do 1º timestamp do bloco)
      repetition   repetição da operação dentro da configuração, somando os blocos
    """
    cols = ["run_order", "block", "block_order", "repetition"]
    for col in cols:
        if col not in hist:
            hist[col] = np.nan
    falta = hist.groupby("experiment")[cols].transform(lambda s: s.isna().any()).any(axis=1)
    if falta.any():
        h = hist.loc[falta].copy()
        if h.run_order.isna().any():
            h["_ts"] = pd.to_datetime(h.timestamp, format="ISO8601")
            h = h.sort_values(["experiment", "_ts"], kind="stable")
            h["run_order"] = h.groupby("experiment").cumcount() + 1
        h = h.sort_values(["experiment", "run_order"], kind="stable")
        h["block"] = h.block.fillna(1)
        inicio = h.groupby(["experiment", *CONFIG, "block"])["run_order"].transform("min")
        h["block_order"] = h.assign(_ini=inicio).groupby("experiment")["_ini"].rank(method="dense")
        h["repetition"] = h.groupby(["experiment", *CONFIG, "operation"]).cumcount() + 1
        hist.loc[h.index, cols] = h[cols]
    for col in cols:
        hist[col] = hist[col].astype("Int64")
    return hist


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
    for bcsv in sorted(glob.glob(str(exp_dir / "exp_*" / "raw" / "builds.csv"))):
        bdf = pd.read_csv(bcsv)
        bdf["src"] = Path(bcsv).parts[-3]
        hx.extend(bdf.to_dict(orient="records"))
    for f in sorted(glob.glob(str(exp_dir / "exp_*" / "bin" / "*.hex"))):
        m = HEX.match(os.path.basename(f))
        if m:
            d = m.groupdict()
            hx.append({
                "algorithm": d["alg"],
                "variant": d["variant"],
                "optimization": "-" + d["opt"],
                "flash_b": hex_bytes(f),
                "src": Path(f).parts[-3],
            })
    flash = (pd.DataFrame(hx)
             .groupby(["algorithm", "variant", "optimization"], as_index=False)
             .last())
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

    # Campanha principal: a mais recente com LA, os 3 algoritmos e o fatorial -O3 x -Os
    # (sem -O0). A campanha complementar -O0 (com controles -O3) vai para bench_O0_tidy.csv.
    la = hist[hist.t_la_ms.notna()]
    perfil = la.groupby("experiment").agg(
        n_alg=("algorithm", "nunique"), opts=("optimization", lambda s: set(s)))
    principal = perfil[(perfil.n_alg >= 3)
                       & perfil.opts.map(lambda o: {"-O3", "-Os"} <= o and "-O0" not in o)]
    la_exp = sorted(principal.index)[-1] if len(principal) else LA_EXP

    df = hist[hist.experiment == la_exp].copy()
    df["t_exec_ms"] = df["t_la_ms"]
    df.to_csv(out / "bench_tidy.csv", index=False)

    o0_exps = sorted(perfil[perfil.opts.map(lambda o: "-O0" in o)].index)
    o0 = hist[hist.experiment == o0_exps[-1]].copy() if o0_exps else hist.iloc[0:0].copy()
    o0["t_exec_ms"] = o0["t_la_ms"]
    o0.to_csv(out / "bench_O0_tidy.csv", index=False)

    falhas = sorted(glob.glob(str(exp_dir / "exp_*" / "raw" / "build_failures.csv")))
    bf = (pd.concat([pd.read_csv(f).assign(src=Path(f).parts[-3]) for f in falhas])
          .drop_duplicates(["algorithm", "variant", "optimization"], keep="last")
          if falhas else pd.DataFrame(columns=["algorithm", "variant", "optimization",
                                               "clock_mhz", "reason", "src"]))
    bf.to_csv(out / "build_failures.csv", index=False)

    sub = hist[(hist.experiment == la_exp) & (hist.variant == "asm") & (hist.optimization == "-O3")]
    overhead = sub.groupby(["algorithm", "operation"]).agg(
        la_gpio_ms=("t_la_ms", "mean"),
        uart_host_ms=("t_exec_ms", "mean"),
        payload_bytes=("payload_bytes", "first"),
    ).reset_index()
    overhead["overhead_uart_ms"] = overhead.uart_host_ms - overhead.la_gpio_ms
    overhead.round(2).to_csv(out / "la_vs_uart_overhead.csv", index=False)

    load_flash(exp_dir).to_csv(out / "flash_sizes.csv", index=False)

    print(f"[prepare] {len(campaigns)} campanhas, {len(hist)} observações; "
          f"campanha LA: {len(df)} observações; campanha -O0: {len(o0)} observações -> {out}")


if __name__ == "__main__":
    main()
