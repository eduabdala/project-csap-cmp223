/*
 * kem_kyber512.c — Adaptador do Kyber-512 para a interface kem.h.
 *
 * Fonte vendorizada em pqc/kyber512/<ref|asm>/ (ver scripts/vendor-pqc.sh).
 * Por padrão usamos o artefato CHES 2026 (whYBeKim/CTRU-Light-and-PQC-on-AVR),
 * cuja API segue a convenção:
 *   crypto_kem_keypair(pk, sk)
 *   crypto_kem_enc(ct, ss, pk)
 *   crypto_kem_dec(ss, ct, sk)
 *
 * Se trocar a fonte por PQClean (prefixo PQCLEAN_MLKEM512_CLEAN_*), redefina
 * as macros KYBER_* abaixo via -D no Makefile, ou ajuste aqui.
 *
 * Tamanhos (ML-KEM-512 / Kyber-512): PK 800, SK 1632, CT 768, SS 32.
 */
#include "kem.h"
#include "api.h"   /* header do pacote vendorizado em pqc/kyber512/ */

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
