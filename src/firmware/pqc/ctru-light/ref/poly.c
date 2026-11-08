#include <stdint.h>
#include <string.h>
#include "params.h"
#include "reduce.h"
#include "poly.h"
#include "coding.h"
#include "cbd.h"
#include "ntt.h"
#include "pack.h"

/***** Basic Arithmetic *****/
void poly_reduce(poly *a)
{
  for (int i = 0; i < CTRU_N; ++i)
    a->coeffs[i] = barrett_reduce(a->coeffs[i]);
}

void poly_freeze(poly *a)
{
  poly_reduce(a);
  for (int i = 0; i < CTRU_N; ++i)
    a->coeffs[i] = fqcsubq(a->coeffs[i]);
}

void poly_fqcsubq(poly *a)
{
  for (int i = 0; i < CTRU_N; ++i)
    a->coeffs[i] = fqcsubq(a->coeffs[i]);
}

void poly_add(poly *c, const poly *a, const poly *b)
{
  for (int i = 0; i < CTRU_N; ++i)
    c->coeffs[i] = a->coeffs[i] + b->coeffs[i];
}

void poly_double(poly *b, const poly *a)
{
  for (int i = 0; i < CTRU_N; ++i)
    b->coeffs[i] = 2 * a->coeffs[i];
}

void poly_multi_p(poly *b, const poly *a)
{
  for (int i = 0; i < CTRU_N / 2; ++i)
  {
    int16_t tmp = a->coeffs[i];
    b->coeffs[i] = a->coeffs[CTRU_N / 2 + i] + tmp;
    b->coeffs[CTRU_N / 2 + i] = a->coeffs[CTRU_N / 2 + i] - tmp;
  }
}

/***** Sampling *****/
void poly_sample_keygen(poly *a, const unsigned char *buf)
{
  cbd1(a, buf);
}

void poly_sample_enc(poly *a, const unsigned char *buf)
{
  cbd1(a, buf);
}


/***** Coding and Decoding *****/
void poly_encode_e8(poly *mp, const unsigned char *msg)
{
  unsigned int i, j;
  int16_t mask;
  uint8_t mh[CTRU_MSGBYTES * 2];
  uint8_t tmp;

  for (i = 0; i < CTRU_MSGBYTES; i++)
  {
    tmp = msg[i] & 0xF;
    mh[2 * i] = encode_e8(tmp);

    tmp = (msg[i] >> 4) & 0xF;
    mh[2 * i + 1] = encode_e8(tmp);
  }

  for (i = 0; i < 256 / 8; i++)
  {
    for (j = 0; j < 8; j++)
    {
      mask = -(int16_t)((mh[i] >> j) & 1);
      mp->coeffs[8 * i + j] = mask & (CTRU_Q2 >> 1);
    }
  }

  for (i = 0; i < 256; i++)
  {
    mp->coeffs[256 + i] = mp->coeffs[i];
  }

}

void poly_decode_e8(unsigned char *msg, const poly *mp)
{
  unsigned int i, j;
  uint32_t tmp_mp[8];

  for (i = 0; i < CTRU_MSGBYTES; i++)
  {
    msg[i] = 0;
  }

  for (i = 0; i < 256 / 8; i++)
  {
    for (j = 0; j < 8; j++)
    {
      tmp_mp[j] = (uint32_t)mp->coeffs[8 * i + j];
    }
    msg[i >> 1] |= decode_e8(tmp_mp) << ((i & 1) << 2);
  }
}

void poly_compress(poly *b, const poly *a)
{
  int16_t t;
  for (int i = 0; i < CTRU_N; i++)
  {
    t = (((int32_t)a->coeffs[i] << CTRU_LOGQ2) + (CTRU_Q >> 1)) / CTRU_Q;
    b->coeffs[i] = t & (CTRU_Q2 - 1);
  }
}

void poly_decompress(poly *b, const poly *a)
{
  for (int i = 0; i < CTRU_N; i++)
  {
    b->coeffs[i] = ((int32_t)a->coeffs[i] * CTRU_Q + (CTRU_LOGQ2 >> 1)) >> CTRU_LOGQ2;
  }
}


/***** Polynomial Arithmetic *****/
void poly_ntt(poly *b)
{
  ntt(b->coeffs);
}

void poly_invntt(poly *b)
{
  invntt(b->coeffs);
}

void poly_basemul(poly *c, const poly *a, const poly *b)
{
	unsigned int i;
	int16_t tmp[8];

	for(i = 0; i < CTRU_N / 8; ++i)
	{
		basemul(&tmp[0], &a->coeffs[8 * i], &b->coeffs[8 * i], zetas[64 + i]);
		basemul(&tmp[4], &a->coeffs[8 * i + 4], &b->coeffs[8 * i + 4], CTRU_Q-zetas[64 + i]);
		memcpy(&c->coeffs[8 * i], tmp, sizeof(int16_t) * 8);
	}
}

int poly_baseinv(poly *b, const poly *a)
{
	int i, r = 0;
	int16_t tmp[8];

	for (i = 0; i < CTRU_N / 8; ++i)
	{
		r += baseinv(&tmp[0], &a->coeffs[8 * i], zetas[64 + i]);
		r += baseinv(&tmp[4], &a->coeffs[8 * i + 4], CTRU_Q-zetas[64 + i]);
		memcpy(&b->coeffs[8 * i], tmp, sizeof(int16_t) * 8);
	}

	return r;
}

int poly_baseinv_opt(poly *b, const poly *a)
{
	int i, r = 0;
	int16_t tmp[8];

	for (i = 0; i < CTRU_N / 8; ++i)
	{
		r += baseinv_opt(&tmp[0], &a->coeffs[8 * i], zetas[64 + i]);
		r += baseinv_opt(&tmp[4], &a->coeffs[8 * i + 4], CTRU_Q-zetas[64 + i]);
		memcpy(&b->coeffs[8 * i], tmp, sizeof(int16_t) * 8);
	}

	return r;
}