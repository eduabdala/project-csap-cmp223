


.macro mc_small_LUT_reduce_asm zero, src_l, src_h, t_l

	mov		r30,		\src_h	
	ldi		r31,		hi8(LUT3_H_3329)
	ld		\src_h,		Z
	ldi		r31,		hi8(LUT3_L_3329)
	ld		\t_l,		Z
	add		\src_l,		\t_l
	adc		\src_h,		\zero	
		
.endm



; multiply 16-bit a and b, and store the result in c (4 bytes)
.macro  mc_muls16x16_32 m_a0, m_a1, m_b0, m_b1, m_c0, m_c1, m_c2, m_c3, m_zero
	muls    \m_a1,   \m_b1        ;   (signed)ah * (signed)
	movw	\m_c2,   r0
	mul     \m_a0,   \m_b0        ;   al * bl
	movw	\m_c0,   r0
	mulsu	\m_a1,   \m_b0        ;   (signed)ah * bl
	sbc     \m_c3,   \m_zero
	add     \m_c1,   r0
	adc     \m_c2,   r1
	adc     \m_c3,   \m_zero
	mulsu	\m_b1,   \m_a0        ;   (signed)bh * al
	sbc     \m_c3,   \m_zero
	add     \m_c1,   r0
	adc     \m_c2,   r1
	adc     \m_c3,   \m_zero
.endm
; the result store in \m_hi0 and \m_hi1
.macro mc_769_montmul m_b0, m_b1, m_z0, m_z1, m_lo0, m_lo1, m_hi0, m_hi1, m_mont0, m_mont1, m_mont2, m_mont3, m_cst_tmp, m_cst_q, m_zero

    
    ldi     \m_cst_q,    0xFD          

    ; Multiply the 16-bit inputs b and z to get a 32-bit product
    ; Output: low 16 bits -> m_lo0|m_lo1, high 16 bits -> m_hi0|m_hi1
    mc_muls16x16_32 \m_b0, \m_b1, \m_z0, \m_z1, \m_lo0, \m_lo1, \m_hi0, \m_hi1, \m_zero

    ; Compute low-byte multiplication of Montgomery factor
    ; r0 will hold the high byte of the 8x8 multiplication result
    mulsu   \m_cst_q,    \m_lo0

    ; Add the high byte from mulsu to the next low byte
    add     \m_lo1,      r0

    ; Load modulus low and high bytes for the next multiplication
    ldi     \m_cst_q,    0x03          ; q low byte (for reduction step)
    ldi     \m_cst_tmp,  0x01          ; q high byte

    ; Multiply the Montgomery factor t by the modulus q
    ; Output intermediate 32-bit result into m_mont0..m_mont3
    mc_muls16x16_32 \m_lo0, \m_lo1, \m_cst_tmp, \m_cst_q, \m_mont0, \m_mont1, \m_mont2, \m_mont3, \m_zero

    ; Subtract the high 16-bit part of (t * q) from the original high 16-bit product
    ; This completes the Montgomery reduction: (a * R^-1) mod 769
    sub    \m_hi0,      \m_mont2
    sbc     \m_hi1,      \m_mont3 

.endm

