"""Gera as figuras do SUT e da bancada de medição (CMP223).

Saídas (em slides/figures/):
  sut_esquematico_v3.{svg,pdf,png}  esquemático elétrico
  sut_bancada_v3.{svg,pdf,png}      diagrama de ligações da bancada
  sut_fluxo_v3.gif                  fluxo animado das 4 fases do experimento

Uso:  python slides/figures/src/gerar_figuras_sut.py
Requer: matplotlib, numpy, pillow.
"""

from __future__ import annotations

import io
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Circle, FancyBboxPatch, Polygon, Rectangle  # noqa: E402
from PIL import Image  # noqa: E402

OUT = Path(__file__).resolve().parent.parent

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "svg.fonttype": "path",
        "pdf.fonttype": 42,
        "axes.unicode_minus": False,
    }
)

# ---------------------------------------------------------------- paleta
INK = "#0f172a"
MUTED = "#64748b"
FAINT = "#94a3b8"
LINE_OFF = "#e2e8f0"
PWR = "#b91c1c"
SENSE = "#1d4ed8"
TRIG = "#047857"
SERIAL = "#7c3aed"
ORANGE = "#c2410c"
FILL_IC = "#fffbeb"
FILL_MOD = "#f8fafc"

W_UNITS, H_UNITS = 320, 180  # sistema de coordenadas (16:9), y para cima

A = None  # eixo corrente


def new_canvas(w_in=16, h_in=9):
    global A
    fig = plt.figure(figsize=(w_in, h_in))
    A = fig.add_axes([0, 0, 1, 1])
    A.set_xlim(0, W_UNITS)
    A.set_ylim(0, H_UNITS)
    A.set_aspect("equal")
    A.axis("off")
    fig.patch.set_facecolor("white")
    return fig


# ---------------------------------------------------------------- primitivas
def T(x, y, s, size=7, c=INK, ha="left", va="center", w="normal", **kw):
    A.text(x, y, s, fontsize=size, color=c, ha=ha, va=va, fontweight=w, zorder=8, **kw)


def W(pts, c=INK, lw=1.3, ls="-", z=2, alpha=1.0):
    xs, ys = zip(*pts)
    A.plot(xs, ys, color=c, lw=lw, ls=ls, solid_capstyle="round",
           solid_joinstyle="round", dash_capstyle="butt", zorder=z, alpha=alpha)


def J(x, y, c=INK, r=0.85):
    A.add_patch(Circle((x, y), r, color=c, zorder=6))


def BOX(x, y, w, h, fc="white", ec=INK, lw=1.2, ls="-", r=0.0, z=1, alpha=1.0):
    if r:
        p = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                           fc=fc, ec=ec, lw=lw, ls=ls, zorder=z, alpha=alpha)
    else:
        p = Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw, ls=ls, zorder=z, alpha=alpha)
    A.add_patch(p)


def GND(x, y, c=INK, lead=3.0):
    W([(x, y), (x, y - lead)], c)
    for i, hw in enumerate((2.4, 1.6, 0.8)):
        yy = y - lead - i * 1.0
        W([(x - hw, yy), (x + hw, yy)], c, lw=1.3)


def RES_V(x, ytop, ybot, c=INK, body=10.0, amp=1.3, n=6):
    m = (ytop + ybot) / 2
    pts = [(x, ytop), (x, m + body / 2)]
    for i in range(n):
        pts.append((x + (amp if i % 2 == 0 else -amp), m + body / 2 - (i + 0.5) * body / n))
    pts += [(x, m - body / 2), (x, ybot)]
    W(pts, c, lw=1.3)


def RES_H(x1, x2, y, c=INK, body=10.0, amp=1.3, n=6, lead_c=None):
    m = (x1 + x2) / 2
    lc = lead_c or c
    W([(x1, y), (m - body / 2, y)], lc, lw=1.6)
    W([(m + body / 2, y), (x2, y)], lc, lw=1.6)
    pts = [(m - body / 2, y)]
    for i in range(n):
        pts.append((m - body / 2 + (i + 0.5) * body / n, y + (amp if i % 2 == 0 else -amp)))
    pts.append((m + body / 2, y))
    W(pts, c, lw=1.3)


def CAP_V(x, ytop, ybot, lead_top=INK, lead_bot=INK, polar=True, plus=True):
    m = (ytop + ybot) / 2
    g = 0.8
    W([(x, ytop), (x, m + g)], lead_top)
    W([(x - 2.4, m + g), (x + 2.4, m + g)], INK, lw=1.8)
    if polar:
        dx = np.linspace(-2.4, 2.4, 30)
        W(list(zip(x + dx, m - g - 0.8 * (1 - (dx / 2.4) ** 2))), INK, lw=1.8)
        W([(x, m - g - 0.8), (x, ybot)], lead_bot)
    else:
        W([(x - 2.4, m - g), (x + 2.4, m - g)], INK, lw=1.8)
        W([(x, m - g), (x, ybot)], lead_bot)
    if plus:
        T(x - 3.4, m + g + 1.4, "+", 6, PWR, ha="center", w="bold")


def IND_H(x1, x2, y, c=INK, lead_c=None, humps=4, body=14.0):
    m = (x1 + x2) / 2
    lc = lead_c or c
    a, b = m - body / 2, m + body / 2
    W([(x1, y), (a, y)], lc, lw=1.6)
    W([(b, y), (x2, y)], lc, lw=1.6)
    r = body / humps / 2
    for k in range(humps):
        cx = a + r + 2 * r * k
        th = np.linspace(math.pi, 0, 20)
        W(list(zip(cx + r * np.cos(th), y + r * np.sin(th))), c, lw=1.3)


