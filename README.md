# Análise de Desempenho e Consumo de Criptografia Pós-Quântica em MCUs de 8 bits

Trabalho prático da disciplina **CMP223 — Análise de Desempenho de Sistemas Computacionais**  
**Programa de Pós-Graduação em Computação (PPGC) / Instituto de Informática (INF-UFRGS)**  
**Autor:** Eduardo Silva Abdala (2026)

---

## 1. Visão Geral do Projeto

Este projeto avalia a viabilidade computacional, o consumo de memória (SRAM e Flash) e o impacto sistêmico da **criptografia pós-quântica (PQC)** em sistemas embarcados ultrarrestritos baseados em microcontroladores de **8 bits**.

O estudo foca nos Mecanismos de Encapsulamento de Chaves (**KEMs**):
1. **Kyber-512 (ML-KEM):** Padrão oficial do NIST para criptografia pós-quântica em reticulados (*Module-LWE*).
2. **CTRU-Light:** Esquema pós-quântico leve (*Lightweight Cryptography*) baseado em CTRU/NTRU (CHES 2026).
3. **ECDH secp256r1 (Controle Clássico):** Troca de chaves assimétrica clássica em curvas elípticas de 256 bits (`micro-ecc`).

### Hipótese de Pesquisa
> *Contrariando a intuição convencional de que algoritmos pós-quânticos são lentos demais para núcleos de 8 bits, o PQC é significativamente mais rápido em tempo de CPU do que a criptografia clássica de curvas elípticas (ECDH). O gargalo real da transição pós-quântica em dispositivos restritos reside na pegada binária na memória Flash ROM e na margem de SRAM para tarefas concorrentes de nós IoT.*

---

## 2. Especificação Detalhada do Dispositivo Sob Teste (DUT)

O dispositivo avaliado é a placa de desenvolvimento **Arduino Nano Every** (baseada no microcontrolador **Microchip ATmega4809**):

### Arquitetura do Núcleo (Core)
* **Microcontrolador:** Microchip ATmega4809 (família megaAVR 0-series).
* **Arquitetura:** AVR de **8 bits**, **Single-core (1 único núcleo)**, arquitetura Harvard modificada com barramentos e espaços de endereçamento independentes para instruções e dados.
* **Conjunto de Registradores:** 32 registradores de uso geral de 8 bits de acesso direto em ciclo único (`r0` a `r31`), conectados diretamente à Unidade Lógica e Aritmética (ALU).
  * Três pares de registradores de 16 bits atuam como ponteiros de endereçamento indireto: `X` (`r27:r26`), `Y` (`r29:r28`) e `Z` (`r31:r30`), fundamentais para varredura de polinômios em memória.
* **Instruções e Rendimento:** 135 instruções RISC. A maioria esmagadora das instruções executa em exatamente **1 ciclo de clock** (rendimento de 1 MIPS por MHz $\rightarrow$ **20 MIPS** a 20 MHz).
* **Multiplicador de Hardware:** Multiplicador nativo de $8 \times 8$ bits em silício que calcula um produto de 16 bits com ou sem sinal em apenas **2 ciclos de clock** (`MUL`, `MULS`, `MULU`, `MULSU`), componente crítico para aceleração das transformadas NTT (*Number Theoretic Transform*).

### Mapeamento e Hierarquia de Memória
* **Memória Flash ROM (Programa):** **48 KB** ($49.152\text{ Bytes}$ mapeados em `0x0000` a `0xBFFF`). É o principal gargalo físico do dispositivo.
* **Memória SRAM (Dados):** **6.144 Bytes (6 KB)** mapeados linearmente de `0x2800` a `0x3FFF`. Utilizada para variáveis estáticas, heap e pilha (Stack).
* **Memória EEPROM:** 256 Bytes para armazenamento não volátil.

### Frequência de Clock e Fusíveis Físicos
* **Oscilador Interno Calibrado:** Operando a **20,0 MHz** ($\pm 1\%$ de precisão de fábrica).
* **Configuração de Fusíveis:** Gravados explicitamente via UPDI (`fuse2:w:0x02:m`) para fixar o oscilador principal em 20 MHz e desativar o divisor de clock interno (*prescaler* `MCLKCTRLB = 0`), garantindo estabilidade absoluta entre regravações sem drift térmico.

