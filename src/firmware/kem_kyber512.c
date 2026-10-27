/*
 * kem_kyber512.c — Kyber-512 adapter for the kem.h interface.
 *
 * Source vendored under pqc/kyber512/<ref|asm>/ (see scripts/vendor-pqc.sh).
 * By default we use the CHES 2026 artifact (whYBeKim/CTRU-Light-and-PQC-on-AVR),
 * whose API follows the convention:
 *   crypto_kem_keypair(pk, sk)
 *   crypto_kem_enc(ct, ss, pk)
 *   crypto_kem_dec(ss, ct, sk)
 *
 * If you switch the source to PQClean (prefix PQCLEAN_MLKEM512_CLEAN_*),
 * redefine the KYBER_* macros below via -D in the Makefile, or adjust here.
 *
 * Sizes (ML-KEM-512 / Kyber-512): PK 800, SK 1632, CT 768, SS 32.
 */
#include "kem.h"
#include "api.h"   /* header from the vendored package under pqc/kyber512/ */

#ifndef KYBER_KEYPAIR
#define KYBER_KEYPAIR crypto_kem_keypair
#endif
#ifndef KYBER_ENC
#define KYBER_ENC     crypto_kem_enc
#endif
#ifndef KYBER_DEC
#define KYBER_DEC     crypto_kem_dec
#endif

int kem_keypair(uint8_t *pk, uint8_t *sk) {
    return KYBER_KEYPAIR(pk, sk);
}

int kem_enc(uint8_t *ct, uint8_t *ss, const uint8_t *pk) {
    return KYBER_ENC(ct, ss, pk);
}

int kem_dec(uint8_t *ss, const uint8_t *ct, const uint8_t *sk) {
    return KYBER_DEC(ss, ct, sk);
}
