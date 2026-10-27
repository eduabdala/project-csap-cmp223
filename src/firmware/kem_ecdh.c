/*
 * kem_ecdh.c — Classical baseline: ECDH (micro-ecc / uECC) adapted to kem.h.
 *
 * ECDH is not a KEM in the strict sense, but it serves as a direct key-exchange
 * counterpart (same purpose as Kyber-512). We model the operations as follows,
 * so the SAME harness can measure it:
 *
 *   kem_keypair -> uECC_make_key()            (generate ephemeral pair)
 *   kem_enc     -> make_key + shared_secret   ("encaps": ephemeral pair + secret)
 *   kem_dec     -> uECC_shared_secret()       ("decaps": derive the same secret)
 *
 * Suggested curve: secp256r1 (security level comparable to classical usage).
 * Requires micro-ecc vendored under pqc/ecdh/ (see scripts/vendor-pqc.sh).
 *
 * NOTE: the semantics differ from a real KEM; document in the paper that the
 * comparison is one of PURPOSE (key exchange), not an identical protocol.
 */
#include "kem.h"
#include "uECC.h"
#include <string.h>

/* secp256r1: pub = 64 bytes (X||Y), priv = 32, secret = 32. */
#define ECDH_PUB   64
#define ECDH_PRIV  32
#define ECDH_SS    32

_Static_assert(KEM_PUBLICKEYBYTES  >= ECDH_PUB,  "adjust KEM sizes for the ECDH baseline build");
_Static_assert(KEM_SECRETKEYBYTES  >= ECDH_PRIV, "adjust KEM sizes for the ECDH baseline build");
_Static_assert(KEM_CIPHERTEXTBYTES >= ECDH_PUB,  "adjust KEM sizes for the ECDH baseline build");
_Static_assert(KEM_BYTES           == ECDH_SS,   "shared secret = 32 bytes");

/* Persistent "recipient" pair (analogous to a long-term sk/pk). */
int kem_keypair(uint8_t *pk, uint8_t *sk) {
    const struct uECC_Curve_t *curve = uECC_secp256r1();
    return uECC_make_key(pk, sk, curve) ? 0 : -1;  /* uECC: 1 = success */
}

/* "Encaps": generate an ephemeral pair (the ephemeral pub becomes the
 * ciphertext) and derive the secret using the recipient's pub. */
int kem_enc(uint8_t *ct, uint8_t *ss, const uint8_t *pk) {
    const struct uECC_Curve_t *curve = uECC_secp256r1();
    uint8_t eph_priv[ECDH_PRIV];
    if (!uECC_make_key(ct, eph_priv, curve)) return -1;   /* ct = ephemeral pub */
    if (!uECC_shared_secret(pk, eph_priv, ss, curve)) return -1;
    return 0;
}

/* "Decaps": the recipient derives the same secret from the ephemeral pub (ct). */
int kem_dec(uint8_t *ss, const uint8_t *ct, const uint8_t *sk) {
    const struct uECC_Curve_t *curve = uECC_secp256r1();
    return uECC_shared_secret(ct, sk, ss, curve) ? 0 : -1;
}
