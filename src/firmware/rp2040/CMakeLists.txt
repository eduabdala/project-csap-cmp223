cmake_minimum_required(VERSION 3.13)

# Default to fetching pico-sdk from git if PICO_SDK_PATH is not set
if(NOT DEFINED PICO_SDK_PATH AND NOT DEFINED ENV{PICO_SDK_PATH})
    set(PICO_SDK_FETCH_FROM_GIT ON)
endif()

include(pico_sdk_import.cmake)

project(cmp223_rp2040_firmware C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

pico_sdk_init()

# ---- Experimental Factors ----------------------------------
set(ALG     "kyber512"     CACHE STRING "Algorithm: kyber512 | ctru-light | ecdh")
set(VARIANT "ref"          CACHE STRING "Variant: ref | asm")
set(OPT     "-O3"          CACHE STRING "Optimization flag: -Os | -O3")
set(F_CPU   "125000000UL"  CACHE STRING "System clock in Hz (min 48000000UL for USB CDC, default 125000000UL)")

set(COMMON_DIR "${CMAKE_CURRENT_LIST_DIR}/../common")
# On RP2040 (ARM Cortex-M0+), the vendored AVR .S files in pqc/*/asm are for
# 8-bit AVR, so both ref and asm use the C sources in ../pqc/<ALG>/ref, while
# for ECDH (micro-ecc) VARIANT=asm enables the ARM Thumb assembly fast path.
set(PQC_DIR    "${CMAKE_CURRENT_LIST_DIR}/../pqc/${ALG}/ref")

if(ALG STREQUAL "kyber512")
    set(ADAPTER "${COMMON_DIR}/kem_kyber512.c")
    set(ALG_DEFS
        ALG_KYBER512=1
        KEM_PUBLICKEYBYTES=800
        KEM_SECRETKEYBYTES=1632
        KEM_CIPHERTEXTBYTES=768
        KEM_BYTES=32
    )
elseif(ALG STREQUAL "ctru-light")
    set(ADAPTER "${COMMON_DIR}/kem_ctru.c")
    set(ALG_DEFS
        ALG_CTRU=1
        KEM_PUBLICKEYBYTES=640
        KEM_SECRETKEYBYTES=848
        KEM_CIPHERTEXTBYTES=512
        KEM_BYTES=16
    )
elseif(ALG STREQUAL "ecdh")
    set(ADAPTER "${COMMON_DIR}/kem_ecdh.c")
    if(VARIANT STREQUAL "asm")
        set(UECC_PLAT "uECC_arm_thumb")
    else()
        set(UECC_PLAT "uECC_arch_other")
    endif()
    set(ALG_DEFS
        ALG_ECDH=1
        KEM_PUBLICKEYBYTES=64
        KEM_SECRETKEYBYTES=64
        KEM_CIPHERTEXTBYTES=64
        KEM_BYTES=32
        uECC_PLATFORM=${UECC_PLAT}
        uECC_OPTIMIZATION_LEVEL=3
    )
else()
    message(FATAL_ERROR "Invalid ALG='${ALG}'. Use kyber512, ctru-light or ecdh.")
endif()

file(GLOB PQC_SOURCES "${PQC_DIR}/*.c")
# Exclude vendored randombytes.c: glue.c routes randombytes() to harness_rng_read()
list(FILTER PQC_SOURCES EXCLUDE REGEX "randombytes\\.c$")

set(TARGET_NAME "firmware-${ALG}-${VARIANT}")

add_executable(${TARGET_NAME}
    main.c
    glue.c
    ${ADAPTER}
    ${PQC_SOURCES}
)

target_include_directories(${TARGET_NAME} PRIVATE
    ${CMAKE_CURRENT_LIST_DIR}
    ${COMMON_DIR}
    ${PQC_DIR}
)

target_compile_definitions(${TARGET_NAME} PRIVATE
    F_CPU=${F_CPU}
    PICO_STACK_SIZE=0x8000
    ${ALG_DEFS}
)

target_compile_options(${TARGET_NAME} PRIVATE
    ${OPT}
    -Wall
    -Wextra
    -ffunction-sections
    -fdata-sections
)

target_link_libraries(${TARGET_NAME}
    pico_stdlib
    hardware_clocks
    hardware_gpio
    hardware_sync
    hardware_vreg
)

# Enable USB-CDC serial (/dev/ttyACM0), disable UART stdio
pico_enable_stdio_usb(${TARGET_NAME} 1)
pico_enable_stdio_uart(${TARGET_NAME} 0)

# Generate .uf2, .hex, .bin, .map
pico_add_extra_outputs(${TARGET_NAME})

