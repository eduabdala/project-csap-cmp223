#include <stdint.h>
#include <stdio.h>
#include "params.h"
#include "ntt.h"
#include "reduce.h"

#define CALC_D(a, b, x, y, d) (fqmul((a[x] + a[y]), (b[x] + b[y])) - d[x] - d[y])

int16_t zetas[128] = {
171, 605, 688, 361, 583, 3, 250, 120, 640, 461, 223, 753, 626, 362, 432, 638,
694, 733, 76, 98, 203, 282, 430, 514, 178, 270, 199, 34, 400, 192, 620, 759,
689, 423, 645, 2, 114, 147, 715, 497, 600, 288, 161, 754, 683, 51, 405, 502,
170, 543, 648, 188, 719, 745, 307, 578, 263, 157, 523, 128, 375, 180, 389, 279,
428, 390, 202, 220, 236, 21, 212, 71, 635, 151, 23, 657, 537, 227, 717, 621,
244, 517, 532, 686, 652, 436, 703, 522, 477, 352, 624, 238, 493, 575, 495, 699,
209, 654, 670, 14, 29, 260, 391, 403, 355, 478, 358, 664, 167, 357, 528, 438,
421, 725, 691, 547, 419, 601, 611, 201, 303, 330, 585, 127, 318, 491, 416, 415
};

/*************************************************
* Name:        ntt
**************************************************/
void ntt(int16_t r[512]) {
  unsigned int len, start, j, k;
  int16_t zeta, t;

  k = 0;
  for(len = 256; len > 2; len >>= 1) {
    for(start = 0; start < 512; start = j + len) {
      zeta = zetas[++k];
      for(j = start; j < start + len; ++j) {
        t = fqmul(zeta, r[j + len]);
        r[j + len] = r[j] - t;
        r[j] = r[j] + t;
      }
    }
  }

}

/*************************************************
* Name:        invntt
**************************************************/
void invntt(int16_t r[512]) {

  unsigned int start, len, j, k;
  int16_t t, zeta;

  k = 127;
  for(len = 4; len < 512; len <<= 1) {
    for(start = 0; start < 512; start = j + len) {
      zeta = zetas[k--];
      for(j = start; j < start + len; ++j) {
        t = r[j];
        r[j] = t + r[j + len];
        r[j + len] = r[j + len] - t;
        r[j + len] = fqmul(zeta, r[j + len]);
      }
    }
  }

  for(j = 0; j < 512; ++j) 
    r[j] = fqmul(r[j], 655);
  
}


/*************************************************
* Name:        basemul
**************************************************/
void basemul(int16_t c[4], const int16_t a[4], const int16_t b[4], int16_t zeta)
{
    int16_t d[4];
    int i;
    for(i=0;i<4;i++)
        d[i] = fqmul(a[i],b[i]);  
    
    c[0] = d[0] + fqmul((CALC_D(a, b, 1, 3, d)+d[2]), zeta);
    c[1] = CALC_D(a, b, 0, 1, d) + fqmul(CALC_D(a, b, 2, 3, d), zeta);
    c[2] = (CALC_D(a, b, 0, 2, d) + d[1] + fqmul(d[3], zeta));
    c[3] = (CALC_D(a, b, 1, 2, d) + CALC_D(a, b, 0, 3, d));
    
}

