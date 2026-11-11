 #include "common.i"
 #include "mul_asm.i"

.section .text

#define	res_mul_l		r0
#define	res_mul_h		r1
#define	zero			r2
#define	tmp0_l			r4
#define	tmp0_h			r5
#define	tmp1_l			r6
#define	tmp1_h			r7
#define res0_l			r8
#define res0_h			r9
#define res1_l			r10
#define res1_h			r11
#define	imm_tmp2		r12
#define	imm_tmp3		r13
#define	tmp_addr_l		r14
#define	tmp_addr_h		r15
#define	tmp_int			r17
#define	zeta_l			r24
#define	zeta_h			r25
#define	src0_l			r20
#define	src0_h			r21
#define	src1_l			r22
#define	src1_h			r23
#define	imm_tmp0		r18
#define	imm_tmp1		r19



.global	basemul_asm
.type	basemul_asm, @function

basemul_asm : 
	mc_prolog 0, 17

	
	movw	r26,		r24
	movw	r28,		r22
	movw	r30,		r20
  movw r24, r18

  clr		zero
  ldi     tmp_int,    0xF3  

	ldd		src0_l,		Y+0
	ldd		src0_h,		Y+1
	ldd		src1_l,		Z+0
	ldd		src1_h,		Z+1

	// LUT_reduction((int32_t) a[0] * b[0]);
  mc_3329_montmul_opt src0_l, src0_h, src1_l, src1_h, imm_tmp0, imm_tmp1, res0_l, res0_h, imm_tmp2, imm_tmp3, tmp_int, zero


	// LUT_reduction((int32_t) (a[0] + a[1]) * (b[1] + b[0]));
  ldd		src0_l,		Y+0
	ldd		src0_h,		Y+1
	ldd		src1_l,		Z+0
	ldd		src1_h,		Z+1
	ldd		tmp0_l,		Y+2
	ldd		tmp0_h,		Y+3
	ldd		tmp1_l,		Z+2
	ldd		tmp1_h,		Z+3

	add		src0_l,		tmp0_l
	adc		src0_h,		tmp0_h

  add		src1_l,		tmp1_l
	adc		src1_h,		tmp1_h
	
	
  mov    res1_l, src0_l
  mov    res1_h, src0_h


  mc_3329_montmul_opt src0_l, src0_h, src1_l, src1_h, imm_tmp0, imm_tmp1, res1_l, res1_h, imm_tmp2, imm_tmp3, tmp_int, zero


	// temp[1] += temp[0]
	sub		res1_l,		res0_l
	sbc		res1_h,		res0_h

	movw	src0_l,		tmp0_l
	movw	src1_l,		tmp1_l

  mc_3329_montmul_opt src0_l, src0_h, src1_l, src1_h, imm_tmp0, imm_tmp1, tmp_addr_l, tmp_addr_h, imm_tmp2, imm_tmp3, tmp_int, zero


  
	// temp[1] += temp[0]
	sub		res1_l,	 tmp_addr_l
	sbc		res1_h,	 tmp_addr_h

	mov src1_l, zeta_l
  mov src1_h, zeta_h
  mov src0_l, tmp_addr_l
  mov src0_h, tmp_addr_h
  mc_3329_montmul_opt src0_l, src0_h, src1_l, src1_h, imm_tmp0, imm_tmp1, tmp_addr_l, tmp_addr_h, imm_tmp2, imm_tmp3, tmp_int, zero

  
  
  add		res0_l,		tmp_addr_l
	adc		res0_h,		tmp_addr_h

	st		X+,			res0_l
	st		X+,			res0_h
	st		X+,			res1_l
	st		X+,			res1_h

	mc_epilog 0, 17
	ret


#undef	res_mul_l		
#undef	res_mul_h		
#undef	zero			
#undef	tmp0_l			
#undef	tmp0_h			
#undef	tmp1_l			
#undef	tmp1_h			
#undef	res0_l			
#undef	res0_h			
#undef	res1_l			
#undef	res1_h			
#undef	imm_tmp2		
#undef	imm_tmp3		
#undef	tmp_addr_l		
#undef	tmp_addr_h		
#undef	tmp_int			
#undef	zeta_l
#undef	zeta_h			
#undef	src0_l			
#undef	src0_h			
#undef	src1_l
#undef	src1_h
#undef	imm_tmp0
#undef	imm_tmp1