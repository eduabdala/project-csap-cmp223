#!/usr/bin/env python3
"""
trigger.py — Envia comandos ('K', 'E', 'D', 'M', 'P') ou baterias ('B', 'BM')
para o ATmega4809 via UART, realiza troca real de mensagem cifrada derivada
do segredo compartilhado do KEM (Kyber-512 / CTRU-Light / ECDH) e opcionalmente
coleta o sinal bruto (RAW) do Analisador Lógico USB (Saleae Logic / fx2lafw).

Exemplos de uso:
    # 1 operação isolada:
    ./src/scripts/trigger.py K /dev/ttyACM0

    # Bateria K -> E -> D + Troca de mensagem cifrada (M):
    ./src/scripts/trigger.py BM /dev/ttyACM0 --msg "Temp: 24.8C | Bateria: OK"

    # Bateria de 5 rodadas coletando o RAW do analisador lógico (CSV):
    ./src/scripts/trigger.py B /dev/ttyACM0 -n 5 --la-out data/raw/bateria_kyber.csv

    # Mesma captura usando o driver libusb embutido em vez do sigrok-cli:
    ./src/scripts/trigger.py B /dev/ttyACM0 --la-out data/raw/k.csv --la-backend libusb
"""
import argparse
import ctypes
import fcntl
import os
import select
import shutil
import signal
import statistics
import struct
import subprocess
import sys
import tempfile
import termios
import threading
import time

BAUD_MAP = {
    9600: termios.B9600,
    19200: termios.B19200,
    38400: termios.B38400,
    57600: termios.B57600,
    115200: termios.B115200,
}

OP_NAMES = {
    "K": "KeyGen",
    "E": "Encaps",
    "D": "Decaps",
    "M": "MsgCrypt",
    "P": "Ping",
}

KEM_CIPHERTEXTBYTES = 768
KEM_BYTES = 32


def stream_xor(data: bytes, key: bytes) -> bytes:
    """Aplica o mesmo fluxo de chave derivado do segredo compartilhado (ss) do firmware."""
    out = bytearray(len(data))
    for i, b in enumerate(data):
        k = key[i % len(key)] ^ ((i * 0x9E + 0x37) & 0xFF)
        out[i] = b ^ k
    return bytes(out)


