#ifndef NTT_H
#define NTT_H

#include <stdint.h>
#include "params.h"

extern __flash const int8_t LUT3_H[256] __attribute__((aligned(256)));
extern __flash const int8_t LUT3_L[256] __attribute__((aligned(256)));
extern __flash const int16_t KRED2X_zetas[128]__attribute__((aligned(256)));
extern __flash const int16_t KRED2X_zetas_inv_neg[128] __attribute__((aligned(256)));
extern void basemulkred_asm(int16_t *r, const int16_t *a, const int16_t *b, int16_t zeta);
extern void nttkred_asm(int16_t a[512]);
extern void invnttkred_asm(int16_t a[512]);
extern void get_sq_kred_asm(int16_t sq[8], const int16_t a[4]);
extern int baseinv_kred_det_asm(int16_t b[4], int16_t sq_fq[8], const int16_t a[4], int16_t zeta);

int baseinvkred_asm(int16_t b[4], const int16_t a[4], int16_t zeta);

#endif
