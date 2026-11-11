#include "common.i"

.section .text
.global small_LUT_reduce_asm
.type small_LUT_reduce_asm, @function
small_LUT_reduce_asm:
    mov r30, r25
    ldi r31, hi8(LUT3_H_3329)
    lpm r25, Z
    ldi r31, hi8(LUT3_L_3329)
    lpm r18, Z
    add r24, r18
    adc r25, r1
    ret

.global csubq_asm
.type csubq_asm, @function
csubq_asm:
    mov r30, r25
    ldi r31, hi8(LUT3_H_3329)
    lpm r25, Z
    ldi r31, hi8(LUT3_L_3329)
    lpm r18, Z
    add r24, r18
    adc r25, r1
    tst r25
    brpl 0f
    ldi r18, 0x01
    add r24, r18
    ldi r18, 0x0D
    adc r25, r18
0:
    subi r24, 0x01
    sbci r25, 0x0D
    brpl 1f
    ldi  r18, 0x01
    add  r24, r18
    ldi  r18, 0x0D
    adc  r25, r18
1:
    ret
