#include "params.h"
#include "poly.h"
#include "pack.h"
#include <stdio.h>

int pke_keygen(unsigned char pk[CTRU_PKE_PUBLICKEYBYTES],
                      unsigned char sk[CTRU_PKE_SECRETKEYBYTES],
                      const unsigned char coins[CTRU_COINBYTES_KEYGEN])
{
  int r;
  poly f,g;

  poly_sample_keygen(&f, coins);
  poly_sample_keygen(&g, coins + CTRU_COINBYTES_KEYGEN / 2);

  poly_multi_p(&f, &f);
  f.coeffs[0] += 1;
  pack_sk(sk, &f);
  poly_ntt_asm(&f);
  poly_ntt_asm(&g);

  r = poly_baseinv_asm(&f, &f);
  poly_basemul_asm(&f, &g, &f);
  poly_invntt_asm(&f);
  poly_freeze(&f);
  pack_pk(pk, &f);

  return r;
}


void pke_enc(unsigned char ct[CTRU_PKE_CIPHERTEXTBYTES],
                    const unsigned char pk[CTRU_PKE_PUBLICKEYBYTES],
                    const unsigned char m[CTRU_MSGBYTES],
                    const unsigned char coins[CTRU_COINBYTES_ENC])
{
  poly r, hhat;

  unpack_pk(&hhat, pk);

  poly_sample_enc(&r, coins);
  poly_ntt_asm(&hhat);
  poly_ntt_asm(&r);
  poly_basemul_asm(&r, &hhat, &r);
  poly_invntt_asm(&r);
  poly_freeze(&r);
  poly_compress(&hhat, &r);
  
  poly_encode_e8(&r, m);
  poly_add(&hhat, &hhat, &r);
  pack_ct(ct, &hhat);
}


void pke_dec(unsigned char m[CTRU_MSGBYTES],
                    const unsigned char ct[CTRU_PKE_CIPHERTEXTBYTES],
                    const unsigned char sk[CTRU_PKE_SECRETKEYBYTES])
{
    poly c, fhat;

    unpack_ct(&c, ct);
    unpack_sk(&fhat, sk);
    poly_decompress(&c, &c);

    poly_ntt_asm(&fhat);
    poly_ntt_asm(&c);
    poly_basemul_asm(&c, &c, &fhat);
    poly_invntt_asm(&c);
    poly_freeze(&c);
    
    poly_decode_e8(m, &c);
}