.macro mc_769_montmul_opt m_b0, m_b1, m_z0, m_z1, m_lo0, m_lo1, m_hi0, m_hi1, m_mont0, m_mont1, m_cst_q, m_zero


    ; Multiply the 16-bit inputs b and z to get a 32-bit product
    ; Output: low 16 bits -> m_lo0|m_lo1, high 16 bits -> m_hi0|m_hi1
    mc_muls16x16_32 \m_b0, \m_b1, \m_z0, \m_z1, \m_lo0, \m_lo1, \m_hi0, \m_hi1, \m_zero

    ; Compute low-byte multiplication of Montgomery factor
    ; r0 will hold the high byte of the 8x8 multiplication result
    mulsu   \m_lo0, \m_cst_q

    ; Add the high byte from mulsu to the next low byte
    add     \m_lo1,      r0

    ; Multiply the Montgomery factor t by the modulus q
    ; Output intermediate 32-bit result into m_mont0..m_mont3
    ldi     \m_b0,    0x03
    muls    \m_b0,    \m_lo1
    movw    \m_mont0,    r0
    mulsu   \m_b0,    \m_lo0
    
    add     r0,          \m_lo1
	adc     \m_mont0,    r1
	adc     \m_mont1,    \m_zero

    lsl     \m_lo1      
    sbc     \m_mont0,    \m_zero
    sbc     \m_mont1,    \m_zero

    ; Subtract the high 16-bit part of (t * q) from the original high 16-bit product
    ; This completes the Montgomery reduction: (a * R^-1) mod 769
    sub    \m_hi0,      \m_mont0
    sbc    \m_hi1,      \m_mont1       

.endm




// 28 cycles: int16_t KRED2X_mul(int16_t a, int16_t b)
// use 9 register (except r0 and r1)
// in:	(ah || al) and (bh || bl)
// out:	(rh || rl)
.macro  mc_KRED2X_mul m_al, m_ah, m_bl, m_bh, m_rl, m_rh, m_t0, m_t1, m_zero

	/*int16_t KRED2X_mul(int16_t a, int16_t b)
	{
		int32_t mul = (int32_t)a * b;

		uint8_t c0;
		uint8_t c1;
		int16_t c2;

		c0 = mul & 0xFF;
		c1 = (mul >> 8) & 0xFF;
		c2 = (mul >> 16) & 0xFFFF;

		return (int16_t)(9*c0 - 3*c1 + c2);
	}*/

	mc_muls16x16_32 \m_al, \m_ah, \m_bl, \m_bh, \m_rl, \m_rh, \m_t0, \m_t1, \m_zero


	mul		\m_rl,		r17
	mov		\m_al,		\m_rh
	movw	\m_rl,		r0

	mul		r21,		\m_al
	sub		\m_rl,		r0
	sbc		\m_rh,		r1

	add		\m_rl,		\m_t0
	adc		\m_rh,		\m_t1

.endm


// 11 cycles: int16_t lut_reduce(int16_t a)
// use 4 register
// in:	(ah || al)
// out:	(ah || al)
.macro  mc_lut_reduce	m_al, m_ah, m_t, m_zero

	/*int16_t lut_reduce(int16_t a)
	{
		uint8_t lo, lut3;

		lo = a & 0xFF;
		lut3 = (a >> 8) & 0xFF;

		return (lo + __LUT3[lut3]);
	}*/

    mov		r30,	\m_ah	
	ldi		r31,	hi8(LUT3_H)
	lpm		\m_ah,	Z
	ldi		r31,	hi8(LUT3_L)
	lpm		\m_t,	Z
	add		\m_al,	\m_t
	adc		\m_ah,	\m_zero

.endm

.macro  mc_lut_reduce_3329	m_al, m_ah, m_t, m_zero

	/*int16_t lut_reduce(int16_t a)
	{
		uint8_t lo, lut3;

		lo = a & 0xFF;
		lut3 = (a >> 8) & 0xFF;

		return (lo + __LUT3[lut3]);
	}*/

    mov		r30,	\m_ah	
	ldi		r31,	hi8(LUT3_H_3329)
	lpm		\m_ah,	Z
	ldi		r31,	hi8(LUT3_L_3329)
	lpm		\m_t,	Z
	add		\m_al,	\m_t
	adc		\m_ah,	\m_zero

.endm
; b0 and b1 are first multiplicand, z0 and z1 are the second multiplicand
; m_mont0, m_mont_1, m_mont2, m_mont3 are used to store intermediate 32-bit product
; m_cst_tmp and m_cst_q are used to store 16-bit constant

