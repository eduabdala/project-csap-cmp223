# Análise do projeto: lacunas, ameaças à validade e pendências

Revisão feita sobre o estado do repositório em 2026-11-06 (branch
`feature/RP2040`, após a campanha `exp_20261105_191552_bench_full_pqc_campaign_8196`).
Cada item diz o que foi verificado e onde. O que não foi verificado está
marcado como **hipótese**.

Prioridade: **A** muda conclusões ou invalida números publicados;
**B** afeta a nota ou a reprodutibilidade; **C** acabamento.

---

## 1. Ameaças à validade da medição

### 1.1 [A] A latência inclui atrasos do próprio firmware, diferentes por operação

Verificado em `src/firmware/atmega4809/main.c` e `src/scripts/trigger.py`.

O host mede `t_exec_ms` do envio do comando até o 1º byte de resposta. Entre
esses dois pontos, além da operação criptográfica, o firmware executa:

| Operação | `id_pulses(n)` (≈ 4n + 5 ms) | `rng_refill()` (512 conversões ADC) |
| :--- | ---: | :---: |
| KeyGen | ~9 ms | sim |
| Encaps | ~13 ms | sim |
| Decaps | ~17 ms | não |
| msgcrypt | ~21 ms | não |

Os pulsos usam `delay_ms_approx`, um laço calibrado só pelo `F_CPU` e
compilado com a flag de otimização de cada build. Isso explica por que o
`msgcrypt` (um XOR de 18 bytes) leva ~38 ms em -O3 e ~41 ms em -Os: a diferença
está no laço de atraso, não no XOR.

Consequências:
- Os valores absolutos estão inflados por um deslocamento de ~10 a 25 ms, que
  depende da operação.
- **As razões entre algoritmos ficam puxadas para 1.** O efeito é pequeno para
  o ECDH (segundos), mas relevante para o CTRU-Light (~91 ms). Exemplo
  aproximado para o Encaps asm -O3, descontando ~25 ms: 319/66 ≈ 4,8× em vez
  dos 3,8× publicados.
- O artigo e os slides afirmam que "as razões são mais confiáveis que os
  valores absolutos" e que o `msgcrypt` é "quase todo overhead de
  comunicação". As duas frases precisam de correção.

Correção:
1. Medir pelo pulso GPIO no analisador lógico (a janela `window_high/low`
   cobre só a chamada criptográfica). Essa é a medida certa.
2. Até lá: estimar o deslocamento por operação com um adaptador "nulo" (KEM
   que retorna imediatamente) e subtraí-lo, ou ao menos reportar os números
   como "tempo de serviço" e não "latência da operação".

### 1.2 [A] O gerador aleatório do firmware AVR é determinístico

Verificado por inspeção de código. Os valores das chaves geradas não foram
conferidos, porque não estão na telemetria.

`main.c` coleta entropia do ADC e da semente do host num pool
(`harness_rng_read`), mas **no ATmega4809 nada chama essa função**. Só o
`rp2040/glue.c` a usa. No AVR, cada biblioteca usa o próprio `randombytes`:

| Algoritmo | Fonte de aleatoriedade no AVR | Efeito |
| :--- | :--- | :--- |
| Kyber-512 | `randombytes_avr_randombytes`: preenche `0, 1, 2, …` | toda chamada recebe os **mesmos** bytes, então chaves e textos cifrados se repetem |
| CTRU-Light | `surf` com semente fixa, estado estático | sequência diferente a cada chamada, mas igual a cada reboot |
| ECDH | `default_RNG` congruencial, gerado por `vendor-pqc.sh` | idem |

Consequências:
- **Segurança:** o firmware não serve para uso real. Precisa constar no artigo.
- **Medição:** o Kyber sempre processa a mesma entrada. A variância medida
  (CV < 1%) pode subestimar a variação real com entradas aleatórias.
- **Bimodalidade do CTRU-Light** (ver 3.1): ele é o único com entrada que muda
  a cada chamada, o que é compatível com a variação observada só nele.
- O `trigger.py` envia a semente do host (`S`), mas no AVR ela não tem efeito.

Correção: ligar o `randombytes` das três bibliotecas ao `harness_rng_read`,
como já é feito no RP2040, e coletar de novo.

### 1.3 [A] A comparação com o ECDH depende da biblioteca escolhida

Verificado nos dados e na literatura.