def DIODE_H(x1, x2, y, c=INK, lead_c=None):
    m = (x1 + x2) / 2
    lc = lead_c or c
    W([(x1, y), (m - 1.8, y)], lc, lw=1.6)
    W([(m + 1.8, y), (x2, y)], lc, lw=1.6)
    A.add_patch(Polygon([(m - 1.8, y + 2.0), (m - 1.8, y - 2.0), (m + 1.8, y)],
                        closed=True, fc=FILL_IC, ec=c, lw=1.3, zorder=4))
    W([(m + 1.8, y + 2.0), (m + 1.8, y - 2.0)], c, lw=1.6)


def BAT_V(x, ytop, ybot):
    """Duas células; placa longa = positivo (topo)."""
    m = (ytop + ybot) / 2
    ys = [m + 3.0, m + 1.6, m - 1.6, m - 3.0]
    W([(x, ytop), (x, ys[0])], PWR, lw=1.6)
    for i, yy in enumerate(ys):
        if i % 2 == 0:
            W([(x - 2.8, yy), (x + 2.8, yy)], INK, lw=1.4)
        else:
            W([(x - 1.5, yy), (x + 1.5, yy)], INK, lw=2.8)
    W([(x, ys[-1]), (x, ybot)], INK, lw=1.6)
    T(x + 3.8, ys[0] + 0.6, "+", 6.5, PWR, ha="center", w="bold")


def TP(x, y, name, sub, c):
    W([(x, y), (x, y + 4.6)], c, lw=1.3)
    A.add_patch(Circle((x, y + 5.8), 1.2, fc="white", ec=c, lw=1.4, zorder=6))
    T(x, y + 11.6, name, 6.2, c, ha="center", w="bold")
    T(x, y + 8.9, sub, 5.4, MUTED, ha="center")


def PAD(x, y, c=INK):
    A.add_patch(Rectangle((x - 1.0, y - 1.0), 2.0, 2.0, fc=c, ec=c, zorder=6))


def arrowhead(p_from, p_to, c, size=2.4):
    (x0, y0), (x1, y1) = p_from, p_to
    d = np.array([x1 - x0, y1 - y0], dtype=float)
    d /= np.linalg.norm(d)
    n = np.array([-d[1], d[0]])
    tip = np.array([x1, y1])
    base = tip - d * size
    A.add_patch(Polygon([tip, base + n * size * 0.5, base - n * size * 0.5],
                        closed=True, fc=c, ec=c, lw=0.5, zorder=7))


def sheet_frame():
    BOX(2, 2, 316, 176, fc="none", ec=INK, lw=1.4)
    BOX(5, 5, 310, 170, fc="none", ec=MUTED, lw=0.6)
    cw = 310 / 6
    for i in range(6):
        cx = 5 + cw * (i + 0.5)
        T(cx, 176.5, str(i + 1), 5, MUTED, ha="center")
        T(cx, 3.5, str(i + 1), 5, MUTED, ha="center")
        if i:
            for yy in ((175, 178), (2, 5)):
                W([(5 + cw * i, yy[0]), (5 + cw * i, yy[1])], MUTED, lw=0.6)
    rh = 170 / 4
    for j, L in enumerate("ABCD"):
        cy = 175 - rh * (j + 0.5)
        T(3.5, cy, L, 5, MUTED, ha="center")
        T(316.5, cy, L, 5, MUTED, ha="center")
        if j:
            for xx in ((2, 5), (315, 318)):
                W([(xx[0], 175 - rh * j), (xx[1], 175 - rh * j)], MUTED, lw=0.6)


