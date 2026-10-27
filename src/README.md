# src — Código-fonte

Código do experimento: firmware para o SUT (Arduino Nano Every / ATmega4809),
ports dos algoritmos PQC e scripts de instrumentação, coleta e tratamento das
métricas.

## Organização

```
src/
├── firmware/            # código embarcado
│   ├── main.c           # harness de medição (máquina de estados)
│   ├── kem.h            # interface KEM independente de algoritmo
│   ├── kem_kyber512.c   # adaptador Kyber-512  -> kem.h
│   ├── kem_ctru.c       # adaptador CTRU-Light -> kem.h
│   ├── kem_ecdh.c       # adaptador ECDH (baseline) -> kem.h
│   ├── Makefile         # cross-compile AVR, parametrizado por ALG × VARIANT
│   └── pqc/<alg>/<var>/ # fontes vendorizadas: <alg> ∈ {kyber512,ctru-light,ecdh}
│                        #                       <var> ∈ {ref, asm}
├── scripts/
│   └── vendor-pqc.sh    # vendoriza os 3 algoritmos (ref + asm)
├── measure/             # captura osciloscópio / analisador lógico [a fazer]
└── analysis/            # Snakemake + Python (parser, estatística)
```

## Os 6 binários (3 algoritmos × 2 variantes)

Cada combinação é um binário distinto, **buildado, gravado e medido
separadamente**:

| ALG          | VARIANT=ref        | VARIANT=asm                 |
|--------------|--------------------|-----------------------------|
| `kyber512`   | C de referência    | Montgomery + assembly AVR   |
| `ctru-light` | C de referência    | Kred-ascon + assembly AVR   |
| `ecdh`       | micro-ecc C        | micro-ecc + assembly AVR    |

`ref` = portabilidade/baseline de implementação; `asm` = versão otimizada em
assembly (fator de primeira classe no experimento).

## Build

Pré-requisito: ambiente Nix (ver `flake.nix` na raiz).

```bash
nix develop                                   # devShell (avr-gcc, avrdude, snakemake...)

src/scripts/vendor-pqc.sh all                 # 1. vendoriza os 3 algoritmos (ref+asm)

# 2. compila uma combinação (ALG × VARIANT × OPT × F_CPU):
make -C src/firmware ALG=kyber512 VARIANT=asm OPT=-O3 F_CPU=20000000UL
make -C src/firmware ALG=kyber512 VARIANT=asm size      # uso de Flash/SRAM
make -C src/firmware ALG=ctru-light VARIANT=ref         # C de referência
make -C src/firmware flash PORT=/dev/ttyACM0            # grava via UPDI
```

## Fontes

- **Kyber-512 e CTRU-Light** (ref + **assembly AVR**): artefato CHES 2026
  [`whYBeKim/CTRU-Light-and-PQC-on-AVR`](https://github.com/whYBeKim/CTRU-Light-and-PQC-on-AVR)
  (MIT), benchmarkado em ATmega4808/1284p — muito próximo do nosso ATmega4809.
- **ECDH** (baseline clássico): [micro-ecc](https://github.com/kmackay/micro-ecc),
  com rotinas assembly AVR embutidas.

Nenhum algoritmo é reimplementado à mão. `vendor-pqc.sh` fixa os commits e grava
`VENDOR.txt` em cada pasta para reprodutibilidade.

> **Atenção (Flash):** o Kyber-512 em C-ref ocupa ~79 KB — não cabe nos 48 KB de
> Flash do ATmega4809. A variante asm (~22 KB) cabe. Confirme com `make size`
> logo após vendorizar.

## Métricas-alvo

- Consumo energético por operação (keygen, encap, decap)
- Uso de stack (watermarking 0xAA -> `RAMEND - endereço_mínimo`)
- Tempo de execução / ciclos (janela GPIO medida por analisador lógico)
- Tamanho dos binários gerados (`avr-size`)
- Margem operacional do sistema (headroom de Flash/SRAM)

Detalhes do SUT, métricas e plano em `../docs/plan.md` e `../docs/roadmap.md`.
