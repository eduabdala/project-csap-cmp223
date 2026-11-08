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
  *	macro : mc_muls16x16_32
  *	description : Signed with Signed multiply of two 16bits numbers with 32bits result.
  * usage: int32_t c3|c2|c1|c0 = (Signed int16_t a1|a0) * (Signed int16_t b1|b0)
  * register usage : 11 registers
  ***************************************************/
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

.macro mc_ntt_gs_lo    m_a0, m_a1, m_b0, m_b1
	st      X,      \m_a1
    st      -X,     \m_a0
    std     Y+0,    \m_b0
    std     Y+1,    \m_b1    
    adiw    r26,    2
    adiw    r28,    2
.endm


