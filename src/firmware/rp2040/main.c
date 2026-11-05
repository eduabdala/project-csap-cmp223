/*
 * main.c — PQC measurement harness on the Raspberry Pi Pico (RP2040, Cortex-M0+).
 *
 * Implements the exact same serial protocol and GPIO window state machine as
 * src/firmware/atmega4809/main.c so that src/scripts/trigger.py and the
 * Snakemake pipeline work unchanged across both architectures (8-bit AVR vs
 * 32-bit ARM Cortex-M0+):
 *   - Serial trigger protocol over USB-CDC (/dev/ttyACM0): K, E, D, M, S, P.
 *   - Measurement window marked by a 1-cycle GPIO toggle via SIO (GP2).
 *   - Stack watermarking with the 0xAA pattern to measure peak stack usage.
 *   - Identifier pulses (5=boot, 1=K, 2=E, 3=D, 4=M) on GP2 before the window.
 *   - Telemetry reported outside the measurement window.
 */
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "pico/stdlib.h"
#include "hardware/clocks.h"
#include "hardware/gpio.h"
#include "hardware/regs/rosc.h"
#include "hardware/structs/rosc.h"
#include "hardware/structs/sio.h"
#include "hardware/sync.h"
#include "hardware/vreg.h"

#include "kem.h"

extern void kem_rng_install(void);

/* ---- Configuration --------------------------------------- */
#ifndef F_CPU
#define F_CPU 125000000UL       /* 125 MHz default on RP2040 */
#endif

#if F_CPU < 48000000UL
#error "RP2040 USB-CDC requires F_CPU >= 48MHz (48000000UL). The hardware USB controller cannot operate when clk_sys < 48MHz."
#endif

#define GPIO_WINDOW_PIN 2       /* GP2 (physical pin 4 on Pico) = measurement window */
#define GPIO_LED_PIN    25      /* GP25 = onboard LED on Raspberry Pi Pico */
#define WM_PATTERN      0xAA    /* stack watermark pattern */
#define STACK_WM_SPAN   32768U  /* paint up to 32 KB below __StackTop */

/* Serial protocol commands (1 byte). */
#define CMD_KEYGEN 'K'
#define CMD_ENCAPS 'E'
#define CMD_DECAPS 'D'
#define CMD_MSG    'M'

/* ---- Measurement window (1-cycle GPIO via RP2040 SIO) ---- */
static inline void window_high(void) { sio_hw->gpio_set = (1u << GPIO_WINDOW_PIN); }
static inline void window_low(void)  { sio_hw->gpio_clr = (1u << GPIO_WINDOW_PIN); }

/* Identifier pulses on GP2 before the measurement window:
 *   - 5 pulses: main() startup (boot)
 *   - 1 pulse : KeyGen (K)
 *   - 2 pulses: Encaps (E)
 *   - 3 pulses: Decaps (D)
 *   - 4 pulses: MsgCrypt (M)
 * Each pulse is 2 ms HIGH / 2 ms LOW, followed by a 5 ms LOW gap. */
static void id_pulses(uint8_t n) {
    for (uint8_t i = 0; i < n; i++) {
        window_high();
        busy_wait_us_32(2000);
        window_low();
        busy_wait_us_32(2000);
    }
    busy_wait_us_32(5000);
}

/* ---- Stack watermarking ---------------------------------- */
extern char __StackTop;
extern char __bss_end__;

static uint8_t *stack_wm_low_bound(void) {
    uintptr_t top = (uintptr_t)&__StackTop;
    uintptr_t bss_end = ((uintptr_t)&__bss_end__ + 15u) & ~(uintptr_t)15u;
    uintptr_t low = (top > STACK_WM_SPAN) ? (top - STACK_WM_SPAN) : bss_end;
    if (low < bss_end) low = bss_end;
    return (uint8_t *)low;
}

static __attribute__((noinline)) void stack_paint(void) {
    uint8_t *p = stack_wm_low_bound();
    uint8_t *sp;
    __asm__ __volatile__("mov %0, sp" : "=r"(sp));
    sp -= 64; /* safety margin below current frame */
    while (p < sp) {
        *p++ = WM_PATTERN;
    }
}

static uint16_t stack_peak(void) {
    uint8_t *p = stack_wm_low_bound();
    uint8_t *top = (uint8_t *)&__StackTop;
    while (p < top && *p == WM_PATTERN) {
        p++;
    }
    uintptr_t used = (uintptr_t)(top - p);
    return (used > 0xFFFFu) ? 0xFFFFu : (uint16_t)used;
}

/* ---- Clock & USB-CDC I/O --------------------------------- */
static void clock_init_rp2040(void) {
    uint32_t khz = (uint32_t)(F_CPU / 1000UL);
    if (khz > 133000U) {
        vreg_set_voltage(VREG_VOLTAGE_1_15);
        busy_wait_us_32(1000);
    }
    set_sys_clock_khz(khz, true);
}

static uint8_t uart_rx(void) {
    for (;;) {
        int c = getchar_timeout_us(100000);
        if (c != PICO_ERROR_TIMEOUT) {
            return (uint8_t)c;
        }
    }
}

static void uart_tx(uint8_t b) {
    putchar_raw((int)b);
}

static void uart_tx_buf(const uint8_t *buf, uint16_t n) {
    fwrite(buf, 1, n, stdout);
}

static void uart_tx_str(const char *s) {
    fputs(s, stdout);
    fflush(stdout);
}

