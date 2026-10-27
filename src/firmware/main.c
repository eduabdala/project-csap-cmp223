/*
 * main.c — Harness de medição PQC no ATmega4809 (Arduino Nano Every).
 *
 * Implementa a máquina de estados do roadmap (docs/roadmap.md, 1.3):
 *   - Protocolo serial de disparo (CMD_KEYGEN / CMD_ENCAPS / CMD_DECAPS).
 *   - Janela de medição marcada por GPIO de 1 ciclo (VPORTx.OUT).
 *   - Stack watermarking com padrão 0xAA para medir o pico de pilha.
 *   - Pulsos identificadores (1/2/3) antes da janela para o parser.
 *   - Relatório via UART FORA da janela de medição.
 *
 * Determinismo: interrupções desativadas (cli) durante a janela medida.
 *
 * Pinos (ajustar ao roteamento físico da bancada):
 *   - GPIO de janela: PORTA bit 0  -> VPORTA.OUT, bit 0
 *   O osciloscópio dispara na borda de subida; o analisador lógico mede a
 *   largura do pulso (latência).
 */
#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdint.h>
#include <string.h>
#include "kem.h"

/* ---- Configuração ---------------------------------------- */
#ifndef F_CPU
#define F_CPU 20000000UL
#endif
#ifndef BAUD
#define BAUD 115200
#endif

#define GPIO_BIT   0            /* PA0 como janela de medição */
#define WM_PATTERN 0xAA         /* padrão de watermark da pilha */

/* Comandos do protocolo serial (1 byte). */
#define CMD_KEYGEN 'K'
#define CMD_ENCAPS 'E'
#define CMD_DECAPS 'D'

/* ---- Janela de medição (GPIO de 1 ciclo via VPORT) ------- */
static inline void window_high(void) { VPORTA.OUT |=  (1 << GPIO_BIT); }
static inline void window_low(void)  { VPORTA.OUT &= ~(1 << GPIO_BIT); }

/* Delay curto sem <util/delay.h> para não depender de F_CPU em macro de header.
 * Grosseiro de propósito: só precisa ser distinguível no analisador lógico. */
static void delay_us_approx(void) {
    for (volatile uint16_t i = 0; i < (F_CPU / 1000000UL); i++) { __asm__ __volatile__("nop"); }
}

/* Pulsos identificadores: n pulsos curtos antes da janela de medição. */
static void id_pulses(uint8_t n) {
    for (uint8_t i = 0; i < n; i++) {
        window_high();
        delay_us_approx();
        window_low();
        delay_us_approx();
    }
}

/* ---- Stack watermarking ---------------------------------- */
/* Símbolos do linker: fim do .bss (início da área livre) e topo da RAM. */
extern uint8_t __heap_start;
extern uint8_t __stack;        /* = RAMEND na prática */

/* Preenche a região livre entre o heap e a pilha com 0xAA. */
static void stack_paint(void) {
    uint8_t *p = &__heap_start;
    uint8_t *sp = (uint8_t *)SP;
    while (p < sp) { *p++ = WM_PATTERN; }
}

/* Varre do heap para cima até achar o primeiro byte intocado (!= 0xAA).
 * Pico de pilha = RAMEND - endereço_mínimo_tocado. */
static uint16_t stack_peak(void) {
    uint8_t *p = &__heap_start;
    while (p < (uint8_t *)RAMEND && *p == WM_PATTERN) { p++; }
    return (uint16_t)(RAMEND - (uint16_t)(uintptr_t)p);
}

/* ---- UART (USART3 na Nano Every / PB0-PB1) --------------- */
static void uart_init(void) {
    /* Baud = (64 * F_CPU) / (16 * BAUD) para modo assíncrono normal. */
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

/* ---- Buffers (alocação estática: sem malloc no AVR) ------ */
static uint8_t pk[KEM_PUBLICKEYBYTES];
static uint8_t sk[KEM_SECRETKEYBYTES];
static uint8_t ct[KEM_CIPHERTEXTBYTES];
static uint8_t ss[KEM_BYTES];

/* ---- Rotina de medição de uma operação ------------------- */
/* Envolve a chamada criptográfica na janela GPIO, com IRQ desativada. */
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
    VPORTA.DIR |= (1 << GPIO_BIT);   /* GPIO de janela como saída */
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
