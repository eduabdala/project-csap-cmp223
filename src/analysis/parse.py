#!/usr/bin/env python3
"""parse.py — Processa um CSV bruto de uma iteração e extrai as métricas.

Entrada (CSV do osciloscópio/analisador lógico), colunas esperadas:
    t_s, v_shunt_v        # tempo (s) e tensão no shunt (V) dentro da janela
Metadados (cabeçalho ou arquivo irmão): latência da janela e pico de stack.

Saída (JSON) com: energia (µJ), latência (s), pico de stack (bytes).

A integração de energia é pura (sem hardware), então esta etapa é testável
offline. E = ∫ V·i dt, com i = v_shunt / R_shunt.
"""
import argparse, json, csv


def integrate_energy(t, v_shunt, r_shunt, v_supply=5.0):
    """Energia (Joules) por regra do trapézio.

    Potência instantânea no MCU: P(t) = V_supply * i(t), i(t)=v_shunt/R.
    (Aproximação: assume V_supply ~ constante; refinar se medir V_mcu.)
    """
    if len(t) < 2:
        return 0.0
    energy = 0.0
    for k in range(1, len(t)):
        dt = t[k] - t[k - 1]
        i0 = v_shunt[k - 1] / r_shunt
        i1 = v_shunt[k] / r_shunt
        p0, p1 = v_supply * i0, v_supply * i1
        energy += 0.5 * (p0 + p1) * dt     # trapézio
    return energy


def read_csv(path):
    t, v = [], []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            t.append(float(row["t_s"]))
            v.append(float(row["v_shunt_v"]))
    return t, v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--shunt", type=float, required=True, help="R_shunt (ohms)")
    ap.add_argument("--vsupply", type=float, default=5.0)
    ap.add_argument("--stack-peak", type=int, default=-1,
                    help="pico de stack em bytes (vindo da telemetria serial)")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    t, v = read_csv(args.inp)
    energy_j = integrate_energy(t, v, args.shunt, args.vsupply)
    latency_s = (t[-1] - t[0]) if len(t) >= 2 else 0.0

    result = {
        "energy_uj": energy_j * 1e6,
        "latency_s": latency_s,
        "stack_peak_bytes": args.stack_peak,
        "source": args.inp,
    }
    with open(args.out, "w") as f:
        json.dump(result, f, indent=2)


if __name__ == "__main__":
    main()