# ================================================================ ESQUEMÁTICO
def esquematico():
    fig = new_canvas()
    sheet_frame()
    R = 128  # trilho principal

    T(10, 168, "Esquemático elétrico — alimentação limpa, shunt de medição e SUT", 11, w="bold")
    T(10, 162.5, "Arduino Nano Every (ATmega4809 @ 20 MHz) alimentado por bateria isolada do USB; "
                 "medição de corrente high-side com sense Kelvin no shunt", 7, MUTED)

    # ---- J1 USB-C (recarga)
    BOX(10, 112, 14, 22, fc=FILL_IC)
    T(17, 136.8, "J1  USB-C", 6.5, w="bold", ha="center")
    T(22.6, 128, "VBUS", 5.4, ha="right")
    T(22.6, 116, "GND", 5.4, ha="right")
    T(17, 108.5, "só recarga\n(desligado na\nmedição)", 5.2, MUTED, ha="center", va="top")
    W([(24, 128), (40, 128)], PWR, lw=1.6)
    W([(24, 116), (40, 116)])

    # ---- U1 TP4056 + DW01A
    BOX(40, 106, 30, 32, fc=FILL_IC, lw=1.3)
    T(55, 141.2, "U1  módulo TP4056 + DW01A", 6.5, w="bold", ha="center")
    T(41.3, 128, "IN+", 5.4)
    T(41.3, 116, "IN−", 5.4)
    T(68.7, 128, "OUT+", 5.4, ha="right")
    T(68.7, 116, "OUT−", 5.4, ha="right")
    T(48, 108.2, "B+", 5.4, ha="center")
    T(62, 108.2, "B−", 5.4, ha="center")
    T(55, 124.2, "carga CC/CV", 6, ORANGE, ha="center", w="bold")
    T(55, 120.6, "proteção BMS", 5.4, MUTED, ha="center")

    # ---- BT1
    W([(48, 106), (48, 99)], PWR, lw=1.6)
    BAT_V(48, 99, 87)
    W([(48, 87), (48, 82), (62, 82), (62, 106)], INK, lw=1.6)
    BOX(43.3, 85.3, 9.4, 15.4, fc="none", ec=MUTED, lw=0.8, ls=(0, (3, 2)))
    T(41.5, 96, "BT1", 6.5, w="bold", ha="right")
    T(41.5, 92.5, "Li-ion 18650", 5.6, ha="right")
    T(41.5, 89.3, "3,7 V (4,2 V)", 5.4, MUTED, ha="right")

    W([(70, 128), (85.1, 128)], PWR, lw=1.6)
    W([(70, 116), (76, 116)])
    GND(76, 116)

    # ---- SW1 SPDT
    for (cx, cy) in ((86, 128), (96, 131.5), (96, 124.5)):
        A.add_patch(Circle((cx, cy), 0.9, fc="white", ec=INK, lw=1.2, zorder=6))
    W([(86.8, 128.4), (95.2, 131.2)], PWR, lw=1.7)
    W([(96.9, 131.5), (100, 131.5), (100, R), (106, R)], PWR, lw=1.6)
    W([(96.9, 124.5), (99, 124.5)])
    W([(98.4, 123.9), (99.6, 125.1)], lw=1.0)
    W([(98.4, 125.1), (99.6, 123.9)], lw=1.0)
    T(91, 137, "SW1", 6.5, w="bold", ha="center")
    T(91, 120.5, "SPDT", 5.4, MUTED, ha="center")

    # ---- U2 módulo MT3608
    BOX(106, 76, 96, 70, fc=FILL_MOD, ec=MUTED, lw=0.9, ls=(0, (4, 2)))
    T(108.5, 142.5, "U2  módulo step-up MT3608", 6.8, w="bold")
    PAD(106, R, PWR)
    PAD(202, R, PWR)
    T(108, 131, "VIN+", 5, MUTED)
    T(200, 131, "VOUT+", 5, MUTED, ha="right")
    W([(106, R), (122, R)], PWR, lw=1.6)
    J(114, R, PWR)
    CAP_V(114, R, 110, lead_top=PWR, plus=False, polar=False)
    GND(114, 110)
    T(111.6, 120, "C2", 5.8, w="bold", ha="right")
    T(111.6, 116.6, "22 µF", 5.2, ha="right")
    J(122, R, PWR)
    IND_H(122, 146, R, lead_c=PWR)
    T(134, 133.2, "L1  22 µH", 5.6, ha="center")
    J(146, R, PWR)
    BOX(128, 96, 26, 18, fc=FILL_IC, lw=1.3)
    T(141, 107.4, "MT3608", 6.2, w="bold", ha="center")
    W([(122, R), (122, 101), (128, 101)], PWR)
    W([(122, 110), (128, 110)], PWR)
    J(122, 110, PWR)
    T(129.1, 110, "IN", 5)
    T(129.1, 101, "EN", 5)
    W([(146, 114), (146, R)], PWR)
    T(146, 112.4, "SW", 5, ha="center")
    W([(141, 96), (141, 92)])
    GND(141, 92)
    T(141, 97.6, "GND", 4.8, ha="center")
    W([(154, 104), (170, 104)])
    T(152.9, 104, "FB", 5, ha="right")
    DIODE_H(146, 170, R, lead_c=PWR)
    T(158, 133.2, "D1  SS34", 5.6, ha="center")
    J(170, R, PWR)
    RES_V(170, R, 104, body=12)
    W([(170, R), (170, 122)], PWR)
    A.annotate("", xy=(174, 121.5), xytext=(166, 110.5),
               arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.0, mutation_scale=7), zorder=7)
    J(170, 104)
    RES_V(170, 104, 88, body=9)
    GND(170, 88)
    T(165, 119.5, "RV1", 5.8, w="bold", ha="right")
    T(165, 116.2, "100 kΩ", 5.2, ha="right")
    T(165, 97.5, "R2", 5.8, w="bold", ha="right")
    T(165, 94.2, "2,2 kΩ", 5.2, ha="right")
    W([(170, R), (202, R)], PWR, lw=1.6)
    J(186, R, PWR)
    CAP_V(186, R, 110, lead_top=PWR, plus=False, polar=False)
    GND(186, 110)
    T(189, 120, "C3", 5.8, w="bold")
    T(189, 116.6, "22 µF", 5.2)
    T(108.5, 80, "V_OUT = 0,6 V · (1 + RV1/R2)  →  RV1 ajustado para 5,00 V", 5.6, MUTED)

    # ---- trilho +5V_REG, C1, shunt
    W([(202, R), (226, R)], PWR, lw=1.8)
    J(207, R, PWR)
    TP(207, R, "TP1", "DMM1", MUTED)
    J(212, R, PWR)
    CAP_V(212, R, 110, lead_top=PWR)
    GND(212, 110)
    T(215, 120, "C1", 5.8, w="bold")
    T(215, 116.6, "10–100 µF", 5.2)
    T(215.5, 130.2, "+5V_REG", 5.4, PWR, ha="center", w="bold")
    J(224, R, SENSE)
    TP(224, R, "TP2", "S+", SENSE)
    RES_H(224, 244, R, body=10, lead_c=PWR)
    T(234, 123.6, "R_shunt", 6.2, w="bold", ha="center")
    T(234, 120.2, "1–10 Ω · 0,1 %", 5.2, ha="center")
    J(244, R, SENSE)
    TP(244, R, "TP3", "S−", SENSE)
    W([(244, R), (260, R)], PWR, lw=1.8)
    T(250.5, 130.2, "+5V_SUT", 5.4, PWR, ha="center", w="bold")

    # ---- U3 Arduino Nano Every
    BOX(256, 34, 57, 116, fc=FILL_MOD, ec=MUTED, lw=0.9, ls=(0, (4, 2)))
    T(258.5, 146.5, "U3  Arduino Nano Every (SUT)", 6.8, SENSE, w="bold")
    PAD(256, R, PWR)
    T(257.6, 131, "5V", 5, MUTED)
    BOX(264, 104, 30, 36, fc=FILL_IC, lw=1.3)
    W([(260, R), (264, R)], PWR)
    T(265.2, R, "VDD", 5)
    T(279, 137.4, "ATmega4809", 6.2, SENSE, ha="center", w="bold")
    T(278, 132.6, "AVRxt, 8 bits", 5, ha="center")
    T(278, 129.0, "20 MHz", 5, ha="center")
    T(278, 125.4, "48 KB Flash", 5, MUTED, ha="center")
    T(278, 121.8, "6 KB SRAM", 5, MUTED, ha="center")
    pins_r = [(134, "PA0 (D2)"), (124, "PB4 TX"), (119, "PB5 RX"), (112, "UPDI")]
    for y, name in pins_r:
        W([(294, y), (298, y)])
        T(292.9, y, name, 4.9, ha="right")
    W([(284, 104), (284, 100)])
    GND(284, 100)
    T(284, 105.7, "GND", 4.6, ha="center")
    # pinos USART1 (rota alternativa) usados pelo cabo TTL: D0 = PC5 (RX1), D1 = PC4 (TX1)
    for y, pin, name in ((114, "D0", "PC5 RX1"), (109.5, "D1", "PC4 TX1")):
        W([(256, y), (264, y)], SERIAL, lw=1.3)
        PAD(256, y, SERIAL)
        T(265.2, y, name, 4.9)
    T(257.6, 116.6, "D0", 4.6, MUTED)
    T(257.6, 106.9, "D1", 4.6, MUTED)

    # ---- J3 cabo USB-TTL (host)
    BOX(226, 80, 18, 21, fc="#f5f3ff", ec=SERIAL, lw=1.3)
    T(235, 104, "J3  cabo USB-TTL", 6.2, SERIAL, w="bold", ha="center")
    T(235, 76.8, "→ host · 5 V · 115200 bps", 4.8, MUTED, ha="center")
    for y, name in ((97, "TXD"), (92, "RXD"), (87, "GND"), (82.5, "VCC")):
        T(242.8, y, name, 4.8, ha="right")
    W([(244, 97), (252, 97), (252, 114), (256, 114)], SERIAL, lw=1.3)
    W([(244, 92), (254, 92), (254, 109.5), (256, 109.5)], SERIAL, lw=1.3)
    W([(244, 87), (248, 87)])
    GND(248, 87, lead=1.5)
    W([(244, 82.5), (246.5, 82.5)], lw=1.0)
    W([(246, 81.9), (247.2, 83.1)], lw=1.0)
    W([(246, 83.1), (247.2, 81.9)], lw=1.0)
    T(248.2, 82.5, "n.c.", 4.6, MUTED)
    # TP4 / trigger
    W([(298, 134), (307, 134)], TRIG, lw=1.5)
    J(307, 134, TRIG)
    TP(307, 134, "TP4", "D2/PA0", TRIG)

    # U4 ATSAMD11
    BOX(264, 58, 30, 26, fc=FILL_IC, lw=1.3)
    T(278, 77.5, "ATSAMD11D14A", 5.6, w="bold", ha="center")
    T(278, 73.6, "USB ↔ UART/UPDI", 5, ha="center")
    T(278, 70.0, "(consumo no", 4.6, MUTED, ha="center")
    T(278, 67.2, "baseline)", 4.6, MUTED, ha="center")
    for y, name in ((78, "UPDI"), (72, "TX"), (66, "RX")):
        W([(294, y), (298, y)])
        T(292.9, y, name, 4.9, ha="right")
    W([(298, 112), (299, 112), (299, 78), (298, 78)], lw=1.1)
    W([(298, 119), (302, 119), (302, 72), (298, 72)], lw=1.1)
    W([(298, 124), (305, 124), (305, 66), (298, 66)], lw=1.1)
    W([(270, 84), (270, 89.5)], PWR)
    W([(268, 89.5), (272, 89.5)], PWR, lw=1.5)
    T(270, 92.0, "+3V3", 5, PWR, ha="center", w="bold")
    T(270, 82.4, "VDD", 4.6, ha="center")
    W([(264, 64), (260, 64)])
    GND(260, 64)
    T(265.2, 64, "GND", 4.6)
    for x, name in ((272, "D+"), (280, "D−")):
        W([(x, 58), (x, 49)])
        T(x, 59.7, name, 4.6, ha="center")
    BOX(266, 41, 22, 8, fc="#e2e8f0", lw=1.2)
    T(277, 45, "J2  µUSB", 5.6, w="bold", ha="center")
    T(277, 37.6, "→ host: só gravação UPDI", 4.8, MUTED, ha="center")

    # ---- instrumentação
    BOX(10, 34, 240, 38, fc="white", ec=SENSE, lw=0.9, ls=(0, (4, 2)))
    T(13, 68, "INSTRUMENTAÇÃO EXTERNA (pontas de prova nos pontos de teste)", 6.8, SENSE, w="bold")
    cols = [
        (13, "OSC1  osciloscópio (2 canais + EXT TRIG)", SENSE,
         ["CH1 → TP2 (S+)        CH2 → TP3 (S−)",
          "MATH = CH1 − CH2 = v_shunt",
          "EXT TRIG → TP4 (D2/PA0)   ·   terra → GND"]),
        (95, "LA1  analisador lógico (24 MHz)", TRIG,
         ["CH0 → TP4 (D2/PA0)   ·   GND → GND",
          "T_exec = t1 − t0 (bordas de D2)",
          "resolução ≈ 42 ns"]),
        (177, "DMM1  multímetro", ORANGE,
         ["V+ → TP1 (+5V_REG)  ·  COM → GND",
          "ajuste de RV1 até 5,00 V",
          "antes de conectar o SUT"]),
    ]
    for x, title, c, lines in cols:
        BOX(x, 37, 70 if x == 177 else 78, 26, fc=FILL_MOD, ec=c, lw=1.0, r=1.2)
        T(x + 2.5, 59, title, 6.2, c, w="bold")
        for k, s in enumerate(lines):
            T(x + 3.5, 53.2 - k * 5.2, s, 5.6)

    # ---- notas e carimbo
    BOX(10, 8, 190, 23, fc="white", ec=INK, lw=1.0)
    T(13, 27.6, "NOTAS", 6.2, w="bold")
    notas = [
        "1. Todos os símbolos GND são a mesma malha; a referência do sistema é OUT− de U1.",
        "2. Medição high-side: v_shunt = V(TP2) − V(TP3);  I_SUT(t) = v_shunt(t) / R_shunt.",
        "3. P_SUT(t) = V(TP3) · I_SUT(t);  E_op = ∫ P_SUT dt na janela marcada por D2/PA0.",
        "4. J1 e J2 desconectados na captura; o host fica ligado só por J3 (TXD, RXD, GND; VCC n.c.).",
    ]
    for k, s in enumerate(notas):
        T(13, 23.4 - k * 4.1, s, 5.5)
    BOX(204, 8, 109, 23, fc=FILL_MOD, ec=INK, lw=1.0)
    W([(204, 23.5), (313, 23.5)], lw=0.7)
    W([(204, 15.5), (313, 15.5)], lw=0.7)
    W([(278, 8), (278, 23.5)], lw=0.7)
    T(206.5, 27.2, "SUT & ALIMENTAÇÃO LIMPA — ESQUEMÁTICO", 6.6, w="bold")
    T(206.5, 19.5, "CMP223 · PQC em sistemas embarcados", 5.4)
    T(206.5, 11.7, "Eduardo S. Abdala (INF-UFRGS)", 5.4)
    T(280.5, 19.5, "IEC 60617", 5.4, MUTED)
    T(280.5, 11.7, "Rev. 3.0 · Folha 1/1", 5.4, w="bold")

    save(fig, "sut_esquematico_v3")


