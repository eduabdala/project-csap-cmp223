# ============================================================
# Firmware Kyber-512 @ ATmega4809 — build cross AVR
# Uso:
#   make            # compila (default: Kyber-512, -Os)
#   make OPT=-O3    # muda nível de otimização
#   make size       # relatório de uso de Flash/SRAM (avr-size)
#   make flash      # grava via UPDI (avrdude)
#   make clean
#
# Dentro do `nix develop`, CC/avr-size/avrdude já estão no PATH.
# ============================================================

# ---- SUT ----------------------------------------------------
MCU      ?= atmega4809
F_CPU    ?= 20000000UL      # 20 MHz (fator: 20/10/5 MHz)
BAUD     ?= 115200

# ---- Toolchain ---------------------------------------------
# No devShell do Nix os binários vêm prefixados como avr-*.
CC        := avr-gcc
OBJCOPY   := avr-objcopy
SIZE      := avr-size
AVRDUDE   := avrdude

# ---- Fator experimental: otimização ------------------------
OPT      ?= -Os            # alternar com -O3

# ---- Algoritmo e variante (fatores) ------------------------
# ALG     ∈ { kyber512, ctru-light, ecdh }
# VARIANT ∈ { ref, asm }   (ref = C puro; asm = otimizada em assembly AVR)
#
# Cada combinação ALG×VARIANT é um binário distinto, buildado, gravado e
# medido separadamente (6 binários no total).
ALG      ?= kyber512
VARIANT  ?= ref

# Valida ALG
ifeq ($(filter $(ALG),kyber512 ctru-light ecdh),)
  $(error ALG inválido: '$(ALG)'. Use kyber512, ctru-light ou ecdh.)
endif
# Valida VARIANT
ifeq ($(filter $(VARIANT),ref asm),)
  $(error VARIANT inválido: '$(VARIANT)'. Use ref ou asm.)
endif

# Adaptador kem.h por algoritmo + tamanhos de buffer (sobrescrevem kem.h).
ifeq ($(ALG),kyber512)
  ADAPTER  := kem_kyber512.c
  SIZEDEFS := -DKEM_PUBLICKEYBYTES=800 -DKEM_SECRETKEYBYTES=1632 \
              -DKEM_CIPHERTEXTBYTES=768 -DKEM_BYTES=32
else ifeq ($(ALG),ctru-light)
  ADAPTER  := kem_ctru.c
  SIZEDEFS := -DKEM_PUBLICKEYBYTES=1206 -DKEM_SECRETKEYBYTES=1206 \
              -DKEM_CIPHERTEXTBYTES=1206 -DKEM_BYTES=32
else ifeq ($(ALG),ecdh)
  ADAPTER  := kem_ecdh.c
  SIZEDEFS := -DKEM_PUBLICKEYBYTES=64 -DKEM_SECRETKEYBYTES=64 \
              -DKEM_CIPHERTEXTBYTES=64 -DKEM_BYTES=32
endif

# Diretório da fonte vendorizada: pqc/<ALG>/<VARIANT>/
PQCDIR   := pqc/$(ALG)/$(VARIANT)

# Na variante asm, incluir também os .S (assembly AVR).
ASMSRC   := $(if $(filter asm,$(VARIANT)),$(wildcard $(PQCDIR)/*.S),)

# ---- Flags --------------------------------------------------
CFLAGS   := -mmcu=$(MCU) -DF_CPU=$(F_CPU) -DBAUD=$(BAUD) $(SIZEDEFS) \
            $(OPT) -std=gnu11 -Wall -Wextra \
            -ffunction-sections -fdata-sections \
            -funsigned-char -funsigned-bitfields
ASFLAGS  := -mmcu=$(MCU) -x assembler-with-cpp $(SIZEDEFS)
LDFLAGS  := -mmcu=$(MCU) -Wl,--gc-sections -Wl,-Map,$(BUILD)/$(TARGET).map

# ---- Fontes -------------------------------------------------
BUILD    := build
TARGET   := firmware-$(ALG)-$(VARIANT)

# main.c + adaptador do algoritmo + fontes C vendorizadas (+ .S na variante asm).
CSRC     := main.c $(ADAPTER) $(wildcard $(PQCDIR)/*.c)
INCLUDES := -I. -I$(PQCDIR)

OBJ      := $(patsubst %.c,$(BUILD)/%.o,$(CSRC)) \
            $(patsubst %.S,$(BUILD)/%.o,$(ASMSRC))

# ---- Regras -------------------------------------------------
.PHONY: all size flash clean

all: $(BUILD)/$(TARGET).elf $(BUILD)/$(TARGET).hex

$(BUILD)/%.o: %.c
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@

# Assembly AVR (.S) — passa pelo pré-processador (assembler-with-cpp).
$(BUILD)/%.o: %.S
	@mkdir -p $(dir $@)
	$(CC) $(ASFLAGS) $(INCLUDES) -c $< -o $@

$(BUILD)/$(TARGET).elf: $(OBJ)
	$(CC) $(LDFLAGS) $^ -o $@

$(BUILD)/$(TARGET).hex: $(BUILD)/$(TARGET).elf
	$(OBJCOPY) -O ihex -R .eeprom $< $@

# Relatório de memória (métrica: tamanho de binário / headroom)
size: $(BUILD)/$(TARGET).elf
	$(SIZE) --mcu=$(MCU) -C $<

# Gravação via UPDI (Nano Every). Ajuste PORT conforme o host.
PORT ?= /dev/ttyACM0
flash: $(BUILD)/$(TARGET).hex
	$(AVRDUDE) -c jtag2updi -p $(MCU) -P $(PORT) -U flash:w:$<:i

clean:
	rm -rf $(BUILD)
