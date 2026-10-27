/*
 * kem_ecdh.c — Baseline clássico: ECDH (micro-ecc / uECC) adaptado à kem.h.
 *
 * ECDH não é um KEM no sentido estrito, mas serve de par comparativo direto
 * de troca de chave (mesma finalidade do Kyber-512). Modelamos as operações
 * assim, para medir com o MESMO harness:
 *
 *   kem_keypair -> uECC_make_key()            (gera par efêmero)
 *   kem_enc     -> make_key + shared_secret   ("encaps": par efêmero + segredo)
 *   kem_dec     -> uECC_shared_secret()       ("decaps": deriva o mesmo segredo)
 *
 * Curva sugerida: secp256r1 (nível de segurança comparável ao uso clássico).
 * Requer micro-ecc vendorizado em pqc/ecdh/ (ver scripts/vendor-ecdh.sh).
 *
 * ATENÇÃO: a semântica difere do KEM real; documentar no artigo que a
 * comparação é de FINALIDADE (troca de chave), não de protocolo idêntico.
 */
#include "kem.h"
#include "uECC.h"
#include <string.h>

/* secp256r1: pub = 64 bytes (X||Y), priv = 32, segredo = 32. */
#define ECDH_PUB   64
#define ECDH_PRIV  32
#define ECDH_SS    32

_Static_assert(KEM_PUBLICKEYBYTES  >= ECDH_PUB,  "ajuste KEM sizes p/ ECDH no build do baseline");
_Static_assert(KEM_SECRETKEYBYTES  >= ECDH_PRIV, "ajuste KEM sizes p/ ECDH no build do baseline");
_Static_assert(KEM_CIPHERTEXTBYTES >= ECDH_PUB,  "ajuste KEM sizes p/ ECDH no build do baseline");
_Static_assert(KEM_BYTES           == ECDH_SS,   "segredo compartilhado = 32 bytes");

/* Par persistente do "destinatário" (análogo ao sk/pk de longo prazo). */
int kem_keypair(uint8_t *pk, uint8_t *sk) {
    const struct uECC_Curve_t *curve = uECC_secp256r1();
    return uECC_make_key(pk, sk, curve) ? 0 : -1;  /* uECC: 1 = sucesso */
}

/* "Encaps": gera par efêmero (vira o ciphertext = pub efêmera) e deriva o
 * segredo com a pub do destinatário. */
int kem_enc(uint8_t *ct, uint8_t *ss, const uint8_t *pk) {
    const struct uECC_Curve_t *curve = uECC_secp256r1();
    uint8_t eph_priv[ECDH_PRIV];
    if (!uECC_make_key(ct, eph_priv, curve)) return -1;   /* ct = pub efêmera */
    if (!uECC_shared_secret(pk, eph_priv, ss, curve)) return -1;
    return 0;
}

/* "Decaps": destinatário deriva o mesmo segredo a partir da pub efêmera (ct). */
int kem_dec(uint8_t *ss, const uint8_t *ct, const uint8_t *sk) {
    const struct uECC_Curve_t *curve = uECC_secp256r1();
    return uECC_shared_secret(ct, sk, ss, curve) ? 0 : -1;
}