# ================================================================ BANCADA / FLUXO
BLOCKS = {
    #        x    y    w   h   título                     linhas                                         cor
    "B1":  (8, 112, 50, 24, "Bateria 18650", ["BT1 Li-ion 3,7 V (4,2 V)", "TP4056 + BMS (DW01A)"], ORANGE),
    "SW":  (66, 114, 20, 20, "SW1", [], ORANGE),
    "U2":  (94, 112, 46, 24, "MT3608 step-up", ["3,7 V → 5,00 V", "trimpot RV1"], ORANGE),
    "SH":  (158, 114, 30, 20, "R_shunt", ["1–10 Ω · 0,1 %"], PWR),
    "SUT": (198, 108, 52, 32, "Arduino Nano Every", ["ATmega4809 @ 20 MHz", "D0/D1: UART (TTL)", "D2 (PA0): trigger"], SENSE),
    "OSC": (262, 104, 50, 42, "Osciloscópio", ["CH1 S+ · CH2 S− · EXT D2"], SENSE),
    "LA":  (262, 56, 50, 40, "Analisador lógico", ["CH0 = D2 · 24 MHz"], TRIG),
    "DMM": (91, 60, 40, 30, "Multímetro (DMM1)", [], ORANGE),
    "HOST": (206, 48, 44, 22, "Host (PC)", ["TTL: comandos/resultados", "µUSB: gravação UPDI"], "#334155"),
    "TTL": (206, 80, 24, 14, "USB-TTL", [], SERIAL),
}