.macro mc_3329_montmul m_b0, m_b1, m_z0, m_z1, m_lo0, m_lo1, m_hi0, m_hi1, \
                        m_mont0, m_mont1, m_mont2, m_mont3, m_cst_tmp, m_cst_q, m_zero

    ; Load low and high bytes of Montgomery factor QinvR = 3329^-1 mod 2^16 = 62209  = 0xF301  → low byte: 0xFF, high byte: 0x0C
    ldi     \m_cst_q,    0x01        ; low byte
    ldi     \m_cst_tmp,  0xF3        ; high byte

    ; Inputs: m_b0|m_b1 and m_z0|m_z1 are the 16-bit operands
    ; multiply b and z to get 32-bit product in lo0 lo1 h0 h1
    ; lo0 and lo1 store a0, h0 and h1 store a1
    mc_muls16x16_32 \m_b0, \m_b1, \m_z0, \m_z1, \
                     \m_lo0, \m_lo1, \m_hi0, \m_hi1, \m_zero
    
    ; multiply a0 with Qinv
    ; b0 and b1 store m
    mc_muls16x16_32 \m_lo0, \m_lo1, \m_cst_q, \m_cst_tmp, \
                     \m_b0, \m_b1, \m_mont2, \m_mont3, \m_zero
    ;multiply m with q and get the higher 16 bits
    ldi     \m_cst_q,    0x01        ; low byte
    ldi     \m_cst_tmp,  0x0D        ; high byte
    ; mont2 and mont3 store the t1 = mq >> 16
    mc_muls16x16_32 \m_b0, \m_b1, \m_cst_q, \m_cst_tmp, \
                    \m_lo0, \m_lo1, \m_mont2, \m_mont3, \m_zero
    ; a1 - t1 
    sub    \m_hi0,      \m_mont2
    sbc    \m_hi1,     \m_mont3  

.endm

.macro mc_3329_montmul_opt m_b0, m_b1, m_z0, m_z1, m_lo0, m_lo1, m_hi0, m_hi1, m_mont0, m_mont1, m_cst_q, m_zero

    
           

    ; Multiply the 16-bit inputs b and z to get a 32-bit product
    ; Output: low 16 bits -> m_lo0|m_lo1, high 16 bits -> m_hi0|m_hi1
    mc_muls16x16_32 \m_b0, \m_b1, \m_z0, \m_z1, \m_lo0, \m_lo1, \m_hi0, \m_hi1, \m_zero

    ; Compute low-byte multiplication of Montgomery factor
    ; r0 will hold the high byte of the 8x8 multiplication result
    mulsu   \m_cst_q,    \m_lo0

    ; Add the high byte from mulsu to the next low byte
    add     \m_lo1,      r0

    ; Multiply the Montgomery factor t by the modulus q
    ; Output intermediate 32-bit result into m_mont0..m_mont3
    ldi     \m_b0,    0x0D
    muls    \m_b0,    \m_lo1
    movw    \m_mont0,    r0
    mulsu   \m_b0,    \m_lo0
    
    add     r0,          \m_lo1
	adc     \m_mont0,    r1
	adc     \m_mont1,    \m_zero

    lsl     \m_lo1      
    sbc     \m_mont0,    \m_zero
    sbc     \m_mont1,    \m_zero

    ; Subtract the high 16-bit part of (t * q) from the original high 16-bit product
    ; This completes the Montgomery reduction: (a * R^-1) mod 769
    sub    \m_hi0,      \m_mont0
    sbc    \m_hi1,      \m_mont1       

.endm