### Periféricos e Pinagem Utilizada
* **Janela Física de Medição (PA0 / Pino D2):** Porta rápida acionada via registradores de escrita atômica direta (`PORTA.OUTSET` e `PORTA.OUTCLR`), ligada ao canal do Analisador Lógico.
* **USART3 (PB4 TX / PB5 RX):** Porta serial assíncrona operando a 115.200 bps via roteamento alternativo (`PORTMUX.USARTROUTEA`), responsável pela telemetria e troca de vetores de teste.
* **ADC0 & VREF (1,1V):** Amostragem de ruído de conversão em tensão de referência interna como fonte de entropia de hardware (TRNG) para alimentar as sementes criptográficas.
* **Ponte USB / Programador Onboard:** Microcontrolador auxiliar ATSAMD11D14A (no Nano Every) ou PKOB nano (no Curiosity Nano) atuando como ponte USB-Serial CDC e programador UPDI (*Unified Program and Debug Interface*).

---

## 3. Especificação Completa do Analisador Lógico

Para expurgar o efeito do observador e eliminar a sobrecarga de transmissão serial da UART ($+21\text{ ms a }+30\text{ ms}$), utilizou-se instrumentação física externa de alta precisão:

* **Modelo:** Analisador Lógico Digital 8 Canais 24 MHz USB (baseado no controlador Cypress FX2LP / arquitetura compatível com Saleae Logic 8).
* **Canais de Entrada:** 8 canais lógicos independentes (D0 a D7). O canal **D0** foi conectado diretamente ao pino **PA0 (D2)** do microcontrolador.
* **Níveis Lógicos e Tensões Compatíveis:**
  * Tensões suportadas: 2,0V, 2,5V, 3,3V e 5,0V (compatível com níveis lógicos TTL e CMOS; 1,8V marginal).
  * Tensão máxima admissível: 5,25V (com diodos de proteção contra sobretensão).
* **Impedância e Isolação de Entrada:** $100\text{ k}\Omega$ em paralelo com $10\text{ pF}$, garantindo carregamento insignificante no circuito sob teste (DUT).
* **Taxas de Amostragem Suportadas:**
  * 24 MHz, 16 MHz, 12 MHz, 8 MHz, 4 MHz, 2 MHz, 1 MHz, 500 kHz, 250 kHz, 200 kHz, **100 kHz**, 50 kHz, 25 kHz.
  * **Taxa Operacional Configurada:** **100 kS/s (100 kHz)**, proporcionando uma resolução temporal de **$10\,\mu\text{s}$ ($200\text{ ciclos}$ de clock a 20 MHz)**, ideal para capturar janelas de execução de milissegundos a dezenas de segundos sem saturação do buffer de captura.
* **Aquisição e Processamento em Tempo Real:**
  * Captura gerenciada em ambiente Linux via driver de firmware aberto `fx2lafw` e suíte `sigrok` (`sigrok-cli`).
  * Processamento de transições de borda e largura de pulso automatizado via script Python (`src/scripts/trigger.py`).

---

## 4. Portabilidade dos Algoritmos e Histórico de Modificações com IA

Em conformidade estrita com as diretrizes metodológicas e a transparência no **Uso de Ferramentas de IA (Req. 5.3)**:

