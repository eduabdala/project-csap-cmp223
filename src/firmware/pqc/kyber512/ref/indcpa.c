#include "indcpa.h"
#include "ntt.h"
#include "params.h"
#include "poly.h"
#include "polyvec.h"
#include "randombytes.h"
#include "symmetric.h"
#include "matacc.h"
#include <stddef.h>
#include <stdint.h>
#include <string.h>

static polyvec sp;
static poly pkp_bp;

void indcpa_keypair(uint8_t pk[KYBER_INDCPA_PUBLICKEYBYTES],
	uint8_t sk[KYBER_INDCPA_SECRETKEYBYTES])
{
	unsigned int i;
	uint8_t buf[2 * KYBER_SYMBYTES];
	const uint8_t* publicseed = buf;
	const uint8_t* noiseseed = buf + KYBER_SYMBYTES;
	uint8_t nonce = 0;

	randombytes(buf, KYBER_SYMBYTES);
	buf[KYBER_SYMBYTES] = KYBER_K;
	hash_g(buf, buf, KYBER_SYMBYTES + 1);

	for (i = 0; i < KYBER_K; i++)
	{
		poly_getnoise_eta1(&sp.vec[i], noiseseed, nonce++);
	}
	polyvec_ntt(&sp);

	for (i = 0; i < KYBER_K; i++)
	{
		matacc(&pkp_bp, &sp, i, publicseed, 0);
		poly_invntt(&pkp_bp);
		poly_addnoise_eta1(&pkp_bp, noiseseed, nonce++);
		poly_ntt(&pkp_bp);
		poly_tobytes(pk + i * KYBER_POLYBYTES, &pkp_bp);
	}
	poly_reduce(&sp.vec[0]);
	poly_reduce(&sp.vec[1]);
	polyvec_tobytes(sk, &sp);
	memcpy(pk + KYBER_POLYVECBYTES, publicseed, KYBER_SYMBYTES);
}

void indcpa_enc(uint8_t c[KYBER_INDCPA_BYTES],
	const uint8_t m[KYBER_INDCPA_MSGBYTES],
	const uint8_t pk[KYBER_INDCPA_PUBLICKEYBYTES],
	const uint8_t coins[KYBER_SYMBYTES])
{
	unsigned int i;
	poly* pkp = &pkp_bp;
	poly* k = &pkp_bp;
	poly* v = &sp.vec[0];
	const unsigned char* seed = pk + KYBER_POLYVECBYTES;
	unsigned char nonce = 0;

	for (i = 0; i < KYBER_K; i++)
		poly_getnoise_eta1(sp.vec + i, coins, nonce++);

	polyvec_ntt(&sp);

	for (i = 0; i < KYBER_K; i++) {
		matacc(&pkp_bp, &sp, i, seed, 1);
		poly_invntt(&pkp_bp);

		poly_addnoise_eta2(&pkp_bp, coins, nonce++);
		poly_reduce(&pkp_bp);

		poly_packcompress(c, &pkp_bp, i);
	}

	poly_frombytes(pkp, pk);
	poly_basemul(v, pkp, &sp.vec[0]);
	for (i = 1; i < KYBER_K; i++) {
		poly_frombytes(pkp, pk + i * KYBER_POLYBYTES);
		poly_basemul_acc(v, pkp, &sp.vec[i]);
	}

	poly_invntt(v);

	poly_addnoise_eta2(v, coins, nonce++);
	poly_frommsg(k, m);
	poly_add(v, v, k);
	poly_reduce(v);

	poly_compress(c + KYBER_POLYVECCOMPRESSEDBYTES, v);
}

unsigned char indcpa_enc_cmp(const unsigned char* c,
	const unsigned char* m,
	const unsigned char* pk,
	const unsigned char* coins) {
	uint8_t rc = 0;
	poly* pkp = &pkp_bp;
	poly* k = &pkp_bp;
	poly* v = &sp.vec[0];
	const unsigned char* seed = pk + KYBER_POLYVECBYTES;
	int i;
	unsigned char nonce = 0;

	for (i = 0; i < KYBER_K; i++)
		poly_getnoise_eta1(sp.vec + i, coins, nonce++);

	polyvec_ntt(&sp);

	for (i = 0; i < KYBER_K; i++) {
		matacc(&pkp_bp, &sp, i, seed, 1);
		poly_invntt(&pkp_bp);

		poly_addnoise_eta2(&pkp_bp, coins, nonce++);
		poly_reduce(&pkp_bp);

		rc |= cmp_poly_packcompress(c, &pkp_bp, i);
	}

	poly_frombytes(pkp, pk);
	poly_basemul(v, pkp, &sp.vec[0]);
	for (i = 1; i < KYBER_K; i++) {
		poly_frombytes(pkp, pk + i * KYBER_POLYBYTES);
		poly_basemul_acc(v, pkp, &sp.vec[i]);
	}

	poly_invntt(v);

	poly_addnoise_eta2(v, coins, nonce++);
	poly_frommsg(k, m);
	poly_add(v, v, k);
	poly_reduce(v);

	rc |= cmp_poly_compress(c + KYBER_POLYVECCOMPRESSEDBYTES, v);

	return (rc != 0);
}

void indcpa_dec(uint8_t m[KYBER_INDCPA_MSGBYTES],
	const uint8_t c[KYBER_INDCPA_BYTES],
	const uint8_t sk[KYBER_INDCPA_SECRETKEYBYTES])
{
	poly* mp = &sp.vec[0];
	poly* v = &pkp_bp;
	int i;

	poly_unpackdecompress(mp, c, 0);
	poly_ntt(mp);

	poly_frombytes_mul(mp, mp, sk);
	for (i = 1; i < KYBER_K; i++) {
		poly_unpackdecompress(&pkp_bp, c, i);
		poly_ntt(&pkp_bp);
		poly_frombytes_mul_acc(mp, &pkp_bp, sk + i * KYBER_POLYBYTES);
	}

	poly_invntt(mp);
	poly_decompress(v, c + KYBER_POLYVECCOMPRESSEDBYTES);
	poly_sub(mp, v, mp);
	poly_reduce(mp);

	poly_tomsg(m, mp);
}
