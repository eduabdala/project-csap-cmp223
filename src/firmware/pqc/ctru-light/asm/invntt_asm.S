 #include "common.inc"
 #include "macros.inc"

.section .data
.equ montfactor, 655
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

#define df_zetas0 r22
#define df_zetas1 r23
#define df_zetas_adr0 r30
#define df_zetas_adr1 r31

#define cst_q r17
#define cst_tmp r21
#define df_src_adr0 r8
#define df_src_adr1 r9

.macro	layer	const_in,	const_out,	const_offset

	ldi	df_cnt_in, \const_in
	mov	df_cnt_tmp, df_cnt_in

	ldi	df_cnt_out, \const_out

	movw	r26, df_src_adr0  ; X
	movw	r28, df_src_adr0  ; Y
	ldi	    r16, \const_offset
	add	    r28, r16
	adc	    r29, zero

0:
	lpm	df_zetas0, Z+
	lpm	df_zetas1, Z+

1:   
  mc_ntt_gs_hi    df_a0, df_a1, df_b0, df_b1, mont0, mont1
  mc_KRED2X_mul   df_b0, df_b1, df_zetas0, df_zetas1, hi0, hi1, mont0, mont1, zero
  mc_ntt_gs_lo    df_a0, df_a1, hi0, hi1

	dec	df_cnt_in
	breq	2f
	rjmp	1b

2:	
	mov	df_cnt_in, df_cnt_tmp

	ldi	r16, \const_offset
	add	r26, r16
	adc	r27, zero
	add	r28, r16
	adc	r29, zero

	dec	df_cnt_out
	breq	3f
	rjmp	0b

3:
.endm




.global	invnttkred_asm
.type	invnttkred_asm, @function

invnttkred_asm : 
	mc_prolog 0, 17


 
  ldi		  cst_q,		0x9
  ldi		  cst_tmp,		0x03
  clr zero

  movw  df_src_adr0,		r24 
	
	
  
	ldi	df_zetas_adr0, lo8(KRED2X_zetas_inv_neg)
	ldi	df_zetas_adr1, hi8(KRED2X_zetas_inv_neg)

	//layer 6
	layer	4, 64, 8
    //layer 5
	layer	8, 32, 16
    //layer 4
	layer	16, 16, 32



layer3: // Layer 3 
    ldi     df_cnt_in,  32      ; 
    movw    r26,    df_src_adr0
    movw    r28,    df_src_adr0
    ldi     r16,  64      ;
    add     r28,    r16
    adc     r29,    zero
    
out3:     
    lpm	df_zetas0, Z+
	lpm	df_zetas1, Z+ 
    push r30
    push r31
in3:
    mc_ntt_gs_hi    df_a0, df_a1, df_b0, df_b1, mont0, mont1
    mc_KRED2X_mul   df_b0, df_b1, df_zetas0, df_zetas1, hi0, hi1, mont0, mont1, zero
    mc_lut_reduce   df_a0, df_a1, mont0, zero
    mc_ntt_gs_lo    df_a0, df_a1, hi0, hi1 
   
    dec     df_cnt_in
    brne    in3             ;

    add     r26,    r16
    adc     r27,    zero
    add     r28,    r16
    adc     r29,    zero
    ldi     df_cnt_in,  32  
    pop r31
    pop r30  

out3_2:     
    lpm	df_zetas0, Z+
	lpm	df_zetas1, Z+ 
    push r30
    push r31
in3_2:
    mc_ntt_gs_hi    df_a0, df_a1, df_b0, df_b1, mont0, mont1
    mc_KRED2X_mul   df_b0, df_b1, df_zetas0, df_zetas1, hi0, hi1, mont0, mont1, zero
    mc_lut_reduce   df_a0, df_a1, mont0, zero
    mc_ntt_gs_lo    df_a0, df_a1, hi0, hi1 

   
    dec     df_cnt_in
    brne    in3_2             ;

    add     r26,    r16
    adc     r27,    zero
    add     r28,    r16
    adc     r29,    zero
    ldi     df_cnt_in,  32  
    pop r31
    pop r30  
 
