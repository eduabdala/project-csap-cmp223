.global poly_add_asm
poly_add_asm:
    push r2
    push r3
    push r4
    push r5
    push r28
    push r29
    push r30
    push r31

    movw r30, r24      ; Z = c pointer
    movw r26, r22      ; X = a pointer
    movw r28, r20      ; Y = b pointer

    ; Set loop counter for 32 iterations (256 coeffs / 8 coeffs per iter = 512 bytes / 16 bytes per iter)
    ldi r18, 32        ; Use a single 8-bit counter

poly_add_loop:
    ; --- Unrolled body: Process 8 coefficients (16 bytes) ---
    ld r2, X+
    ld r3, X+
    ld r4, Y+
    ld r5, Y+
    add r2, r4
    adc r3, r5
    st Z+, r2
    st Z+, r3

    ld r2, X+
    ld r3, X+
    ld r4, Y+
    ld r5, Y+
    add r2, r4
    adc r3, r5
    st Z+, r2
    st Z+, r3

    ld r2, X+
    ld r3, X+
    ld r4, Y+
    ld r5, Y+
    add r2, r4
    adc r3, r5
    st Z+, r2
    st Z+, r3

    ld r2, X+
    ld r3, X+
    ld r4, Y+
    ld r5, Y+
    add r2, r4
    adc r3, r5
    st Z+, r2
    st Z+, r3

    ld r2, X+
    ld r3, X+
    ld r4, Y+
    ld r5, Y+
    add r2, r4
    adc r3, r5
    st Z+, r2
    st Z+, r3

    ld r2, X+
    ld r3, X+
    ld r4, Y+
    ld r5, Y+
    add r2, r4
    adc r3, r5
    st Z+, r2
    st Z+, r3

    ld r2, X+
    ld r3, X+
    ld r4, Y+
    ld r5, Y+
    add r2, r4
    adc r3, r5
    st Z+, r2
    st Z+, r3

    ld r2, X+
    ld r3, X+
    ld r4, Y+
    ld r5, Y+
    add r2, r4
    adc r3, r5
    st Z+, r2
    st Z+, r3

    ; --- Loop control ---
      dec r18
    breq end_poly_add_loop   ; 
    rjmp poly_add_loop       ; 

end_poly_add_loop:
    pop r31
    pop r30
    pop r29
    pop r28
    pop r5
    pop r4
    pop r3
    pop r2
    ret