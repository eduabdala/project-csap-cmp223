#include <stddef.h>
#include "randombytes.h"
#include "symmetric_crypto.h"
#include "params.h"
#include "ctru.h"
#include "api.h"

int crypto_kem_keypair(unsigned char * pk, unsigned char * sk)
{
  unsigned int i;
  unsigned char coins[CTRU_COINBYTES_KEYGEN];
  unsigned char seed[CTRU_SEEDBYTES];

  do
  {
    randombytes(seed, CTRU_SEEDBYTES);
    crypto_hash_shake128(coins, CTRU_COINBYTES_KEYGEN, seed, CTRU_SEEDBYTES);
  } while (pke_keygen(pk, sk, coins));

  for (i = 0; i < CTRU_PKE_PUBLICKEYBYTES; ++i)
    sk[i + CTRU_PKE_SECRETKEYBYTES] = pk[i];

  randombytes(sk + CTRU_PKE_SECRETKEYBYTES + CTRU_PKE_PUBLICKEYBYTES, CTRU_SEEDBYTES);
  return 0;
}

int crypto_kem_enc(unsigned char * pk, unsigned char * ss, unsigned char * ct)
{
  unsigned int i;
  unsigned char buf[CTRU_SHAREDKEYBYTES + CTRU_COINBYTES_ENC], m[CTRU_MSGBYTES];
 
  unsigned char buf2[CTRU_PREFIXHASHBYTES + CTRU_MSGBYTES];
  randombytes(m, CTRU_MSGBYTES);

  for (i = 0; i < CTRU_PREFIXHASHBYTES; ++i)
    buf2[i] = pk[i];
  for (i = 0; i < CTRU_MSGBYTES; ++i)
    buf2[i + CTRU_PREFIXHASHBYTES] = m[i];

  crypto_hash_sha3_256(buf, buf2, CTRU_PREFIXHASHBYTES + CTRU_MSGBYTES);
  crypto_hash_shake128(buf + CTRU_SHAREDKEYBYTES, CTRU_COINBYTES_ENC, buf + CTRU_SHAREDKEYBYTES, CTRU_SHAREDKEYBYTES);

  pke_enc(ct, pk, m, buf + CTRU_SHAREDKEYBYTES);

  for (i = 0; i < CTRU_SHAREDKEYBYTES; ++i)
    ss[i] = buf[i];
  return 0;
}

int crypto_kem_dec(unsigned char * sk, unsigned char * ct, unsigned char * ss)
{
  unsigned int i;
  unsigned char buf[CTRU_SHAREDKEYBYTES + CTRU_COINBYTES_ENC], buf2[SHA3_OUTPUTBYTES], m[CTRU_PREFIXHASHBYTES + CTRU_MSGBYTES];
  unsigned char ct2[CTRU_PREFIXHASHBYTES + CTRU_PKE_CIPHERTEXTBYTES + CTRU_SEEDBYTES];
  int16_t t;
  int32_t fail;

  pke_dec(m + CTRU_PREFIXHASHBYTES, ct, sk);

  for (i = 0; i < CTRU_PREFIXHASHBYTES; ++i)
  {
    m[i] = sk[i + CTRU_PKE_SECRETKEYBYTES];
    ct2[i] = sk[i + CTRU_PKE_SECRETKEYBYTES];
  }

  crypto_hash_sha3_256(buf, m, CTRU_PREFIXHASHBYTES + CTRU_MSGBYTES);
  crypto_hash_shake128(buf + CTRU_SHAREDKEYBYTES, CTRU_COINBYTES_ENC, buf + CTRU_SHAREDKEYBYTES, CTRU_SHAREDKEYBYTES);

  pke_enc(ct2, sk + CTRU_PKE_SECRETKEYBYTES, m + CTRU_PREFIXHASHBYTES, buf + CTRU_SHAREDKEYBYTES);

  t = 0;
  for (i = 0; i < CTRU_PKE_CIPHERTEXTBYTES; ++i)
    t |= ct[i] ^ ct2[i];

  fail = (uint16_t)t;
  fail = (-fail) >> 31;


  //concatenate c
  for(i = 0; i < CTRU_KEM_CIPHERTEXTBYTES; ++i)
  {
    ct2[i + CTRU_PREFIXHASHBYTES] = ct[i];
  }
  //concatenate z
  for(i = 0; i < CTRU_SEEDBYTES; ++i)
  {
    ct2[i + CTRU_PREFIXHASHBYTES + CTRU_KEM_CIPHERTEXTBYTES] = sk[i + CTRU_PKE_SECRETKEYBYTES + CTRU_PKE_PUBLICKEYBYTES];
  }
  //H(ID(pk),c,z)
  crypto_hash_sha3_256(buf2, ct2, CTRU_PREFIXHASHBYTES + CTRU_KEM_CIPHERTEXTBYTES + CTRU_SEEDBYTES);
 

  for (i = 0; i < CTRU_SHAREDKEYBYTES; ++i)
    ss[i] = buf[i] ^ ((-fail) & (buf[i] ^ buf2[i]));
  return fail;
}
