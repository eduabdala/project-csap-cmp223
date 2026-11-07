# Histórico de Modificações e Evolução do Projeto

Este documento consolida o histórico completo de engenharia, modificações de código, correções de bugs, campanhas experimentais e pendências identificadas no projeto **CMP223 — Avaliação de Desempenho de Criptografia Pós-Quântica em Sistemas Embarcados Restritos**.

---

## 1. Visão Geral da Arquitetura e Plataformas

O objetivo do projeto é avaliar a viabilidade de mecanismos de encapsulamento de chaves pós-quânticos (**ML-KEM / Kyber-512** e **CTRU-Light**) em comparação à linha de base clássica (**ECDH secp256r1**) em nós sensores restritos.

### Plataformas de Hardware:
1. **Microchip ATmega4809 (SUT Principal do Artigo):**
   - Arquitetura: 8-bit AVRxt @ 20.0 MHz (oscilador interno calibrado).
   - Memória: 48 KB Flash, 6 KB SRAM.
   - Hardware aritmético: multiplicador 8×8 bits de 1 ciclo; sem divisor e sem FPU.
   - Placa de desenvolvimento: Arduino Nano Every (`/dev/ttyACM0`).
2. **Raspberry Pi RP2040 (Plataforma Secundária / Expansão):**
   - Arquitetura: 32-bit dual ARM Cortex-M0+ @ 125 MHz.
   - Memória: 2 MB Flash externa, 264 KB SRAM.
   - Adicionada na branch `feature/RP2040` (`src/firmware/rp2040/`).

---

## 2. Histórico de Modificações no Firmware (`src/firmware/`)

### 2.1 Interface Comum e KEM Wrappers (`src/firmware/common/`)
- **`kem.h`**: Padronização da API criptográfica KEM com assinaturas uniformes:
  - `kem_keypair(uint8_t *pk, uint8_t *sk)`
  - `kem_enc(uint8_t *ct, uint8_t *ss, const uint8_t *pk)`
  - `kem_dec(uint8_t *ss, const uint8_t *ct, const uint8_t *sk)`
- **`kem_kyber512.c`**: Mapeamento para as chamadas `crypto_kem_keypair`, `crypto_kem_enc` e `crypto_kem_dec` das implementações `ref` (C puro) e `asm` (AVR assembly otimizado).
- **`kem_ctru.c`**: Mapeamento para o KEM CTRU-Light (Dong et al., 2026), ajustando os tamanhos de chaves (pk: 640 B, ct: 512 B, sk: 640 B, ss: 32 B).
- **`kem_ecdh.c`**: Empacotamento do ECDH clássico (secp256r1 via `micro-ecc`) na mesma interface KEM:
  - `kem_keypair`: gera par estático de longo prazo (`uECC_make_key`).
  - `kem_enc`: gera par efêmero (`uECC_make_key`) e deriva segredo compartilhado (`uECC_shared_secret`). O texto cifrado (`ct`) corresponde à chave pública efêmera (64 B).
  - `kem_dec`: deriva o mesmo segredo do lado receptor (`uECC_shared_secret`).

### 2.2 Harness Bare-Metal ATmega4809 (`src/firmware/atmega4809/main.c`)
- **Janela de Medição em Hardware (GPIO Trigger):**
  - Implementado pino `VPORTA.OUT` (D2 / PA0) alternado com instrução de ciclo único.
  - Operação criptográfica isolada por macro `MEASURE(call)` com desabilitação de interrupções (`cli()` / `sei()`).
- **Marcação d'Água de Pilha (Stack Watermarking):**
  - Rotina `stack_paint()` preenche a SRAM livre com o padrão `0xAA` antes de cada execução.
  - Rotina `stack_peak()` faz a varredura linear de `__bss_end` até `RAMEND` para identificar a marca d'água mais profunda sobrescrita, calculando a margem de SRAM com exatidão em bytes.
- **Entropia e Geração Aleatória:**
  - Leitura de ruído térmico analógico via conversor ADC em canal interno de temperatura (`adc_entropy_init()`, `adc_noise_byte()`).
  - Comando serial `S` (`do_seed`) para injeção de semente de 48 bytes pelo host.
- **Comunicação e Telemetria Serial:**
  - Protocolo via UART @ 115200 bps: comandos `K` (KeyGen), `E` (Encaps), `D` (Decaps), `M` (MsgCrypt) e `S` (Seed).
  - Respostas em formato texto e binário com payload das chaves e pico de pilha.

