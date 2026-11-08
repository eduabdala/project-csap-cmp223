#include "macros.inc"
#include "common.inc"


.section .text


#define src0_l r22    
#define src0_h r23    
#define src1_l r18  
#define src1_h r19   
#define d0_l r4
#define d0_h r5

#define d1_l r2
#define d1_h r3

#define d2_l r24
#define d2_h r25

#define d3_l r6
#define d3_h r7
#define c0_l r14
#define c0_h r15

#define mont0 r10
#define mont1 r11
#define mont2 r16
#define mont3 r20

#define	cst_tmp    	r21	

#define zero r12
#define cst_q r17
#define zeta_l r8
#define zeta_h r9


.global basemulkred_asm
basemulkred_asm:

    mc_prolog 0, 17

    //clr zero

    ; move zeta to r18, r19
    movw r8, r18
    movw	r26,		r24 //X
    movw	r28,		r22 //Y
    movw	r30,		r20 //Z

    clr zero
    ldi		  cst_q,		0x9
    ldi		  cst_tmp,		0x03

    ; --- Step 1: Calculate d[i] = fqmul(a[i], b[i]) ---
    ; d[1] = fqmul(a[1], b[1])
    ldd src0_l, Y+2
    ldd src0_h, Y+3
    ldd src1_l, Z+2
    ldd src1_h, Z+3

    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ; d[2] = fqmul(a[2], b[2])
    ldd src0_l, Y+4
    ldd src0_h, Y+5
    ldd src1_l, Z+4
    ldd src1_h, Z+5

    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d2_l, d2_h, mont0, mont1, zero

    ; d[3] = fqmul(a[3], b[3])
    ldd src0_l, Y+6
    ldd src0_h, Y+7
    ldd src1_l, Z+6
    ldd src1_h, Z+7

    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d3_l, d3_h, mont0, mont1, zero


    ; d[0] = fqmul(a[0], b[0])
    ldd src0_l, Y+0
    ldd src0_h, Y+1
    ldd src1_l, Z+0
    ldd src1_h, Z+1
    ;fqmul(a[0], b[0])
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d0_l, d0_h, mont0, mont1, zero

    ; (a[1] + a[3])(b[1] + b[3])
    ldd src0_l, Y+2     ; a[1]
    ldd src0_h, Y+3
    ldd src1_l, Y+6     ; a[3]
    ldd src1_h, Y+7
    add src0_l, src1_l
    adc src0_h, src1_h
    ldd src1_l, Z+2     ; b[1]
    ldd src1_h, Z+3
    ldd mont0, Z+6      ; b[3]
    ldd mont1, Z+7
    add src1_l, mont0
    adc src1_h, mont1
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, c0_l, c0_h, mont0, mont1, zero
    ; (a[1] + a[3])(b[1] + b[3]) - d[1] 
    sub c0_l, d1_l
    sbc c0_h, d1_h
   
    ; (a[1] + a[3])(b[1] + b[3]) - d[1] - d[3]
    sub c0_l, d3_l
    sbc c0_h, d3_h
    
    ;  (((a[1] + a[3])(b[1] + b[3]) - d[1] - d[3]) + d[2])
    add c0_l, d2_l
    adc c0_h, d2_h

    ;  (((a[1] + a[3])(b[1] + b[3]) - d[1] - d[3]) + d[2]) zeta 
    mov src0_l, c0_l
    mov src0_h, c0_h
    mov src1_l, zeta_l
    mov src1_h, zeta_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, c0_l, c0_h, mont0, mont1, zero
 
    ; c[0] = d[0] + fqmul((CALC_D(1,3)+d[2]), zeta);
    add c0_l, d0_l
    adc c0_h, d0_h


    push r30
    push r31
    mc_lut_reduce c0_l, c0_h, mont0, zero
    pop  r31
    pop  r30

    st X+, c0_l
    st X+, c0_h
    

    ; compute c[1]
    ;CALC_D(a, b, 0, 1, d)
    ldd src0_l, Y+0     ; a[0]
    ldd src0_h, Y+1
    ldd src1_l, Y+2     ; a[1]
    ldd src1_h, Y+3
    add src0_l, src1_l
    adc src0_h, src1_h
    ldd src1_l, Z+0     ; b[0]
    ldd src1_h, Z+1
    ldd mont0, Z+2      ; b[1]
    ldd mont1, Z+3
    add src1_l, mont0
    adc src1_h, mont1
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, c0_l, c0_h, mont0, mont1, zero
    sub c0_l, d0_l
    sbc c0_h, d0_h
    sub c0_l, d1_l
    sbc c0_h, d1_h

    

    push d0_l
    push d0_h
    ; --- CALC_D(a, b, 2, 3, d)  -> d0_l, d0_h
    ldd src0_l, Y+4     ; a[2]
    ldd src0_h, Y+5
    ldd src1_l, Y+6     ; a[3]
    ldd src1_h, Y+7
    add src0_l, src1_l
    adc src0_h, src1_h
    ldd src1_l, Z+4     ; b[2]
    ldd src1_h, Z+5
    ldd mont0, Z+6     ; b[3]
    ldd mont1, Z+7
    add src1_l, mont0
    adc src1_h, mont1
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d0_l, d0_h, mont0, mont1, zero
    sub d0_l, d2_l
    sbc d0_h, d2_h
    sub d0_l, d3_l
    sbc d0_h, d3_h
    

    ; --- (CALC_D(a, b, 2, 3, d))zeta
    mov src0_l, d0_l
    mov src0_h, d0_h
    mov src1_l, zeta_l
    mov src1_h, zeta_h
    ; because d0_l and d0_h now is free, we can use them again to store (CALC_D(a, b, 2, 3, d))zeta
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d0_l, d0_h, mont0, mont1, zero
    ; --- c[1] = CALC_D(a, b, 0, 1, d) + (CALC_D(a, b, 2, 3, d))zeta
    add c0_l, d0_l
    adc c0_h, d0_h
    push r30
    push r31
    mc_lut_reduce c0_l, c0_h, mont0, zero
    pop  r31
    pop  r30
    st X+, c0_l
    st X+, c0_h
    pop d0_h
    pop d0_l 
    

    ;compute c[2]
    ;CALC_D(a, b, 0, 2, d)
    ldd src0_l, Y+0     ; a[0]
    ldd src0_h, Y+1
    ldd src1_l, Y+4     ; a[2]
    ldd src1_h, Y+5
    add src0_l, src1_l
    adc src0_h, src1_h
    ldd src1_l, Z+0     ; b[0]
    ldd src1_h, Z+1
    ldd mont0, Z+4     ; b[2]
    ldd mont1, Z+5
    add src1_l, mont0
    adc src1_h, mont1
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, c0_l, c0_h, mont0, mont1, zero
    sub c0_l, d0_l
    sbc c0_h, d0_h
    sub c0_l, d2_l
    sbc c0_h, d2_h
    
    ;CALC_D(a, b, 0, 2, d) + d[1]
    add c0_l, d1_l
    adc c0_h, d1_h
    

    ;free d0_l and d0_h
    push d0_l
    push d0_h
    ;fqmul(d[3], zeta)
    mov src0_l, d3_l
    mov src0_h, d3_h
    mov src1_l, zeta_l
    mov src1_h, zeta_h
    ;d0_l and d0_h to store fqmul(d[3], zeta)
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d0_l, d0_h, mont0, mont1, zero
    ;CALC_D(a, b, 0, 2, d) + d[1] + fqmul(d[3], zeta)
    add c0_l, d0_l
    adc c0_h, d0_h
   

    push r30
    push r31
    mc_lut_reduce c0_l, c0_h, mont0, zero
    pop  r31
    pop  r30
    st X+, c0_l
    st X+, c0_h

    pop d0_h
    pop d0_l

    ;compute c[3]
    ;(CALC_D(a, b, 1, 2, d)
    ldd src0_l, Y+2     ; a[1]
    ldd src0_h, Y+3
    ldd src1_l, Y+4     ; a[2]
    ldd src1_h, Y+5
    add src0_l, src1_l
    adc src0_h, src1_h
    ldd src1_l, Z+2     ; b[1]
    ldd src1_h, Z+3
    ldd mont0, Z+4     ; b[2]
    ldd mont1, Z+5
    add src1_l, mont0
    adc src1_h, mont1
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, c0_l, c0_h, mont0, mont1, zero
    sub c0_l, d1_l
    sbc c0_h, d1_h
    sub c0_l, d2_l
    sbc c0_h, d2_h

    
    ; --- CALC_D(a, b, 0, 3, d) 
    ldd src0_l, Y+0     ; a[0]
    ldd src0_h, Y+1
    ldd src1_l, Y+6     ; a[3]
    ldd src1_h, Y+7
    add src0_l, src1_l
    adc src0_h, src1_h
    ldd src1_l, Z+0     ; b[0]
    ldd src1_h, Z+1
    ldd mont0, Z+6     ; b[3]
    ldd mont1, Z+7
    add src1_l, mont0
    adc src1_h, mont1
    ; use d1_l and d1_h to store CALC_D(a, b, 0, 3, d) 
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero
    sub d1_l, d0_l
    sbc d1_h, d0_h
    sub d1_l, d3_l
    sbc d1_h, d3_h
    ;(CALC_D(a, b, 1, 2, d) + CALC_D(a, b, 0, 3, d))
    add c0_l, d1_l
    adc c0_h, d1_h
    mc_lut_reduce c0_l, c0_h, mont0, zero
    st X+, c0_l
    st X+, c0_h


end:

    ; Epilog: Restore registers
    mc_epilog 0, 17

    ret

