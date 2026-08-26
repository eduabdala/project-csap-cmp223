---
marp: true
theme: inf-ufrgs
style: @import 'inf-ufrgs.css';
paginate: true
_paginate: false
footer: 'CMP223 - Relatório Parcial | INF-UFRGS'
---

<!-- class: lead -->

# Avaliação de Desempenho de Criptografia Pós-Quântica em Sistemas Embarcados
Subtítulo: Relatório Parcial de Experimentos (Etapa 2)

**Eduardo Silva Abdala**  
*Análise de Desempenho em Sistemas Computacionais (CMP223)*  
Porto Alegre, 2026

---

## Ambiente Experimental (DESC / REPRO)

- **Plataformas de Teste:**
  - Placa A: [Preencher: modelo, clock, memória RAM/Flash]
  - Placa B: [Preencher: modelo, clock, memória RAM/Flash]
- **Toolchains & Compiladores:**
  - [Preencher: versão do compilador e flags utilizadas]
- **Automação & Reprodutibilidade (REPRO / DSBOX):**
  - Scripts em Python/Make para compilação e coleta automatizada de logs seriais.

---

## Projeto Experimental & Boas Práticas (DOE / BOAS)

- **Controle Experimental:**
  - Execução em ambiente isolado (*bare-metal*).
  - Amostragem com $N = [Preencher: número de repetições]$ iterações por cenário.
- **Programação Literal (LITERAL):**
  - Processamento e análise dos logs brutos via Jupyter Notebook (`pandas`/`seaborn`).

---

## Resultados Preliminares (RESULTS)

| Algoritmo | Arquitetura | Peak Stack (Bytes) | Peak Heap (Bytes) | Flash (Bytes) |
| :--- | :--- | :--- | :--- | :--- |
| **[Algoritmo 1]** | [Arquitetura A] | [Dados] | [Dados] | [Dados] |
| **[Algoritmo 1]** | [Arquitetura B] | [Dados] | [Dados] | [Dados] |
| **[Algoritmo 2]** | [Arquitetura A] | [Dados] | [Dados] | [Dados] |

> *[Inserir observação preliminar sobre as tendências observadas nos dados]*

---

## Dificuldades Encontradas & Soluções (DIFF)

1. **[Dificuldade 1 - ex: Stack Overflow]:**
   - *Problema:* [Descrever o problema observado]
   - *Solução:* [Descrever a solução aplicada]
2. **[Dificuldade 2 - ex: Ruído de Medição]:**
   - *Problema:* [Descrever o problema observado]
   - *Solução:* [Descrever a solução aplicada]

---

<!-- class: lead -->

# Perguntas & Discussão

**Eduardo Silva Abdala**  
*Instituto de Informática - UFRGS*