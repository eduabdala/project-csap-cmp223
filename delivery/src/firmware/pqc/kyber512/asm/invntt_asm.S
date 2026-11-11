 #include "common.i"
 #include "mul_asm.i"

.section .data
.equ barret_asm, 0x4EBF
.equ Q_asm, 3329
.equ montfactor, 1441

.section .text

#define zero r5



#define df_carry r2
#define df_cnt_tmp r3

#define df_cnt_in r24
#define df_cnt_out r25


#define mont0 r10
#define mont1 r11
#define mont2 r12
#define mont3 r13

#define	hi0    	r14	
#define	hi1    	r15

#define df_a0 r6
#define df_a1 r7
#define df_b0 r18
#define df_b1 r19

#define lo0 r20
#define lo1 r21



#define df_zetas0 r22
#define df_zetas1 r23
#define df_zetas_adr0 r26
#define df_zetas_adr1 r27

#define cst_q r16
#define c_tmp r17
#define df_src_adr0 r8
#define df_src_adr1 r9

.macro	layer_reduce	const_in,	const_out,	const_offset

	ldi	df_cnt_in, \const_in
	mov	df_cnt_tmp, df_cnt_in

	ldi	df_cnt_out, \const_out

	movw	r28, df_src_adr0  ;Y
	movw	r30, df_src_adr0  ;Z
	ldi	r17, \const_offset
	add	r30, r17
	adc	r31, zero

0:
	ld	df_zetas1, -X
	ld	df_zetas0, -X

1:   
  mc_ntt_gs_hi_sram    df_a0, df_a1, df_b0, df_b1, mont0, mont1
	
	
	mc_3329_montmul_opt  df_b0, df_b1, df_zetas0, df_zetas1, lo0, lo1, hi0, hi1, mont0, mont1, cst_q, zero
  push r30
  push r31
	mc_lut_reduce_3329   df_a0, df_a1, mont0, zero
	pop  r31
  pop  r30
	mc_ntt_gs_lo_sram    df_a0, df_a1, hi0, hi1

	dec	df_cnt_in
	breq	2f
	rjmp	1b

2:	
	mov	df_cnt_in, df_cnt_tmp

	ldi	r17, \const_offset
	add	r28, r17
	adc	r29, zero
	add	r30, r17
	adc	r31, zero

	dec	df_cnt_out
	breq	3f
	rjmp	0b

3:
.endm


.macro	layer	const_in,	const_out,	const_offset

	ldi	df_cnt_in, \const_in
	mov	df_cnt_tmp, df_cnt_in

	ldi	df_cnt_out, \const_out

	movw	r28, df_src_adr0  ;Y
	movw	r30, df_src_adr0  ;Z
	ldi	r17, \const_offset
	add	r30, r17
	adc	r31, zero

0:
	ld	df_zetas1, -X
	ld	df_zetas0, -X

1:   
  mc_ntt_gs_hi_sram    df_a0, df_a1, df_b0, df_b1, mont0, mont1
	
	
	mc_3329_montmul_opt  df_b0, df_b1, df_zetas0, df_zetas1, lo0, lo1, hi0, hi1, mont0, mont1, cst_q, zero

	
	mc_ntt_gs_lo_sram    df_a0, df_a1, hi0, hi1

	dec	df_cnt_in
	breq	2f
	rjmp	1b

2:	
	mov	df_cnt_in, df_cnt_tmp

	ldi	r17, \const_offset
	add	r28, r17
	adc	r29, zero
	add	r30, r17
	adc	r31, zero

	dec	df_cnt_out
	breq	3f
	rjmp	0b

3:
.endm

.global	invntt_asm
.type	invntt_asm, @function

invntt_asm : 
	mc_prolog 0, 17

  movw  df_src_adr0,		r24 
	
	
  clr zero
	clr df_carry
	ldi     cst_q,    0xF3  
	ldi	df_zetas_adr0, lo8(zetas)
	ldi	df_zetas_adr1, hi8(zetas)
  inc	df_zetas_adr1

  //layer 7
	layer	2, 64, 4

	//layer 6
	layer	4, 32, 8

	//layer 5
	layer_reduce	8, 16, 16

	//layer 4
	layer	16, 8, 32

	//layer 3
	layer	32, 4, 64

	//layer 2
	layer_reduce	64, 2, 128



// layer 1
layer1 :
  ; 0 -255
	movw	r28, df_src_adr0 
	movw	r30, df_src_adr0
	inc	r31

	ldi	df_cnt_in, 128
  mov	df_cnt_tmp, df_cnt_in

  ldi df_zetas0, lo8(-758)
  ldi df_zetas1, hi8(-758)

1:

	mc_ntt_gs_hi_sram    df_a0, df_a1, df_b0, df_b1, mont0, mont1
  mc_3329_montmul_opt  df_b0, df_b1, df_zetas0, df_zetas1, lo0, lo1, hi0, hi1, mont0, mont1, cst_q, zero
  mc_ntt_gs_lo_sram    df_a0, df_a1, hi0, hi1

  dec	df_cnt_in
	breq  2f
	rjmp	1b      


2:
; fqmul(r[j],f)

	movw	r28, df_src_adr0
	ldi     r24, lo8(256)  
  ldi     r25, hi8(256)  
	ldi	df_zetas0, lo8(montfactor)
	ldi	df_zetas1, hi8(montfactor)

14:
	ldd	df_b0, Y+0
	ldd	df_b1, Y+1

	
    ;mc_769_montmul  df_b0, df_b1, df_zetas0, df_zetas1, lo0, lo1, hi0, hi1, mont0, mont1, mont2, mont3, c_tmp, cst_q, zero
	mc_3329_montmul_opt  df_b0, df_b1, df_zetas0, df_zetas1, lo0, lo1, hi0, hi1, mont0, mont1, cst_q, zero
	st	Y+, hi0
	st	Y+, hi1
	sbiw    r24, 1
	brne	14b

 
#undef zero

#undef df_carry
#undef df_cnt_tmp

#undef df_cnt_in
#undef df_cnt_out

#undef mont0
#undef mont1
#undef mont2
#undef mont3

#undef hi0
#undef hi1

#undef df_a0
#undef df_a1
#undef df_b0
#undef df_b1

#undef lo0
#undef lo1

#undef df_zetas0
#undef df_zetas1
#undef df_zetas_adr0
#undef df_zetas_adr1

#undef cst_q
#undef c_tmp
#undef df_src_adr0
#undef df_src_adr1



end:


	mc_epilog 0, 17
	ret
 