PATHS = {
    "pw1": ([(58, 124), (66, 124)], "pwr"),
    "pw2": ([(86, 124), (94, 124)], "pwr"),
    "pw3": ([(140, 124), (158, 124)], "pwr"),
    "pw4": ([(188, 124), (198, 124)], "pwr"),
    "sp": ([(163, 136), (163, 151), (300, 151), (300, 146)], "sense"),
    "sn": ([(183, 136), (183, 148), (290, 148), (290, 146)], "sense"),
    "tosc": ([(250, 128), (262, 128)], "trig"),
    "tla": ([(250, 128), (258, 128), (258, 76), (262, 76)], "trig"),
    "dmm": ([(111, 112), (111, 90)], "temp"),
    "usb": ([(243, 108), (243, 70)], "temp"),
    "ttl1": ([(218, 108), (218, 94)], "serial"),
    "ttl2": ([(218, 80), (218, 70)], "serial"),
}
BIDIR = {"usb", "ttl1", "ttl2"}
CLS_COLOR = {"pwr": PWR, "sense": SENSE, "trig": TRIG, "temp": MUTED, "serial": SERIAL}

PHASES = [
    dict(title="Fase 1/4 — Calibração da alimentação",
         desc="SW1 ligada: a bateria alimenta o MT3608 e o DMM1 mede a saída enquanto o trimpot RV1 "
              "é ajustado para 5,00 V, ainda sem o SUT.",
         color=ORANGE, blocks={"B1", "SW", "U2", "DMM"}, paths={"pw1", "pw2", "dmm"}, sw=True),
    dict(title="Fase 2/4 — Gravação do firmware (UPDI)",
         desc="SW1 desligada: o host alimenta o SUT pelo µUSB apenas para gravar o firmware via UPDI; "
              "depois o cabo µUSB é removido.",
         color=SENSE, blocks={"SUT", "HOST"}, paths={"usb"}, sw=False),
    dict(title="Fase 3/4 — Execução com alimentação isolada",
         desc="A bateria alimenta o SUT por MT3608 → C1 → R_shunt; o host envia comandos e recebe "
              "resultados e stack watermark pelo cabo USB-TTL (TXD, RXD, GND).",
         color=PWR, blocks={"B1", "SW", "U2", "SH", "SUT", "TTL", "HOST"},
         paths={"pw1", "pw2", "pw3", "pw4", "ttl1", "ttl2"}, sw=True),
    dict(title="Fase 4/4 — Captura sincronizada",
         desc="D2/PA0 marca cada operação: dispara o EXT TRIG do osciloscópio e o analisador lógico, "
              "enquanto CH1 − CH2 registra v_shunt(t). A UART fica em silêncio na janela.",
         color=TRIG, blocks={"B1", "SW", "U2", "SH", "SUT", "OSC", "LA", "TTL", "HOST"},
         paths={"pw1", "pw2", "pw3", "pw4", "sp", "sn", "tosc", "tla", "ttl1", "ttl2"},
         still={"ttl1", "ttl2"}, sw=True),
]

