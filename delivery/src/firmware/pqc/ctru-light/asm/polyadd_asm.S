
.global poly_add_asm
poly_add_asm:
    push r28
    push r29
    push r30
    push r31

    movw r30, r24      ; Z = c pointer
    movw r26, r22      ; X = a pointer
    movw r28, r20      ; Y = b pointer

    ; Set loop counter for 64 iterations (512 / 8)
    ldi r18, 64        ; Use a single 8-bit counter
    
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
    ret


// poly_double_8bit_asm
.global poly_double_8bit_asm
poly_double_8bit_asm:
    push r2
    push r3
    push r4
    push r5
    push r6
    push r7
    push r8
    push r9
    push r18
    push r30
    push r31

    movw r30, r24      ; Z = b (output)
    movw r26, r22      ; X = a (input)
    ldi r18, 64        ; 512 / 8 = 64

poly_double_8bit_loop:
    ld r2, X+          ; a[0]
    add r2, r2
    st Z+, r2

    ld r3, X+          ; a[1]
    add r3, r3
    st Z+, r3

    ld r4, X+          ; a[2]
    add r4, r4
    st Z+, r4

    ld r5, X+          ; a[3]
    add r5, r5
    st Z+, r5

    ld r6, X+          ; a[4]
    add r6, r6
    st Z+, r6

    ld r7, X+          ; a[5]
    add r7, r7
    st Z+, r7

    ld r8, X+          ; a[6]
    add r8, r8
    st Z+, r8

    ld r9, X+          ; a[7]
    add r9, r9
    st Z+, r9

    dec r18
    brne poly_double_8bit_loop

    pop r31
    pop r30
    pop r18
    pop r9
    pop r8
    pop r7
    pop r6
    pop r5
    pop r4
    pop r3
    pop r2
    ret