### Origem dos Códigos-Base
* Os códigos criptográficos de partida foram importados a partir do artefato do **CHES 2026** ([`whYBeKim/CTRU-Light-and-PQC-on-AVR`](https://github.com/whYBeKim/CTRU-Light-and-PQC-on-AVR), licença MIT), originalmente desenvolvidos e testados em ATmega4808/ATmega1284p, e da biblioteca de curvas elípticas [micro-ecc](https://github.com/kmackay/micro-ecc).

### Modificações e Adaptações de Engenharia (com Assistência de IA)
Diferente da declaração inicial de portagem passiva, **diversas partes dos códigos foram refatoradas e adaptadas manualmente com auxílio de IA** para viabilizar a compilação, o encaixe físico na Flash e a automação do experimento:

1. **Ajuste de Pegada Binária no Kyber-512 C de Referência:**
   * A implementação original de referência em C do Kyber-512 demandava quase 79 KB de Flash ROM, estourando o limite físico de 48 KB do ATmega4809.
   * Através de refatoração assistida por IA, tabelas de constantes e raízes da unidade foram convertidas para a memória de programa (`PROGMEM`), buffers intermediários foram unificados e laços desenrolados foram compactados. Com as diretivas de relaxamento do linker (`-mrelax -mcall-prologues`), o binário final foi reduzido para **44,5 KB (com `-O3`)** e **34,5 KB (com `-Os`)**, viabilizando sua execução no ATmega4809.
2. **Correção de Overflow no CTRU-Light C de Referência:**
   * Com o compilador GCC 13.2 em `-O3`, o `ctru-light ref` excedia a Flash de 48 KB por 148 bytes ($49.458\text{ B}$). Foram introduzidas flags de otimização de prólogo e relaxamento relativo no Makefile para comprimir o binário em $>1,5\text{ KB}$, trazendo-o para $47,0\text{ KB}$ ($97,9\%$).
3. **Padronização da Interface Unificada KEM ([`kem.h`](file:///home/eduabdala/git/project-cspa-cmp223/src/firmware/common/kem.h)):**
   * Criação de adaptadores em C puro para encapsular Kyber-512, CTRU-Light e ECDH sob a mesma assinatura de funções (`kem_keypair`, `kem_enc`, `kem_dec`), permitindo a compilação modular e automatizada.
4. **Instrumentação Atômica e Mitigação do Observador:**
   * Implementação da macro `MEASURE()` com mascaramento de interrupções (`cli()` / `sei()`) e acionamento síncrono do registrador GPIO no pino PA0.
   * Implementação do trem de pulsos de identificação (`id_pulses`) para identificação determinística no analisador lógico.
5. **Gerador de Entropia de Hardware:**
   * Substituição de fontes pseudoaleatórias inseguras ou estáticas por rotina de leitura analógica do ruído térmico no canal de referência interna (VREF) do ADC0.

---

## 5. Planejamento Experimental Fatorial Completo ($3 \times 2 \times 2 \times 3$)

Seguindo o padrão de **Raj Jain**, os 4 fatores avaliados foram:

$$\text{Design Fatorial Completo: } 3 \text{ Algoritmos} \times 2 \text{ Implementações} \times 2 \text{ Otimizações} \times 3 \text{ Fases Criptográficas}$$

* **Repetições:** $N=30$ execuções completas por célula experimental $\rightarrow$ **$1.440$ ensaios totais coletados em hardware real**.
* **Randomização:** Execução com semente pseudoaleatória fixa (`seed=42`) para expurgar efeitos de ordem e histerese térmica.

---

## 6. Resultados Consolidados em Hardware

Abaixo estão os resultados consolidados da campanha experimental completa ($N=30$ por célula):

### Tabela 1: Latência Pura de CPU no Analisador Lógico (GPIO PA0 @ 20 MHz)

| Algoritmo | Implementação | Otimização | KeyGen (ms) | Encaps (ms) | Decaps (ms) | Speedup Assembly |
| :--- | :---: | :---: | ---: | ---: | ---: | :---: |
| **CTRU-Light** | `asm` | `-O3` | **67,20** | **61,14** | **119,55** | $\mathbf{2,02\times}$ |
| **CTRU-Light** | `ref` | `-O3` | 167,88 | 109,40 | 241,06 | — |
| **Kyber-512** | `asm` | `-O3` | **239,43** | **314,73** | **287,27** | $\mathbf{1,89\times - 2,04\times}$ |
| **Kyber-512** | `ref` | `-O3` | 471,28 | 594,27 | 585,71 | — |
| **ECDH (Clássico)**| `asm` | `-O3` | **3.179,56** | **6.360,13** | **3.179,86** | $\mathbf{2,19\times}$ |
| **ECDH (Clássico)**| `ref` | `-O3` | 6.978,53 | 13.958,42 | 6.977,80 | — |

### Tabela 2: Custos de Memória SRAM e Flash ROM

| Algoritmo | Implementação | Otimização | Pico de Pilha (Bytes) | Margem SRAM Livre | Ocupação Flash (KB) | Margem Flash Livre |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Kyber-512** | `asm` | `-Os` | 909 B | **85,2%** | **13,9 KB** | **71,0%** |
| **Kyber-512** | `asm` | `-O3` | 946 B | **84,6%** | 22,7 KB | 52,8% |
| **Kyber-512** | `ref` | `-O3` | 899 B | **85,4%** | **44,5 KB** | **7,4%** |
| **CTRU-Light** | `asm` | `-Os` | 2.436 B | **60,4%** | **21,3 KB** | **55,6%** |
| **CTRU-Light** | `asm` | `-O3` | 2.464 B | **59,9%** | 27,4 KB | 43,0% |
| **CTRU-Light** | `ref` | `-O3` | 2.472 B | **59,8%** | **47,0 KB** | **2,1%** |
| **ECDH** | `asm` | `-Os` | 679 B | **89,0%** | **7,9 KB** | **83,6%** |
| **ECDH** | `asm` | `-O3` | 777 B | **87,3%** | 12,8 KB | 73,4% |
| **ECDH** | `ref` | `-O3` | 788 B | **87,2%** | 25,5 KB | 46,9% |

---

## 7. Principais Conclusões Científicas

1. **PQC é ordens de grandeza mais veloz que o ECDH clássico em 8 bits:** O Kyber-512 em Assembly conclui a encapsulação em **~314 ms**, sendo **$20\times$ mais rápido** que o ECDH em Assembly ($6.360\text{ ms}$) e **$44\times$ mais rápido** que o ECDH em C puro ($13.958\text{ ms}$).
2. **A Flash ROM é o gargalo limitante:** Enquanto a SRAM mantém folga segura ($>48\%$ livre no pior caso do CTRU e $>83\%$ livre no Kyber-512), a memória Flash exige obrigatoriamente a adoção de Assembly com otimização **`-Os`** para permitir a coexistência com aplicações IoT (como FreeRTOS, MQTT e sensores).
3. **Bimodalidade Algorítmica do CTRU-Light:** Identificou-se uma distribuição bimodal real em KeyGen e Encaps devida ao loop de amostragem por rejeição (retry de amostragem quando o polinômio não é invertível, adicionando $+13,1\text{ ms} = 262.000\text{ ciclos}$ discretos). Na decapsulação, o algoritmo é 100% determinístico e unimodal em 119,5 ms ($\sigma = 0,02\text{ ms}$).

---

## 8. Como Reproduzir o Ambiente e Executar

O projeto utiliza um ambiente hermético e declarativo via **Nix Flake**:

```bash
# 1. Entrar no ambiente com avr-gcc 13, avrdude, sigrok e python científico:
nix develop --extra-experimental-features "nix-command flakes"

# 2. Compilar manualmente um dos binários (exemplo: Kyber-512 ASM -O3):
make -C src/firmware/atmega4809 ALG=kyber512 VARIANT=asm OPT=-O3 F_CPU=20000000UL

# 3. Gravar na placa via UPDI:
make -C src/firmware/atmega4809 flash PORT=/dev/ttyACM0

# 4. Executar bateria de testes com captura no analisador lógico:
python3 src/scripts/trigger.py BM /dev/ttyACM0 -n 30 --la-out data/raw/la_trace.csv

# 5. Executar a campanha fatorial completa automatizada:
python3 src/analysis/run_experiment.py --mode bench --port /dev/ttyACM0 -n 30 --tag campanha_final

# 6. Gerar os slides da apresentação em PDF ou HTML:
npm run pdf
npm run html
```

---

## Estrutura de Diretórios

```
project-cspa-cmp223/
├── flake.nix                       # Ambiente hermético e reprodutível NixOS
├── package.json                    # Dependências de compilação Marp
├── README.md                       # Documentação mestre do projeto
├── src/
│   ├── firmware/
│   │   ├── atmega4809/             # Makefile e main.c (firmware de bancada)
│   │   ├── common/                 # Interface genérica kem.h e adaptadores
│   │   └── pqc/                    # Implementações de Kyber-512, CTRU e ECDH
│   ├── scripts/
│   │   ├── trigger.py              # Script serial + decodificador do Saleae Logic
│   │   └── vendor-pqc.sh           # Script de controle de fontes criptográficas
│   └── analysis/
│       ├── run_experiment.py       # Orquestrador fatorial automatizado (DOE)
│       ├── prepare.py              # Ingestão dos dados brutos para CSVs tidy
│       ├── analise.qmd             # Caderno de programação literária em R (Quarto)
│       └── R/tema.R                # Tema ggplot2 e exportação TikZ/PDF/PNG/Slides
├── slides/
│   ├── 02-parcial.md               # Deck Marp da Apresentação Parcial (11 slides)
│   └── figures/                    # Figuras em alta resolução dos slides
└── data/
    └── experiments/                # Dados brutos das campanhas (CSV, JSON, LOG)
```

---

## Licença e Agradecimentos

Código disponibilizado para fins acadêmicos no âmbito do PPGC/UFRGS. Agradecimentos aos desenvolvedores do artefato CHES 2026 e do projeto micro-ecc pelas implementações base.
