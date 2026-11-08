
#include "macros.inc"
#include "common.inc"
.section .text


.global nttkred_asm
.type   nttkred_asm, @function                      
nttkred_asm:



#define	zero    r2		
#define	a0     	r6	
#define	a1     	r7	
#define	adr0   	r8	
#define	adr1   	r9	
#define	mont0  	r10	
#define	mont1  	r11	
#define	mont2  	r12	
#define	mont3  	r13	
#define	hi0    	r14	
#define	hi1    	r15	
#define	cst_q  	r17	
#define	offset	r16	
#define	b0     	r18	
#define	b1     	r19	
#define	cst_tmp    	r21	
#define	lo1    	r20	
#define	z0     	r22	
#define	z1     	r23	
#define	i_cnt  	r24	
#define	o_cnt  	r25	

    ;prolog
    mc_prolog 0, 17



    ldi		  cst_q,		0x9
    ldi		  cst_tmp,		0x03
    clr     zero
    
    movw	r26,		r24 //X
    movw	r28,		r24 //Y
    inc   r29
    inc   r29 // &r[256]
    movw	adr0,		r24 
    // Z
    ldi     r30,    lo8(KRED2X_zetas)
    ldi     r31,    hi8(KRED2X_zetas)
    adiw    r30,    2

 
    
layer0: // Layer 0 interval = 256
    ;   load cnt 
    
    lpm     z0,     Z+
    lpm     z1,     Z+ 
 
    ldi     r24, lo8(256)  
    ldi     r25, hi8(256)  ; r25 = 0x02   => r25:r24 = 0x0200 = 512
in0:    
    mc_ntt_ct_hi    a0, a1, b0, b1
    mc_KRED2X_mul   b0, b1, z0, z1, hi0, hi1, mont0, mont1, zero
    mc_ntt_ct_lo    a0, a1, hi0, hi1, mont0, mont1 
    
  
    
    sbiw    r24, 1          ; r25:r24 = r25:r24 - 1
    brne    in0     


layer1: // Layer 1
    ldi     i_cnt,  128      ;
    ldi     o_cnt,  2       ;    
    movw    r26,    adr0
    movw    r28,    adr0
    inc     r29 ; +256 bytes 128 coefficients
    
out1:        
    lpm     z0,     Z+
    lpm     z1,     Z+  
in1:
    mc_ntt_ct_hi    a0, a1, b0, b1
    mc_KRED2X_mul   b0, b1, z0, z1, hi0, hi1, mont0, mont1, zero
    mc_ntt_ct_lo    a0, a1, hi0, hi1, mont0, mont1    
    dec     i_cnt
    brne    in1             ;
    
    inc     r27;  +256 bytes 128 coefficients
    inc     r29  
    ldi     i_cnt,  128      ;
    
    dec     o_cnt
    brne    out1            ;



layer2: // Layer 2
    ldi     i_cnt,  64      ;
    ldi     o_cnt,  4       ;    
    movw    r26,    adr0
    movw    r28,    adr0
    ldi     offset,  128     ;
    add     r28,    offset
    adc     r29,    zero
    
out2:        
    lpm     z0,     Z+
    lpm     z1,     Z+   
in2:
    mc_ntt_ct_hi    a0, a1, b0, b1
    mc_KRED2X_mul   b0, b1, z0, z1, hi0, hi1, mont0, mont1, zero
    mc_ntt_ct_lo    a0, a1, hi0, hi1, mont0, mont1 
    
    dec     i_cnt
    brne    in2             ;
    
    add     r26,    offset
    adc     r27,    zero
    add     r28,    offset
    adc     r29,    zero
    ldi     i_cnt,  64      ;
    
    dec     o_cnt
    brne    out2            ;


layer3: // Layer 3 
    ldi     i_cnt,  32      ;   
    movw    r26,    adr0
    movw    r28,    adr0
    ldi     offset,  64      ;
    add     r28,    offset
    adc     r29,    zero
    
