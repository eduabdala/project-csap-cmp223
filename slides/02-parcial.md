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
Relatório Parcial (Etapa 2)

**Eduardo Silva Abdala**
*Análise de Desempenho em Sistemas Computacionais (CMP223)*
Porto Alegre, 2026

---

## Pergunta e objeto de estudo

- **Pergunta:** qual o limite de aplicabilidade de KEMs pós-quânticos num MCU de 8 bits?
- **Objeto:** Kyber-512 (ML-KEM, FIPS 203) e CTRU-Light (KEM para nós sensores AVR, CHES 2026)
- **Operações medidas:** KeyGen, Encaps e Decaps
- **Métricas:** latência, pico de pilha, Flash ocupada e energia (pendente)
- **Método:** medição em bancada, com projeto fatorial e análise por modelo linear

---

## Ambiente de teste (DESC)

- **SUT:** Arduino Nano Every, ATmega4809 (AVRxt 8 bits, 48 KB Flash, 6 KB SRAM), 5 V, 20 MHz
- **Firmware:** bare-metal, `cli` na janela de medição, GPIO de 1 ciclo (`VPORTA.OUT`), telemetria UART fora da janela
- **Implementações:** C de referência e assembly AVR, do artefato público do CTRU-Light
- **Toolchain:** avr-gcc + avrdude (UPDI), ambiente fixado em `flake.nix`
- **Latência:** host, do envio do comando até o 1º byte de resposta
- **Pilha:** watermark `0xAA`. **Flash:** bytes de dados do `.hex`
- **Energia:** integrador `E = ∫ V·i dt` pronto, aguardando shunt de 1 Ω e bateria

---

## Projeto experimental (DOE)

| Fator | Níveis | Status |
| :--- | :--- | :--- |
| Algoritmo | Kyber-512, CTRU-Light, ECDH | ECDH sem dados de bancada |
| Implementação | `ref`, `asm` | coletado |
| Otimização | `-O3`, `-Os` | coletado |
| Operação | KeyGen, Encaps, Decaps | coletado |
| Clock | 20, 10, 5 MHz | só 20 MHz |

- Matriz gerada por código (`design.py`, pyDOE3) a partir do `config.yaml`
- 2000 observações de bancada, N de 10 a 165 por célula

---

## Boas práticas e reprodutibilidade (BOAS / REPRO)

- Uma pasta por experimento: binários, telemetria bruta, cronograma
- `catalog.py` classifica cada pasta **pela evidência**: só a telemetria gravada com a placa conta como bancada
- Dados simulados (do desenvolvimento do pipeline) ficam **fora** da análise
- **Ordem de execução:** planejada aleatória (`schedule.json`), mas **na bancada rodou em blocos**: uma configuração por vez, ciclo fixo K→E→D
- Verificado depois: sem deriva temporal relevante (Spearman, p < 0,01: só 1 de 30 séries com N ≥ 30 tem tendência, de −0,36 ms no total)

---

## Programação literal e ferramentas (LITERAL / DSBOX)

- Caderno `src/analysis/analise.ipynb`: do JSON bruto à tabela, figuras, comparações e ANOVA, com o texto de interpretação junto
- pandas · seaborn · statsmodels · scipy, com versões fixadas em `requirements-notebook.txt`
- Reexecução completa: `jupyter nbconvert --execute`
- O mesmo caderno gera as tabelas e figuras do artigo (template ACM)

---

## Resultados: latência, pilha e Flash (20 MHz)

| Algoritmo | Impl. | Otim. | KeyGen (ms) | Encaps (ms) | Decaps (ms) | Pilha (B) | Flash (KB) |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: |
| Kyber-512 | asm | -O3 | 261,7 ± 0,3 | 343,6 ± 0,2 | 317,0 ± 0,2 | 1.019 | 25,6 |
| Kyber-512 | asm | -Os | 274,1 ± 0,4 | 362,3 ± 0,5 | 334,2 ± 0,4 | 997 | 15,1 |
| Kyber-512 | ref | -O3 | 498,3 ± 0,5 | 629,0 ± 0,5 | 621,0 ± 0,5 | 976 | 46,1 |
| Kyber-512 | ref | -Os | 508,9 ± 0,8 | 642,2 ± 0,9 | 635,1 ± 0,8 | 939 | 35,6 |
| CTRU-Light | asm | -O3 | 91,0 ± 1,6 | 91,4 ± 1,4 | 151,1 ± 0,1 | 3.177 | 28,1 |
| CTRU-Light | asm | -Os | 93,4 ± 1,7 | 93,9 ± 1,5 | 156,5 ± 0,4 | 3.137 | 22,6 |
| CTRU-Light | ref | -O3 | 194,7 ± 3,7 | 140,0 ± 3,1 | 272,8 ± 0,2 | 3.049 | 46,0 |
| CTRU-Light | ref | -Os | 199,9 ± 4,1 | 145,3 ± 3,5 | 284,0 ± 0,2 | 3.009 | 40,0 |

