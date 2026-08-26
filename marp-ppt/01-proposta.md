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

---

## Objeto Computacional (DESC)

- **Objeto de Estudo:** Algoritmos de Criptografia Pós-Quântica (PQC) [ex: ML-KEM / ML-DSA].
- **Domínio de Aplicação:** Dispositivos e nós de IoT com restrições severas de hardware.
- **Problema:** A transição para PQC exige maior capacidade computacional e de memória em relação aos algoritmos clássicos.
- **Objetivo:** Avaliar a viabilidade e o custo de memória RAM/Flash ao executar PQC em microcontroladores embarcados.

---

## Métricas de Desempenho (METR)

- **Footprint de Memória RAM (Pico de Uso):**
  - Consumo de **Stack** e **Heap** nas etapas de operação.
- **Tempo de Execução / Ciclos de Clock:**
  - Latência computacional para realização das operações criptográficas.
- **Ocupação de Memória Flash (Código):**
  - Tamanho do binário gerado na ROM do dispositivo.

---

## Fatores de Comparação & Variáveis

- **Arquiteturas de Hardware:** [ex: ARM Cortex-M4 vs. RISC-V 32-bit vs. ESP32]
- **Níveis de Segurança NIST:** [ex: Nível 1 vs. Nível 3 vs. Nível 5]
- **Flags de Compilação:** [ex: `-O2` vs. `-Os`]

---

## Método de Análise e Justificativa (CHOI)

- **Método Selecionado:** Medição Direta em hardware real.
- **Justificativa:**
  - Captura precisa do comportamento de pilha e limitações físicas de memória em tempo de execução.
  - Elimina distorções de simuladores quanto a barramentos e latências de memória flash.
- **Ferramentas Previstas:** Instrumentação de código, contadores de ciclos internos e captura via interface serial/SWD.

---

<!-- class: lead -->

# Perguntas & Sugestões

**Eduardo Silva Abdala**  
*Instituto de Informática - UFRGS*