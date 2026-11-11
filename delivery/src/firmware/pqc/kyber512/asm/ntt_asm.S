
#include "mul_asm.i"
#include "common.i"
.section .text
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
#define	cst_q  	r16	
#define	offset	r17	
#define	b0     	r18	
#define	b1     	r19	
#define	lo0    	r20	
#define	lo1    	r21	
#define	z0     	r22	
#define	z1     	r23	
#define	i_cnt  	r24	
#define	o_cnt  	r25	
.global ntt_asm
.type ntt_asm, @function

ntt_asm:
    ;prolog
    mc_prolog 0, 17



    ldi     cst_q,    0xF3   
    clr     zero
    
    movw	r26,		r24 //X
    movw	r28,		r24 //Y
    inc     r29// &r[128]
    movw	adr0,		r24 
    // Z
    ldi     r30,    lo8(zetas)
    ldi     r31,    hi8(zetas)
    adiw    r30,    2

 
layer1: // Layer 1
    ldi     i_cnt,  128      ;   
    movw    r26,    adr0
    movw    r28,    adr0
    inc     r29 ; +256 bytes 128 coefficients
    

    ld     z0,     Z+
    ld     z1,     Z+  
in1:
    mc_ntt_ct_hi    a0, a1, b0, b1
    mc_3329_montmul_opt  b0, b1, z0, z1, lo0, lo1, hi0, hi1, mont0, mont1, cst_q, zero
    mc_ntt_ct_lo    a0, a1, hi0, hi1, mont0, mont1 


    dec     i_cnt
    brne    in1             ;
    
   



layer2: // Layer 2
    ldi     i_cnt,  64      ;
    ldi     o_cnt,  2       ;    
    movw    r26,    adr0
    movw    r28,    adr0
    ldi     offset,  128     ;
    add     r28,    offset
    adc     r29,    zero
    
out2:        
    ld     z0,     Z+
    ld     z1,     Z+   
in2:
    mc_ntt_ct_hi    a0, a1, b0, b1
    mc_3329_montmul_opt  b0, b1, z0, z1, lo0, lo1, hi0, hi1, mont0, mont1, cst_q, zero
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
    ldi     o_cnt,  4       ;    
    movw    r26,    adr0
    movw    r28,    adr0
    ldi     offset,  64      ;
    add     r28,    offset
    adc     r29,    zero
    
out3:        
    ld     z0,     Z+
    ld     z1,     Z+       
in3:
    mc_ntt_ct_hi    a0, a1, b0, b1
    mc_3329_montmul_opt  b0, b1, z0, z1, lo0, lo1, hi0, hi1, mont0, mont1, cst_q, zero
    mc_ntt_ct_lo    a0, a1, hi0, hi1, mont0, mont1    
    
    dec     i_cnt
    brne    in3             ;
    
    add     r26,    offset
    adc     r27,    zero
    add     r28,    offset
    adc     r29,    zero
    ldi     i_cnt,  32      ;
    
    dec     o_cnt
    brne    out3            ;


layer4: // Layer 4 
    ldi     i_cnt,  16       ;
    ldi     o_cnt,  8      ;    
    movw    r26,    adr0
    movw    r28,    adr0
    ldi     offset,  32      ;
    add     r28,    offset
    adc     r29,    zero
    
out4:        
    ld     z0,     Z+
    ld     z1,     Z+   
in4:
    mc_ntt_ct_hi    a0, a1, b0, b1
    mc_3329_montmul_opt  b0, b1, z0, z1, lo0, lo1, hi0, hi1, mont0, mont1, cst_q, zero
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
    ldi     o_cnt,  16      ;    
    movw    r26,    adr0
    movw    r28,    adr0
    ldi     offset,  16      ;
    add     r28,    offset
    adc     r29,    zero
    
out5:        
    ld     z0,     Z+
    ld     z1,     Z+   
in5:
    mc_ntt_ct_hi    a0, a1, b0, b1
    mc_3329_montmul_opt  b0, b1, z0, z1, lo0, lo1, hi0, hi1, mont0, mont1, cst_q, zero
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
    ldi     o_cnt,  32      ;    
    movw    r26,    adr0
    movw    r28,    adr0
    ldi     offset,  8      ;
    add     r28,    offset
    adc     r29,    zero
    
out6:        
    ld     z0,     Z+
    ld     z1,     Z+      
in6:
    mc_ntt_ct_hi    a0, a1, b0, b1
    mc_3329_montmul_opt  b0, b1, z0, z1, lo0, lo1, hi0, hi1, mont0, mont1, cst_q, zero
    mc_ntt_ct_lo  a0, a1, hi0, hi1, mont0, mont1   
    
    dec     i_cnt
    brne    in6             ;
    
    add     r26,    offset
    adc     r27,    zero
    add     r28,    offset
    adc     r29,    zero
    ldi     i_cnt,  4      ;
    
    dec     o_cnt
    breq    layer7  ;
    rjmp    out6


layer7: // Layer 7
    ldi     i_cnt,  2       ;
    ldi     o_cnt,  64      ;    
    movw    r26,    adr0
    movw    r28,    adr0
    ldi     offset,  4      ;
    add     r28,    offset
    adc     r29,    zero
    
out7:        
    ld     z0,     Z+
    ld     z1,     Z+      
in7:
    mc_ntt_ct_hi    a0, a1, b0, b1
    mc_3329_montmul_opt  b0, b1, z0, z1, lo0, lo1, hi0, hi1, mont0, mont1, cst_q, zero
    mc_ntt_ct_lo  a0, a1, hi0, hi1, mont0, mont1   
    
    dec     i_cnt
    brne    in7             ;
    
    add     r26,    offset
    adc     r27,    zero
    add     r28,    offset
    adc     r29,    zero
    ldi     i_cnt,  2      ;
    
    dec     o_cnt
    breq    end_ntt3329ntt  ;
    rjmp    out7



#undef	zero
#undef	offset
#undef	a0
#undef	a1
#undef	adr0
#undef	adr1
#undef	mont0
#undef	mont1
#undef	mont2
#undef	mont3
#undef	hi0
#undef	hi1
#undef	cst_q
#undef	offset
#undef	b0
#undef	b1
#undef	lo0
#undef	lo1
#undef	z0
#undef	z1
#undef	i_cnt
#undef	o_cnt


end_ntt3329ntt:
;epilog
    mc_epilog 0, 17
    
    ret