def path_len(pts):
    return sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def point_at(pts, s):
    for i in range(len(pts) - 1):
        seg = math.dist(pts[i], pts[i + 1])
        if s <= seg or i == len(pts) - 2:
            f = 0 if seg == 0 else min(1.0, s / seg)
            return (pts[i][0] + f * (pts[i + 1][0] - pts[i][0]),
                    pts[i][1] + f * (pts[i + 1][1] - pts[i][1]))
        s -= seg
    return pts[-1]


def flow_dots(pts, t, c, spacing=6.0, reverse=False, r=0.95):
    L = path_len(pts)
    s = (t * spacing * 3) % spacing
    while s < L:
        x, y = point_at(pts, L - s if reverse else s)
        A.add_patch(Circle((x, y), r, fc=c, ec="white", lw=0.6, zorder=9))
        s += spacing


def draw_block(key, active, accent=None):
    x, y, w, h, title, lines, color = BLOCKS[key]
    color = accent or color
    if active:
        BOX(x - 1.2, y - 1.2, w + 2.4, h + 2.4, fc=color, ec="none", r=3.2, alpha=0.10, z=1)
    BOX(x, y, w, h, fc="white", ec=color if active else "#cbd5e1", lw=2.0 if active else 1.2, r=2.2, z=2)
    tc = color if active else FAINT
    lc = INK if active else FAINT
    T(x + w / 2, y + h - 5, title, 10.5 if w > 30 else 10, tc, ha="center", w="bold")
    for k, s in enumerate(lines):
        T(x + w / 2, y + h - 11.5 - k * 4.8, s, 8.2, lc, ha="center")


def osc_screen(active, prog, show_all):
    x0, y0, x1, y1 = 265, 107, 309, 129
    BOX(x0, y0, x1 - x0, y1 - y0, fc="#0b1220", ec="#334155", lw=1.0, r=1.0, z=3)
    for gx in np.linspace(x0, x1, 9)[1:-1]:
        W([(gx, y0 + 0.5), (gx, y1 - 0.5)], "#1e293b", lw=0.5, z=3)
    for gy in np.linspace(y0, y1, 5)[1:-1]:
        W([(x0 + 0.5, gy), (x1 - 0.5, gy)], "#1e293b", lw=0.5, z=3)
    if not active:
        return
    xs = np.linspace(x0 + 1, x1 - 1, 220)
    u = (xs - xs[0]) / (xs[-1] - xs[0])
    rng = np.random.default_rng(3)
    on = (u > 0.18) & (u < 0.82)
    ys = y0 + 4 + on * 10 + rng.normal(0, 0.35, xs.size) + on * 1.3 * np.sin(u * 90)
    n = xs.size if show_all else max(2, int(prog * xs.size))
    A.plot(xs[:n], ys[:n], color="#38bdf8", lw=1.2, zorder=4)
    if show_all or prog > 0.85:
        T(x0 + 2, y1 - 2.8, "E_op = ∫ V_SUT · I_SUT dt", 7, "#7dd3fc", w="bold")
    T(x0 + 2, y0 + 1.8, "CH1 − CH2", 6, "#94a3b8")


