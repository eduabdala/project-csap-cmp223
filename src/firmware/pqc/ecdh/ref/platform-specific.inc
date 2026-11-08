#ifndef _UECC_PLATFORM_SPECIFIC_H_
#define _UECC_PLATFORM_SPECIFIC_H_

static int default_RNG(uint8_t *dest, unsigned size) {
    static uint8_t s = 0x5A;
    for (unsigned i = 0; i < size; ++i) {
        s = (uint8_t)(s * 13U + 7U + i);
        dest[i] = s;
    }
    return 1;
}
#define default_RNG_defined 1

#endif /* _UECC_PLATFORM_SPECIFIC_H_ */

