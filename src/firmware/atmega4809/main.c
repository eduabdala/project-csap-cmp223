/*
 * main.c — PQC measurement harness on the ATmega4809 (Arduino Nano Every).
 *
 * Implements the state machine from the roadmap (docs/roadmap.md, 1.3):
 *   - Serial trigger protocol (CMD_KEYGEN / CMD_ENCAPS / CMD_DECAPS).
 *   - Measurement window marked by a 1-cycle GPIO toggle (VPORTx.OUT).
 *   - Stack watermarking with the 0xAA pattern to measure peak stack usage.
 *   - Identifier pulses (1/2/3) before the window, for the parser.
 *   - Telemetry reported over UART OUTSIDE the measurement window.
 *
 * Determinism: interrupts are disabled (cli) during the measured window.
 *
 * Pins (adjust to the physical bench wiring):
 *   - Measurement-window GPIO: PORTA bit 0 -> VPORTA.OUT, bit 0
 *   The oscilloscope triggers on the rising edge; the logic analyzer measures
 *   the pulse width (latency).
 */
#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include "kem.h"

/* ---- Configuration --------------------------------------- */
#ifndef F_CPU
#define F_CPU 20000000UL
#endif
#ifndef BAUD_RATE
#define BAUD_RATE 115200
#endif

#define GPIO_BIT   0            /* PA0 (D2) as the measurement window */
#define LED_BIT    2            /* PE2 (D13 / LED_BUILTIN) for visual status */
#define WM_PATTERN 0xAA         /* stack watermark pattern */

/* Serial protocol commands (1 byte). */
#define CMD_KEYGEN 'K'
#define CMD_ENCAPS 'E'
#define CMD_DECAPS 'D'
#define CMD_MSG    'M'

/* ---- Measurement window & ID pulses on PA0 (D2) ---------- */
static inline void window_high(void) { VPORTA.OUT |=  (1 << GPIO_BIT); }
static inline void window_low(void)  { VPORTA.OUT &= ~(1 << GPIO_BIT); }

static void delay_ms_approx(uint16_t ms) {
    while (ms--) {
        for (volatile uint16_t i = 0; i < (F_CPU / 10000UL); i++) {
            __asm__ __volatile__("nop");
        }
    }
}

/* Identifier pulses on PA0 (D2) before the measurement window:
 *   - 5 pulses: main() startup (boot)
 *   - 1 pulse : KeyGen (K)
 *   - 2 pulses: Encaps (E)
 *   - 3 pulses: Decaps (D)
 * Each pulse is ~2 ms HIGH / ~2 ms LOW, followed by a ~5 ms LOW gap before
 * the measurement window rising edge, making it clearly distinguishable in the
 * logic analyzer capture at any sampling rate. */
static void id_pulses(uint8_t n) {
    for (uint8_t i = 0; i < n; i++) {
        window_high();
        delay_ms_approx(2);
        window_low();
        delay_ms_approx(2);
    }
    delay_ms_approx(5);
}

/* ---- Stack watermarking ---------------------------------- */
/* Linker symbols: end of .bss (start of the free area) and top of RAM. */
extern uint8_t __heap_start;
extern uint8_t __stack;        /* = RAMEND in practice */

/* Fill the free region between the heap and the stack with 0xAA. */
static __attribute__((noinline)) void stack_paint(void) {
    uint8_t *p = &__heap_start;
    uint8_t *sp = (uint8_t *)SP - 32;
    while (p < sp) { *p++ = WM_PATTERN; }
}

/* Scan upward from the heap until the first untouched byte (!= 0xAA).
 * Peak stack = RAMEND - lowest_touched_address. */
static uint16_t stack_peak(void) {
    uint8_t *p = &__heap_start;
    while (p < (uint8_t *)RAMEND && *p == WM_PATTERN) { p++; }
    return (uint16_t)(RAMEND - (uint16_t)(uintptr_t)p);
}

/* ---- Clock & UART (USART3 on Nano Every USB bridge: PB4/PB5) ---- */
static void clock_init(void) {
#if F_CPU == 20000000UL
    _PROTECTED_WRITE(CLKCTRL.MCLKCTRLB, 0);
#elif F_CPU == 10000000UL
    _PROTECTED_WRITE(CLKCTRL.MCLKCTRLB, CLKCTRL_PDIV_2X_gc | CLKCTRL_PEN_bm);
#elif F_CPU == 5000000UL
    _PROTECTED_WRITE(CLKCTRL.MCLKCTRLB, CLKCTRL_PDIV_4X_gc | CLKCTRL_PEN_bm);
#else
#error "Unsupported F_CPU: use 20000000UL, 10000000UL or 5000000UL"
#endif
}