static void uart_tx_u16(uint16_t v) {
    uint8_t b[2] = { (uint8_t)(v >> 8), (uint8_t)(v & 0xFF) };
    fwrite(b, 1, 2, stdout);
}

/* ---- Buffers (static allocation) ------------------------- */
static uint8_t pk[KEM_PUBLICKEYBYTES];
static uint8_t sk[KEM_SECRETKEYBYTES];
static uint8_t ct[KEM_CIPHERTEXTBYTES];
static uint8_t ss_enc[KEM_BYTES];
static uint8_t ss[KEM_BYTES];
static uint8_t msg_buf[64];

static void stream_xor(uint8_t *buf, uint8_t len, const uint8_t key[KEM_BYTES]) {
    for (uint8_t i = 0; i < len; i++) {
        uint8_t k = key[i % KEM_BYTES] ^ (uint8_t)(i * 0x9E + 0x37);
        buf[i] ^= k;
    }
}

/* ---- Entropy pool (ROSC randombit + host seed) ----------- */
#define RNG_POOL_SIZE 64
static uint8_t rng_pool[RNG_POOL_SIZE];
static uint8_t host_seed[RNG_POOL_SIZE];
static uint8_t rng_idx;

void harness_rng_read(uint8_t *buf, size_t n) {
    for (size_t i = 0; i < n; i++) {
        buf[i] = rng_pool[rng_idx];
        rng_idx = (uint8_t)((rng_idx + 1) % RNG_POOL_SIZE);
    }
}

static uint8_t rosc_noise_byte(void) {
    uint8_t b = 0;
    for (uint8_t i = 0; i < 8; i++) {
        b = (uint8_t)((b << 1) | (rosc_hw->randombit & 1u));
        busy_wait_at_least_cycles(16);
    }
    return b;
}

static void rng_refill(void) {
    for (uint8_t i = 0; i < RNG_POOL_SIZE; i++) {
        rng_pool[i] = rosc_noise_byte() ^ host_seed[i];
    }
    memset(host_seed, 0, sizeof(host_seed));
    rng_idx = 0;
}

static void do_seed(void) {
    for (uint8_t i = 0; i < RNG_POOL_SIZE; i++) {
        host_seed[i] = uart_rx();
    }
    uart_tx('s');
    uart_tx_str("\r\nDONE S\r\n");
}

/* ---- Per-operation measurement routine ------------------- */
#define MEASURE(call) do {                              \
        uint32_t _irq = save_and_disable_interrupts();  \
        window_high();                                  \
        (void)(call);                                   \
        window_low();                                   \
        restore_interrupts(_irq);                       \
    } while (0)

static void do_keygen(void) {
    rng_refill();
    stack_paint();
    id_pulses(1);
    MEASURE(kem_keypair(pk, sk));
    uart_tx('k');
    uart_tx_u16(stack_peak());
    uart_tx_buf(pk, KEM_PUBLICKEYBYTES);
    uart_tx_str("\r\nDONE K\r\n");
}

static void do_encaps(void) {
    rng_refill();
    stack_paint();
    id_pulses(2);
    MEASURE(kem_enc(ct, ss_enc, pk));
    uart_tx('e');
    uart_tx_u16(stack_peak());
    uart_tx_buf(ct, KEM_CIPHERTEXTBYTES);
    uart_tx_buf(ss_enc, KEM_BYTES);
    uart_tx_str("\r\nDONE E\r\n");
}

static void do_decaps(void) {
    memset(ss, 0, KEM_BYTES);
    stack_paint();
    id_pulses(3);
    MEASURE(kem_dec(ss, ct, sk));
    uart_tx('d');
    uart_tx_u16(stack_peak());
    uart_tx_buf(ss, KEM_BYTES);
    uart_tx_str("\r\nDONE D\r\n");
}

static void do_msg(void) {
    uint8_t len = uart_rx();
    if (len > sizeof(msg_buf)) len = sizeof(msg_buf);
    for (uint8_t i = 0; i < len; i++) {
        msg_buf[i] = uart_rx();
    }
    stack_paint();
    id_pulses(4);
    MEASURE(stream_xor(msg_buf, len, ss));
    uart_tx('m');
    uart_tx_u16(stack_peak());
    uart_tx_buf(msg_buf, len);
    uart_tx_str("\r\nDONE M\r\n");
}

int main(void) {
    clock_init_rp2040();
    stdio_init_all();
    stdio_set_translate_crlf(&stdio_usb, false);

    gpio_init(GPIO_WINDOW_PIN);
    gpio_set_dir(GPIO_WINDOW_PIN, GPIO_OUT);
    window_low();

    gpio_init(GPIO_LED_PIN);
    gpio_set_dir(GPIO_LED_PIN, GPIO_OUT);
    gpio_put(GPIO_LED_PIN, 1);

    kem_rng_install();

    /* Boot pattern on GP2: 5 pulses */
    id_pulses(5);

    for (;;) {
        uint8_t cmd = uart_rx();
        switch (cmd) {
            case CMD_KEYGEN: do_keygen(); break;
            case CMD_ENCAPS: do_encaps(); break;
            case CMD_DECAPS: do_decaps(); break;
            case CMD_MSG:    do_msg();    break;
            case 'S':        do_seed();   break;
            case 'P':        uart_tx_str("PONG\r\n"); break;
            default:         uart_tx('?'); fflush(stdout); break;
        }
    }
}
