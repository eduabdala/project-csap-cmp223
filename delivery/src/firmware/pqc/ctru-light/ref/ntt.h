#ifndef NTT_H
#define NTT_H

#include <stdint.h>
#include "params.h"

void ntt(int16_t a[512]);
void invntt(int16_t a[512]);
void basemul(int16_t c[4], const int16_t a[4], const int16_t b[4], int16_t zeta);
int baseinv(int16_t b[4], const int16_t a[4], int16_t zeta);
int baseinv_opt(int16_t r[4], const int16_t a[4], int16_t zeta);

extern int16_t zetas[128];
#endif