.macro mc_7681_montmul m_b0, m_b1, m_z0, m_z1, m_lo0, m_lo1, m_hi0, m_hi1, \
                        m_mont0, m_mont1, m_mont2, m_mont3, m_cst_tmp, m_cst_q, m_zero

    ; Load low and high bytes of Montgomery factor QinvR = 7681^-1 mod 2^16 = 57857  = 0xE201  
    ldi     \m_cst_q,    0x01        ; low byte
    ldi     \m_cst_tmp,  0xE2        ; high byte

    ; Inputs: m_b0|m_b1 and m_z0|m_z1 are the 16-bit operands
    ; multiply b and z to get 32-bit product in lo0 lo1 h0 h1
    ; lo0 and lo1 store a0, h0 and h1 store a1
    mc_muls16x16_32 \m_b0, \m_b1, \m_z0, \m_z1, \
                     \m_lo0, \m_lo1, \m_hi0, \m_hi1, \m_zero
    
    ; multiply a0 with Qinv
    ; mont0 and mont1 store m
    mc_muls16x16_32 \m_lo0, \m_lo1, \m_cst_q, \m_cst_tmp, \
                     \m_b0, \m_b1, \m_mont2, \m_mont3, \m_zero
    ;multiply m with q and get the higher 16 bits
    ; 7681 = 0x1E01
    ldi     \m_cst_q,    0x01        ; low byte
    ldi     \m_cst_tmp,  0x1E        ; high byte
    ; mont2 and mont3 store the t1 = mq >> 16
    mc_muls16x16_32 \m_b0, \m_b1, \m_cst_q, \m_cst_tmp, \
                    \m_lo0, \m_lo1, \m_mont2, \m_mont3, \m_zero
    ; a1 - t1 
    sub    \m_hi0,      \m_mont2
    sbc    \m_hi1,     \m_mont3  

.endm


.macro mc_7681_montmul_opt m_b0, m_b1, m_z0, m_z1, m_lo0, m_lo1, m_hi0, m_hi1, m_mont0, m_mont1, m_cst_q, m_zero

    
           
 
    ; Multiply the 16-bit inputs b and z to get a 32-bit product
    ; Output: low 16 bits -> m_lo0|m_lo1, high 16 bits -> m_hi0|m_hi1
    mc_muls16x16_32 \m_b0, \m_b1, \m_z0, \m_z1, \m_lo0, \m_lo1, \m_hi0, \m_hi1, \m_zero

    ; Compute low-byte multiplication of Montgomery factor
    ; r0 will hold the high byte of the 8x8 multiplication result
    mulsu   \m_cst_q,    \m_lo0

    ; Add the high byte from mulsu to the next low byte
    add     \m_lo1,      r0

    ; Multiply the Montgomery factor t by the modulus q
    ; Output intermediate 32-bit result into m_mont0..m_mont3
    ldi     \m_b0,    0x1E
    muls    \m_b0,    \m_lo1
    movw    \m_mont0,    r0
    mulsu   \m_b0,    \m_lo0
    
    add     r0,          \m_lo1
	adc     \m_mont0,    r1
	adc     \m_mont1,    \m_zero

    lsl     \m_lo1      
    sbc     \m_mont0,    \m_zero
    sbc     \m_mont1,    \m_zero

    ; Subtract the high 16-bit part of (t * q) from the original high 16-bit product
    ; This completes the Montgomery reduction: (a * R^-1) mod 769
    sub    \m_hi0,      \m_mont0
    sbc    \m_hi1,      \m_mont1       

.endm


.macro fqmul res_l, res_h, a_l, a_h, b_l, b_h, zero
    mc_769_montmul \a_l, \a_h, \b_l, \b_h, lo0, lo1, \res_l, \res_h, mont0, mont1, mont2, mont3, cst_tmp, cst_q, \zero
.endm


.macro	mc_ntt_ct_hi	m_a0, m_a1, m_b0, m_b1
	ld      \m_a0,   X+
    ld      \m_a1,   X
    ldd     \m_b0,   Y+0
    ldd     \m_b1,   Y+1
.endm

.macro	mc_ntt_ct_lo	m_a0, m_a1, m_b0, m_b1, m_tmp0, m_tmp1
	movw    \m_tmp0, \m_a0
    add     \m_a0,   \m_b0
    adc     \m_a1,   \m_b1
    sub     \m_tmp0, \m_b0
    sbc     \m_tmp1, \m_b1

    st      X,      \m_a1
    st      -X,     \m_a0
    std     Y+0,    \m_tmp0
    std     Y+1,    \m_tmp1
    adiw    r26,    2
    adiw    r28,    2
