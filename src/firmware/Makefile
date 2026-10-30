# ============================================================
# PQC firmware @ ATmega4809 — AVR cross build
# Usage:
#   make            # build (default: Kyber-512, ref, -Os)
#   make OPT=-O3    # change optimization level
#   make size       # Flash/SRAM usage report (avr-size)
#   make flash      # program via UPDI (avrdude)
#   make clean
#
# Inside `nix develop`, CC/avr-size/avrdude are already on the PATH.
# ============================================================

# ---- SUT ----------------------------------------------------
MCU      ?= atmega4809
F_CPU    ?= 20000000UL      # 20 MHz (factor: 20/10/5 MHz)
BAUD     ?= 115200

# ---- Toolchain ---------------------------------------------
# In the Nix devShell the binaries are prefixed as avr-*.
CC        := avr-gcc
OBJCOPY   := avr-objcopy
SIZE      := avr-size
AVRDUDE   := avrdude

# ---- Experimental factor: optimization ---------------------
OPT      ?= -Os            # switch with -O3

# ---- Algorithm and variant (factors) -----------------------
# ALG     in { kyber512, ctru-light, ecdh }
# VARIANT in { ref, asm }   (ref = plain C; asm = AVR assembly optimized)
#
# Each ALG x VARIANT combination is a distinct binary, built, flashed and
# measured separately (6 binaries in total).
ALG      ?= kyber512
VARIANT  ?= ref

# Validate ALG
ifeq ($(filter $(ALG),kyber512 ctru-light ecdh),)
  $(error invalid ALG: '$(ALG)'. Use kyber512, ctru-light or ecdh.)
endif
# Validate VARIANT
ifeq ($(filter $(VARIANT),ref asm),)
  $(error invalid VARIANT: '$(VARIANT)'. Use ref or asm.)
endif

# Per-algorithm kem.h adapter + buffer sizes (override kem.h).
ifeq ($(ALG),kyber512)
  ADAPTER  := kem_kyber512.c
  SIZEDEFS := -DKEM_PUBLICKEYBYTES=800 -DKEM_SECRETKEYBYTES=1632 \
              -DKEM_CIPHERTEXTBYTES=768 -DKEM_BYTES=32
else ifeq ($(ALG),ctru-light)
  ADAPTER  := kem_ctru.c
  SIZEDEFS := -DKEM_PUBLICKEYBYTES=640 -DKEM_SECRETKEYBYTES=848 \
              -DKEM_CIPHERTEXTBYTES=512 -DKEM_BYTES=16
else ifeq ($(ALG),ecdh)
  ADAPTER  := kem_ecdh.c
  SIZEDEFS := -DKEM_PUBLICKEYBYTES=64 -DKEM_SECRETKEYBYTES=64 \
              -DKEM_CIPHERTEXTBYTES=64 -DKEM_BYTES=32 \
              $(if $(filter asm,$(VARIANT)),-DuECC_PLATFORM=uECC_avr -DuECC_OPTIMIZATION_LEVEL=3,-DuECC_PLATFORM=uECC_arch_other)
endif

# Vendored source directory: pqc/<ALG>/<VARIANT>/
PQCDIR   := pqc/$(ALG)/$(VARIANT)

# In the asm variant, also include the .S files (AVR assembly).
ASMSRC   := $(if $(filter asm,$(VARIANT)),$(wildcard $(PQCDIR)/*.S $(PQCDIR)/*/*.S),)

# ---- Sources ------------------------------------------------
BUILD    := build
TARGET   := firmware-$(ALG)-$(VARIANT)

# ---- Flags --------------------------------------------------
DFP_FLAGS := $(if $(wildcard .dfp/gcc/dev/$(MCU)),-B .dfp/gcc/dev/$(MCU) -I .dfp/include,)
CFLAGS   := -mmcu=$(MCU) $(DFP_FLAGS) -DF_CPU=$(F_CPU) -DBAUD_RATE=$(BAUD) $(SIZEDEFS) \
            $(OPT) -std=gnu11 -Wall -Wextra \
            -ffunction-sections -fdata-sections \
            -funsigned-char -funsigned-bitfields
ASFLAGS  := -mmcu=$(MCU) $(DFP_FLAGS) -x assembler-with-cpp $(SIZEDEFS)
LDFLAGS  := -mmcu=$(MCU) $(DFP_FLAGS) -Wl,--gc-sections -Wl,-Map,$(BUILD)/$(TARGET).map

# main.c + algorithm adapter + vendored C sources (+ .S in the asm variant).
CSRC     := main.c $(ADAPTER) $(wildcard $(PQCDIR)/*.c $(PQCDIR)/*/*.c)
INCLUDES := -I. -I$(PQCDIR) $(addprefix -I,$(wildcard $(PQCDIR)/*/))

OBJ      := $(patsubst %.c,$(BUILD)/%.o,$(CSRC)) \
            $(patsubst %.S,$(BUILD)/%.o,$(ASMSRC))

# ---- Rules --------------------------------------------------
.PHONY: all size flash clean

all: $(BUILD)/$(TARGET).elf $(BUILD)/$(TARGET).hex

$(BUILD)/%.o: %.c
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@

# AVR assembly (.S) — runs through the preprocessor (assembler-with-cpp).
$(BUILD)/%.o: %.S
	@mkdir -p $(dir $@)
	$(CC) $(ASFLAGS) $(INCLUDES) -c $< -o $@

$(BUILD)/$(TARGET).elf: $(OBJ)
	$(CC) $(LDFLAGS) $^ -o $@

$(BUILD)/$(TARGET).hex: $(BUILD)/$(TARGET).elf
	$(OBJCOPY) -O ihex -R .eeprom $< $@

# Memory report (metric: binary size / headroom)
size: $(BUILD)/$(TARGET).elf
	@$(SIZE) --mcu=$(MCU) -C $< 2>/dev/null || $(SIZE) $<

# Program via UPDI (Nano Every).
# The Nano Every's onboard SAMD11 USB-serial bridge only enters jtag2updi
# programming mode after a 1200-baud touch on the serial port.
PORT ?= /dev/ttyACM0
flash: $(BUILD)/$(TARGET).hex
	stty -F $(PORT) 1200 hupcl && sleep 0.5
	$(AVRDUDE) -c jtag2updi -p $(MCU) -P $(PORT) -b 115200 -e -D -U fuse2:w:0x02:m -U flash:w:$<:i

clean:
	rm -rf $(BUILD)
