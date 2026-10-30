/*
 * glue.c — Routes the vendored algorithms' RNG to the harness entropy pool.
 *
 * The vendored randombytes.c files are excluded from the RP2040 build (they
 * are host/AVR specific or deterministic stubs). Instead, every algorithm
 * draws from harness_rng_read() (main.c), which only copies from a pool that
 * is filled OUTSIDE the measured window.
 */
#include <stddef.h>
#include <stdint.h>

extern void harness_rng_read(uint8_t *buf, size_t n);

#if defined(ALG_ECDH)

#include "uECC.h"

static int uecc_rng(uint8_t *dest, unsigned size) {
    harness_rng_read(dest, size);
    return 1;
}

void kem_rng_install(void) { uECC_set_rng(uecc_rng); }

#else

#include "randombytes.h"   /* vendored header: the compiler checks our prototype */

#if defined(ALG_KYBER512)
int randombytes(uint8_t *out, size_t n) {
    harness_rng_read(out, n);
    return 0;
}
#else /* ALG_CTRU */
void randombytes(uint8_t *out, unsigned int n) {
    harness_rng_read(out, n);
}
#endif

void kem_rng_install(void) { }

#endif
