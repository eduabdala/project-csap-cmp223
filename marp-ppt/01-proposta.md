---
marp: true
theme: inf-ufrgs
style: @import 'inf-ufrgs.css';
paginate: true
_paginate: false
footer: 'CMP223 - Proposta de Trabalho Final | INF-UFRGS'
---

<!-- class: lead -->

# Analise de Desempenho de algoritimos PQC em microcontroladores de 8bits
Subtítulo: Proposta do Trabalho Final (Etapa 1)

**Eduardo Silva Abdala**  
*Computer System Performance Analysis (CMP223)*  
Porto Alegre, 2026

![logo](logo_inf.png)

---

## Objeto Computacional (DESC)

- **Objeto de Estudo:** Implementações do algoritmo pós-quântico Kyber-512 (ML-KEM, padrão NIST) em comparação com alternativas leves (ex: CTRU-Light).
- **Ambiente de Restrição:** Microcontroladores da família megaAVR 0-series (ex: ATmega4808/ATmega4809), operando no limite restrito de 6 KB de SRAM.
- **Problema:** O padrão global PQC exige milhares de ciclos de clock, gerando dreno severo de bateria e sobrecarga de processamento em hardwares legados.
- **Objetivo:** Determinar o limite de aplicabilidade do Kyber-512, quantificando o custo energético absoluto e avaliando a margem operacional sistêmica (CPU/Memória livre) para as demais tarefas do sistema (sensoriamento, MQTT, RTOS).

---

## Métricas de Desempenho (METR)

- **Consumo Energético (Custo por Operação):**
  - Medição da degradação de bateria (energia em µJ/operação) nas etapas de KeyGen, Encaps e Decaps.
- **Margem Operacional Sistêmica (Headroom):**
  - Fração de tempo de CPU e quantidade de SRAM (bytes) que restam livres para o sistema base.
- **Tempo de Execução e Latência:**
  - Ciclos de clock (k-cycles) e latência real de parede (wall-clock).
- **Footprint de Memória:**
  - Pico de uso da pilha (Stack Peak) e tamanho do binário gerado na ROM (Code Size).

---

## Fatores de Comparação & Variáveis

- **Algoritmos (Padrão vs. Leve):** Kyber-512 (ML-KEM) vs. CTRU-Light.
- **Estratégias de Implementação:** Código de referência em C puro vs. Assembly otimizado (ex: multiplicação Montgomery).
- **Alocação de Memória:** Tabelas (LUTs) residentes em Flash (PROGMEM) vs. alocação em Stack/SRAM.

---

## Método de Análise e Justificativa (CHOI)

- **Método Selecionado:** Metodologia Híbrida (Simulação *Cycle-accurate* + Medição Física *Bare-metal*).
- **Justificativa:**
  - Simulação extrai a contagem exata de ciclos instrução por instrução, isolando o custo computacional puro sem intrusão (Efeito do Observador).
  - Medição física valida a latência real e possibilita a telemetria de energia, preenchendo lacunas de benchmarks puramente teóricos.
- **Ferramentas Previstas:** Instrumentação elétrica (resistor *shunt* / osciloscópio) para energia, *toggle* de pinos GPIO via analisador lógico para latência, e *Stack Watermarking* para pico de memória.

---

<!-- class: lead -->

# Perguntas & Sugestões

**Eduardo Silva Abdala**  
*Instituto de Informática - UFRGS*

![logo](logo_inf.png)