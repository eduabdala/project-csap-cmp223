# ============================================================
# PQC firmware @ RP2040 (Raspberry Pi Pico) — ARM Cortex-M0+ build
#
# Same CLI interface as ../atmega4809/Makefile:
#   make                                    # build (default: kyber512, ref, -O3, 125 MHz)
#   make ALG=kyber512 VARIANT=ref OPT=-O3 F_CPU=125000000UL
#   make size                               # Flash/SRAM usage report (arm-none-eabi-size)
#   make flash MOUNT=/media/$USER/RPI-RP2   # copy .uf2 to Pico in BOOTSEL mode
#   make clean
# ============================================================

ALG      ?= kyber512
VARIANT  ?= ref
OPT      ?= -O3
F_CPU    ?= 125000000UL

BUILD    := build
TARGET   := firmware-$(ALG)-$(VARIANT)
SIZE     := arm-none-eabi-size

# Use ~/pico-sdk by default (override with PICO_SDK_PATH=/path/to/pico-sdk)
PICO_SDK_PATH ?= $(HOME)/pico-sdk

.PHONY: all sdk size flash clean

all: $(BUILD)/$(TARGET).uf2

sdk:
	@if [ ! -f "$(PICO_SDK_PATH)/pico_sdk_init.cmake" ]; then \
		echo "[RP2040] Clonando pico-sdk em $(PICO_SDK_PATH)..."; \
		git clone --depth 1 --branch 2.0.0 https://github.com/raspberrypi/pico-sdk.git "$(PICO_SDK_PATH)" && \
		git -C "$(PICO_SDK_PATH)" submodule update --init --depth 1 lib/tinyusb; \
	fi

$(BUILD)/$(TARGET).uf2: sdk main.c glue.c CMakeLists.txt
	@mkdir -p $(BUILD)
	cmake -S . -B $(BUILD) \
		-DPICO_SDK_PATH="$(PICO_SDK_PATH)" \
		-DPICO_NO_PICOTOOL=1 \
		-DALG=$(ALG) \
		-DVARIANT=$(VARIANT) \
		-DOPT=$(OPT) \
		-DF_CPU=$(F_CPU)
	$(MAKE) -C $(BUILD) -j$$(nproc) $(TARGET)
	@python3 -c 'import struct, sys; data = open(sys.argv[1], "rb").read(); n = (len(data) + 255) // 256; out = open(sys.argv[2], "wb"); [out.write(struct.pack("<8I476sI", 0x0A324655, 0x9E5D5157, 0x2000, 0x10000000 + i*256, 256, i, n, 0xE48BFF56, data[i*256:(i+1)*256].ljust(256, b"\x00"), 0x0AB16F30)) for i in range(n)]' $(BUILD)/$(TARGET).bin $(BUILD)/$(TARGET).uf2

size: $(BUILD)/$(TARGET).uf2
	@$(SIZE) -B $(BUILD)/$(TARGET).elf

# Flash RP2040: either via picotool (if installed) or by copying .uf2 to RPI-RP2 mass storage
MOUNT ?= $(firstword $(wildcard /media/$(USER)/RPI-RP2 /run/media/$(USER)/RPI-RP2))
flash: $(BUILD)/$(TARGET).uf2
	@if command -v picotool >/dev/null 2>&1; then \
		picotool load -f $(BUILD)/$(TARGET).uf2 && picotool reboot; \
	elif [ -n "$(MOUNT)" ] && [ -d "$(MOUNT)" ]; then \
		cp $(BUILD)/$(TARGET).uf2 "$(MOUNT)/" && sync && echo "[RP2040] Gravado em $(MOUNT)/"; \
	else \
		echo "Conecte o Raspberry Pi Pico segurando o botão BOOTSEL e rode novamente (ou passe MOUNT=/caminho/RPI-RP2)."; \
		exit 1; \
	fi

clean:
	rm -rf $(BUILD)

