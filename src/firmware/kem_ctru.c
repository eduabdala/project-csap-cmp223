/*
 * kem_ctru.c — Adaptador do CTRU-Light para a interface kem.h.
 *
 * Fonte: whYBeKim/CTRU-Light-and-PQC-on-AVR (artefato CHES 2026, MIT).
 * Vendorizado em pqc/ctru-light/ (ver scripts/vendor-pqc.sh).
 *
 * A API do artefato segue a convenção:
 *   crypto_kem_keypair(pk, sk)
 *   crypto_kem_enc(ct, ss, pk)
 *   crypto_kem_dec(ss, ct, sk)
 * (confirmar nomes/prefixo exatos no api.h vendorizado e ajustar as macros.)
 *
 * Tamanhos CTRU-Light: pk = ct = 1206 bytes; ss = 32 (ver paper, MDPI 13-21-3388).
 * Ajuste os KEM_* no build do CTRU (ver Makefile: CPPFLAGS por algoritmo).
 */
#include "kem.h"
#include "api.h"   /* header do pacote vendorizado em pqc/ctru-light/ */

#ifndef CTRU_KEYPAIR
#define CTRU_KEYPAIR crypto_kem_keypair
#endif
#ifndef CTRU_ENC
#define CTRU_ENC     crypto_kem_enc
#endif
#ifndef CTRU_DEC
#define CTRU_DEC     crypto_kem_dec
#endif

int kem_keypair(uint8_t *pk, uint8_t *sk) {
    return CTRU_KEYPAIR(pk, sk);
}

int kem_enc(uint8_t *ct, uint8_t *ss, const uint8_t *pk) {
    return CTRU_ENC(ct, ss, pk);
}

int kem_dec(uint8_t *ss, const uint8_t *ct, const uint8_t *sk) {
    return CTRU_DEC(ss, ct, sk);
}
