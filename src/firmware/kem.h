/*
 * kem.h — Interface KEM independente de algoritmo.
 *
 * O harness de medição (main.c) chama apenas estas funções. A implementação
 * concreta (Kyber-512 via PQClean) é plugada em pqc/<ALG>/ e adaptada em
 * kem_<ALG>.c. Trocar de algoritmo = trocar a implementação, não o harness.
 *
 * Tamanhos (bytes) para ML-KEM-512 / Kyber-512:
 *   PK = 800, SK = 1632, CT = 768, SS = 32
 * Confirmar com os #define do pacote vendorizado em build time (static_assert).
 */
#ifndef KEM_H
#define KEM_H

#include <stdint.h>

/* Preenchidos pelo header do algoritmo vendorizado (ver kem_kyber512.c).
 *
 * Os defaults abaixo são do Kyber-512 (ML-KEM-512). Outros algoritmos
 * sobrescrevem via -D no Makefile (CPPFLAGS por ALG), pois os buffers
 * estáticos em main.c precisam do MAIOR tamanho em build time.
 *
 * Tamanhos por algoritmo (bytes):
 *   Kyber-512 : PK 800  SK 1632 CT 768  SS 32
 *   CTRU-Light: PK 1206 SK ~1200 CT 1206 SS 32   (ver api.h vendorizado)
 *   ECDH p256 : PK 64   SK 32   CT 64   SS 32
 */
#ifndef KEM_PUBLICKEYBYTES
#define KEM_PUBLICKEYBYTES  800
#endif
#ifndef KEM_SECRETKEYBYTES
#define KEM_SECRETKEYBYTES  1632
#endif
#ifndef KEM_CIPHERTEXTBYTES
#define KEM_CIPHERTEXTBYTES 768
#endif
#ifndef KEM_BYTES
#define KEM_BYTES           32      /* shared secret */
#endif

/* Retornam 0 em sucesso. */
int kem_keypair(uint8_t *pk, uint8_t *sk);
int kem_enc(uint8_t *ct, uint8_t *ss, const uint8_t *pk);
int kem_dec(uint8_t *ss, const uint8_t *ct, const uint8_t *sk);

#endif /* KEM_H */