O micro-ecc é portável, mas não é o estado da arte em AVR. Para Curve25519 em
AVR, [Düll et al. (2015)](https://eprint.iacr.org/2015/343) reportam
13.900.397 ciclos por segredo compartilhado, ou ~0,70 s a 20 MHz. O ECDH
medido aqui leva ~3,3 s no Decaps (asm -O3), ou seja, ~4,7× mais.

| Comparação (Decaps, asm -O3) | Medido aqui | Com ECDH estado da arte |
| :--- | ---: | ---: |
| ECDH | 3.280 ms | ~700 ms |
| ECDH / Kyber-512 (317 ms) | 10,3× | ~2,2× |
| ECDH / CTRU-Light (151 ms) | 21,7× | ~4,6× |

A conclusão qualitativa se mantém: os KEMs pós-quânticos continuam mais
rápidos. A magnitude, porém, cai de "uma ordem de grandeza" para 2 a 5 vezes.
O artigo deve citar essa referência e dizer explicitamente que a linha de
base é o micro-ecc.

Inconsistência relacionada: o `Makefile` compila o ECDH asm com
`uECC_OPTIMIZATION_LEVEL=2`, mas o `vendor-pqc.sh` recomenda 3. É preciso
escolher um valor e documentá-lo.

### 1.4 [B] Execução em blocos, não aleatorizada

Verificado em `run_experiment.py` e nos timestamps. Já está nas limitações do
artigo.

O `schedule.json` traz uma ordem aleatória, mas a bancada roda uma
configuração por vez (ciclo fixo K→E→D→M). Configuração e campanha ficam
confundidas com o tempo. A deriva medida é desprezível (1 de 30 séries com
tendência, −0,36 ms no total), o que atenua o problema, mas não substitui a
aleatorização.

Correção: sortear a ordem das configurações e, dentro de cada uma, a ordem
das operações. Incluir a campanha como fator (ou efeito aleatório) no modelo.

### 1.5 [B] Um único exemplar de placa, sem registro de temperatura

Toda a variabilidade medida é intra-placa. Não há estimativa de variação entre
unidades, e a temperatura não é registrada. Isso precisa constar nas
limitações. Se houver uma segunda placa, uma campanha curta nela basta para
mostrar a ordem de grandeza.

### 1.6 [C] Flash e pilha incluem o harness

A Flash vem do `.hex` inteiro (harness + UART + KEM) e o pico de pilha inclui
os quadros do `main`. As comparações entre algoritmos são válidas porque o
harness é o mesmo em todos, mas os valores absolutos não são "o custo do
KEM". Correção: compilar um firmware com adaptador nulo e reportar a
diferença.

### 1.7 [A] O firmware não é reprodutível a partir do repositório

Verificado em 2026-11-06, compilando no WSL (Ubuntu 24.04) com o DFP
`Microchip.ATmega_DFP.3.3.279`.

| Toolchain | Resultado |
| :--- | :--- |
| Ubuntu `gcc-avr` 7.3 + binutils 2.26 | Kyber-512 asm não linka: `.bss is not within region data` |
| Microchip AVR8 3.7.0 (gcc 7.3) | mesmo erro |
| avr-gcc 14.1.0 (binutils 2.42) | linka Kyber ref -O3, CTRU-Light asm -O3, ECDH asm e ref -O3; **falha** Kyber asm -O3 e -Os e CTRU-Light ref -O3 |

No Kyber asm, o `reduce.S` coloca 1.536 B de tabelas em `.data`, que somados
aos 5.120 B de `.bss` passam dos 6.144 B de SRAM. O `.hex` gravado na
campanha `_8196` não tem o laço de cópia de `.data` no startup. Ou seja, foi
compilado com um toolchain que deixou essas tabelas fora da SRAM, e esse
toolchain não está registrado em lugar nenhum.

Os binários também mudam de tamanho com o compilador:

| Configuração | `.hex` da campanha `_8196` | avr-gcc 14.1.0 |
| :--- | ---: | ---: |
| Kyber-512 ref -O3 | 47.200 B | 44.850 B |
| CTRU-Light asm -O3 | 28.794 B | 28.912 B |
| ECDH asm -O3 | 14.806 B | 13.826 B |
| ECDH ref -O3 | 38.752 B | 27.874 B |

Consequências:
- **A tabela de Flash do artigo vale só para o toolchain usado**, que não
  está documentado.
- Pela mesma razão, latência e pilha também podem mudar de um compilador para
  outro.
- Quem clonar o repositório hoje não consegue gerar os mesmos binários.

Correção: registrar a versão do `avr-gcc`, do binutils e do DFP em cada
experimento (junto do `git_commit`), fixá-las no `flake.nix` e citá-las no
artigo. Se o firmware for compilado com `nix develop .#firmware`, o
`flake.lock` já fixa a versão; falta só registrá-la.

**Bloqueio atual:** sem saber qual toolchain gerou os `.hex` da bancada, as
correções de firmware (1.2 e o adaptador nulo de 1.1 e 1.6) não podem ser
compiladas e validadas fora da máquina do autor. Para destravar, rodar no
ambiente onde o firmware é compilado:

```bash
nix develop .#firmware -c sh -c 'avr-gcc --version | head -1; avr-ld --version | head -1'
```

Se o build não usa o Nix, informar também de onde vem o DFP (`.dfp`).

Ambiente montado nesta verificação (local, fora do git):
- WSL Ubuntu 24.04: `gcc-avr`, `avr-libc` e `binutils-avr` via `apt`
  (reversível com `apt remove`).
- DFP `Microchip.ATmega_DFP.3.3.279` (sha256 `4fbb8a96…09ed`) em
  `src/firmware/atmega4809/.dfp/`, já ignorado pelo `.gitignore`.
- avr-gcc 14.1.0 (build ZakKemble, sha256 `4e9c6edf…b224`) em `/tmp` do WSL.
- Toolchain Microchip AVR8 3.7.0 (sha256 `a541771c…4096`) em `/tmp` do WSL.

---

## 2. Resultado ainda não explorado: custo de transmissão

Verificado nos dados (`t_total_ms − t_exec_ms`, médias em -O3, 115200 baud).

| Algoritmo | KeyGen: payload | Envio | Encaps: payload | Envio |
| :--- | ---: | ---: | ---: | ---: |
| Kyber-512 | 800 B | 73 ms | 800 B | 78 ms |
| CTRU-Light | 640 B | 68 ms | 528 B | 47 ms |
| ECDH | 64 B | 9 ms | 96 B | 12 ms |

800 bytes a 115200 baud levam ~69 ms, então os dados são coerentes. As
mensagens do PQC são 8 a 12 vezes maiores. Em rádios de baixa taxa (LoRa
SF12 transmite ~250 bit/s, ou ~26 s por 800 bytes), esse custo supera de longe
o de processamento. A frase "PQC custa memória, não tempo" fica mais precisa
como "PQC custa memória **e banda**, não processamento".

A fazer: gerar a tabela no caderno e incluí-la na discussão do artigo e no
slide de trade-off.

---

## 3. Pontos em aberto na análise

### 3.1 [B] Bimodalidade do CTRU-Light

Fatos verificados:
- A variação aparece só no KeyGen e no Encaps (CV de 3–6%, mediana acima da
  média, IQR de ~10 ms). O Decaps tem CV de 0,1%.
- O `crypto_kem_keypair` tem um laço de rejeição
  (`do { … } while (pke_keygen(...))`). Uma rejeição repetiria o KeyGen
  inteiro (~+90 ms), mas a diferença observada é de ~10 ms. Portanto **não é
  esse laço**.

**Hipótese:** amostragem com tempo dependente dos dados dentro de
`pke_keygen` e `pke_enc`, sensível à sequência aleatória que muda a cada
chamada (ver 1.2). A verificar no código e com a medição pelo analisador
lógico, separando os dois modos.

### 3.2 [B] Modelo estatístico

- As células são desbalanceadas (N de 10 a 185). O ECDH e o CTRU-Light `ref`
  têm uma ou duas campanhas.
- Os resíduos não são normais nas células bimodais. Com N grande o efeito é
  pequeno, mas um bootstrap dos ICs das razões fecharia a questão.
- O fator clock (10 e 5 MHz) é o que mais falta. Com ele dá para testar se a
  latência escala como 1/f, o que é uma boa pergunta para o critério MODEL.
  Os atrasos da seção 1.1 escalam com 1/f (laço calibrado por `F_CPU`), mas o
  overhead USB não; esse teste ajudaria a separar os dois.

---

## 4. Lacunas frente aos requisitos da disciplina

| Critério | Situação | Falta |
| :--- | :--- | :--- |
| Energia (métrica proposta) | integrador pronto e validado com sinal sintético | shunt, bateria, coleta |
| DOE | matriz gerada por código | aleatorização aplicada; fator clock |
| REPRO | catálogo, caderno, artigo gerado pelos dados | **firmware não recompila fora da máquina do autor** (1.7); `flake.nix` quebrado; fontes PQC sem versão fixa; experimentos sem `git_commit` nem versão do toolchain (ver `docs/release.md`) |
| LIT / DSBOX | caderno completo | — |
| STAT / MODEL | ICs, Welch, ANOVA | bootstrap; campanha no modelo; clock |
| FORM | template ACM 2.14 | conferir códigos CCS; e-mail |
| REV / RELAT | texto completo | introdução e fundamentação com `TODO(autor)` |
| Uso de IA (5.3) | seção no artigo e slide | **"verificação humana" ainda vazia**; este documento também entra na lista de partes com auxílio de IA |
| Etapa 3 | — | `slides/03-final.md` ainda é template |

---

## 5. Higiene do repositório

| Item | Onde | Ação |
| :--- | :--- | :--- |
| `texput.log` solto na raiz | raiz | apagar e ignorar `*.log` na raiz |
| README desatualizado (não cita o caderno nem o fluxo real; lista energia como medida) | `README.md` | reescrever junto com o release |
| Scripts antigos ou esqueleto (`experiment_zero.py`, `experiment_one.py`, `pipeline.py`, `process_partial_experiment.py`, `Snakefile`, `collect.py`, `aggregate.py`, `figures.py`) | `src/analysis/` | marcar como legado ou mover; ficam fora do release |
| `config.yaml` não é lido pelo `run_experiment.py` | `src/analysis/` | ligar os dois ou documentar a divergência |
| Sem testes | — | ao menos `parse.integrate_energy`, `catalog.classify` e `aggregate_experiment` |
| RP2040 presente, mas fora dos resultados | `src/firmware/rp2040/` | decidir: escopo futuro ou segunda plataforma |
| `.venv` com Python de 64 bits; o padrão da máquina é de 32 bits | ambiente | documentado em `requirements-notebook.txt` |

---

## 6. Correções a propagar no artigo e nos slides

Itens já publicados que estes achados tornam imprecisos:

1. "As razões entre configurações são mais confiáveis que os valores
   absolutos": falso para operações curtas (1.1).
2. "O `msgcrypt` é quase todo overhead de comunicação": é principalmente o
   atraso dos pulsos de identificação (1.1).
3. "PQC 10–23× (Kyber) e 21–102× (CTRU-Light) mais rápido que o ECDH": vale só
   para o micro-ecc. Acrescentar a comparação com o estado da arte (1.3).
4. Faltam nas limitações: RNG determinístico (1.2), placa única (1.5), Flash
   e pilha incluindo o harness (1.6) e a dependência do toolchain (1.7).
   Faltam na metodologia as versões do `avr-gcc`, do binutils e do DFP.
5. Falta na discussão: o custo de transmissão (2).

---

## 7. Ordem sugerida

**Bloqueado até o autor informar o toolchain (1.7):**

1. **Firmware**: ligar o RNG ao pool (1.2) e o adaptador nulo (1.1, 1.6).
   Fixar o `uECC_OPTIMIZATION_LEVEL` (1.3). Registrar a versão do toolchain.
2. **Bancada**: nova campanha com ordem aleatorizada (1.4), N = 30 balanceado,
   20/10/5 MHz. Se possível, medir pelo analisador lógico.

**Pode avançar já, sem firmware:**

3. **Caderno**: tabela de transmissão (2), bootstrap e campanha no modelo
   (3.2). A correção por adaptador nulo espera o item 1.
4. **Artigo e slides**: as correções da seção 6.
5. **Reprodutibilidade**: fixar os commits das fontes PQC no `vendor-pqc.sh`,
   gravar `git_commit` e a versão do toolchain em cada experimento, e as
   demais pendências de `docs/release.md`.

**Quando o shunt chegar:** a energia.

## 8. Registro de andamento

| Data | Item | O que foi feito |
| :--- | :--- | :--- |
| 2026-11-06 | — | Documento criado (seções 1 a 7). |
| 2026-11-06 | 1.7 | Lacuna encontrada ao tentar compilar as correções de firmware; três toolchains testados; bloqueio registrado. Nenhum item resolvido ainda. |
