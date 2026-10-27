#!/usr/bin/env python3
"""collect.py — Trigger one operation on the MCU and capture the waveform.

BENCH STUB: depends on the connected hardware (oscilloscope + logic analyzer +
board). The parts marked TODO need your specific oscilloscope driver (e.g.
python-vxi11, pyvisa) and sigrok-cli.

Flow:
  1. Open the serial port and send the command byte (K/E/D).
  2. Arm the oscilloscope to trigger on the GPIO rising edge.
  3. Read back the telemetry (stack peak) over serial.
  4. Save the waveform to CSV (t_s, v_shunt_v).
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

    # TODO(bench): arm the oscilloscope (pyvisa/vxi11) for the GPIO trigger.
    # TODO(bench): fire sigrok-cli for the pulse width (latency).

    try:
        import serial  # pyserial
    except ImportError:
        sys.exit("pyserial not installed (enter the `nix develop` shell).")

    with serial.Serial(args.port, args.baud, timeout=5) as ser:
        ser.write(CMD[args.op])
        # TODO(bench): read ACK + stack peak (2 bytes big-endian) + artifact.
        _ = ser.read(3)

    # TODO(bench): download the waveform from the scope and write it as:
    #   t_s,v_shunt_v
    #   ...
    # Placeholder so the pipeline doesn't break on dry-run:
    with open(args.out, "w") as f:
        f.write("t_s,v_shunt_v\n")

    print(f"[collect] {args.op} -> {args.out} (STUB: no real capture)")


if __name__ == "__main__":
    main()