.endm


.macro	mc_ntt_ct_lo_LUT_reduce	m_a0, m_a1, m_b0, m_b1, m_tmp0, m_tmp1
	movw    \m_tmp0, \m_a0
    add     \m_a0,   \m_b0
    adc     \m_a1,   \m_b1
    sub     \m_tmp0, \m_b0
    sbc     \m_tmp1, \m_b1

    
    mc_lut_reduce \m_a0, \m_a1, \m_b0, r2
    mc_lut_reduce \m_tmp0, \m_tmp1, \m_b0, r2


    st      X,      \m_a1
    st      -X,     \m_a0
    std     Y+0,    \m_tmp0
    std     Y+1,    \m_tmp1
    adiw    r26,    2
    adiw    r28,    2
.endm




.macro	mc_ntt_gs_hi	m_a0, m_a1, m_b0, m_b1, m_tmp0, m_tmp1
	ld      \m_a0,   X+
    ld      \m_a1,   X
    ldd     \m_b0,   Y+0
    ldd     \m_b1,   Y+1

    movw    \m_tmp0, \m_a0
    add     \m_a0,   \m_b0
    adc     \m_a1,   \m_b1
    sub     \m_b0,   \m_tmp0
    sbc     \m_b1,   \m_tmp1
.endm

.macro	mc_ntt_gs_hi_sram	m_a0, m_a1, m_b0, m_b1, m_tmp0, m_tmp1
	ld      \m_a0,   Y+
    ld      \m_a1,   Y
    ldd     \m_b0,   Z+0
    ldd     \m_b1,   Z+1

    movw    \m_tmp0, \m_a0
    add     \m_a0,   \m_b0
    adc     \m_a1,   \m_b1
    sub     \m_b0,   \m_tmp0
    sbc     \m_b1,   \m_tmp1
.endm


.macro mc_ntt_gs_lo_sram    m_a0, m_a1, m_b0, m_b1
	st      Y,      \m_a1
    st      -Y,     \m_a0
    std     Z+0,    \m_b0
    std     Z+1,    \m_b1    
    adiw    r28,    2
    adiw    r30,    2
.endm

.macro	mc_ntt_gs_hi_LUT_reduce	m_a0, m_a1, m_b0, m_b1, m_tmp0, m_tmp1
	ld      \m_a0,   X+
    ld      \m_a1,   X
    ldd     \m_b0,   Y+0
    ldd     \m_b1,   Y+1

    movw    \m_tmp0, \m_a0
    add     \m_a0,   \m_b0
    adc     \m_a1,   \m_b1
    
    sub     \m_b0,   \m_tmp0
    sbc     \m_b1,   \m_tmp1
    ;mc_lut_reduce \m_a0, \m_a1, \m_tmp0, r5
.endm





.macro mc_ntt_gs_lo    m_a0, m_a1, m_b0, m_b1
	st      X,      \m_a1
    st      -X,     \m_a0
    std     Y+0,    \m_b0
    std     Y+1,    \m_b1    
    adiw    r26,    2
    adiw    r28,    2
.endm


 /**************************************************
  *	macro : mc_muls16x16_32
  *	description : Signed multiply of two 16bits numbers with 32bits result.
  * usage: int32_t c3|c2|c1|c0 = (int16_t a1|a0) * (int16_t b1|b0)
  * register usage : 11 registers
  ***************************************************/

 .macro mc_muls16x16_32_v2 a0, a1, b0, b1, c0, c1, c2, c3, carry, fixed_r0, fixed_r1

	//clr	\carry
	muls	\a1, \b1		; (signed)ah * (signed)bh
	movw	\c2, \fixed_r0
	mul	\a0, \b0			; al * bl
	movw	\c0, \fixed_r0
	mulsu	\a1, \b0		; (signed)ah * bl
	sbc	\c3, \carry
	add	\c1, \fixed_r0
	adc	\c2, \fixed_r1
	adc	\c3, \carry
	mulsu	\b1, \a0		; (signed)bh * al
	sbc	\c3, \carry
	add	\c1, \fixed_r0
	adc	\c2, \fixed_r1
	adc	\c3, \carry

