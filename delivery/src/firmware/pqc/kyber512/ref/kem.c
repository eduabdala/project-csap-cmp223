#include "indcpa.h"
#include "params.h"
#include "randombytes.h"
#include "symmetric.h"
#include "verify.h"
#include <stddef.h>
#include <stdint.h>

int crypto_kem_keypair(uint8_t* pk, uint8_t* sk) {
    size_t i;
    indcpa_keypair(pk, sk);
    for (i = 0; i < KYBER_INDCPA_PUBLICKEYBYTES; i++) {
        sk[i + KYBER_INDCPA_SECRETKEYBYTES] = pk[i];
    }
    hash_h(sk + KYBER_SECRETKEYBYTES - 2 * KYBER_SYMBYTES, pk, KYBER_PUBLICKEYBYTES);
    /* Value z for pseudo-random output on reject */
    randombytes(sk + KYBER_SECRETKEYBYTES - KYBER_SYMBYTES, KYBER_SYMBYTES);
    return 0;
}

int crypto_kem_enc(uint8_t* ct, uint8_t* ss, const uint8_t* pk) {
    uint8_t buf[2 * KYBER_SYMBYTES];
    uint8_t kr[2 * KYBER_SYMBYTES];

    randombytes(buf, KYBER_SYMBYTES);
    hash_h(buf, buf, KYBER_SYMBYTES);

    hash_h(buf + KYBER_SYMBYTES, pk, KYBER_PUBLICKEYBYTES);
    hash_g(kr, buf, 2 * KYBER_SYMBYTES);

    indcpa_enc(ct, buf, pk, kr + KYBER_SYMBYTES);

    hash_h(kr + KYBER_SYMBYTES, ct, KYBER_CIPHERTEXTBYTES);
    kdf(ss, kr, 2 * KYBER_SYMBYTES);
    return 0;
}

int crypto_kem_dec(unsigned char* ss, const unsigned char* ct, const unsigned char* sk)
{
    size_t i;
    unsigned char fail;
    unsigned char buf[2 * KYBER_SYMBYTES];
    unsigned char kr[2 * KYBER_SYMBYTES];
    const unsigned char* pk = sk + KYBER_INDCPA_SECRETKEYBYTES;

    indcpa_dec(buf, ct, sk);

    for (i = 0; i < KYBER_SYMBYTES; i++) {
        buf[KYBER_SYMBYTES + i] = sk[KYBER_SECRETKEYBYTES - 2 * KYBER_SYMBYTES + i];
    }
    hash_g(kr, buf, 2 * KYBER_SYMBYTES);

    fail = indcpa_enc_cmp(ct, buf, pk, kr + KYBER_SYMBYTES);

    hash_h(kr + KYBER_SYMBYTES, ct, KYBER_CIPHERTEXTBYTES);

    cmov(kr, sk + KYBER_SECRETKEYBYTES - KYBER_SYMBYTES, KYBER_SYMBYTES, fail);

    kdf(ss, kr, 2 * KYBER_SYMBYTES);
    return 0;
}
