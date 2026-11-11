/*
 * kem_ctru.c — CTRU-Light adapter for the kem.h interface.
 *
 * Source: whYBeKim/CTRU-Light-and-PQC-on-AVR (CHES 2026 artifact, MIT).
 * Vendored under pqc/ctru-light/ (see scripts/vendor-pqc.sh).
 *
 * The artifact's API follows the convention:
 *   crypto_kem_keypair(pk, sk)
 *   crypto_kem_enc(ct, ss, pk)
 *   crypto_kem_dec(ss, ct, sk)
 * (confirm the exact names/prefix in the vendored api.h and adjust the macros.)
 *
 * CTRU-Light sizes: pk = ct = 1206 bytes; ss = 32 (see paper, MDPI 13-21-3388).
 * Set the KEM_* sizes in the CTRU build (see Makefile: per-algorithm CPPFLAGS).
 */
#include "kem.h"
#include "api.h"   /* header from the vendored package under pqc/ctru-light/ */

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
    /* CTRU-Light signature: (pk, ss, ct) */
    return CTRU_ENC((uint8_t *)pk, ss, ct);
}

int kem_dec(uint8_t *ss, const uint8_t *ct, const uint8_t *sk) {
    /* CTRU-Light signature: (sk, ct, ss) */
    return CTRU_DEC((uint8_t *)sk, (uint8_t *)ct, ss);
}
