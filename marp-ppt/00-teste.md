---
marp: true
theme: layout-test
style: @import 'layout-test.css';
paginate: true
_paginate: false
footer: 'CMP223 — Análise de Desempenho | INF-UFRGS'
---

<!-- class: lead -->

# Avaliação Pós-Quântica
Análise de Custo de Memória em Sistemas Embarcados Restritos

**Eduardo Silva Abdala**  
Instituto de Informática — UFRGS

---

## O Desafio Computacional

A transição dos algoritmos criptográficos atuais para a criptografia Pós-Quântica (PQC) introduz um gargalo significativo em dispositivos de borda.

- **Foco Analítico:** Avaliação experimental dos algoritmos ML-KEM (Kyber).
- **Ambiente:** Nós de Internet das Coisas (IoT) operando *bare-metal*.
- **Métricas Chave:** Monitoramento contínuo de pico de **RAM** (Stack/Heap) e contagem de ciclos de CPU.

---

<!-- class: split -->

## Comparativo de Arquiteturas Alvo

<div class="col">

### ARM Cortex-M4
Plataforma dominante, otimizada para processamento de sinais digitais (DSP).
- **Clock:** 168 MHz
- **RAM Volátil:** 192 KB SRAM
- **Compilador:** `arm-none-eabi-gcc`

</div>
<div class="col">

### RISC-V 32-bit (RV32I)
Arquitetura livre (ISA), permitindo extensões vetoriais no futuro.
- **Clock:** 160 MHz
- **RAM Volátil:** 128 KB SRAM
- **Compilador:** `riscv64-unknown-elf-gcc`

</div>

---

<!-- class: cards -->

## Estágios Críticos do Algoritmo

<div class="card-container">
<div class="card">

### 1. KeyGen
A geração das chaves demanda alta entropia e utiliza vastos arrays temporários na memória.
</div>

<div class="card">

### 2. Encapsulate
O encapsulamento da chave simétrica apresenta carga computacional moderada e menor demanda de RAM.
</div>

<div class="card">

### 3. Decapsulate
A recuperação do segredo é o estágio mais oneroso, onde os **estouros de pilha (Stack Overflow)** são frequentes.
</div>
</div>

---

<!-- class: stat-highlight -->

## Impacto Direto na Memória RAM

<div class="big-number">

### + 244%
<p>Incremento de Stack</p>
</div>

<div>

A substituição direta de **RSA-2048** por **Kyber-512** na mesma arquitetura resulta em um consumo insustentável para a maioria dos nós sensores IoT tradicionais.

O pico de consumo medido durante o *Decapsulate* saltou de **3.6 KB** para mais de **12.4 KB** em nossas amostras preliminares.

</div>

---

## Tabela de Resultados Consolidados

<div class="col">

Resultados médios obtidos após execução de instrumentação experimental ($N = 100$ amostras).

<div>

<div class="col">

| Esquema Criptográfico | Arquitetura | Tempo (ms) | Peak Stack (KB) | Flash (KB) |
| :--- | :--- | :--- | :--- | :--- |
| **RSA-2048** (Baseline) | ARM Cortex-M4 | 45.2 | 3.6 | 14.2 |
| **ML-KEM-512** | ARM Cortex-M4 | **2.1** | **12.4** | 28.6 |
| **ML-KEM-768** | ARM Cortex-M4 | 3.8 | 16.1 | 36.1 |
| **ML-KEM-512** | RISC-V 32-bit | 2.9 | 15.8 | 31.0 |

<div>

---

<!-- class: lead -->

# Obrigado.
Sessão de Perguntas e Defesa da Proposta.

**Eduardo Silva Abdala**  
Mestrando no Instituto de Informática