.endm

 /**************************************************
  *	macro : mc_mulsu16x16_32
  *	description : Signed with Unsigned multiply of two 16bits numbers with 32bits result.
  * usage: int32_t c3|c2|c1|c0 = (Signed int16_t a1|a0) * (UnSigned int16_t b1|b0)
  * register usage : 11 registers
  ***************************************************/

 .macro mc_mulsu16x16_32 a0, a1, b0, b1, c0, c1, c2, c3, carry, fixed_r0, fixed_r1

	//clr	\carry
	mulsu	\a1, \b1		; (signed)ah * (Unsigned)bh
	movw	\c2, \fixed_r0
	mul	\a0, \b0			; al * bl
	movw	\c0, \fixed_r0
	mulsu	\a1, \b0		; (signed)ah * bl
	sbc	\c3, \carry
	add	\c1, \fixed_r0
	adc	\c2, \fixed_r1
	adc	\c3, \carry
	mul	\b1, \a0			; (Unsigned)bh * al
	add	\c1, \fixed_r0
	adc	\c2, \fixed_r1
	adc	\c3, \carry

.endm

 /**************************************************
  *	macro : mc_montgomery_reduce
  *	description : Montgomery reduction; given a 32-bit integer a, 
  *				  computes 16-bit integer congruent to a * R^-1 mod q, where R=2^16
  * usage: int16_t res1|res0 = motgomery (int32_t a3|a2|a1|a0)
  * register usage : 17 registers
  * note : Registers which hold value of res0, res1, Q_asm0, and Q_asm1 must be in R16 or higher.
  ***************************************************/

.macro mc_montgomery_reduce	a0, a1, a2, a3, res0, res1, t_Qinv0, t_Qinv1, t_Qinv2, t_Qinv3, carry, Qinv_asm0, Qinv_asm1, Q_asm0, Q_asm1, fixed_r0, fixed_r1

	;t = (int16_t)a * 0X3FED;
	mul \Qinv_asm0, \a0		
	movw	\res0, \fixed_r0
	mul	\a1, \Qinv_asm0
	add	\res1, \fixed_r0
	mul	\Qinv_asm1, \a0
	add	\res1, \fixed_r0
	
	;t = (int32_t)t * 0XEEFD)
	mc_mulsu16x16_32	\res0, \res1, \Q_asm0, \Q_asm1, \t_Qinv0, \t_Qinv1, \t_Qinv2, \t_Qinv3, \carry, \fixed_r0, \fixed_r1
	
	;t = t >> 16;
	sub	\a0, \t_Qinv0
	sbc	\a1, \t_Qinv1
	sbc	\a2, \t_Qinv2
	sbc	\a3, \t_Qinv3
	movw \res0, \a2

.endm


 /**************************************************
  *	macro : mc_butterfly
  *	description : Cooly-Tukey butterfly
  * usage: (int16_t a0|a1, int16_t b0|b1) = (int16_t a0|a1 + (b0|b1 * zetas0|zetas1), int16_t a0|a1 - (b0|b1 * zetas0|zetas1))
  * register usage : 23 registers
  ***************************************************/
.macro mc_butterfly	a0, a1, b0, b1, zetas0, zetas1, c0, c1, c2, c3, carry, fixed_r0, fixed_r1, res_mont0, res_mont1, tmp0, tmp1, tmp2, tmp3, Qinv0, Qinv1, Q0, Q1

	ldd	\b0, Y+0
	ldd	\b1, Y+1

	mc_muls16x16_32_v2 \b0, \b1, \zetas0, \zetas1, \c0, \c1, \c2, \c3, \carry, \fixed_r0, \fixed_r1
	mc_montgomery_reduce \c0, \c1, \c2, \c3, \res_mont0, \res_mont1, \tmp0, \tmp1, \tmp2, \tmp3, \carry, \Qinv0, \Qinv1, \Q0, \Q1, \fixed_r0, \fixed_r1

	ld	\a0, X+
	ld	\a1, X

	movw	\b0, \a0

	add	\a0, \res_mont0
	adc	\a1, \res_mont1
	sub	\b0, \res_mont0
	sbc	\b1, \res_mont1

	st	X, \a1
	st	-X, \a0
	st	Y+, \b0
	st	Y+, \b1
    adiw    r26,    2

