#include <stdint.h>
#include "params.h"
#include "randombytes.h"
#include "reduce.h"


int16_t montgomery_reduce(int32_t a)
{
  int32_t t;
  int16_t u;

  u = a * QINV;
  t = (int32_t)u * CTRU_Q;
  t = a - t;
  t >>= 16;
  return t;
}

int16_t barrett_reduce(int16_t a)
{
  int32_t t;

  t = (int32_t)BARRETT_V * a;
  t >>= 24;
  t *= CTRU_Q;
  return a - t;
}

int16_t fqcsubq(int16_t a)
{
  a += (a >> 15) & CTRU_Q;
  a -= CTRU_Q;
  a += (a >> 15) & CTRU_Q;
  return a;
}

int16_t fqinv(int16_t a)
{
  unsigned int i;
  int16_t t;
  a = fqmul(a, MONT2); // to normal representation

  t = a;
  for (i = 1; i <= 9; ++i)
  {
    a = fqmul(a, a);
    if (i != 8)
      t = fqmul(t, a);
  }

  t = fqmul(t, 1); // t = a^767
  return t;
}

int16_t fqmul(int16_t a, int16_t b)
{
  return montgomery_reduce((int32_t)a * b);
}

