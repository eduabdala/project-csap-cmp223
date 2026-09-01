---
marp: true
theme: inf-ufrgs
style: @import 'inf-ufrgs-claro.css';
paginate: true
_paginate: false
footer: 'CMP223 - Proposta de Trabalho Final | INF-UFRGS'
---

<!-- class: lead -->

# Análise de Desempenho e Consumo Energético de Algoritmos PQC em Microcontroladores de 8 bits
Proposta do Trabalho Final

**Eduardo Silva Abdala**  
*Computer System Performance Analysis (CMP223)*  
Porto Alegre, 2026

![logo](logo_inf.png)

---

## Objeto Computacional

- **Objeto de Estudo:** Kyber-512 (ML-KEM, padrão NIST) vs. CTRU-Light (LWC), com ECDH clássico como linha de base de controle.
- **Ambiente de Restrição:** Microcontrolador ATmega4809 (6 KB de SRAM, 48 KB de Flash, 20Mhz).
- **Problema:** O padrão PQC opera com anéis polinomiais e hashing pesado (SHA-3/Keccak), exigindo milhares de k-ciclos e sobrecarregando a SRAM e a bateria.
- **Objetivo:** Determinar o limite de aplicabilidade do Kyber-512, quantificando o custo energético e avaliando a margem operacional (CPU e SRAM livres) para tarefas concorrentes (Sensoriamento, MQTT, RTOS).

---

## Métricas

- **Consumo Energético ($E_{\text{op}}$ em $\mu\text{J}$):**
  - *Registro:* Queda de tensão em resistor *shunt* via osciloscópio, com *trigger* em pino GPIO.
  - *Cálculo:* $E_{\text{op}} = \int_{t_0}^{t_1} V_{\text{cc}} \cdot \left(\frac{v_{\text{shunt}}(t)}{R_{\text{shunt}}}\right) dt$.
- **Tempo de Execução e Latência ($T_{\text{exec}}$ e $K_{\text{cycles}}$):**
  - *Registro:* Analisador lógico em pino de *toggle* GPIO ($T_{\text{exec}} = t_1 - t_0$).
  - *Cálculo:* $K_{\text{cycles}} = (T_{\text{exec}} \cdot f_{\text{cpu}}) / 1000$.

---

- **Footprint de Memória (Stack Peak e ROM):**
  - *Registro & Cálculo:* *Stack Watermarking* ($\text{RAMEND} - \text{Endereço Mínimo}$) e `avr-size`.
- **Margem Operacional Sistêmica (Headroom %):**
  - *Cálculo:* $\text{CPU}_{\text{livre}} = (1 - T_{\text{exec}}/T_{\text{ciclo}}) \times 100$ e $\text{SRAM}_{\text{livre}} = \text{SRAM}_{\text{total}} - (\text{Stack Peak} + \text{SRAM}_{\text{estática}})$.

---

## Fatores de Comparação e Variáveis

- **Algoritmos:** ECDH vs. CTRU-Light vs. Kyber-512.
- **Estratégias de Implementação:** Código de referência em C puro vs. Assembly otimizado.
- **Fase Criptográfica:** Geração de Chaves (KeyGen), Encapsulamento (Encaps) e Decapsulamento (Decaps).

---

## Método de Análise e Justificativa

- **Método Selecionado:** Medição.
- **Justificativa da Escolha:**
  - **Disponibilidade do Sistema:** O microcontrolador e o código existem fisicamente, tornando a medição a abordagem mais fidedigna.

---

- **Fidelidade:** Captura transições reais de corrente e o dreno de bateria.
- **Mitigação do Efeito do Observador:** Instrumentação puramente externa e passiva (*shunt*, osciloscópio, analisador lógico e *Stack Watermarking*).

---

## Diagrama da Metodologia e Pipeline

<div style="text-align: center;">

![pipeline](pipeline.png)

</div>

---

<!-- class: lead -->

# Perguntas & Sugestões

**Eduardo Silva Abdala**  
*Instituto de Informática - UFRGS*

![logo](logo_inf.png)