out3:     
    lpm     z0,     Z+
    lpm     z1,     Z+ 
    push r30
    push r31
in3:
    mc_ntt_ct_hi    a0, a1, b0, b1
    mc_KRED2X_mul   b0, b1, z0, z1, hi0, hi1, mont0, mont1, zero
    mc_ntt_ct_lo_LUT_reduce    a0, a1, hi0, hi1, mont0, mont1 
   
    dec     i_cnt
    brne    in3             ;

    add     r26,    offset
    adc     r27,    zero
    add     r28,    offset
    adc     r29,    zero
    ldi     i_cnt,  32  
    pop r31
    pop r30  
out3_2:     
    lpm     z0,     Z+
    lpm     z1,     Z+
    push r30
    push r31
in3_2:
    mc_ntt_ct_hi    a0, a1, b0, b1
    mc_KRED2X_mul   b0, b1, z0, z1, hi0, hi1, mont0, mont1, zero
    mc_ntt_ct_lo_LUT_reduce    a0, a1, hi0, hi1, mont0, mont1    
    dec     i_cnt
    brne    in3_2  
    add     r26,    offset
    adc     r27,    zero
    add     r28,    offset
    adc     r29,    zero
    ldi     i_cnt,  32     
    pop r31
    pop r30 
out3_3:  
    lpm     z0,     Z+
    lpm     z1,     Z+
    push r30
    push r31
in3_3:
    mc_ntt_ct_hi    a0, a1, b0, b1
    mc_KRED2X_mul   b0, b1, z0, z1, hi0, hi1, mont0, mont1, zero
    mc_ntt_ct_lo_LUT_reduce    a0, a1, hi0, hi1, mont0, mont1 
 
    dec     i_cnt
    brne    in3_3  
    add     r26,    offset
    adc     r27,    zero
    add     r28,    offset
    adc     r29,    zero
    ldi     i_cnt,  32  
    pop r31
    pop r30 
out3_4:      
    lpm     z0,     Z+
    lpm     z1,     Z+
    push r30
    push r31
in3_4:
    mc_ntt_ct_hi    a0, a1, b0, b1
    mc_KRED2X_mul   b0, b1, z0, z1, hi0, hi1, mont0, mont1, zero
    mc_ntt_ct_lo_LUT_reduce    a0, a1, hi0, hi1, mont0, mont1   
    dec     i_cnt
    brne    in3_4  
    add     r26,    offset
    adc     r27,    zero
    add     r28,    offset
    adc     r29,    zero
    ldi     i_cnt,  32      ;
    pop r31
    pop r30  

out3_5:     
    lpm     z0,     Z+
    lpm     z1,     Z+
    push r30
    push r31
in3_5:
    mc_ntt_ct_hi    a0, a1, b0, b1
    mc_KRED2X_mul   b0, b1, z0, z1, hi0, hi1, mont0, mont1, zero
    mc_ntt_ct_lo_LUT_reduce    a0, a1, hi0, hi1, mont0, mont1   
    dec     i_cnt
    brne    in3_5  
    add     r26,    offset
    adc     r27,    zero
    add     r28,    offset
    adc     r29,    zero
    ldi     i_cnt,  32  
    pop r31
    pop r30  

out3_6:     
    lpm     z0,     Z+
    lpm     z1,     Z+
    push r30
    push r31
in3_6:
    mc_ntt_ct_hi    a0, a1, b0, b1
    mc_KRED2X_mul   b0, b1, z0, z1, hi0, hi1, mont0, mont1, zero
    mc_ntt_ct_lo_LUT_reduce    a0, a1, hi0, hi1, mont0, mont1   
    dec     i_cnt
    brne    in3_6  
    add     r26,    offset
    adc     r27,    zero
    add     r28,    offset
    adc     r29,    zero
    ldi     i_cnt,  32     
    pop r31
    pop r30