/*************************************************
* Name:        baseinv
**************************************************/
int baseinv(int16_t b[4], const int16_t a[4], int16_t zeta)
{
	int16_t det;
	int16_t f0_sq, f1_sq, f2_sq, f3_sq, zeta_sq;
	int16_t f0_f, f1_f, f2_f, f3_f;
	int16_t tmp, tmp2;
	int32_t rtmp;
	uint16_t r;
	
	f0_sq = fqmul(a[0], a[0]);
	f1_sq = fqmul(a[1], a[1]);
	f2_sq = fqmul(a[2], a[2]);
	f3_sq = fqmul(a[3], a[3]);
	zeta_sq = fqmul(zeta, zeta);
	
	f0_f = fqmul(f0_sq, f0_sq);
	f1_f = fqmul(f1_sq, f1_sq);
	f2_f = fqmul(f2_sq, f2_sq);
	f3_f = fqmul(f3_sq, f3_sq);
	

	// compute determinant
	det = 4*(int32_t)f0_sq;
	det = fqmul(a[1], det);
	det = fqmul(a[3], det);
	det = fqmul(det, zeta);
	det = f0_f - det; //2q
	
	tmp = 2*(int32_t)f0_sq;
	tmp = fqmul(tmp, f2_sq);
	tmp = fqmul(tmp, zeta);

	det -= tmp; //3q
	
	tmp = 4*(int32_t)a[0];
	tmp2 = fqmul(tmp, a[2]);
	tmp2 = fqmul(tmp2, f3_sq);
	tmp2 = fqmul(tmp2, zeta_sq);
	tmp = fqmul(tmp, f1_sq);
	tmp = fqmul(tmp, a[2]);
	tmp = fqmul(tmp, zeta);
	
	det += tmp;  //5q
	det += tmp2; //6q
	
	tmp =  fqmul(f1_f, zeta);
	
	det -= tmp; //7q
	
	tmp = 2*(int32_t)f1_sq;
	tmp = fqmul(tmp, f3_sq);
	tmp = fqmul(tmp, zeta_sq);
	
	det += tmp; //8q
	
	tmp = 4*(int32_t)a[1];
	tmp = fqmul(tmp, f2_sq);
	tmp = fqmul(tmp, a[3]);
	tmp = fqmul(tmp, zeta_sq);
	
	det -= tmp;//9q
	
	tmp = fqmul(f2_f,zeta_sq);
	
	det += tmp; //10q
	
	tmp = fqmul(zeta_sq, zeta);
	tmp = fqmul(tmp, f3_f);
	
	det -= tmp; //11q
	
	// compute inverse of determinant
	det = fqinv(det); //q
	
	b[0] =  fqmul(f0_sq, a[0]);
	
	tmp = 2*(int32_t)a[0];
	tmp = fqmul(tmp, a[1]);
	tmp = fqmul(tmp, a[3]);
	tmp = fqmul(tmp, zeta);
	
	b[0] -= tmp; //2q
	
	tmp = fqmul(a[0], f2_sq);
	tmp = fqmul(tmp, zeta);
	
	b[0] -= tmp; //3q
	
	tmp = fqmul(a[2], f1_sq);
	tmp = fqmul(tmp, zeta);
	
	b[0] += tmp; //4q


	tmp = fqmul(a[2], f3_sq);
	tmp = fqmul(tmp, zeta_sq);


	b[0] += tmp; //5q
	b[1]= 2*(int32_t)a[0];
	b[1] = fqmul(b[1], a[2]);
	b[1] = fqmul(b[1], a[3]);
	b[1] = fqmul(b[1], zeta);

	tmp = fqmul(f0_sq, a[1]);
	b[1] -= tmp;

	tmp = fqmul(f1_sq, a[3]);
	tmp = fqmul(tmp, zeta);
	b[1] += tmp;

	tmp = fqmul(a[1], f2_sq);
	tmp = fqmul(tmp, zeta);
	b[1] -= tmp;
	tmp = fqmul(f3_sq, a[3]);
	tmp = fqmul(tmp, zeta_sq);
	b[1] -= tmp;
	b[2] =fqmul(a[0], f1_sq);
	tmp = fqmul(f0_sq, a[2]);
	b[2] -= tmp;
	tmp = fqmul(a[0], f3_sq);
	tmp = fqmul(tmp, zeta);
	b[2] += tmp;
	tmp = 2*a[1];
	tmp = fqmul(tmp, a[2]);
	tmp = fqmul(tmp, a[3]);
	tmp = fqmul(tmp, zeta);
	b[2] -= tmp;

	tmp = fqmul(f2_sq,a[2]);
	tmp = fqmul(tmp, zeta);
	b[2] += tmp;
	b[3] = 2*(int32_t)a[0];
	b[3] = fqmul(b[3],a[1]);
	b[3] = fqmul(b[3],a[2]);
	
	tmp = fqmul(f0_sq,a[3]);
	b[3] -= tmp;
	tmp = fqmul(f1_sq,a[1]);
	b[3] -= tmp;
	tmp = fqmul(f3_sq,a[1]);
	tmp = fqmul(tmp, zeta);
	b[3] += tmp;
	tmp = fqmul(f2_sq,a[3]);
	tmp = fqmul(tmp, zeta);
	b[3] -= tmp;
	b[0] = fqmul(b[0], det);
	b[1] = fqmul(b[1], det);
	b[2] = fqmul(b[2], det);
	b[3] = fqmul(b[3], det);
	r = (uint16_t)det;
	rtmp = (uint32_t)(-(int32_t)r) >> 31;
	
	return rtmp - 1;
}

int baseinv_opt(int16_t r[4], const int16_t a[4], int16_t zeta)
{
	int16_t t0, t1, t2, t3;
	
	t0 = montgomery_reduce((int32_t)a[2]*a[2] - 2*(int32_t)a[1]*a[3]);                     // R^-1
	t1 = montgomery_reduce((int32_t)a[3]*a[3]);                                            // R^-1
	t0 = montgomery_reduce((int32_t)a[0]*a[0] + (int32_t)t0*zeta);                         // R^-1
	t1 = montgomery_reduce((int32_t)a[1]*a[1] + (int32_t)t1*zeta - 2*(int32_t)a[0]*a[2]);  // R^-1
	t2 = montgomery_reduce((int32_t)t1*zeta);                                              // R^-1
	
	t3 = montgomery_reduce((int32_t)t0*t0 - (int32_t)t1*t2);  // R^-3

	if (t3 == 0) return 1;

	r[0] = montgomery_reduce((int32_t)a[0]*t0 + (int32_t)a[2]*t2); // R^-2
	r[1] = montgomery_reduce((int32_t)a[3]*t2 + (int32_t)a[1]*t0); // R^-2
	r[2] = montgomery_reduce((int32_t)a[2]*t0 + (int32_t)a[0]*t1); // R^-2
	r[3] = montgomery_reduce((int32_t)a[1]*t1 + (int32_t)a[3]*t0); // R^-2

	t3 = fqinv(t3); // R^3

	r[0] =  montgomery_reduce((int32_t)r[0]*t3); // R^0
	r[1] = -montgomery_reduce((int32_t)r[1]*t3); // R^0
	r[2] =  montgomery_reduce((int32_t)r[2]*t3); // R^0
	r[3] = -montgomery_reduce((int32_t)r[3]*t3); // R^0

	return 0;
}

