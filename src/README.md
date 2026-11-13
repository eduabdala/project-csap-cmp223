# Código-Fonte do Experimento (`src/`)

Diretório raiz do código-fonte: firmware embarcado para a placa **Arduino Nano Every / ATmega4809**, implementações dos algoritmos criptográficos (Kyber-512, CTRU-Light e ECDH), rotinas de instrumentação física e scripts de coleta e análise estatística.

---

## 1. Estrutura de Diretórios

```
src/
├── firmware/
│   ├── atmega4809/          # Firmware específico para a arquitetura megaAVR 0-series
│   │   ├── main.c           # Máquina de estados, trigger GPIO PA0, stack paint e telemetria
│   │   └── Makefile         # Build com avr-gcc 13, linker relaxation (-mrelax) e UPDI
│   ├── common/              # Interface KEM agnóstica e adaptadores de integração
│   │   ├── kem.h            # Interface universal (kem_keypair, kem_enc, kem_dec)
│   │   ├── kem_kyber512.c   # Adaptador Kyber-512 -> kem.h
│   │   ├── kem_ctru.c       # Adaptador CTRU-Light -> kem.h
│   │   └── kem_ecdh.c       # Adaptador ECDH (controle clássico) -> kem.h
│   └── pqc/                 # Fontes criptográficas nativas em C e Assembly AVR
│       ├── kyber512/        # ref (C de referência adaptado) e asm (Assembly otimizado)
│       ├── ctru-light/      # ref (C de referência) e asm (Assembly otimizado)
│       └── ecdh/            # micro-ecc (C de referência e rotinas em Assembly)
├── scripts/
│   ├── trigger.py           # Comunicação serial e decodificador sigrok do analisador lógico
│   └── vendor-pqc.sh        # Script auxiliar de importação dos fontes base
└── analysis/
    ├── run_experiment.py    # Orquestrador mestre do plano fatorial (DOE com pyDOE3)
    ├── prepare.py           # Ingestão dos dados brutos para bases tidy (results/processed/)
    ├── analise.qmd          # Caderno de programação literária em R (Quarto)
    └── R/tema.R             # Tema visual ggplot2 e exportação TikZ/PDF/PNG/Slides
```

---

## 2. As 12 Configurações Fatoriais Avaliadas

O projeto avalia as 12 combinações completas ($3 \text{ Algoritmos} \times 2 \text{ Implementações} \times 2 \text{ Otimizações}$):

| Algoritmo | Variante (`VARIANT`) | Otimização (`OPT`) | Características Técnicas |
| :--- | :---: | :---: | :--- |
| `kyber512` | `asm` | `-O3` / `-Os` | Aceleração vetorial NTT em Assembly nativo AVR; cabe em 13,9 KB Flash |
| `kyber512` | `ref` | `-O3` / `-Os` | C de referência portado e otimizado com IA para caber em 48 KB Flash |
| `ctru-light`| `asm` | `-O3` / `-Os` | Aceleração polinomial em Assembly; bimodal por rejeição (~61–72 ms) |
| `ctru-light`| `ref` | `-O3` / `-Os` | C de referência ajustado com `-mrelax` para não estourar a Flash |
| `ecdh` | `asm` | `-O3` / `-Os` | Curvas elípticas secp256r1 com Assembly AVR (`micro-ecc`); ~3,18s a 6,36s |
| `ecdh` | `ref` | `-O3` / `-Os` | Curvas elípticas em C puro (`micro-ecc`); ~6,98s a 13,96s |

---

## 3. Origem e Adaptações dos Algoritmos

* **Fontes Base:**
  * Kyber-512 e CTRU-Light (C e Assembly AVR): artefato CHES 2026 ([`whYBeKim/CTRU-Light-and-PQC-on-AVR`](https://github.com/whYBeKim/CTRU-Light-and-PQC-on-AVR), MIT).
  * ECDH: [micro-ecc](https://github.com/kmackay/micro-ecc).
* **Adaptações e Refatorações Realizadas com IA (Req. 5.3):**
  * **Adequação da Flash no Kyber-512 C de referência:** Originalmente demandava ~79 KB de Flash. Foi refatorado manualmente com assistência de IA (conversão de tabelas constantes para `PROGMEM`, unificação de buffers e compactação), atingindo **44,5 KB (com `-O3`)** e **34,5 KB (com `-Os`)**, viabilizando sua execução no ATmega4809.
  * **Linker Relaxation no CTRU-Light:** Ajuste no Makefile com `-mrelax` e `-mcall-prologues` para eliminar o estouro de 148 bytes no compilador GCC 13.2.
  * **Interface Unificada:** Implementação de adaptadores homogêneos sobre a interface [`kem.h`](file:///home/eduabdala/git/project-cspa-cmp223/src/firmware/common/kem.h).
  * **Entropia de Hardware:** Rotina baseada no ruído térmico da referência analógica (VREF 1,1V) do ADC0.
  * **Sincronização Lógica:** Geração determinística de trens de pulsos prévios de sincronização (`id_pulses`) para casamento 1:1 no analisador lógico.

---

## 4. Compilação e Gravação

Utilizando o ambiente hermético via `nix develop`:

```bash
# Compilar uma combinação específica (ex: Kyber-512 ASM -O3):
make -C src/firmware/atmega4809 ALG=kyber512 VARIANT=asm OPT=-O3 F_CPU=20000000UL

# Checar consumo de memória Flash e SRAM:
make -C src/firmware/atmega4809 ALG=kyber512 VARIANT=asm OPT=-O3 size

# Gravar na placa via UPDI:
make -C src/firmware/atmega4809 flash PORT=/dev/ttyACM0
```
