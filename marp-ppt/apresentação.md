---
marp: true
theme: inf-ufrgs
style: @import 'inf-ufrgs.css';
paginate: true
_paginate: false
footer: 'CMP223 - Análise de Desempenho de Sistemas Computacionais | INF-UFRGS'
---

<!-- class: lead -->

# Avaliação de Desempenho de Criptografia Pós-Quântica em Sistemas Embarcados
Subtítulo: Proposta de Análise de Memória e Custo Computacional em Arquiteturas Restritas

**Eduardo Silva Abdala**  
Orientador/Avaliador: Prof. [Nome do Professor]  
Porto Alegre, 2026

---

<!-- 
====================================================================
ETAPA 1: PROPOSTA DO TRABALHO FINAL (Proposta & Metodologia)
====================================================================
-->

## ETAPA 1: Definição do Objeto Computacional (DESC)

- **Objeto de Estudo:** Algoritmos de Criptografia Pós-Quântica (PQC) padronizados pelo NIST (ex: ML-KEM / ML-DSA).
- **Alvo:** Microcontroladores e sistemas embarcados com restrições severas de memória RAM e processamento.
- **Motivação:** Avaliar a viabilidade de implantação de PQC em nós de IoT e dispositivos embarcados frente aos algoritmos clássicos (RSA/ECC).

---

## ETAPA 1: Métricas de Desempenho (METR) & Fatores

### Métricas Selecionadas
1. **Footprint de Memória (RAM):** Pico de consumo de Heap e Stack durante keygen, encriptação e decriptação.
2. **Tempo de Execução:** Ciclos de clock por operação criptográfica.
3. **Ocupação de Código (Flash):** Tamanho do binário gerado.

### Fatores de Comparação
- **Arquiteturas de Hardware:** ARM Cortex-M4 vs. RISC-V 32-bit vs. ESP32.
- **Níveis de Segurança:** Algoritmos PQC de nível 1, 3 e 5 do NIST.

---

## ETAPA 1: Escolha do Método de Análise (CHOI)

- **Método Adotado:** **Medição Direta** (Análise Experimental em Hardware Real).
- **Justificativa:** 
  - Simulações de ciclo para arquiteturas embarcadas frequentemente ignoram sobretaxas de latência de barramento e gerenciamento real de memória.
  - A medição direta garante maior fidelidade para os perfis de consumo e limites físicos de RAM.
- **Ferramental Previsto:** Profilers baseados em SWD/JTAG, bancada de medição de corrente e amostragem de ponteiros de Stack/Heap.

---

<!-- 
====================================================================
ETAPA 2: PARCIAL (Progresso, Ambiente e Resultados Preliminares)
====================================================================
-->

## ETAPA 2: Ambiente Experimental & Reprodutibilidade (DESC / REPRO)

- **Hardware:**
  - Placa A: [ex: STM32F4 Discovery - ARM Cortex-M4]
  - Placa B: [ex: ESP32-WROOM / Board RISC-V]
- **Toolchain & Compiladores:** `arm-none-eabi-gcc` vs `riscv64-unknown-elf-gcc` (Flags: `-O2`, `-Os`).
- **Controle Experimental (BOAS/DOE):**
  - Scripts de automação via Makefile e Python para compilação contínua e coleta serial.
  - Armazenamento de logs brutos e cadernos de análise (Jupyter Notebooks).

---

## ETAPA 2: Resultados Preliminares (RESULTS)

### Comparativo Preliminar de Consumo de RAM (KB)

| Algoritmo | Arquitetura | KeyGen (RAM) | Encrypt/Sign (RAM) | Flash Occupancy |
| :--- | :--- | :--- | :--- | :--- |
| **Kyber-512** | ARM Cortex-M4 | *A definir* | *A definir* | *A definir* |
| **Kyber-512** | RISC-V 32b | *A definir* | *A definir* | *A definir* |
| **RSA-2048** (Base) | ARM Cortex-M4 | *A definir* | *A definir* | *A definir* |

> *Acompanhamento de tendências preliminares e identificação de gargalos de memória no estresse de pilha.*

---

## ETAPA 2: Dificuldades Encontradas & Soluções (DIFF)

- **Gargalo de Memória (Stack Overflow):**
  - *Problema:* Determinados esquemas PQC estouram a pilha padrão alocada no microcontrolador.
  - *Solução:* Reconfiguração da tabela de vetores/linker script e otimização de buffers estáticos.
- **Precisão de Medição de Ciclos:**
  - *Problema:* Interferência do overhead do sistema operacional de tempo real (FreeRTOS).
  - *Solução:* Execução bare-metal para isolamento completo dos testes do Kernel.

---

<!-- 
====================================================================
ETAPA 3: FINAL (Análise Completa, Modelos e Recomendações)
====================================================================
-->

## ETAPA 3: Análise Estatística e Resultados Finais (RESUL / STAT)

- **Tratamento dos Dados:**
  - Média, desvio padrão e intervalos de confiança (95%) para tempo de execução sobre $N = 1000$ iterações.
  - Testes de hipótese para comparação entre arquiteturas.

*(Gráficos de barras comparando pico de RAM e scatter plots de Tempo vs. RAM gerados via Python/DSBOX entrarão nesta seção)*

---

## ETAPA 3: Discussão Crítica e Limitações (DISC)

- **Interpretação dos Resultados:**
  - O overhead de memória RAM do PQC em relação à criptografia clássica inviabiliza o uso direto em microcontroladores com menos de $X$ KB de SRAM.
- **Limitações do Estudo:**
  - Não foram consideradas otimizações assembly específicas de hardware (ex: extensões vetoriais RISC-V).
  - Análise limitada a medições em temperatura ambiente e sem presença de ataques por canais laterais (SCA).

---

## ETAPA 3: Conclusões e Implicações Práticas (CONCL)

- **Recomendações de Desempenho:**
  - Para nós IoT com estritas restrições de RAM, o algoritmo $Y$ apresentou a melhor relação custo-benefício.
  - A escolha da flag de compilação `-Os` reduziu o consumo de memória em $Z\%$ com impacto aceitável em tempo de execução.
- **Trabalhos Futuros (Desdobramento do Mestrado):**
  - Implementação de co-processadores criptográficos ou aceleração em hardware.

---

<!-- class: lead -->

# Perguntas e Discussão

**Eduardo Silva Abdala**  
*Instituto de Informática - UFRGS*  
Análise de Desempenho em Sistemas Computacionais (CMP223)