out3_7:     
    lpm     z0,     Z+
    lpm     z1,     Z+
    push r30
    push r31
in3_7:
    mc_ntt_ct_hi    a0, a1, b0, b1
    mc_KRED2X_mul   b0, b1, z0, z1, hi0, hi1, mont0, mont1, zero
    mc_ntt_ct_lo_LUT_reduce    a0, a1, hi0, hi1, mont0, mont1    
    dec     i_cnt
    brne    in3_7  
    add     r26,    offset
    adc     r27,    zero
    add     r28,    offset
    adc     r29,    zero
    ldi     i_cnt,  32     
    pop r31
    pop r30  
out3_8:     
    lpm     z0,     Z+
    lpm     z1,     Z+
    push r30
    push r31
in3_8:
    mc_ntt_ct_hi    a0, a1, b0, b1
    mc_KRED2X_mul   b0, b1, z0, z1, hi0, hi1, mont0, mont1, zero
    mc_ntt_ct_lo_LUT_reduce    a0, a1, hi0, hi1, mont0, mont1 
    dec     i_cnt
    brne    in3_8  
    pop r31
    pop r30 



layer4: // Layer 4 
    ldi     i_cnt,  16       ;
    ldi     o_cnt,  16      ;    
    movw    r26,    adr0
    movw    r28,    adr0
    ldi     offset,  32      ;
    add     r28,    offset
    adc     r29,    zero
    
out4:        
    lpm     z0,     Z+
    lpm     z1,     Z+   
in4:
    mc_ntt_ct_hi    a0, a1, b0, b1
    mc_KRED2X_mul   b0, b1, z0, z1, hi0, hi1, mont0, mont1, zero
    mc_ntt_ct_lo    a0, a1, hi0, hi1, mont0, mont1    
    
    dec     i_cnt
    brne    in4             ;
    
    add     r26,    offset
    adc     r27,    zero
    add     r28,    offset
    adc     r29,    zero
    ldi     i_cnt,  16      ;
    
    dec     o_cnt
    brne    out4            ;

layer5: // Layer 5 
    ldi     i_cnt,  8       ;
    ldi     o_cnt,  32      ;    
    movw    r26,    adr0
    movw    r28,    adr0
    ldi     offset,  16      ;
    add     r28,    offset
    adc     r29,    zero
    
out5:        
    lpm     z0,     Z+
    lpm     z1,     Z+   
in5:
    mc_ntt_ct_hi    a0, a1, b0, b1
    mc_KRED2X_mul   b0, b1, z0, z1, hi0, hi1, mont0, mont1, zero
    mc_ntt_ct_lo    a0, a1, hi0, hi1, mont0, mont1    
    
    dec     i_cnt
    brne    in5             ;
    
    add     r26,    offset
    adc     r27,    zero
    add     r28,    offset
    adc     r29,    zero
    ldi     i_cnt,  8      ;
    
    dec     o_cnt
    brne    out5            ;

layer6: // Layer 6
    ldi     i_cnt,  4       ;
    ldi     o_cnt,  64      ;    
    movw    r26,    adr0
    movw    r28,    adr0
    ldi     offset,  8      ;
    add     r28,    offset
    adc     r29,    zero
    
out6:        
    lpm     z0,     Z+
    lpm     z1,     Z+      
in6:
    mc_ntt_ct_hi    a0, a1, b0, b1
    mc_KRED2X_mul   b0, b1, z0, z1, hi0, hi1, mont0, mont1, zero
    mc_ntt_ct_lo  a0, a1, hi0, hi1, mont0, mont1   
    
    dec     i_cnt
    brne    in6             ;
    
    add     r26,    offset
    adc     r27,    zero
    add     r28,    offset
    adc     r29,    zero
    ldi     i_cnt,  4      ;
    
    dec     o_cnt
    breq    end_ntt769ntt  ;
    rjmp    out6






end_ntt769ntt:
;epilog
    mc_epilog 0, 17
    
    ret


