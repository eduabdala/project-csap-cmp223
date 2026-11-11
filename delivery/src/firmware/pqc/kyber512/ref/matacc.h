#ifndef MATACC_H
#define MATACC_H

#include "poly.h"
#include "polyvec.h"

void matacc(poly* res, polyvec* src, unsigned char i, const unsigned char* seed, int transposed);

#endif