out3_3:     
    lpm	df_zetas0, Z+
	lpm	df_zetas1, Z+ 
    push r30
    push r31
in3_3:
    mc_ntt_gs_hi    df_a0, df_a1, df_b0, df_b1, mont0, mont1
    mc_KRED2X_mul   df_b0, df_b1, df_zetas0, df_zetas1, hi0, hi1, mont0, mont1, zero
    mc_lut_reduce   df_a0, df_a1, mont0, zero
    mc_ntt_gs_lo    df_a0, df_a1, hi0, hi1 
 
   
    dec     df_cnt_in
    brne    in3_3             ;

    add     r26,    r16
    adc     r27,    zero
    add     r28,    r16
    adc     r29,    zero
    ldi     df_cnt_in,  32  
    pop r31
    pop r30  


out3_4:     
    lpm	df_zetas0, Z+
	lpm	df_zetas1, Z+ 
    push r30
    push r31
in3_4:
    mc_ntt_gs_hi    df_a0, df_a1, df_b0, df_b1, mont0, mont1
    mc_KRED2X_mul   df_b0, df_b1, df_zetas0, df_zetas1, hi0, hi1, mont0, mont1, zero
    mc_lut_reduce   df_a0, df_a1, mont0, zero
    mc_ntt_gs_lo    df_a0, df_a1, hi0, hi1 
 
   
    dec     df_cnt_in
    brne    in3_4             ;

    add     r26,    r16
    adc     r27,    zero
    add     r28,    r16
    adc     r29,    zero
    ldi     df_cnt_in,  32  
    pop r31
    pop r30  

out3_5:     
    lpm	df_zetas0, Z+
	lpm	df_zetas1, Z+ 
    push r30
    push r31
in3_5:
    mc_ntt_gs_hi    df_a0, df_a1, df_b0, df_b1, mont0, mont1
    mc_KRED2X_mul   df_b0, df_b1, df_zetas0, df_zetas1, hi0, hi1, mont0, mont1, zero
    mc_lut_reduce   df_a0, df_a1, mont0, zero
    mc_ntt_gs_lo    df_a0, df_a1, hi0, hi1 
 
   
    dec     df_cnt_in
    brne    in3_5             ;

    add     r26,    r16
    adc     r27,    zero
    add     r28,    r16
    adc     r29,    zero
    ldi     df_cnt_in,  32  
    pop r31
    pop r30  



out3_6:     
    lpm	df_zetas0, Z+
	lpm	df_zetas1, Z+ 
    push r30
    push r31
in3_6:
    mc_ntt_gs_hi    df_a0, df_a1, df_b0, df_b1, mont0, mont1
    mc_KRED2X_mul   df_b0, df_b1, df_zetas0, df_zetas1, hi0, hi1, mont0, mont1, zero
    mc_lut_reduce   df_a0, df_a1, mont0, zero
    mc_ntt_gs_lo    df_a0, df_a1, hi0, hi1 
 
   
    dec     df_cnt_in
    brne    in3_6             ;

    add     r26,    r16
    adc     r27,    zero
    add     r28,    r16
    adc     r29,    zero
    ldi     df_cnt_in,  32  
    pop r31
    pop r30  



out3_7:     
    lpm	df_zetas0, Z+
	lpm	df_zetas1, Z+ 
    push r30
    push r31
in3_7:
    mc_ntt_gs_hi    df_a0, df_a1, df_b0, df_b1, mont0, mont1
    mc_KRED2X_mul   df_b0, df_b1, df_zetas0, df_zetas1, hi0, hi1, mont0, mont1, zero
    mc_lut_reduce   df_a0, df_a1, mont0, zero
    mc_ntt_gs_lo    df_a0, df_a1, hi0, hi1 
 
   
    dec     df_cnt_in
    brne    in3_7             ;

    add     r26,    r16
    adc     r27,    zero
    add     r28,    r16
    adc     r29,    zero
    ldi     df_cnt_in,  32  
    pop r31
    pop r30  



