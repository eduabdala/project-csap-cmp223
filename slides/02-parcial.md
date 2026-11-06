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
- **Linha de base clássica:** ECDH secp256r1 (micro-ecc), empacotado como KEM
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
| Algoritmo | Kyber-512, CTRU-Light, ECDH | coletado |
| Implementação | `ref`, `asm` | coletado |
| Otimização | `-O3`, `-Os` | coletado |
| Operação | KeyGen, Encaps, Decaps | coletado |
| Clock | 20, 10, 5 MHz | só 20 MHz |

- Matriz gerada por código (`design.py`, pyDOE3) a partir do `config.yaml`
- 2160 observações de KEM em bancada (10 campanhas), N de 10 a 185 por célula
- Última campanha (`_8196`): primeira com as **12 configurações**, 480 obs., 100% válidas

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

## Resultados: KEMs pós-quânticos (20 MHz)

| Algoritmo | Impl. | Otim. | KeyGen (ms) | Encaps (ms) | Decaps (ms) | Pilha (B) | Flash (KB) |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: |
| Kyber-512 | asm | -O3 | 261,8 ± 0,3 | 343,7 ± 0,2 | 317,0 ± 0,2 | 1.019 | 25,6 |
| Kyber-512 | asm | -Os | 274,1 ± 0,3 | 362,2 ± 0,4 | 334,1 ± 0,3 | 997 | 15,1 |
| Kyber-512 | ref | -O3 | 498,4 ± 0,5 | 629,1 ± 0,5 | 621,1 ± 0,5 | 976 | 46,1 |
| Kyber-512 | ref | -Os | 508,7 ± 0,6 | 642,0 ± 0,6 | 635,0 ± 0,6 | 939 | 35,6 |
| CTRU-Light | asm | -O3 | 91,2 ± 1,3 | 91,3 ± 1,1 | 151,1 ± 0,1 | 3.177 | 28,1 |
| CTRU-Light | asm | -Os | 93,6 ± 1,4 | 93,8 ± 1,2 | 156,7 ± 0,6 | 3.137 | 22,6 |
| CTRU-Light | ref | -O3 | 194,6 ± 1,9 | 139,9 ± 1,5 | 272,8 ± 0,1 | 3.049 | 46,0 |
| CTRU-Light | ref | -Os | 199,9 ± 2,0 | 145,2 ± 1,7 | 284,1 ± 0,1 | 3.009 | 40,0 |

Média ± IC 95% (t de Student). Flash total: 48 KB. SRAM total: 6 KB.

---

## Resultados: ECDH, a linha de base clássica

| Algoritmo | Impl. | Otim. | KeyGen (ms) | Encaps (ms) | Decaps (ms) | Pilha (B) | Flash (KB) |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: |
| ECDH | asm | -O3 | 3.273,2 ± 0,5 | 6.529,8 ± 1,0 | 3.280,2 ± 0,6 | 826 | 14,5 |
| ECDH | asm | -Os | 3.292,0 ± 0,5 | 6.566,3 ± 1,0 | 3.299,7 ± 0,6 | 698 | 9,4 |
| ECDH | ref | -O3 | 6.981,7 ± 1,1 | 13.947,3 ± 1,3 | 6.989,0 ± 1,2 | 893 | 37,8 |
| ECDH | ref | -Os | 7.440,6 ± 0,7 | 14.864,4 ± 1,6 | 7.448,1 ± 1,3 | 732 | 10,5 |

- **O ECDH é 10–23× mais lento que o Kyber-512 e 21–102× mais lento que o CTRU-Light**
- O Encaps do ECDH faz duas operações de curva (par efêmero + segredo), por isso é ~2× o KeyGen
- Em troca, usa menos pilha (≤ 0,9 KB) e menos Flash (9,4 KB em asm -Os)

---

## Resultados: latência por configuração

![w:900](../artigo/figures/latency.png)

Escala log · CTRU-Light < Kyber-512 ≪ ECDH sempre · `ref` ≈ 2× `asm` · `-Os` ≈ `-O3`

---

## Modelo linear: quem explica a latência? (MODEL / STAT)

`log T ~ algoritmo × implementação × otimização × operação` (ANOVA tipo II, R² > 0,999)

| Termo | η² (com ECDH) | η² (só PQC) |
| :--- | ---: | ---: |
| Algoritmo | 86,7% | 63,1% |
| Implementação | 9,9% | 28,8% |
| Algoritmo × Operação | 2,0% | |
| Operação | 1,2% | 3,9% |
| Otimização | < 0,1% | < 0,1% |

Comparações par a par (Welch sobre log T, todas com p < 0,05):
**asm** é 1,5–2,3× mais rápido · **-Os** é 0,6–7% mais lento · **CTRU-Light** é 2,1–4,5× mais rápido que o Kyber

---

## Trade-off memória × tempo

<div style="display:grid;grid-template-columns:1.25fr 1fr;gap:28px;align-items:center">
<div>

![w:580](../artigo/figures/tradeoff.png)

</div>
<div>

- **PQC custa memória, não tempo**
- SRAM livre: 86–90% (ECDH), 83–86% (Kyber), 48–62% (CTRU-Light)
- Kyber `ref -O3` ocupa 46 KB dos 48 KB de Flash
- **`asm` + `-Os` cai para 15 KB** (ECDH: 9,4 KB)

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
- **Por que o ECDH é tão lento?** Hipótese: multiplicador de 8×8 bits torna cara a aritmética de 256 bits. A verificar com perfilamento
- **Overhead serial** na latência: o `msgcrypt` (XOR simples) já leva ~38 ms, então os valores absolutos dos KEMs estão inflados
- Medir a latência pelo pulso GPIO no analisador lógico
- Instalar shunt + bateria e medir a energia por operação
- Coletar 10 e 5 MHz na bancada
- Balancear as células (N = 30, sobretudo ECDH e CTRU-Light `ref`) e aplicar a ordem aleatória

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