.endm

.macro mc_butterfly_flash	a0, a1, b0, b1, zetas0, zetas1, c0, c1, c2, c3, carry, fixed_r0, fixed_r1, res_mont0, res_mont1, tmp0, tmp1, tmp2, tmp3, Qinv0, Qinv1, Q0, Q1

	ldd	\b0, Y+0
	ldd	\b1, Y+1

	mc_muls16x16_32_v2 \b0, \b1, \zetas0, \zetas1, \c0, \c1, \c2, \c3, \carry, \fixed_r0, \fixed_r1
	mc_montgomery_reduce \c0, \c1, \c2, \c3, \res_mont0, \res_mont1, \tmp0, \tmp1, \tmp2, \tmp3, \carry, \Qinv0, \Qinv1, \Q0, \Q1, \fixed_r0, \fixed_r1

	ld	\a0, X+
	ld	\a1, X

	movw	\b0, \a0

	add	\a0, \res_mont0
	adc	\a1, \res_mont1
	sub	\b0, \res_mont0
	sbc	\b1, \res_mont1

	st	X, \a1
	st	-X, \a0
	st	Y+, \b0
	st	Y+, \b1
    adiw    r26,    2

.endm

.macro mc_butterfly_opt	a0, a1, b0, b1, zetas0, zetas1, c0, c1, c2, c3, carry, res_mont0, res_mont1, zero, Qinv1, Q0, Q1

	ldd	\b0, Z+0
	ldd	\b1, Z+1

    ;mc_3329_montmul_opt src0_l, src0_h, src1_l, src1_h, lo0, lo1, d1_l, d1_h, mont0, mont1, cst_q, zero

    mc_3329_montmul_opt \b0, \b1, \zetas0, \zetas1, \res_mont0, \res_mont1, \c0, \c1, \c2, \c3, \Q0, \zero


	ldd	\a0, Y+0
	ldd	\a1, Y+1

	movw	\b0, \a0

	add	\a0, \c0
	adc	\a1, \c1
	sub	\b0, \c0
	sbc	\b1, \c1

	st	Y+, \a0
	st	Y+, \a1
	st	Z+, \b0
	st	Z+, \b1

.endm



 /**************************************************
  *	macro : mc_barrett_reduce
  *	description : Barrett reduction; given a 16-bit integer a, computes
  *               centered representative congruent to a mod q in {-(q-1)/2,...,(q-1)/2}
  * usage: int16_t res1|res0 = barrett_reduce (int16_t a1|a0)
  * register usage : 13 registers
  * note : Registers which hold value of a0, a1, barret0, barret1, \tmp2, and \tmp3 must be in R16 or higher.
  ***************************************************/
.macro mc_barrett_reduce	a0, a1, tmp0, tmp1, tmp2, tmp3, carry, barret0, barret1,  Q0, Q1, fixed_r0, fixed_r1

	ldi	\barret0, lo8(barret_asm)
	ldi	\barret1, hi8(barret_asm)

	mc_mulsu16x16_32 \a0, \a1, \barret0, \barret1, \tmp0, \tmp1, \tmp2, \tmp3, \carry, \fixed_r0, \fixed_r1
 
	inc	\carry
	inc \carry
	add	\tmp3, \carry
	clr	\carry
	asr	\tmp3
	asr	\tmp3

	ldi	\barret0, lo8(Q_asm)
	ldi	\barret1, hi8(Q_asm)

	muls	\tmp3, \barret0
	movw	\tmp0, \fixed_r0
	muls	\tmp3,	\barret1    
	add	\tmp1, \fixed_r0
	sub	\a0, \tmp0
	sbc	\a1, \tmp1