out3_8:     
    lpm	df_zetas0, Z+
	lpm	df_zetas1, Z+ 
    push r30
    push r31
in3_8:
    mc_ntt_gs_hi    df_a0, df_a1, df_b0, df_b1, mont0, mont1
    mc_KRED2X_mul   df_b0, df_b1, df_zetas0, df_zetas1, hi0, hi1, mont0, mont1, zero
    mc_lut_reduce   df_a0, df_a1, mont0, zero
    mc_ntt_gs_lo    df_a0, df_a1, hi0, hi1 
 
   
    dec     df_cnt_in
    brne    in3_8             ;

    add     r26,    r16
    adc     r27,    zero
    add     r28,    r16
    adc     r29,    zero
    ldi     df_cnt_in,  32  
    pop r31
    pop r30  




	//layer 2
	layer	64, 4, 128


// layer 1
layer1 :
  ; 0 -255
	movw	r26, df_src_adr0 
	movw	r28, df_src_adr0
	inc	r29

	ldi	df_cnt_in, 128
    mov	df_cnt_tmp, df_cnt_in

	lpm	df_zetas0, Z+
	lpm	df_zetas1, Z+

1:

	mc_ntt_gs_hi    df_a0, df_a1, df_b0, df_b1, mont0, mont1
	mc_KRED2X_mul   df_b0, df_b1, df_zetas0, df_zetas1, hi0, hi1, mont0, mont1, zero
	mc_ntt_gs_lo    df_a0, df_a1, hi0, hi1

	dec	df_cnt_in
	breq	2f
	rjmp	1b      

  
2:  
  ;256 - 511
  mov	df_cnt_in, df_cnt_tmp

  movw	r26, df_src_adr0 
  movw	r28, df_src_adr0

  ldi   r16, 0x00
  add   r26, r16
  ldi   r16, 0x02
  adc   r27, r16

  ldi   r16, 0x00
  add   r28, r16
  ldi   r16, 0x03
  adc   r29, r16

  lpm	df_zetas0, Z+
  lpm	df_zetas1, Z+

10: 
  mc_ntt_gs_hi    df_a0, df_a1, df_b0, df_b1, mont0, mont1
  mc_KRED2X_mul  df_b0, df_b1, df_zetas0, df_zetas1, hi0, hi1, mont0, mont1, zero
  mc_ntt_gs_lo    df_a0, df_a1, hi0, hi1
  dec	df_cnt_in
  breq	11f
  rjmp	10b     


11:
; layer 0
layer0 :

	movw	r26, df_src_adr0 
	movw	r28, df_src_adr0
	inc	r29
    inc r29

	ldi	df_cnt_in, 0

	lpm	df_zetas0, Z+
	lpm	df_zetas1, Z+

12:

	mc_ntt_gs_hi    df_a0, df_a1, df_b0, df_b1, mont0, mont1
	mc_KRED2X_mul  df_b0, df_b1, df_zetas0, df_zetas1, hi0, hi1, mont0, mont1, zero
	mc_ntt_gs_lo    df_a0, df_a1, hi0, hi1
	dec	df_cnt_in
	breq	13f
	rjmp	12b  

13:



; fqmul(r[j],f)

	movw	r28, df_src_adr0
	ldi     r24, lo8(512)  
    ldi     r25, hi8(512)  
	ldi	df_zetas0, lo8(montfactor)
	ldi	df_zetas1, hi8(montfactor)

14:
	ldd	df_b0, Y+0
	ldd	df_b1, Y+1

	
    ;mc_769_montmul  df_b0, df_b1, df_zetas0, df_zetas1, lo0, lo1, hi0, hi1, mont0, mont1, mont2, mont3, c_tmp, cst_q, zero
	mc_KRED2X_mul  df_b0, df_b1, df_zetas0, df_zetas1, hi0, hi1, mont0, mont1, zero
	st	Y+, hi0
	st	Y+, hi1
	sbiw    r24, 1
	brne	14b











end:


	mc_epilog 0, 17


	ret
 