Média ± IC 95% (t de Student). Flash total: 48 KB. SRAM total: 6 KB.

---

## Resultados: latência por configuração

![w:900](../artigo/figures/latency.png)

CTRU-Light < Kyber-512 sempre · `ref` ≈ 2× `asm` · `-Os` ≈ `-O3`

---

## Modelo linear: quem explica a latência? (MODEL / STAT)

`log T ~ algoritmo × implementação × otimização × operação` (ANOVA tipo II, R² > 0,99)

| Termo | η² |
| :--- | ---: |
| Algoritmo | 57,8% |
| Implementação | 34,0% |
| Operação | 4,5% |
| Algoritmo × Operação | 3,2% |
| Otimização | < 0,1% |

Comparações par a par (Welch sobre log T, todas com p < 0,05):
**asm** é 1,5–2,1× mais rápido · **-Os** é 2–5% mais lento · **CTRU-Light** é 2,1–4,5× mais rápido

---

## Trade-off memória × tempo

<div style="display:grid;grid-template-columns:1.25fr 1fr;gap:28px;align-items:center">
<div>

![w:560](../artigo/figures/tradeoff.png)

</div>
<div>

- O CTRU-Light troca memória por tempo: ~3× mais pilha
- SRAM livre: 48–62% (CTRU-Light) contra 84–86% (Kyber)
- Kyber `ref -O3` ocupa 46 KB dos 48 KB de Flash
- **`asm` + `-Os` cai para 15 KB**

</div>
</div>

---

## Dificuldades encontradas e soluções (DIFF)

1. **Shunt e bateria não chegaram.** Energia fica como `NA`. O integrador foi validado com sinal sintético
2. **Dados simulados misturados com os reais.** Proveniência gravada em cada observação e `catalog.py` para auditar
3. **Energia "estimada" com corrente constante** numa versão antiga do runner. Removida: nenhum valor não medido é reportado
4. **Ordem não aleatorizada na bancada.** Regravar a Flash a cada ensaio é caro. Plano: sortear a ordem das configurações e das operações dentro de cada uma
5. **Execuções interrompidas** (8 pastas vazias). Mantidas e catalogadas
6. **Clock errado (16 em vez de 20 MHz).** `fuse2` gravado junto com o firmware

---

## Pontos em aberto e próximos passos

- **Bimodalidade** no KeyGen/Encaps do CTRU-Light (CV de 3–6%): possivelmente amostragem com rejeição, a verificar
- **Overhead serial** na latência: o `msgcrypt` (XOR simples) já leva ~38 ms, então os valores absolutos estão inflados
- Medir a latência pelo pulso GPIO no analisador lógico
- Instalar shunt + bateria e medir a energia por operação
- Coletar 10 e 5 MHz e o ECDH na bancada
- Balancear as células (N = 30) e aplicar a ordem aleatória

---

## Uso de IA (Requisito 5.3)

- **Agente:** Kiro (Claude Opus), em modo autônomo no repositório, com tarefas pedidas uma a uma
- **Fluxo:** pedido → implementação pelo agente → revisão humana das alterações e reexecução → integração
- **Com auxílio de IA:** revisão do projeto, separação sim/bench, `catalog.py`, caderno de análise, formatação do artigo no template ACM, estes slides
- Detalhes na seção "Uso de ferramentas de IA" do artigo

---

<!-- class: lead -->

# Perguntas & Discussão

**Eduardo Silva Abdala**
*Instituto de Informática - UFRGS*
