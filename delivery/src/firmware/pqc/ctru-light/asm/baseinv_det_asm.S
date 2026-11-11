#include "macros.inc"
#include "common.inc"

.section .text

; --- src0 and src1 ---
#define src0_l r18    
#define src0_h r19    
#define src1_l r22   
#define src1_h r23   
; --- d[i] ---
; compute on the fly
#define d0_l r4
#define d0_h r5

#define d1_l r2
#define d1_h r3

#define d2_l r12
#define d2_h r13

#define d3_l r6
#define d3_h r7
; ---  c[i] ---
#define c0_l r14
#define c0_h r15

; --- temp variable ---
#define mont0 r10
#define mont1 r11

; --- constant ---
#define zero r24
#define cst_q r17
#define	cst_tmp    	r21	
; --- constant ---
#define zeta_l r8
#define zeta_h r9


.global baseinv_kred_det_asm
baseinv_kred_det_asm:

    mc_prolog 0, 17

    //clr zero
    ; first parameter r24 r23, second r22 r21, third r20 r19 fourth 18 17
    ; move zeta (r18 r17) to r8, r9
    movw r8, r18
    movw	r26,		r24 //X b
    movw	r28,		r22 //Y sq_fq
    movw	r30,		r20 //Z a

    clr zero
    ldi		  cst_q,		0x9
    ldi		  cst_tmp,		0x03

    ;zeta_sq = fqmul(zeta, zeta); zeta_sq = > d0_l d0_h
    mov src0_l, zeta_l
    mov src0_h, zeta_h
    mov src1_l, zeta_l
    mov src1_h, zeta_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d0_l, d0_h, mont0, mont1, zero
   
     ; det = 4*f0_sq; without fqmul
    ldd c0_l, Y+0
    ldd c0_h, Y+1
    lsl    c0_l          ; left shift 1 bit (¡Á2)
    rol    c0_h         
    lsl    c0_l         ; left shift 1 bit (¡Á2)
    rol    c0_h    
    
    ;det = fqmul(a[1], det);
    mov src0_l, c0_l
    mov src0_h, c0_h
    ldd src1_l, Z+2
    ldd src1_h, Z+3
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, c0_l, c0_h, mont0, mont1, zero
    
    ;det = fqmul(a[3], det);
    mov src0_l, c0_l
    mov src0_h, c0_h
    ldd src1_l, Z+6
    ldd src1_h, Z+7
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, c0_l, c0_h, mont0, mont1, zero

    ;det = fqmul(det, zeta);
    mov src0_l, c0_l
    mov src0_h, c0_h
    mov src1_l, zeta_l
    mov src1_h, zeta_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, c0_l, c0_h, mont0, mont1, zero

    ;det = sq_fq[4] - det; //2q
    ldd src0_l, Y+8       
    ldd src0_h, Y+9       

    sub src0_l, c0_l      ; mont0 = d0_l - c0_l
    sbc src0_h, c0_h      ; mont1 = d0_h - c0_h - borrow

    mov c0_l, src0_l      ; det_low = result_low
    mov c0_h, src0_h      ; det_high = result_high

    ;tmp = 2*sq_fq[0];
    ldd d1_l, Y+0
    ldd d1_h, Y+1
    lsl    d1_l          ; left shift 1 bit (¡Á2)
    rol    d1_h         
    
    ;tmp = fqmul(tmp, sq_fq[2]);
    mov src0_l, d1_l
    mov src0_h, d1_h
    ldd src1_l, Y+4
    ldd src1_h, Y+5
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ;tmp = fqmul(tmp, zeta);
    mov src0_l, d1_l
    mov src0_h, d1_h
    mov src1_l, zeta_l
    mov src1_h, zeta_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ;det -= tmp; //3q
    sub c0_l, d1_l
    sbc c0_h, d1_h

    ;tmp = 4*a[0];
    ldd d1_l, Z+0
    ldd d1_h, Z+1
    lsl    d1_l          ; left shift 1 bit (¡Á2)
    rol    d1_h         
    lsl    d1_l         ; left shift 1 bit (¡Á2)
    rol    d1_h    
    
    ;tmp2 = fqmul(tmp, a[2]); 
    mov src0_l, d1_l
    mov src0_h, d1_h
    ldd src1_l, Z+4
    ldd src1_h, Z+5
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d2_l, d2_h, mont0, mont1, zero

    ;tmp2 = fqmul(tmp2, sq_fq[3]);
    mov src0_l, d2_l
    mov src0_h, d2_h
    ldd src1_l, Y+6
    ldd src1_h, Y+7
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d2_l, d2_h, mont0, mont1, zero

    ;tmp2 = fqmul(tmp2, zeta_sq);
    mov src0_l, d2_l
    mov src0_h, d2_h
    mov src1_l, d0_l
    mov src1_h, d0_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d2_l, d2_h, mont0, mont1, zero

    ;tmp = fqmul(tmp, sq_fq[1]);
    mov src0_l, d1_l
    mov src0_h, d1_h
    ldd src1_l, Y+2
    ldd src1_h, Y+3
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ;tmp = fqmul(tmp, a[2]);
    mov src0_l, d1_l
    mov src0_h, d1_h
    ldd src1_l, Z+4
    ldd src1_h, Z+5
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ;tmp = fqmul(tmp, zeta);
    mov src0_l, d1_l
    mov src0_h, d1_h
    mov src1_l, zeta_l
    mov src1_h, zeta_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ;det += tmp;  //5q
    add c0_l, d1_l
    adc c0_h, d1_h

    ;det += tmp2; //6q
    add c0_l, d2_l
    adc c0_h, d2_h
  
    ;tmp =  fqmul(sq_fq[5], zeta);
    ldd src0_l, Y+10
    ldd src0_h, Y+11
    mov src1_l, zeta_l
    mov src1_h, zeta_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ;det -= tmp; //7q
    sub c0_l, d1_l
    sbc c0_h, d1_h
    
    ;tmp = 2*sq_fq[1];
    ldi src0_l, 2
    ldi src0_h, 0
    ldd src1_l, Y+2
    ldd src1_h, Y+3
    mc_muls16x16_32 src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ;tmp = fqmul(tmp, sq_fq[3]);
    mov src0_l, d1_l
    mov src0_h, d1_h
    ldd src1_l, Y+6
    ldd src1_h, Y+7
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ;tmp = fqmul(tmp, zeta_sq);
    mov src0_l, d1_l
    mov src0_h, d1_h
    mov src1_l, d0_l
    mov src1_h, d0_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ;det += tmp; //8q
    add c0_l, d1_l
    adc c0_h, d1_h

    ;tmp = 4*a[1];
    ldd d1_l, Z+2
    ldd d1_h, Z+3
    lsl    d1_l          ; left shift 1 bit (¡Á2)
    rol    d1_h         
    lsl    d1_l         ; left shift 1 bit (¡Á2)
    rol    d1_h   

    ;tmp = fqmul(tmp, sq_fq[2]);
    mov src0_l, d1_l
    mov src0_h, d1_h
    ldd src1_l, Y+4
    ldd src1_h, Y+5
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ;tmp = fqmul(tmp, a[3]);
    mov src0_l, d1_l
    mov src0_h, d1_h
    ldd src1_l, Z+6
    ldd src1_h, Z+7
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ;tmp = fqmul(tmp, zeta_sq);
    mov src0_l, d1_l
    mov src0_h, d1_h
    mov src1_l, d0_l
    mov src1_h, d0_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ;det -= tmp;//9q
    sub c0_l, d1_l
    sbc c0_h, d1_h

    ;tmp = fqmul(sq_fq[6],zeta_sq);
    ldd src0_l, Y+12
    ldd src0_h, Y+13
    mov src1_l, d0_l
    mov src1_h, d0_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ;det += tmp; //10q
    add c0_l, d1_l
    adc c0_h, d1_h
   
    ;tmp = fqmul(zeta_sq, zeta);
    mov src0_l, d0_l
    mov src0_h, d0_h
    mov src1_l, zeta_l
    mov src1_h, zeta_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ;tmp = fqmul(tmp, sq_fq[7]);
    mov src0_l, d1_l
    mov src0_h, d1_h
    ldd src1_l, Y+14
    ldd src1_h, Y+15
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ;det -= tmp; //11q
    sub c0_l, d1_l
    sbc c0_h, d1_h

    ;det = fqinv(det) = det^767
    ;det = fqmul(det, 19);
    mov src0_l, c0_l
    mov src0_h, c0_h
    ldi src1_l, 19
    ldi src1_h, 0
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, c0_l, c0_h, mont0, mont1, zero
 
    ; loop = 1
    ; t = det
    mov d1_l, c0_l
    mov d1_h, c0_h

    ; det = det^2
    mov src0_l, c0_l
    mov src0_h, c0_h
    mov src1_l, c0_l
    mov src1_h, c0_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, c0_l, c0_h, mont0, mont1, zero

    ; t = t*det^2 = det^3
    mov src0_l, d1_l
    mov src0_h, d1_h
    mov src1_l, c0_l
    mov src1_h, c0_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ; loop = 2
     ; det = det^4
    mov src0_l, c0_l
    mov src0_h, c0_h
    mov src1_l, c0_l
    mov src1_h, c0_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, c0_l, c0_h, mont0, mont1, zero

    ; t = t*det^4 = det^3*det^4 = det^7
    mov src0_l, d1_l
    mov src0_h, d1_h
    mov src1_l, c0_l
    mov src1_h, c0_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ; loop = 3
     ; det = det^8
    mov src0_l, c0_l
    mov src0_h, c0_h
    mov src1_l, c0_l
    mov src1_h, c0_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, c0_l, c0_h, mont0, mont1, zero

    ; t = t*det^8 = det^7*det^8 = det^15
    mov src0_l, d1_l
    mov src0_h, d1_h
    mov src1_l, c0_l
    mov src1_h, c0_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ; loop = 4
     ; det = det^16
    mov src0_l, c0_l
    mov src0_h, c0_h
    mov src1_l, c0_l
    mov src1_h, c0_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, c0_l, c0_h, mont0, mont1, zero

    ; t = t*det^15 = det^15*det^16 = det^31
    mov src0_l, d1_l
    mov src0_h, d1_h
    mov src1_l, c0_l
    mov src1_h, c0_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ; loop = 5
     ; det = det^32
    mov src0_l, c0_l
    mov src0_h, c0_h
    mov src1_l, c0_l
    mov src1_h, c0_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, c0_l, c0_h, mont0, mont1, zero

    ; t = t*det^32 = det^31*det^32 = det^63
    mov src0_l, d1_l
    mov src0_h, d1_h
    mov src1_l, c0_l
    mov src1_h, c0_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ; loop = 6
     ; det = det^64
    mov src0_l, c0_l
    mov src0_h, c0_h
    mov src1_l, c0_l
    mov src1_h, c0_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, c0_l, c0_h, mont0, mont1, zero

    ; t = t*det^64 = det^63*det^64 = det^127
    mov src0_l, d1_l
    mov src0_h, d1_h
    mov src1_l, c0_l
    mov src1_h, c0_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ; loop = 7
    ; det = det^128
    mov src0_l, c0_l
    mov src0_h, c0_h
    mov src1_l, c0_l
    mov src1_h, c0_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, c0_l, c0_h, mont0, mont1, zero

    ; t = t*det^128 = det^127*det^128 = det^255
    mov src0_l, d1_l
    mov src0_h, d1_h
    mov src1_l, c0_l
    mov src1_h, c0_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ; loop = 8
    ; det = det^256
    mov src0_l, c0_l
    mov src0_h, c0_h
    mov src1_l, c0_l
    mov src1_h, c0_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, c0_l, c0_h, mont0, mont1, zero

    ; loop = 9
    ; det = det^512
    mov src0_l, c0_l
    mov src0_h, c0_h
    mov src1_l, c0_l
    mov src1_h, c0_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, c0_l, c0_h, mont0, mont1, zero

    ; t = t*det^512 = det^255*det^512 = det^767
    mov src0_l, d1_l
    mov src0_h, d1_h
    mov src1_l, c0_l
    mov src1_h, c0_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, c0_l, c0_h, mont0, mont1, zero

    ldi src0_l, 1
    ldi src0_h, 0
    mov src1_l, c0_l
    mov src1_h, c0_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, c0_l, c0_h, mont0, mont1, zero

    ; det stores in c0_l and c0_h always
    ; b[0] =  fqmul(sq_fq[0], a[0]);
    ldd src0_l, Y+0
    ldd src0_h, Y+1
    ldd src1_l, Z+0
    ldd src1_h, Z+1
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d3_l, d3_h, mont0, mont1, zero
    
    ;tmp = 2*a[0];
    ldd d1_l, Z+0
    ldd d1_h, Z+1
    lsl    d1_l          ; left shift 1 bit (¡Á2)
    rol    d1_h 

    ;tmp = fqmul(tmp, a[1]);
    mov src0_l, d1_l
    mov src0_h, d1_h
    ldd src1_l, Z+2
    ldd src1_h, Z+3
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ;tmp = fqmul(tmp, a[3]);
    mov src0_l, d1_l
    mov src0_h, d1_h
    ldd src1_l, Z+6
    ldd src1_h, Z+7
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ;tmp = fqmul(tmp, zeta);
    mov src0_l, d1_l
    mov src0_h, d1_h
    mov src1_l, zeta_l
    mov src1_h, zeta_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ;b[0] -= tmp; //2q
    sub d3_l, d1_l
    sbc d3_h, d1_h   

    ;tmp = fqmul(a[0], sq_fq[2]);
    ldd src0_l, Z+0
    ldd src0_h, Z+1
    ldd src1_l, Y+4
    ldd src1_h, Y+5
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ;tmp = fqmul(tmp, zeta);
    mov src0_l, d1_l
    mov src0_h, d1_h
    mov src1_l, zeta_l
    mov src1_h, zeta_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ;b[0] -= tmp; //3q
    sub d3_l, d1_l
    sbc d3_h, d1_h  

    ;tmp = fqmul(a[2], sq_fq[1]);
    ldd src0_l, Z+4
    ldd src0_h, Z+5
    ldd src1_l, Y+2
    ldd src1_h, Y+3
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ;tmp = fqmul(tmp, zeta);
    mov src0_l, d1_l
    mov src0_h, d1_h
    mov src1_l, zeta_l
    mov src1_h, zeta_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ;b[0] += tmp; //4q
    add d3_l, d1_l
    adc d3_h, d1_h  

    ;tmp = fqmul(a[2], sq_fq[3]);
    ldd src0_l, Z+4
    ldd src0_h, Z+5
    ldd src1_l, Y+6
    ldd src1_h, Y+7
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ;tmp = fqmul(tmp, zeta_sq);
    mov src0_l, d1_l
    mov src0_h, d1_h
    mov src1_l, d0_l
    mov src1_h, d0_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ;b[0] += tmp; //5q
    add d3_l, d1_l
    adc d3_h, d1_h 

    ;b[0] = fqmul(b[0], det);
    mov src0_l, d3_l
    mov src0_h, d3_h
    mov src1_l, c0_l
    mov src1_h, c0_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d3_l, d3_h, mont0, mont1, zero

    st X+, d3_l
    st X+, d3_h

    ;b[1]= 2*a[0];
    ldd d3_l, Z+0
    ldd d3_h, Z+1
    lsl    d3_l          ; left shift 1 bit (¡Á2)
    rol    d3_h 
    
    ;b[1] = fqmul(b[1], a[2]);
    mov src0_l, d3_l
    mov src0_h, d3_h
    ldd src1_l, Z+4
    ldd src1_h, Z+5
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d3_l, d3_h, mont0, mont1, zero

    ;b[1] = fqmul(b[1], a[3]);
    mov src0_l, d3_l
    mov src0_h, d3_h
    ldd src1_l, Z+6
    ldd src1_h, Z+7
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d3_l, d3_h, mont0, mont1, zero

    ;b[1] = fqmul(b[1], zeta);
    mov src0_l, d3_l
    mov src0_h, d3_h
    mov src1_l, zeta_l
    mov src1_h, zeta_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d3_l, d3_h, mont0, mont1, zero

    ;tmp = fqmul(sq_fq[0], a[1]);
    ldd src0_l, Y+0
    ldd src0_h, Y+1
    ldd src1_l, Z+2
    ldd src1_h, Z+3
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ;b[1] -= tmp;
    sub d3_l, d1_l
    sbc d3_h, d1_h

    ;tmp = fqmul(sq_fq[1], a[3]);
    ldd src0_l, Y+2
    ldd src0_h, Y+3
    ldd src1_l, Z+6
    ldd src1_h, Z+7
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ;tmp = fqmul(tmp, zeta);
    mov src0_l, d1_l
    mov src0_h, d1_h
    mov src1_l, zeta_l
    mov src1_h, zeta_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ;b[1] += tmp;
    add d3_l, d1_l
    adc d3_h, d1_h

    ;tmp = fqmul(a[1], sq_fq[2]);
    ldd src0_l, Y+4
    ldd src0_h, Y+5
    ldd src1_l, Z+2
    ldd src1_h, Z+3
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ;tmp = fqmul(tmp, zeta);
    mov src0_l, d1_l
    mov src0_h, d1_h
    mov src1_l, zeta_l
    mov src1_h, zeta_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ;b[1] -= tmp;
    sub d3_l, d1_l
    sbc d3_h, d1_h

    ;tmp = fqmul(sq_fq[3], a[3]);
    ldd src0_l, Y+6
    ldd src0_h, Y+7
    ldd src1_l, Z+6
    ldd src1_h, Z+7
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero
    ;tmp = fqmul(tmp, zeta_sq);
    mov src0_l, d1_l
    mov src0_h, d1_h
    mov src1_l, d0_l
    mov src1_h, d0_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ;b[1] -= tmp;
    sub d3_l, d1_l
    sbc d3_h, d1_h

    ;b[1] = fqmul(b[1], det);
    mov src0_l, d3_l
    mov src0_h, d3_h
    mov src1_l, c0_l
    mov src1_h, c0_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d3_l, d3_h, mont0, mont1, zero
    
    st X+, d3_l
    st X+, d3_h
    ;b[2] =fqmul(a[0], sq_fq[1]);
    ldd src0_l, Y+2
    ldd src0_h, Y+3
    ldd src1_l, Z+0
    ldd src1_h, Z+1
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d3_l, d3_h, mont0, mont1, zero
    
    ;tmp = fqmul(sq_fq[0], a[2]);
    ldd src0_l, Y+0
    ldd src0_h, Y+1
    ldd src1_l, Z+4
    ldd src1_h, Z+5
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero
    ;b[2] -= tmp;
    sub d3_l, d1_l
    sbc d3_h, d1_h

    ;tmp = fqmul(a[0], sq_fq[3]);
    ldd src0_l, Y+6
    ldd src0_h, Y+7
    ldd src1_l, Z+0
    ldd src1_h, Z+1
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero
    ;tmp = fqmul(tmp, zeta);
    mov src0_l, d1_l
    mov src0_h, d1_h
    mov src1_l, zeta_l
    mov src1_h, zeta_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero
    ;b[2] += tmp;
    add d3_l, d1_l
    adc d3_h, d1_h
    
    ;tmp = 2*a[1];
    ldd d1_l, Z+2
    ldd d1_h, Z+3
    lsl    d1_l          ; left shift 1 bit (¡Á2)
    rol    d1_h 

    ;tmp = fqmul(tmp, a[2]);
    mov src0_l, d1_l
    mov src0_h, d1_h
    ldd src1_l, Z+4
    ldd src1_h, Z+5
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero
    ;tmp = fqmul(tmp, a[3]);
    mov src0_l, d1_l
    mov src0_h, d1_h
    ldd src1_l, Z+6
    ldd src1_h, Z+7
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero
    ;tmp = fqmul(tmp, zeta);
    mov src0_l, d1_l
    mov src0_h, d1_h
    mov src1_l, zeta_l
    mov src1_h, zeta_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero
    ;b[2] -= tmp;
    sub d3_l, d1_l
    sbc d3_h, d1_h  

    ;tmp = fqmul(sq_fq[2],a[2]);
    ldd src0_l, Y+4
    ldd src0_h, Y+5
    ldd src1_l, Z+4
    ldd src1_h, Z+5
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero
    ;tmp = fqmul(tmp, zeta);
    mov src0_l, d1_l
    mov src0_h, d1_h
    mov src1_l, zeta_l
    mov src1_h, zeta_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ;b[2] += tmp;
    add d3_l, d1_l
    adc d3_h, d1_h
    
    ;b[2] = fqmul(b[2], det);
    mov src0_l, d3_l
    mov src0_h, d3_h
    mov src1_l, c0_l
    mov src1_h, c0_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d3_l, d3_h, mont0, mont1, zero

    st X+, d3_l
    st X+, d3_h

    ;b[3] = 2*a[0];
    ldd d3_l, Z+0
    ldd d3_h, Z+1
    lsl    d3_l          ; left shift 1 bit (¡Á2)
    rol    d3_h 
    ;b[3] = fqmul(b[3],a[1]);
    mov src0_l, d3_l
    mov src0_h, d3_h
    ldd src1_l, Z+2
    ldd src1_h, Z+3
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d3_l, d3_h, mont0, mont1, zero

    ;b[3] = fqmul(b[3],a[2]);
    mov src0_l, d3_l
    mov src0_h, d3_h
    ldd src1_l, Z+4
    ldd src1_h, Z+5
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d3_l, d3_h, mont0, mont1, zero

    ;tmp = fqmul(sq_fq[0],a[3]);
    ldd src0_l, Y+0
    ldd src0_h, Y+1
    ldd src1_l, Z+6
    ldd src1_h, Z+7
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ;b[3] -= tmp;
    sub d3_l, d1_l
    sbc d3_h, d1_h

    ;tmp = fqmul(sq_fq[1],a[1]);
    ldd src0_l, Y+2
    ldd src0_h, Y+3
    ldd src1_l, Z+2
    ldd src1_h, Z+3
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ;b[3] -= tmp;
    sub d3_l, d1_l
    sbc d3_h, d1_h

    ;tmp = fqmul(sq_fq[3],a[1]);
    ldd src0_l, Y+6
    ldd src0_h, Y+7
    ldd src1_l, Z+2
    ldd src1_h, Z+3
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ;tmp = fqmul(tmp, zeta);

    mov src0_l, d1_l
    mov src0_h, d1_h
    mov src1_l, zeta_l
    mov src1_h, zeta_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ;b[3] += tmp;
    add d3_l, d1_l
    adc d3_h, d1_h

    ;tmp = fqmul(sq_fq[2],a[3]);

    ldd src0_l, Y+4
    ldd src0_h, Y+5
    ldd src1_l, Z+6
    ldd src1_h, Z+7
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ;tmp = fqmul(tmp, zeta);

    mov src0_l, d1_l
    mov src0_h, d1_h
    mov src1_l, zeta_l
    mov src1_h, zeta_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d1_l, d1_h, mont0, mont1, zero

    ;b[3] -= tmp;
    sub d3_l, d1_l
    sbc d3_h, d1_h

    ;b[3] = fqmul(b[3], det);
    mov src0_l, d3_l
    mov src0_h, d3_h
    mov src1_l, c0_l
    mov src1_h, c0_h
    mc_KRED2X_mul src0_l, src0_h, src1_l, src1_h, d3_l, d3_h, mont0, mont1, zero

    st X+, d3_l
    st X+, d3_h

    ; input: c0_l:c0_h = 16-bit det
    ; output: r25:r24 = (r8:r7 == 0 ? 1 : 0)

    mov     r24, c0_h        ; r24 = high byte
    or      r24, c0_l        ; r24 = c0_h | c0_l
    ; if det = 0 ¡ú r24=0
    ; if det ! =0       ¡ú r24!=0

    subi    r24, 1         ; r24 = r24 - 1
    sbc     r24, r24       ; r24 = 0xFF if input==0 else 0x00
    neg     r24            ; r24 = 1 if input==0 else 0

    clr     r25            ;  return value = r25:r24


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