# ============================================================================
# Coleta do Analisador Lógico (Saleae Logic 0925:3881 / fx2lafw via libusb/sigrok)
# ============================================================================
class Fx2LogicAnalyzer:
    """Coletor direto via libusb-1.0 para analisadores Saleae Logic 8ch (0925:3881)."""

    VID = 0x0925
    PID = 0x3881
    FW_PATH = "/usr/share/sigrok-firmware/fx2lafw-saleae-logic.fw"

    def __init__(self, samplerate: int = 100000):
        self.samplerate = samplerate
        self.samples = bytearray()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._usb = None
        self._ctx = ctypes.c_void_p()
        self._handle = ctypes.c_void_p()

    def _init_libusb(self) -> bool:
        try:
            self._usb = ctypes.CDLL("libusb-1.0.so.0")
        except OSError:
            return False

        self._usb.libusb_init.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
        self._usb.libusb_open_device_with_vid_pid.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint16,
            ctypes.c_uint16,
        ]
        self._usb.libusb_open_device_with_vid_pid.restype = ctypes.c_void_p
        self._usb.libusb_claim_interface.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self._usb.libusb_release_interface.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self._usb.libusb_close.argtypes = [ctypes.c_void_p]
        self._usb.libusb_exit.argtypes = [ctypes.c_void_p]
        self._usb.libusb_control_transfer.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint8,
            ctypes.c_uint8,
            ctypes.c_uint16,
            ctypes.c_uint16,
            ctypes.c_char_p,
            ctypes.c_uint16,
            ctypes.c_uint,
        ]
        self._usb.libusb_bulk_transfer.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint8,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_int),
            ctypes.c_uint,
        ]

        if self._usb.libusb_init(ctypes.byref(self._ctx)) != 0:
            return False
        self._handle = ctypes.c_void_p(
            self._usb.libusb_open_device_with_vid_pid(self._ctx, self.VID, self.PID)
        )
        if not self._handle.value:
            return False
        self._usb.libusb_claim_interface(self._handle, 0)
        self._ensure_firmware()
        return True

    def _ensure_firmware(self) -> None:
        # Check if fx2lafw is already running via CMD_GET_FW_VERSION (0xB0)
        ver_buf = ctypes.create_string_buffer(2)
        ret = self._usb.libusb_control_transfer(
            self._handle, 0xC0, 0xB0, 0, 0, ver_buf, 2, 200
        )
        if ret == 2:
            return
        if not os.path.exists(self.FW_PATH):
            return
        with open(self.FW_PATH, "rb") as f:
            fw = f.read()
        # Put 8051 in reset (CPUCS = 0xE600 <- 1)
        b_one = ctypes.create_string_buffer(b"\x01", 1)
        self._usb.libusb_control_transfer(self._handle, 0x40, 0xA0, 0xE600, 0, b_one, 1, 200)
        # Upload firmware in 4096-byte chunks
        for offset in range(0, len(fw), 4096):
            chunk = fw[offset : offset + 4096]
            cbuf = ctypes.create_string_buffer(chunk, len(chunk))
            self._usb.libusb_control_transfer(
                self._handle, 0x40, 0xA0, offset, 0, cbuf, len(chunk), 500
            )
        # Release 8051 reset (CPUCS = 0xE600 <- 0)
        b_zero = ctypes.create_string_buffer(b"\x00", 1)
        self._usb.libusb_control_transfer(self._handle, 0x40, 0xA0, 0xE600, 0, b_zero, 1, 200)
        self._usb.libusb_release_interface(self._handle, 0)
        self._usb.libusb_close(self._handle)
        time.sleep(1.8)
        self._handle = ctypes.c_void_p(
            self._usb.libusb_open_device_with_vid_pid(self._ctx, self.VID, self.PID)
        )
        if self._handle.value:
            self._usb.libusb_claim_interface(self._handle, 0)

    def start(self) -> bool:
        if not self._init_libusb():
            return False
        # Configure fx2lafw CMD_START (0xB1): 30 MHz base clock (flags=0x00)
        delay = max(1, int(30_000_000 // self.samplerate) - 1)
        cmd_start = struct.pack(">BH", 0x00, delay)
        cbuf = ctypes.create_string_buffer(cmd_start, 3)
        ret = self._usb.libusb_control_transfer(
            self._handle, 0x40, 0xB1, 0, 0, cbuf, 3, 500
        )
        if ret < 0:
            return False
        self._stop.clear()
        self._thread = threading.Thread(target=self._reader_loop, daemon=True)
        self._thread.start()
        return True

    def _reader_loop(self) -> None:
        chunk_size = 16384
        buf = ctypes.create_string_buffer(chunk_size)
        transferred = ctypes.c_int(0)
        while not self._stop.is_set():
            rc = self._usb.libusb_bulk_transfer(
                self._handle, 0x82, buf, chunk_size, ctypes.byref(transferred), 100
            )
            if rc == 0 and transferred.value > 0:
                self.samples.extend(buf.raw[: transferred.value])

    def stop(self) -> bytes:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=1.0)
        if self._handle and self._handle.value:
            self._usb.libusb_release_interface(self._handle, 0)
            self._usb.libusb_close(self._handle)
            self._handle = ctypes.c_void_p()
        if self._ctx and self._ctx.value:
            self._usb.libusb_exit(self._ctx)
            self._ctx = ctypes.c_void_p()
        return bytes(self.samples)


class SigrokLogicAnalyzer:
    """Captura contínua via sigrok-cli (fx2lafw cuida do firmware do Saleae Logic).

    Saída em formato 'binary': 1 byte por amostra (bit n = canal Dn), o mesmo
    layout do coletor libusb, então decode_la_pulses/save_la_csv não mudam.
    """

    def __init__(self, samplerate: int = 100000, driver: str = "fx2lafw"):
        self.samplerate = samplerate
        self.driver = driver
        self._proc: subprocess.Popen | None = None
        self._path: str | None = None

    def start(self) -> bool:
        exe = shutil.which("sigrok-cli")
        if not exe:
            print("[LA] sigrok-cli não encontrado no PATH (entre no `nix develop`).", file=sys.stderr)
            return False
        fd, self._path = tempfile.mkstemp(prefix="la_", suffix=".bin")
        os.close(fd)
        cmd = [
            exe, "-d", self.driver,
            "--config", f"samplerate={self.samplerate}",
            "--continuous", "-O", "binary", "-o", self._path,
        ]
        self._proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        # Pronto quando o arquivo começa a crescer (1º upload de firmware leva ~2 s)
        deadline = time.perf_counter() + 6.0
        while time.perf_counter() < deadline:
            if self._proc.poll() is not None:
                err = self._proc.stderr.read().decode(errors="replace").strip() if self._proc.stderr else ""
                print(f"[LA] sigrok-cli encerrou: {err}", file=sys.stderr)
                self._cleanup()
                return False
            if os.path.getsize(self._path) > 0:
                return True
            time.sleep(0.05)
        print("[LA] sigrok-cli não começou a amostrar em 6 s.", file=sys.stderr)
        self.stop()
        return False

    def stop(self) -> bytes:
        if self._proc and self._proc.poll() is None:
            self._proc.send_signal(signal.SIGINT)  # sigrok-cli finaliza e faz flush do arquivo
            try:
                self._proc.wait(timeout=5.0)
            except subprocess.TimeoutExpired:
                self._proc.kill()
                self._proc.wait()
        data = b""
        if self._path and os.path.exists(self._path):
            with open(self._path, "rb") as f:
                data = f.read()
        self._cleanup()
        return data

    def _cleanup(self) -> None:
        if self._path and os.path.exists(self._path):
            os.remove(self._path)
        self._path = None
        self._proc = None


def decode_la_pulses(raw_bytes: bytes, samplerate: int) -> tuple[int, list[dict]]:
    """Detecta o canal ativo (D0..D7) e extrai os pulsos (ID + janela MEASURE)."""
    if not raw_bytes:
        return 0, []

    # Descobre qual canal (0..7) teve transições
    active_ch = 0
    best_edges = 0
    mv = memoryview(raw_bytes)
    step = max(1, len(mv) // 50000)
    for ch in range(8):
        mask = 1 << ch
        edges = 0
        prev = mv[0] & mask
        for i in range(1, len(mv), step):
            cur = mv[i] & mask
            if cur != prev:
                edges += 1
                prev = cur
        if edges > best_edges:
            best_edges = edges
            active_ch = ch

    mask = 1 << active_ch
    pulses: list[tuple[float, float]] = []
    in_high = False
    start_idx = 0
    for idx, b in enumerate(mv):
        high = bool(b & mask)
        if high and not in_high:
            in_high = True
            start_idx = idx
        elif not high and in_high:
            in_high = False
            t_start = start_idx / samplerate
            dur_ms = (idx - start_idx) * 1000.0 / samplerate
            pulses.append((t_start, dur_ms))

    # Classifica grupos: pulsos curtos (~1..4 ms) são id_pulses, pulsos longos (>15 ms) são janelas MEASURE
    events: list[dict] = []
    id_count = 0
    for t_start, dur_ms in pulses:
        if 0.5 <= dur_ms <= 8.0:
            id_count += 1
        elif dur_ms > 15.0:
            op_map = {1: "K (KeyGen)", 2: "E (Encaps)", 3: "D (Decaps)", 4: "M (MsgCrypt)"}
            events.append(
                {
                    "id_pulses": id_count,
                    "op": op_map.get(id_count, f"Janela ({id_count}p)"),
                    "t_start_s": t_start,
                    "width_ms": dur_ms,
                }
            )
            id_count = 0
    return active_ch, events


def save_la_csv(path: str, raw_bytes: bytes, samplerate: int, active_ch: int) -> None:
    """Salva o trace do analisador lógico em CSV compacto (transições + amostras)."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    mask = 1 << active_ch
    with open(path, "w") as f:
        f.write(f"# samplerate_hz={samplerate}, active_channel=D{active_ch}, total_samples={len(raw_bytes)}\n")
        f.write(f"sample_idx,t_s,D{active_ch},raw_byte_hex\n")
        prev = None
        for idx, b in enumerate(raw_bytes):
            val = 1 if (b & mask) else 0
            # Grava transições e também pontos periódicos a cada 1 ms para manter o CSV leve e fiel
            if val != prev or (idx % max(1, samplerate // 1000) == 0):
                t_s = idx / samplerate
                f.write(f"{idx},{t_s:.6f},{val},{b:02x}\n")
                prev = val


# ============================================================================
# Comunicação Serial com o ATmega4809
# ============================================================================
def open_serial(port: str, baud: int) -> int:
    if baud not in BAUD_MAP:
        raise ValueError(f"Unsupported baud rate: {baud}")
    fd = os.open(port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    attrs = termios.tcgetattr(fd)
    needs_bridge_init = bool(attrs[2] & termios.HUPCL) or (attrs[4] != BAUD_MAP[baud])

    attrs[0] = 0
    attrs[1] = 0
    attrs[2] = (attrs[2] & ~termios.HUPCL) | termios.CS8 | termios.CREAD | termios.CLOCAL
    attrs[3] = 0
    if needs_bridge_init:
        attrs[4] = termios.B9600
        attrs[5] = termios.B9600
        termios.tcsetattr(fd, termios.TCSANOW, attrs)
    attrs[4] = BAUD_MAP[baud]
    attrs[5] = BAUD_MAP[baud]
    termios.tcsetattr(fd, termios.TCSANOW, attrs)

    try:
        status = struct.unpack("I", fcntl.ioctl(fd, termios.TIOCMGET, struct.pack("I", 0)))[0]
        if not (status & termios.TIOCM_DTR):
            needs_bridge_init = True
        bits = struct.pack("I", termios.TIOCM_DTR | termios.TIOCM_RTS)
        fcntl.ioctl(fd, termios.TIOCMBIS, bits)
    except OSError:
        pass

    if needs_bridge_init:
        time.sleep(0.75)
    termios.tcflush(fd, termios.TCIOFLUSH)
    return fd


def send_seed(fd: int, timeout: float) -> bool:
    """Injeta 64 bytes de os.urandom no pool de entropia da placa (comando 'S').

    Feito FORA da janela de medição; a placa mistura com ruído do ADC e consome
    a semente no próximo K/E.
    """
    termios.tcflush(fd, termios.TCIFLUSH)
    os.write(fd, b"S" + os.urandom(64))
    expected = b"s\r\nDONE S\r\n"
    buf = b""
    deadline = time.perf_counter() + min(timeout, 2.0)
    while not buf.endswith(expected):
        rem = deadline - time.perf_counter()
        if rem <= 0:
            return False
        r, _, _ = select.select([fd], [], [], rem)
        if not r:
            return False
        buf += os.read(fd, 256)
    return True


def run_single_cmd(
    fd: int,
    cmd: str,
    port: str,
    baud: int,
    timeout: float,
    state: dict,
    msg_text: str,
) -> dict | None:
    termios.tcflush(fd, termios.TCIFLUSH)
    t0 = time.perf_counter()

    if cmd == "M":
        # Usa a chave compartilhada gerada no Encaps (ou Decaps) para cifrar a mensagem no PC
        key = state.get("ss_enc") or state.get("ss_dec")
        if not key:
            print(
                "Aviso: nenhuma chave compartilhada em sessão; executando K -> E -> D automaticamente antes de M..."
            )
            for pre_cmd in ("K", "E", "D"):
                res = run_single_cmd(fd, pre_cmd, port, baud, timeout, state, msg_text)
                if res is None:
                    return None
            key = state.get("ss_enc") or state.get("ss_dec")

        pt_bytes = msg_text.encode("utf-8")[:64]
        ct_msg = stream_xor(pt_bytes, key)
        t0 = time.perf_counter()
        os.write(fd, b"M" + bytes([len(ct_msg)]) + ct_msg)
    else:
        if cmd in ("K", "E") and not send_seed(fd, timeout):
            print("Aviso: placa não confirmou a semente (firmware antigo?). Seguindo com entropia do ADC.",
                  file=sys.stderr)
        t0 = time.perf_counter()
        os.write(fd, cmd.encode("ascii"))

    # 1. Aguarda o primeiro byte não-nulo ('k', 'e', 'd', 'm', 'P' ou '?')
    buf = b""
    deadline = t0 + timeout
    while not buf:
        rem = deadline - time.perf_counter()
        if rem <= 0:
            print(
                f"Timeout ({timeout}s) aguardando resposta de '{cmd}' em {port}.",
                file=sys.stderr,
            )
            return None
        r, _, _ = select.select([fd], [], [], rem)
        if not r:
            print(
                f"Timeout ({timeout}s) aguardando resposta de '{cmd}' em {port}.",
                file=sys.stderr,
            )
            return None
        chunk = os.read(fd, 4096)
        buf = chunk.lstrip(b"\x00")

    t_exec = time.perf_counter() - t0

    # 2. Lê os demais bytes até receber o trailer DONE (a ponte USB do SAMD11
    #    pode pausar >50 ms no meio do payload, então só o trailer encerra a leitura)
    trailer = f"\r\nDONE {cmd}\r\n".encode("ascii")
    while True:
        if cmd in ("K", "E", "D", "M") and buf.endswith(trailer):
            break
        idle = 1.0 if cmd in ("K", "E", "D", "M") else 0.05
        rem = deadline - time.perf_counter()
        r, _, _ = select.select([fd], [], [], max(0.0, min(idle, rem)))
        if not r:
            break
        chunk = os.read(fd, 4096)
        if not chunk:
            break
        buf += chunk

    t_total = time.perf_counter() - t0

    if cmd == "P":
        msg = buf.decode("ascii", errors="replace").strip()
        print(f"Resposta PING: {msg}")
        return {"cmd": "P", "t_exec_ms": t_exec * 1000.0, "t_total_ms": t_total * 1000.0}

    ack = chr(buf[0]) if buf else "?"
    if ack == "?" or len(buf) < 3:
        print(f"Resposta inesperada ({len(buf)} bytes): {buf!r}", file=sys.stderr)
        return None

    stack_peak = (buf[1] << 8) | buf[2]
    payload = buf[3:]
    done_msg = None
    if payload.endswith(trailer):
        done_msg = f"DONE {cmd}"
        payload = payload[: -len(trailer)]

    sram_total = 6144
    sram_headroom = (sram_total - stack_peak) / sram_total * 100.0

    op_name = OP_NAMES[cmd]
    print(f"Operação       : {cmd} ({op_name})")
    print(f"Porta          : {port} @ {baud} bps")
    print(f"ACK recebido   : '{ack}'")
    print(f"Tempo (janela) : {t_exec * 1000:.2f} ms  (aprox. via serial até 1º byte)")
    print(f"Tempo total    : {t_total * 1000:.2f} ms  (incluindo envio de {len(payload)} B na UART)")
    print(f"Stack Peak     : {stack_peak} B / {sram_total} B  (margem: {sram_headroom:.1f}%)")

    if cmd == "K":
        state.pop("ss_enc", None)  # novo par de chaves invalida a sessão anterior
        state.pop("ss_dec", None)

    if cmd == "E" and len(payload) >= KEM_CIPHERTEXTBYTES + KEM_BYTES:
        ct_bytes = payload[:KEM_CIPHERTEXTBYTES]
        ss_enc = payload[KEM_CIPHERTEXTBYTES : KEM_CIPHERTEXTBYTES + KEM_BYTES]
        state["ss_enc"] = ss_enc
        print(f"Ciphertext (ct): {len(ct_bytes)} B ({ct_bytes[:16].hex()}...)")
        print(f"Segredo (Enc)  : {ss_enc.hex()}")
    elif cmd == "E":
        state.pop("ss_enc", None)
        print(f"[ERRO] Payload do Encaps incompleto: {len(payload)} B (esperado {KEM_CIPHERTEXTBYTES + KEM_BYTES} B)",
              file=sys.stderr)
    elif cmd == "D" and len(payload) == KEM_BYTES:
        state["ss_dec"] = payload
        print(f"Segredo (Dec)  : {payload.hex()}")
        if "ss_enc" in state:
            match = state["ss_enc"] == payload
            status_str = "[OK] CHAVES IDÊNTICAS (KEM VALIDADO!)" if match else "[ERRO] CHAVES DIFERENTES!"
            print(f"Validação KEM  : {status_str}")
    elif cmd == "M":
        dec_text = payload.decode("utf-8", errors="replace")
        print(f"Msg Original   : {msg_text!r}")
        print(f"Cifrado (UART) : {ct_msg.hex()}")
        print(f"Decifrado MCU  : {dec_text!r}")
        match = dec_text == msg_text
        print(
            f"Validação Msg  : {'[OK] MENSAGEM DECIFRADA COM SUCESSO NA PLACA!' if match else '[ERRO] Falha na decifragem!'}"
        )
    else:
        print(f"Payload        : {len(payload)} bytes")
        if payload:
            preview = payload[:16].hex()
            suffix = "..." if len(payload) > 16 else ""
            print(f"Payload (hex)  : {preview}{suffix}")

    if done_msg:
        print(f"Status final   : [OK] Placa respondeu '{done_msg}' (comando {cmd} concluído!)")
    else:
        print(f"Status final   : [OK] Recebimento concluído para o comando {cmd}.")

    return {
        "cmd": cmd,
        "op_name": op_name,
        "t_exec_ms": t_exec * 1000.0,
        "t_total_ms": t_total * 1000.0,
        "stack_peak": stack_peak,
        "sram_headroom": sram_headroom,
        "payload_bytes": len(payload),
    }


def resolve_sequence(raw_cmd: str) -> list[str] | None:
    token = raw_cmd.strip().upper()
    if token in ("B", "BATERIA", "ALL", "BATTERY"):
        return ["K", "E", "D"]
    if token in ("BM", "FULL", "TROCA"):
        return ["K", "E", "D", "M"]
    if token and all(ch in ("K", "E", "D", "M", "P") for ch in token):
        return list(token)
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Envia comando (K/E/D/M/P) ou bateria (B/BM) para a placa, troca mensagem cifrada e coleta RAW do analisador lógico."
    )
    parser.add_argument(
        "cmd",
        help="Comando: K, E, D, M (Msg cifrada), B (K->E->D), BM (K->E->D->M) ou sequência ex: KEDM",
    )
    parser.add_argument(
        "port",
        nargs="?",
        default="/dev/ttyACM0",
        help="Porta serial (padrão: /dev/ttyACM0)",
    )
    parser.add_argument(
        "-n",
        "--repeat",
        type=int,
        default=1,
        help="Número de repetições da bateria/comando (padrão: 1)",
    )
    parser.add_argument(
        "--msg",
        default="Ola Kyber512 no ATmega4809!",
        help="Mensagem em texto claro para cifrar e enviar no comando M",
    )
    parser.add_argument(
        "--la-out",
        default=None,
        help="Caminho do arquivo CSV para salvar a captura RAW do Analisador Lógico (ex: data/raw/la_kyber.csv)",
    )
    parser.add_argument(
        "--la-rate",
        type=int,
        default=100000,
        help="Taxa de amostragem do Analisador Lógico em Hz (padrão: 100000 = 100 kHz)",
    )
    parser.add_argument(
        "--la-backend",
        choices=("sigrok", "libusb"),
        default="sigrok",
        help="Backend de captura: sigrok (sigrok-cli, padrão) ou libusb (driver fx2lafw embutido)",
    )
    parser.add_argument(
        "--la-driver",
        default="fx2lafw",
        help="Driver sigrok do analisador (padrão: fx2lafw p/ Saleae Logic 8ch; ex: saleae-logic16)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.05,
        help="Intervalo em segundos entre operações na bateria (padrão: 0.05s)",
    )
    parser.add_argument(
        "--baud",
        type=int,
        default=115200,
        help="Baud rate (padrão: 115200)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Timeout máximo de espera por operação em segundos (padrão: 10.0)",
    )
    args = parser.parse_args()

    seq = resolve_sequence(args.cmd)
    if not seq:
        print(
            f"Erro: comando inválido '{args.cmd}'. Use K, E, D, M, P, B (K->E->D), BM (K->E->D->M) ou sequência como KEDM.",
            file=sys.stderr,
        )
        return 1

    total_steps = len(seq) * args.repeat
    is_battery = total_steps > 1

    try:
        fd = open_serial(args.port, args.baud)
    except OSError as e:
        print(f"Erro ao abrir {args.port}: {e}", file=sys.stderr)
        return 1

    la: SigrokLogicAnalyzer | Fx2LogicAnalyzer | None = None
    if args.la_out:
        if args.la_backend == "sigrok":
            la = SigrokLogicAnalyzer(samplerate=args.la_rate, driver=args.la_driver)
        else:
            la = Fx2LogicAnalyzer(samplerate=args.la_rate)
        if la.start():
            print(f"[LA] Captura iniciada no Saleae Logic ({args.la_backend}) @ {args.la_rate // 1000} kHz...")
            time.sleep(0.05)
        else:
            print(
                "[LA] Aviso: não foi possível iniciar o analisador lógico USB (verifique conexão/permissão).",
                file=sys.stderr,
            )
            la = None

    results: list[dict] = []
    state: dict = {}
    try:
        step_idx = 0
        for r_idx in range(1, args.repeat + 1):
            for c in seq:
                step_idx += 1
                if is_battery:
                    print(
                        f"\n--- [Rodada {r_idx}/{args.repeat} | Passo {step_idx}/{total_steps}: {c} ({OP_NAMES[c]})] ---"
                    )
                res = run_single_cmd(fd, c, args.port, args.baud, args.timeout, state, args.msg)
                if res is None:
                    return 2
                results.append(res)
                if step_idx < total_steps and args.delay > 0:
                    time.sleep(args.delay)

        if la is not None:
            time.sleep(0.05)
            raw_la = la.stop()
            la = None
            active_ch, la_events = decode_la_pulses(raw_la, args.la_rate)
            save_la_csv(args.la_out, raw_la, args.la_rate, active_ch)
            print(f"\n[LA] Captura salva em: {args.la_out} ({len(raw_la)} amostras, canal ativo: D{active_ch})")
            if la_events:
                print("\n" + "=" * 72)
                print(f"MEDIÇÕES DO ANALISADOR LÓGICO (Canal D{active_ch} @ {args.la_rate // 1000} kHz)")
                print("=" * 72)
                print(f"{'#':<4} {'Operação (ID)':<18} {'Início (s)':>12} {'Largura Pulso (ms)':>20} {'Ciclos (@20MHz)':>16}")
                print("-" * 72)
                for idx, ev in enumerate(la_events, 1):
                    cycles = int(round(ev["width_ms"] * 20_000))
                    print(
                        f"{idx:<4} {ev['op']:<18} {ev['t_start_s']:>12.4f} {ev['width_ms']:>20.3f} {cycles:>16,}"
                    )
                print("=" * 72)

        if is_battery:
            print("\n" + "=" * 72)
            print(f"RESUMO DA BATERIA ({args.repeat}x {' -> '.join(seq)})")
            print("=" * 72)
            print(f"{'Op':<14} {'N':>4} {'Média (ms)':>12} {'Min (ms)':>10} {'Max (ms)':>10} {'Stack Peak':>14}")
            print("-" * 72)
            for op_code in ("K", "E", "D", "M"):
                op_rows = [r for r in results if r.get("cmd") == op_code]
                if not op_rows:
                    continue
                times = [r["t_exec_ms"] for r in op_rows]
                peaks = [r["stack_peak"] for r in op_rows]
                mean_t = statistics.mean(times)
                min_t = min(times)
                max_t = max(times)
                max_pk = max(peaks)
                label = f"{op_code} ({OP_NAMES[op_code]})"
                print(f"{label:<14} {len(op_rows):>4} {mean_t:>12.2f} {min_t:>10.2f} {max_t:>10.2f} {max_pk:>9} B")
            print("=" * 72)

        return 0
    finally:
        if la is not None:
            la.stop()
        os.close(fd)


if __name__ == "__main__":
    sys.exit(main())