def la_screen(active, prog, show_all):
    x0, y0, x1, y1 = 265, 59, 309, 81
    BOX(x0, y0, x1 - x0, y1 - y0, fc="#0b1220", ec="#334155", lw=1.0, r=1.0, z=3)
    if not active:
        return
    xs = np.linspace(x0 + 1, x1 - 1, 400)
    u = (xs - xs[0]) / (xs[-1] - xs[0])
    on = (u > 0.18) & (u < 0.82)
    ys = y0 + 4 + on * 9.0
    n = xs.size if show_all else max(2, int(prog * xs.size))
    A.plot(xs[:n], ys[:n], color="#34d399", lw=1.5, zorder=4, drawstyle="steps-post")
    xa, xb = x0 + 1 + 0.18 * (x1 - x0 - 2), x0 + 1 + 0.82 * (x1 - x0 - 2)
    if show_all or prog > 0.2:
        T(xa, y0 + 1.8, "t0", 6.5, "#a7f3d0", ha="center")
    if show_all or prog > 0.85:
        T(xb, y0 + 1.8, "t1", 6.5, "#a7f3d0", ha="center")
        A.annotate("", xy=(xb, y1 - 3.5), xytext=(xa, y1 - 3.5),
                   arrowprops=dict(arrowstyle="<->", color="#a7f3d0", lw=0.9, mutation_scale=7), zorder=5)
        T((xa + xb) / 2, y1 - 1.6, "T_exec = t1 − t0", 6.5, "#a7f3d0", ha="center", w="bold")


def dmm_display(active, value):
    BOX(98, 65, 26, 13, fc="#ecfccb" if active else "#f1f5f9", ec="#475569", lw=1.0, r=1.0, z=3)
    T(111, 71.5, value if active else "– – –", 12 if active else 10, "#1a2e05" if active else FAINT,
      ha="center", w="bold", family="DejaVu Sans Mono")


def sw_glyph(active, closed, color):
    c = color if active else FAINT
    W([(66, 124), (70, 124)], c, lw=1.6, z=3)
    W([(82, 124), (86, 124)], c, lw=1.6, z=3)
    for cx in (70.8, 81.2):
        A.add_patch(Circle((cx, 124), 0.9, fc="white", ec=c, lw=1.3, zorder=5))
    if closed:
        W([(71.6, 124.3), (80.4, 124.6)], c, lw=2.0, z=4)
        T(76, 118.0, "ligada", 7.5, c, ha="center")
    else:
        W([(71.6, 124.4), (79.6, 126.7)], c, lw=2.0, z=4)
        T(76, 118.0, "desligada", 7.5, c, ha="center")


def legend():
    BOX(8, 5, 304, 22, fc="#f8fafc", ec="#e2e8f0", lw=1.0, r=1.5)
    items = [(PWR, "-", "Alimentação (bateria → +5 V)"), (INK, "-", "GND comum"),
             (SENSE, "-", "Sense Kelvin (S+, S−)"), (TRIG, "-", "Trigger D2/PA0"),
             (SERIAL, "-", "Serial TTL (TX, RX, GND)"), (MUTED, "--", "Ligação temporária (DMM1, µUSB)")]
    for x, (c, ls, s) in zip((13, 64, 97, 141, 175, 223), items):
        W([(x, 20.5), (x + 9, 20.5)], c, lw=2.2, ls=ls)
        T(x + 11, 20.5, s, 8.2)
    T(13, 11.5, "Montagem em protoboard (400/830 pts) com jumpers M-M / M-F.   "
                "I_SUT = v_shunt / R_shunt;   E_op = ∫ V_SUT · I_SUT dt na janela de D2.", 8.2, MUTED)