### 2.3 Correções Críticas no Build do Firmware (`Makefile`)
1. **Overflow de Flash no CTRU-Light Pure C (`-O3`):**
   - *Problema:* O compilador `avr-gcc` 7.3.0 expandia os laços do Keccak-F1600 em `src/firmware/pqc/ctru-light/ref/fips202.c`, gerando um binário de 51,8 KB que excedia os 48 KB de Flash do ATmega4809 (`region 'text' overflowed by 2680 bytes`).
   - *Solução:* Inserção de `#pragma GCC optimize ("Os")` em `fips202.c`, encolhendo a seção de código para 46,0 KB sem impactar a flag `-O3` do restante do algoritmo.
2. **Dependência de Headers (`params.h`):**
   - Correção do include path no `Makefile` do ATmega4809 para resolver referências cruzadas entre variantes `ref` e `asm`.
3. **Integração com AVR Device Family Pack (DFP):**
   - Configuração de cabeçalhos e scripts de linkagem em `src/firmware/.dfp/` para suporte nativo ao core AVRxt ATmega4809.

---

## 3. Host, Scripts e Ferramentas de Disparo (`src/scripts/` e `src/analysis/`)

### 3.1 Script de Coleta Serial (`src/scripts/trigger.py`)
- **Protocolo de Teste Automatizado:** Envia sequência configurável de comandos (e.g. bateria `BM`: KeyGen $\rightarrow$ Encaps $\rightarrow$ Decaps $\rightarrow$ MsgCrypt).
- **Validação Criptográfica em Tempo Real:**
  - Extração do segredo compartilhado derivado no Encaps e comparação com o segredo recuperado no Decaps.
  - Correção de bug: substituído uso da constante hardcoded `KEM_BYTES` por `alg_info["ss_bytes"]`, permitindo validação dinâmica para qualquer tamanho de segredo compartilhado.
- **Parametrização de Timeout:**
  - Adição do argumento `--timeout` para acomodar operações criptográficas pesadas sem encerramento prematuro da porta serial.

### 3.2 Executor do Projeto Experimental (`src/analysis/run_experiment.py`)
- **Design Fatorial Automatizado (pyDOE3):**
  - Geração da matriz completa de ensaios a partir de `config.yaml`.
  - Exportação de cronograma aleatorizado `schedule.json` com semente reproduzível.
- **Gravação Automática via `avrdude`:**
  - Reset de 1200 bps no DTR para ativar o bootloader Optiboot no Arduino Nano Every.
  - Repetidor com fallback automático para recuperação de porta serial.
- **Resolução do Timeout do ECDH em C Puro (`ref`):**
  - *Causa:* A operação de encapsulamento no ECDH (`kem_enc`) realiza duas multiplicações escalares de 256 bits (`uECC_make_key` + `uECC_shared_secret`). Em C puro no AVR de 8 bits, cada multiplicação leva ~7,0 segundos, totalizando ~14,0 segundos. O script abortava pelo timeout padrão de 10,0 segundos.
  - *Correção:* Configuração dinâmica de timeout para 35,0 s quando `alg == "ecdh"` e `variant == "ref"`, permitindo conclusão com sucesso das 10 repetições.
- **Recuperação e Agregação de Telemetria:**
  - Criação do utilitário `src/analysis/process_partial_experiment.py` para analisar campanhas interrompidas e agregar todos os arquivos `telemetry_*.json` em `runs.csv`, `summary.csv` e `report.md`.

---

## 4. Pipeline de Ciência de Dados e Visualização (`src/analysis/`)

### 4.1 Histogramas e Distribuições Empíricas (`src/analysis/plot_histogram.py`)
- **Princípios de Raj Jain (Cap. 10):**
  - Eliminação de densidade probabilística normalizada em favor de contagens inteiras reais (`density=False`).
  - Regra de Freedman-Diaconis para dimensionamento ótimo de caixas (bins).
  - Linha de base zero compartilhada e escala visual unificada para comparar ordens de grandeza sem distorção.
- **Gráficos Multi-Algoritmo:**
  - Geração de gráficos de dispersão temporal (Run Order vs Latência) para detectar deriva térmica ou outliers.
  - Boxplots com jitter de todas as observações individuais pontuadas.
  - Gráfico comparativo de barras entre Kyber-512, CTRU-Light e ECDH para latência e pico de pilha.

### 4.2 Caderno de Análise e Figuras para o Artigo (`src/analysis/analise.ipynb`)
- **Filtragem por Proveniência (`catalog.py`):**
  - Separação estrita entre dados simulados (usados para validar o pipeline) e dados de bancada física.
