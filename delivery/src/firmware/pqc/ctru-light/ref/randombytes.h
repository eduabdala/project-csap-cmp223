#ifndef RANDOMBYTES_H
#define RANDOMBYTES_H

#include <stddef.h>
#include <stdint.h>

// Generate random bytes and output the result to random_array
void randombytes(uint8_t *buf, unsigned int xlen);

#endif
