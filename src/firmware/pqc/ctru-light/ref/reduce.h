#ifndef REDUCE_H
#define REDUCE_H

#include <stdint.h>
#include "params.h"

#define MONT 171   // 2^16 mod 769
#define MONT2 19 // Mont^2 mod q
#define QINV 64769   // 769^(-1) mod 2^16
#define BARRETT_V 21817

int16_t montgomery_reduce(int32_t a);
int16_t barrett_reduce(int16_t a);
int16_t fqcsubq(int16_t a);
int16_t fqmul(int16_t a, int16_t b);
int16_t fqinv(int16_t a);

#endif