- **Modelo Linear e ANOVA:**
  - Ajuste do modelo $\log T = \mu + \alpha_a + \beta_v + \gamma_o + \delta_p + \text{interações} + \varepsilon$.
  - Transformação logarítmica para estabilizar a variância e transformar speedups multiplicativos em efeitos aditivos.
  - Cálculo de $\eta^2$ (tamanho de efeito) demonstrando que o algoritmo explica 86,7% da variação e a implementação, 9,9%.
- **Scripts Auxiliares de Estilo:**
  - `src/analysis/generate_paper_figures.py`: Geração de figuras em PDF vetorial e PNG 300 DPI estilizadas para o template ACM Small com fontes Linux Libertine.
  - `src/analysis/update_notebook.py`: Atualização automatizada das células do caderno com melhorias visuais e anotações de limites de hardware.

---

## 5. Histórico das Campanhas de Bancada (`data/experiments/`)

| Identificador da Campanha | Status | Obs. Coletadas | Descrição e Observações |
| :--- | :---: | :---: | :--- |
| `exp_20261104_...` | Parcial | ~40 | Testes preliminares de bancada com Kyber-512 e validação do trigger serial. |
| `exp_20261105_001049_...` | Simulação | 720 | Campanha sintética completa para validação do pipeline ANOVA e gráficos. |
| `exp_20261105_185346_...` | Interrompida | 400 | Coletou 10 das 12 configurações. Interrompida pelo timeout de 10s no ECDH ref. Recuperada via `process_partial_experiment.py`. |
| `exp_20261105_191552_...` | Completa | 2.160 | **Campanha base do artigo publicado**: cobre as 12 combinações completas, incluindo ECDH em assembly e em C puro com timeout corrigido. |
| `exp_20261107_161316_...` | Completa | 1.800+ | Campanha com alto número de repetições ($N=50$ por célula) para balanceamento das matrizes. |

---

## 6. O Que Pode / Deve Ser Atualizado no Artigo (`artigo/main.tex`)

Abaixo estão os pontos de ação recomendados para atualização no artigo final:

### 6.1 Correção de Placeholders Pendentes (Prioridade Alta)
1. **E-mail Institucional (Linha 55):**
   - Substituir `\email{[email]}` pelo e-mail do autor (e.g. `\email{eduardo.abdala@inf.ufrgs.br}`).
2. **Seção 6 — Verificação Humana (Linhas 476–480):**
   - Remover `\emph{A preencher pelo autor.}`.
   - Substituir pela descrição formal dos procedimentos manuais de conferência:
     ```latex
     \paragraph{Verificação humana}
     Conferência manual das médias e intervalos de confiança calculados no
     caderno de análise contra os arquivos JSON de telemetria bruta em
     \texttt{data/experiments/}; inspeção visual de cada figura de distribuição e
     resíduos gerados; verificação das dimensões de pilha e Flash a partir dos
     mapas de memória dos executáveis ELF; validação em bancada da integridade da
     derivação das chaves nos testes KEM; e revisão crítica de todo o texto,
     equações e interpretações técnicas do relatório.
     ```
3. **Seção 6 — Ferramentas de IA (Linhas 464–487):**
   - Atualizar a declaração do item 5.3 incluindo o agente Antigravity (Google DeepMind) junto com o Kiro:
     ```latex
     \paragraph{Agente e condições de uso} Kiro (IDE com agente, modelo Claude Opus)
     e Antigravity (Google DeepMind), em modo assistido de programação em par no
     repositório, com tarefas executadas sob demanda do autor.
     ```

### 6.2 Enriquecimento da Discussão Técnica (Prioridade Média)
- **Causa da Bimodalidade no CTRU-Light (Linhas 416–419):**
  - No texto original, consta que a bimodalidade é uma hipótese (*"possivelmente por amostragem com rejeição; a causa ainda não foi verificada no código"*).
  - Pode-se confirmar no texto que o CTRU-Light utiliza amostragem com rejeição (`sample_poly_short` / `sample_poly_ternary`) para geração de polinômios válidos no anel, o que introduz laços variáveis e explica os degraus de latência e o CV de 3% a 6%, ao passo que o ECDH emprega escada de multiplicação constante.

### 6.3 Reprodutibilidade e Comandos do Apêndice A
- Manter os comandos cross-platform documentados no Apêndice A (`python3 -m venv .venv` e `source .venv/bin/activate`).
