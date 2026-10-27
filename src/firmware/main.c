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
#include <string.h>
#include "kem.h"

/* ---- Configuration --------------------------------------- */
#ifndef F_CPU
#define F_CPU 20000000UL
#endif
#ifndef BAUD
#define BAUD 115200
#endif

#define GPIO_BIT   0            /* PA0 as the measurement window */
#define WM_PATTERN 0xAA         /* stack watermark pattern */

/* Serial protocol commands (1 byte). */
#define CMD_KEYGEN 'K'
#define CMD_ENCAPS 'E'
#define CMD_DECAPS 'D'

/* ---- Measurement window (1-cycle GPIO via VPORT) --------- */
static inline void window_high(void) { VPORTA.OUT |=  (1 << GPIO_BIT); }
static inline void window_low(void)  { VPORTA.OUT &= ~(1 << GPIO_BIT); }

/* Short delay without <util/delay.h> so we don't depend on F_CPU in a header
 * macro. Deliberately coarse: it only needs to be distinguishable on the
 * logic analyzer. */
static void delay_us_approx(void) {
    for (volatile uint16_t i = 0; i < (F_CPU / 1000000UL); i++) { __asm__ __volatile__("nop"); }
}

/* Identifier pulses: n short pulses before the measurement window. */
static void id_pulses(uint8_t n) {
    for (uint8_t i = 0; i < n; i++) {
        window_high();
        delay_us_approx();
        window_low();
        delay_us_approx();
    }
}

/* ---- Stack watermarking ---------------------------------- */
/* Linker symbols: end of .bss (start of the free area) and top of RAM. */
extern uint8_t __heap_start;
extern uint8_t __stack;        /* = RAMEND in practice */

/* Fill the free region between the heap and the stack with 0xAA. */
static void stack_paint(void) {
    uint8_t *p = &__heap_start;
    uint8_t *sp = (uint8_t *)SP;
    while (p < sp) { *p++ = WM_PATTERN; }
}

/* Scan upward from the heap until the first untouched byte (!= 0xAA).
 * Peak stack = RAMEND - lowest_touched_address. */
static uint16_t stack_peak(void) {
    uint8_t *p = &__heap_start;
    while (p < (uint8_t *)RAMEND && *p == WM_PATTERN) { p++; }
    return (uint16_t)(RAMEND - (uint16_t)(uintptr_t)p);
}

/* ---- UART (USART3 on the Nano Every / PB0-PB1) ----------- */
static void uart_init(void) {
    /* Baud = (64 * F_CPU) / (16 * BAUD) in normal asynchronous mode. */
    USART3.BAUD = (uint16_t)((64UL * F_CPU) / (16UL * BAUD));
    USART3.CTRLB = USART_TXEN_bm | USART_RXEN_bm;
    PORTB.DIRSET = (1 << 0);   /* TX */
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

static void uart_tx_u16(uint16_t v) {
    uart_tx((uint8_t)(v >> 8));
    uart_tx((uint8_t)(v & 0xFF));
}

/* ---- Buffers (static allocation: no malloc on AVR) ------- */
static uint8_t pk[KEM_PUBLICKEYBYTES];
static uint8_t sk[KEM_SECRETKEYBYTES];
static uint8_t ct[KEM_CIPHERTEXTBYTES];
static uint8_t ss[KEM_BYTES];

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
    stack_paint();
    id_pulses(1);
    MEASURE(kem_keypair(pk, sk));
    uart_tx('k');
    uart_tx_u16(stack_peak());
    uart_tx_buf(pk, KEM_PUBLICKEYBYTES);
}

static void do_encaps(void) {
    stack_paint();
    id_pulses(2);
    MEASURE(kem_enc(ct, ss, pk));
    uart_tx('e');
    uart_tx_u16(stack_peak());
    uart_tx_buf(ct, KEM_CIPHERTEXTBYTES);
}

static void do_decaps(void) {
    stack_paint();
    id_pulses(3);
    MEASURE(kem_dec(ss, ct, sk));
    uart_tx('d');
    uart_tx_u16(stack_peak());
    uart_tx_buf(ss, KEM_BYTES);
}

int main(void) {
    VPORTA.DIR |= (1 << GPIO_BIT);   /* measurement-window GPIO as output */
    window_low();
    uart_init();

    for (;;) {
        uint8_t cmd = uart_rx();
        switch (cmd) {
            case CMD_KEYGEN: do_keygen(); break;
            case CMD_ENCAPS: do_encaps(); break;
            case CMD_DECAPS: do_decaps(); break;
            default: uart_tx('?'); break;
        }
    }
}
