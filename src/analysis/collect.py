#!/usr/bin/env python3
"""collect.py — Dispara uma operação no MCU e captura a forma de onda.

STUB DE BANCADA: depende do hardware conectado (osciloscópio + analisador
lógico + placa). As partes marcadas com TODO precisam do driver específico
do seu osciloscópio (ex.: python-vxi11, pyvisa) e do sigrok-cli.

Fluxo:
  1. Abre a serial e envia o byte de comando (K/E/D).
  2. Arma o osciloscópio p/ trigger na borda de subida do GPIO.
  3. Lê a telemetria (stack peak) de volta pela serial.
  4. Salva a forma de onda em CSV (t_s, v_shunt_v).
"""
import argparse, sys

CMD = {"keygen": b"K", "encaps": b"E", "decaps": b"D"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--op", required=True, choices=CMD.keys())
    ap.add_argument("--port", required=True)
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    # TODO(bancada): armar osciloscópio (pyvisa/vxi11) para trigger GPIO.
    # TODO(bancada): disparar sigrok-cli p/ largura do pulso (latência).

    try:
        import serial  # pyserial
    except ImportError:
        sys.exit("pyserial não instalado (entre no `nix develop`).")

    with serial.Serial(args.port, args.baud, timeout=5) as ser:
        ser.write(CMD[args.op])
        # TODO(bancada): ler ACK + stack peak (2 bytes big-endian) + artefato.
        _ = ser.read(3)

    # TODO(bancada): baixar a waveform do osciloscópio e gravar como:
    #   t_s,v_shunt_v
    #   ...
    # Placeholder para o pipeline não quebrar em dry-run:
    with open(args.out, "w") as f:
        f.write("t_s,v_shunt_v\n")

    print(f"[collect] {args.op} -> {args.out} (STUB: sem captura real)")


if __name__ == "__main__":
    main()