.endm
.macro mc_barrett_reduce_3329	a0, a1, tmp0, tmp1, tmp2, tmp3, carry, barret0, barret1

	ldi	\barret0, lo8(barret_asm)
	ldi	\barret1, hi8(barret_asm)

	mc_mulsu16x16_32 \a0, \a1, \barret0, \barret1, \tmp0, \tmp1, \tmp2, \tmp3, \carry, r0, r1
 
	inc	\carry
	inc \carry
	add	\tmp3, \carry
	clr	\carry
	asr	\tmp3
	asr	\tmp3

	ldi	\barret0, lo8(Q_asm)
	ldi	\barret1, hi8(Q_asm)

	muls	\tmp3, \barret0
	movw	\tmp0, r0
	muls	\tmp3,	\barret1    
	add	\tmp1, r0
	sub	\a0, \tmp0
	sbc	\a1, \tmp1

.endm
.macro mc_barrett_reduce_7681	a0, a1, tmp0, tmp1, tmp2, tmp3, carry, barret0, barret1

	ldi	\barret0, lo8(barret_asm)
	ldi	\barret1, hi8(barret_asm)

	mc_mulsu16x16_32 \a0, \a1, \barret0, \barret1, \tmp0, \tmp1, \tmp2, \tmp3, \carry, r0, r1
 
	inc	\carry
	inc \carry
	add	\tmp3, \carry
	clr	\carry
	asr	\tmp3
	asr	\tmp3

	ldi	\barret0, lo8(Q_asm)
	ldi	\barret1, hi8(Q_asm)

	muls	\tmp3, \barret0
	movw	\tmp0, r0
	muls	\tmp3,	\barret1    
	add	\tmp1, r0
	sub	\a0, \tmp0
	sbc	\a1, \tmp1

.endm
/**************************************************
  *	macro : mc_inv_butterfly
  *	description : Gentleman-Sande butterfly
  * usage: (int16_t a0|a1, int16_t b0|b1) = (int16_t a0|a1 + b0|b1), int16_t (b0|b1 - a0|a1) * zetas0|zetas1))
  * register usage : 25 registers
  ***************************************************/
.macro mc_inv_butterfly	a0, a1, b0, b1, zetas0, zetas1, c0, c1, c2, c3, carry, fixed_r0, fixed_r1, res_mont0, res_mont1, tmp0, tmp1, tmp2, tmp3, Qinv0, Qinv1, Q0, Q1, barret0, barret1

	ld	\a0, X+
	ld	\a1, X
	movw	r12, \a0

	ldd	\b0, Y+0
	ldd	\b1, Y+1
	movw	r8, \b0

	add	\b0, \a0
	adc	\b1, \a1

	mc_barrett_reduce	\b0, \b1, \tmp0, \tmp1, r22, r23, \carry, \barret0, \barret1, \Q0, \Q1, \fixed_r0, \fixed_r1

	st	X, \b1
	st	-X, \b0
    adiw    r26,    2

	movw	\b0, r8
	movw	\a0, r12

	sub	\b0, \a0
	sbc	\b1, \a1

	ldi	\Q0, lo8(Q_asm)
	ldi	\Q1, hi8(Q_asm)

	mc_muls16x16_32_v2 \b0, \b1, \zetas0, \zetas1, \c0, \c1, \c2, \c3, \carry, \fixed_r0, \fixed_r1
	mc_montgomery_reduce \c0, \c1, \c2, \c3, \res_mont0, \res_mont1, \tmp0, \tmp1, \tmp2, \tmp3, \carry, \Qinv0, \Qinv1, \Q0, \Q1, \fixed_r0, \fixed_r1


	st	Y+, \res_mont0
	st	Y+, \res_mont1

.endm



