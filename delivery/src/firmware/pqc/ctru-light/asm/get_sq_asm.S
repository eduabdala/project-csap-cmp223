#include "macros.inc"
#include "common.inc"

.section .text

; --- src0 and src1 ---
#define src0_l r22    
#define src0_h r23    
#define src1_l r18   
#define src1_h r19   
; --- d[i] ---
; compute on the fly
#define d0_l r4
#define d0_h r5

#define d1_l r2
#define d1_h r3

#define d2_l r14
#define d2_h r15

#define d3_l r6
#define d3_h r7
; ---  c[i] ---

; --- temp variable ---
#define mont0 r10
#define mont1 r11
#define mont2 r12
#define mont3 r13

; --- constant ---
#define zero r8
#define cst_q r17
#define	cst_tmp    	r21	



.global get_sq_kred_asm
get_sq_kred_asm:

    mc_prolog 0, 17

    //clr zero
    ; first parameter r24 r23, second r22 r21, third r20 r19
    movw	r26,		r24 //X
    movw	r28,		r22 //Y

    clr zero
    ldi		  cst_q,		0x9
    ldi		  cst_tmp,		0x03

    ; f0_sq = fqmul(a[0], a[0])
    ldd src0_l, Y+0
    ldd src0_h, Y+1
    ldd src1_l, Y+0
    ldd src1_h, Y+1

    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d0_l, d0_h, mont0, mont1, zero

    ; f1_sq = fqmul(a[1], a[1])
    ldd src0_l, Y+2
    ldd src0_h, Y+3
    ldd src1_l, Y+2
    ldd src1_h, Y+3

    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ; f2_sq = fqmul(a[2], a[2])
    ldd src0_l, Y+4
    ldd src0_h, Y+5
    ldd src1_l, Y+4
    ldd src1_h, Y+5

    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d2_l, d2_h, mont0, mont1, zero

    ; f3_sq = fqmul(a[3], a[3])
    ldd src0_l, Y+6
    ldd src0_h, Y+7
    ldd src1_l, Y+6
    ldd src1_h, Y+7

    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d3_l, d3_h, mont0, mont1, zero

    st X+, d0_l
    st X+, d0_h
    st X+, d1_l
    st X+, d1_h
    st X+, d2_l
    st X+, d2_h
    st X+, d3_l
    st X+, d3_h

     ; f0_f = fqmul(f0_sq, f0_sq)
    mov src0_l, d0_l
    mov src0_h, d0_h
    mov src1_l, d0_l
    mov src1_h, d0_h

    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d0_l, d0_h, mont0, mont1, zero

    ; f1_f = fqmul(f1_sq, f1_sq)
    mov src0_l, d1_l
    mov src0_h, d1_h
    mov src1_l, d1_l
    mov src1_h, d1_h
    
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero
   
    ; f2_f = fqmul(f2_sq, f2_sq)
    mov src0_l, d2_l
    mov src0_h, d2_h
    mov src1_l, d2_l
    mov src1_h, d2_h
    
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d2_l, d2_h, mont0, mont1, zero

    ; f3_f = fqmul(f3_sq, f3_sq)
    mov src0_l, d3_l
    mov src0_h, d3_h
    mov src1_l, d3_l
    mov src1_h, d3_h
    
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d3_l, d3_h, mont0, mont1, zero

    st X+, d0_l
    st X+, d0_h
    st X+, d1_l
    st X+, d1_h
    st X+, d2_l
    st X+, d2_h
    st X+, d3_l
    st X+, d3_h


    ; Epilog: Restore registers
    mc_epilog 0, 17

    ret


; --- src0 and src1 ---
#undef src0_l
#undef src0_h
#undef src1_l
#undef src1_h

; --- d[i] ---
#undef d0_l
#undef d0_h
#undef d1_l
#undef d1_h
#undef d2_l
#undef d2_h
#undef d3_l
#undef d3_h

; --- c[i] ---
#undef c0_l
#undef c0_h
#undef c1_l
#undef c1_h

; --- temp variable ---
#undef tmp_l
#undef tmp_h
#undef tmp2_l
#undef tmp2_h
#undef lo0_l
#undef lo0_h
#undef hi0_l
#undef hi0_h

; --- constant ---
#undef cst_q

; --- constant ---
#undef zeta_l
#undef zeta_h

; --- zero register ---
#undef zero