def bancada(phase=None, t=1.0):
    """phase=None: diagrama estático completo; phase=0..3: quadro do GIF."""
    fig = new_canvas()
    static = phase is None
    ph = PHASES[phase] if not static else None
    act_b = set(BLOCKS) if static else ph["blocks"]
    act_p = set(PATHS) if static else ph["paths"]
    accent = None if static else ph["color"]

    # cabeçalho
    if static:
        T(10, 170, "Bancada de medição do SUT — ligações físicas", 15, w="bold")
        T(10, 163.5, "Bateria isolada do USB → step-up 5,00 V → shunt de precisão → Arduino Nano Every; "
                     "osciloscópio e analisador lógico sincronizados por D2/PA0", 9.5, MUTED)
    else:
        BOX(8, 156, 304, 20, fc="white", ec=accent, lw=2.0, r=2.0)
        T(12, 170.2, ph["title"], 14, accent, w="bold")
        T(12, 162.6, ph["desc"], 8.8, INK)
        for k in range(4):
            on = k == phase
            A.add_patch(Circle((286 + k * 7, 170.2), 2.1 if on else 1.4,
                               fc=PHASES[k]["color"] if on else "#cbd5e1", ec="none", zorder=5))

    # GND comum
    gnd_drops = [(33, 112), (136, 112), (201, 108)]
    W([(33, 38), (316, 38)], INK, lw=1.6)
    for x, ytop in gnd_drops:
        W([(x, ytop), (x, 38)], INK, lw=1.3)
        J(x, 38)
    W([(312, 127), (316, 127), (316, 38)], INK, lw=1.3)
    W([(312, 80), (316, 80)], INK, lw=1.3)
    J(316, 80)
    GND(170, 38)
    T(174, 33.8, "GND comum", 8.2, INK, w="bold")

    # C1 no trilho de +5 V
    c1_on = static or "pw3" in act_p
    W([(149, 124), (149, 104)], PWR if c1_on else LINE_OFF, lw=1.6)
    W([(146.4, 103.2), (151.6, 103.2)], INK if c1_on else FAINT, lw=1.8)
    dx = np.linspace(-2.6, 2.6, 30)
    W(list(zip(149 + dx, 101.4 - 0.8 * (1 - (dx / 2.6) ** 2))), INK if c1_on else FAINT, lw=1.8)
    W([(149, 100.6), (149, 38)], INK, lw=1.3)
    J(149, 38)
    J(149, 124, PWR if c1_on else FAINT)
    T(152.5, 103, "C1", 8.2, INK if c1_on else FAINT, w="bold")
    T(152.5, 99.0, "10–100 µF", 7.5, INK if c1_on else FAINT)
    T(149, 127.3, "+5,00 V", 7.5, PWR if c1_on else FAINT, ha="center", w="bold")

    # ligações
    for key, (pts, cls) in PATHS.items():
        on = key in act_p
        c = CLS_COLOR[cls]
        dashed = cls == "temp"
        if static:
            W(pts, c, lw=1.6, ls=(0, (4, 3)) if dashed else "-", z=3)
            arrowhead(pts[-2], pts[-1], c)
            if key in BIDIR:
                arrowhead(pts[1], pts[0], c)
        elif on:
            cc = accent if dashed else c
            W(pts, cc, lw=2.4, ls=(0, (4, 3)) if dashed else "-", z=3)
            arrowhead(pts[-2], pts[-1], cc)
            if key in BIDIR:
                arrowhead(pts[1], pts[0], cc)
            if key in ph.get("still", ()):
                pass
            elif key in BIDIR:
                flow_dots(pts, t, cc, spacing=5, reverse=(key == "usb"))
            else:
                flow_dots(pts, t, cc)
        else:
            W(pts, LINE_OFF, lw=1.4, ls=(0, (4, 3)) if dashed else "-", z=2)
    if static or "tosc" in act_p:
        J(258, 128, TRIG)
    T(251.5, 130.8, "D2", 7.5, TRIG if (static or "tosc" in act_p) else FAINT, w="bold")
    sense_on = static or "sp" in act_p
    T(161.5, 141.5, "S+", 7.5, SENSE if sense_on else FAINT, ha="right", w="bold")
    T(184.5, 141.5, "S−", 7.5, SENSE if sense_on else FAINT, w="bold")
    # µUSB desconectado
    if not static and phase != 1:
        x, y = 243, 89
        W([(x - 1.8, y - 1.8), (x + 1.8, y + 1.8)], PWR, lw=2.0, z=8)
        W([(x - 1.8, y + 1.8), (x + 1.8, y - 1.8)], PWR, lw=2.0, z=8)
        T(245.5, 89, "µUSB\nremovido", 6.5, PWR, linespacing=1.0)
    elif static:
        T(245.5, 89, "µUSB\nUPDI", 6.5, MUTED, linespacing=1.0)
    if static:
        T(113.5, 99, "calibração", 7.5, MUTED)

    # blocos
    for key in BLOCKS:
        draw_block(key, key in act_b)
    sw_glyph("SW" in act_b, True if static else ph["sw"], ORANGE)
    osc_screen(static or (phase == 3), t, static)
    la_screen(static or (phase == 3), t, static)
    if static:
        dmm_display(True, "5,00 V")
    elif phase == 0:
        v = 3.70 + 1.30 * min(1.0, t / 0.75)
        dmm_display(True, f"{v:.2f} V".replace(".", ","))
    else:
        dmm_display(False, "")
    if not static and phase in (2, 3):
        T(224, 111.5, "▶ executando KEM", 8, PWR if phase == 2 else TRIG, ha="center", w="bold")

    legend()
    return fig


def save(fig, stem):
    for ext in ("svg", "pdf"):
        fig.savefig(OUT / f"{stem}.{ext}", facecolor="white")
    fig.savefig(OUT / f"{stem}.png", dpi=200, facecolor="white")
    plt.close(fig)
    print("ok:", stem)


def fig_to_image(fig, dpi=100):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf).convert("RGB")


def gif(frames_per_phase=28, frame_ms=70, hold_ms=1400):
    frames, durations = [], []
    for p in range(4):
        for i in range(frames_per_phase):
            t = i / (frames_per_phase - 1)
            frames.append(fig_to_image(bancada(p, t)))
            durations.append(hold_ms if i == frames_per_phase - 1 else frame_ms)
    w, h = frames[0].size
    sample = Image.new("RGB", (w, h * 4))
    for p in range(4):
        sample.paste(frames[(p + 1) * frames_per_phase - 1], (0, h * p))
    pal = sample.quantize(colors=128, method=Image.Quantize.MEDIANCUT)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    q[0].save(OUT / "sut_fluxo_v3.gif", save_all=True, append_images=q[1:],
              duration=durations, loop=0, optimize=True, disposal=1)
    print("ok: sut_fluxo_v3.gif", f"{w}x{h}", len(q), "quadros")


if __name__ == "__main__":
    esquematico()
    save(bancada(None), "sut_bancada_v3")
    gif()