static void uart_init(void) {
    /* On the Arduino Nano Every, USART3 connects to the SAMD11 USB-serial
     * bridge on the alternate pins PB4 (TX) and PB5 (RX). */
    PORTMUX.USARTROUTEA = (PORTMUX.USARTROUTEA & ~PORTMUX_USART3_gm) | PORTMUX_USART3_ALT1_gc;
    PORTB.OUTSET = (1 << 4);
    PORTB.DIRSET = (1 << 4);   /* PB4 = TX */
    PORTB.DIRCLR = (1 << 5);   /* PB5 = RX */

    /* Detect actual oscillator frequency from FUSE.OSCCFG (0x01 = 16 MHz
     * Arduino factory default, 0x02 = 20 MHz) and apply SIGROW factory
     * calibration so 115200 baud is exact regardless of fuse settings. */
    uint32_t f_osc = ((FUSE.OSCCFG & 0x03) == 0x01) ? 16000000UL : 20000000UL;
    int8_t sigrow_err = ((FUSE.OSCCFG & 0x03) == 0x01)
                        ? (int8_t)SIGROW.OSC16ERR5V
                        : (int8_t)SIGROW.OSC20ERR5V;
#if F_CPU == 20000000UL
    uint32_t f_clk = f_osc;
#elif F_CPU == 10000000UL
    uint32_t f_clk = f_osc / 2UL;
#elif F_CPU == 5000000UL
    uint32_t f_clk = f_osc / 4UL;
#endif
    int32_t baud_reg = (int32_t)((64UL * f_clk) / (16UL * BAUD_RATE));
    baud_reg += (baud_reg * sigrow_err) / 1024;
    USART3.BAUD = (uint16_t)baud_reg;
    USART3.CTRLB = USART_TXEN_bm | USART_RXEN_bm;
}

static void uart_tx(uint8_t b) {
    while (!(USART3.STATUS & USART_DREIF_bm)) { }
    USART3.TXDATAL = b;
}

static uint8_t uart_rx(void) {
    while (!(USART3.STATUS & USART_RXCIF_bm)) { }
    return USART3.RXDATAL;
}

static void uart_tx_buf(const uint8_t *buf, uint16_t n) {
    for (uint16_t i = 0; i < n; i++) uart_tx(buf[i]);
}

static void uart_tx_str(const char *s) {
    while (*s) uart_tx((uint8_t)*s++);
}

static void uart_tx_u16(uint16_t v) {
    uart_tx((uint8_t)(v >> 8));
    uart_tx((uint8_t)(v & 0xFF));
}

/* ---- Buffers (static allocation: no malloc on AVR) ------- */
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

/* ---- Entropy pool for randombytes() ---------------------- */
/* The ATmega4809 has no TRNG. The pool is filled OUTSIDE the measured window
 * from (a) ADC noise LSBs of the internal temperature sensor and (b) an
 * optional 64-byte seed injected by the host ('S' command, os.urandom).
 * Inside the window, randombytes() only copies from the pool, so the
 * latency measurement is not affected by entropy collection. */
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

static void adc_entropy_init(void) {
    VREF.CTRLA = (VREF.CTRLA & ~VREF_ADC0REFSEL_gm) | VREF_ADC0REFSEL_1V1_gc;
    ADC0.CTRLC = ADC_PRESC_DIV16_gc | ADC_REFSEL_INTREF_gc | ADC_SAMPCAP_bm;
    ADC0.MUXPOS = ADC_MUXPOS_TEMPSENSE_gc;
    ADC0.CTRLA = ADC_ENABLE_bm;
}

static uint8_t adc_noise_byte(void) {
    uint8_t b = 0;
    for (uint8_t i = 0; i < 8; i++) {
        ADC0.COMMAND = ADC_STCONV_bm;
        while (!(ADC0.INTFLAGS & ADC_RESRDY_bm)) { }
        uint16_t r = ADC0.RES;          /* reading RES clears RESRDY */
        b = (uint8_t)((b << 1) | (b >> 7)) ^ (uint8_t)r;
    }
    return b;
}

/* Refill before each KeyGen/Encaps; the host seed is consumed once. */
static void rng_refill(void) {
    for (uint8_t i = 0; i < RNG_POOL_SIZE; i++) {
        rng_pool[i] = adc_noise_byte() ^ host_seed[i];
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
/* Wraps the crypto call in the GPIO window, with interrupts disabled. */
#define MEASURE(call) do {         \
        cli();                     \
        window_high();             \
        (void)(call);              \
        window_low();              \
        sei();                     \
    } while (0)

static void do_keygen(void) {
    rng_refill();                    /* entropia coletada FORA da janela */
    stack_paint();
    id_pulses(1);                    /* 1 pulso no PA0 (D2) antes da janela */
    MEASURE(kem_keypair(pk, sk));
    uart_tx('k');
    uart_tx_u16(stack_peak());
    uart_tx_buf(pk, KEM_PUBLICKEYBYTES);
    uart_tx_str("\r\nDONE K\r\n");
}

static void do_encaps(void) {
    rng_refill();                    /* entropia coletada FORA da janela */
    stack_paint();
    id_pulses(2);                    /* 2 pulsos no PA0 (D2) antes da janela */
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
    id_pulses(3);                    /* 3 pulsos no PA0 (D2) antes da janela */
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
    id_pulses(4);                    /* 4 pulsos no PA0 (D2) antes da janela */
    MEASURE(stream_xor(msg_buf, len, ss));
    uart_tx('m');
    uart_tx_u16(stack_peak());
    uart_tx_buf(msg_buf, len);
    uart_tx_str("\r\nDONE M\r\n");
}

int main(void) {
    clock_init();
    VPORTA.DIR |= (1 << GPIO_BIT);   /* PA0 (D2): measurement-window GPIO as output */
    window_low();
    uart_init();
    adc_entropy_init();

    /* Padrão de inicialização da main no PA0 (D2): 5 pulsos */
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
            default: uart_tx('?'); break;
        }
    }
}
