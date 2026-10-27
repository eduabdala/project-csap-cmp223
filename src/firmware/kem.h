/*
 * kem.h — Algorithm-agnostic KEM interface.
 *
 * The measurement harness (main.c) calls only these functions. The concrete
 * implementation (Kyber-512, CTRU-Light, ECDH) is plugged in under pqc/<alg>/
 * and adapted in kem_<alg>.c. Switching algorithms = swapping the
 * implementation, not the harness.
 *
 * Sizes (bytes) for ML-KEM-512 / Kyber-512:
 *   PK = 800, SK = 1632, CT = 768, SS = 32
 * Confirmed against the vendored package's #defines at build time
 * (static_assert in the adapters).
 */
#ifndef KEM_H
#define KEM_H

#include <stdint.h>

/* Filled in from the vendored algorithm header (see kem_kyber512.c).
 *
 * The defaults below are Kyber-512 (ML-KEM-512). Other algorithms override
 * them via -D in the Makefile (per-ALG CPPFLAGS), because the static buffers
 * in main.c must be sized for the LARGEST algorithm at build time.
 *
 * Per-algorithm sizes (bytes):
 *   Kyber-512 : PK 800  SK 1632 CT 768  SS 32
 *   CTRU-Light: PK 1206 SK ~1200 CT 1206 SS 32   (see vendored api.h)
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

/* Return 0 on success. */
int kem_keypair(uint8_t *pk, uint8_t *sk);
int kem_enc(uint8_t *ct, uint8_t *ss, const uint8_t *pk);
int kem_dec(uint8_t *ss, const uint8_t *ct, const uint8_t *sk);

#endif /* KEM_H */
