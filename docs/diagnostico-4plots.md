# Diagnóstico dos 4-plots das baterias com analisador lógico

Análise dos gráficos de sequência, *lag* 1, histograma e probabilidade normal
gerados pela seção 3.1 do `analise.qmd`, por bateria e configuração, para as
baterias #17 (08/11, n = 30), #18 (12/11, n = 150, 9 configurações) e #19
(13/11, n = 150, 12 configurações). As figuras ficam em
`results/figures/diagnostico/4plot_<bateria>_<config>.png` (geradas pelo
caderno) e os testes em `results/processed/diag_4plot.csv`.

Além dos gráficos, alguns pontos foram conferidos nos dados brutos para separar
as causas. Os scripts estão em `delivery/results/.cache/`
(`ctru_pairs.py`, `resumo_graficos.py`, `entrada_vs_deriva.py`).

Cada achado está marcado como **confirmado** (verificado no código ou nos
dados) ou **hipótese** (compatível com os dados, ainda sem teste direto).

## Resumo

| # | Problema | Onde aparece | Tipo | Situação |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Analisador amostrado a 100 kHz (resolução de 10 µs), e não a 24 MHz | todos os gráficos | instrumento | confirmado |
| 2 | Semente fixa: CTRU-Light e ECDH repetem as mesmas chaves a cada reset | CTRU-Light, ECDH | desenho / firmware | confirmado, corrigido em `6374aca` |
| 3 | ECDH `asm` não valida em nenhuma execução | ECDH `asm` | implementação | confirmado, causa desconhecida |
| 4 | Deriva lenta durante o bloco (0,03% a 0,07%), causada pela variação do oscilador do MCU e não pela carga de trabalho | todos | fator não controlado | confirmado |
| 5 | Experimento não aleatorizado: o plano sorteado (`schedule.json`) não foi seguido, a ordem foi fixa e houve um bloco por configuração | todas as baterias | desenho | confirmado |
| 6 | Blocos de duração muito diferente (2 min a 72 min) | ECDH × reticulados | desenho | confirmado |
| 7 | Segundo modo do Kyber (+7 a +12 ms em 2% a 8% das rodadas) | Kyber | algoritmo | confirmado nos dados; mecanismo é hipótese |
| 8 | Dispersão do modo principal do Kyber depende da entrada | Kyber | algoritmo | confirmado |
| 9 | Dois modos do CTRU-Light com padrão periódico | CTRU-Light | consequência do #2 | confirmado |
| 10 | `cycles_la` não é contagem de ciclos | telemetria | registro | confirmado |
| 11 | Decaps sem validação registrada (3 a 4 de 330 por configuração) | Kyber, CTRU-Light | registro | confirmado; causa a investigar |

## Como ler cada gráfico

| Gráfico | Com o experimento sob controle | O que indica problema |
| :--- | :--- | :--- |
| Sequência | faixa horizontal, sem tendência, degraus ou padrão repetido | tendência ou ondulação (deriva), degraus (mudança de condição), padrão periódico (entrada determinística) |
| *Lag* 1 | nuvem redonda, sem direção | nuvem alongada na diagonal (autocorrelação), grupos fora da diagonal (mistura de modos), pontos em grade (quantização) |
| Histograma | um pico, forma contínua | vários picos (modos), barras isoladas (quantização), caudas |
| Probabilidade normal | pontos sobre a reta | degraus horizontais (quantização), saltos (modos), curvatura (assimetria) |

## Problemas que afetam todos os gráficos

### 1. Resolução de 10 µs: o analisador rodou a 100 kHz (confirmado)

**O que os gráficos mostram:**
- No *lag* plot, os pontos formam uma grade.
- No normal probability plot, os pontos sobem em degraus horizontais de 0,01 ms. Isso é mais visível no Decaps do CTRU-Light.
- No histograma, as barras caem em múltiplos de 0,01 ms.
- O MsgCrypt alterna só entre 0,02 e 0,03 ms.

**Causa.** Os CSVs das 5 campanhas com analisador lógico (#12 e #16 a #19) foram gravados com `samplerate_hz=100000`, que é o padrão de `--la-rate` no `trigger.py`. Mas o caderno e a legenda da bancada falam em "analisador lógico de 24 MHz". O aparelho suporta 24 MHz, mas não foi usado assim.

**Consequências:**
- **Valores repetidos.** No modo principal, há de 6 a 43 valores distintos em 150 execuções. Isso dá muitos empates, que distorcem o Shapiro-Wilk e os testes de postos.
- **MsgCrypt sem resolução.** A operação dura cerca de 2 amostras, então a latência medida é basicamente zero.
  - A fração de leituras de 0,03 ms é de cerca de 25% em todas as configurações `-Os` e perto de 0% nas `-O3`.
  - Isso indica que a duração real fica em torno de 22,5 µs no `-Os` e de 20 µs no `-O3`. Essa diferença só aparece através do arredondamento.
- **Arredondamento comparável à dispersão.** No Decaps do CTRU-Light, a faixa inteira é de 0,09 a 0,24 ms, ou seja, de 9 a 24 amostras. Um erro de ±1 amostra já pesa na dispersão.
- **Falha de instrumentação, não do algoritmo.** O texto do artigo e do caderno descreve uma resolução que a medição não teve.

**Possível erro de controle:** o instrumento não foi configurado para a resolução necessária. A taxa de 100 kHz provavelmente foi escolhida para limitar o tamanho dos CSVs (o ECDH `asm` gerou 53 MB por configuração).

### 4. Deriva lenta durante o bloco (confirmado; causa confirmada: oscilador do MCU, ver seção "Carga de trabalho e temporalidade")

**O que os gráficos mostram:**
- **ECDH:** a sequência ondula e tem tendência. Na #19, cai no `asm -O3` (ρ ≈ −0,45) e sobe no `ref -Os` (ρ ≈ +0,46). O *lag* plot mostra a nuvem alongada na diagonal (r1 de 0,26 a 0,55).
- **Decaps do CTRU-Light:** a sequência sobe e desce devagar, e o *lag* plot é diagonal (r1 de 0,44 a 0,65).
- **Modo principal do Kyber:**
  - **Visível nos gráficos:** no `-Os`, o Spearman fica em torno de ±0,5, com sinais opostos entre `asm` (+) e `ref` (−).
  - **Achado nos dados:** a autocorrelação do KeyGen entre rodadas seguidas é r1 de 0,45 a 0,67, embora cada rodada use uma semente nova.

**Evidência de que é deriva no tempo, e não efeito da entrada:**
- **Kyber.** Cada rodada recebe semente nova, então duas rodadas seguidas não compartilham entrada. Mesmo assim, há r1 de 0,45 a 0,67. Removendo uma mediana móvel de 15 rodadas, o r1 cai para 0,14 a 0,34. A componente lenta tem amplitude de 100 a 210 µs em blocos de 3 a 5 min, entre 0,04% e 0,07% da latência.
- **ECDH `asm -O3`.**
  - Nas baterias #18 e #19, as chaves são as mesmas pelo índice (semente fixa).
  - A tendência na #18 é nula (ρ = 0,04) e na #19 é forte (ρ = −0,45).
  - Como a entrada é a mesma, a tendência da #19 veio da condição da sessão.

**Causa (confirmada nos dados da #19): variação do oscilador interno do MCU.** O ATmega4809 roda no RC interno (OSC20M), e o analisador mede tempo real com o próprio cristal. Por isso, a variação do clock do MCU aparece como variação de latência. O teste e os números estão na seção "Carga de trabalho e temporalidade".

**Outras causas, avaliadas e descartadas:**
- **Aquecimento por carga de trabalho:** a deriva não acompanha o ciclo de trabalho nem a duração do bloco.
- **Instrumento:** o relógio do analisador é a referência; a deriva está no MCU.

**Ainda não determinado:** por que o oscilador varia, se por temperatura ambiente, tensão da USB ou ruído próprio do RC. Não houve medição de temperatura nem de tensão.

**Possíveis erros de controle:**
- **Fator não medido.** Temperatura, tensão e clock não foram registrados.
- **Sem aquecimento.** A primeira repetição de cada bloco é medida logo após a gravação e o reset.
- **Quebra de pressupostos.** A independência exigida pelo IC t e pela ANOVA não vale dentro do bloco.

### 5. O experimento não foi aleatorizado (confirmado)

**O que os gráficos mostram:**
- No 4-plot de desvios da seção 3.2, cada configuração ocupa uma faixa contínua do eixo de tempo.
- Nas três baterias, a ordem é a mesma e segue o laço do código: Kyber (`asm -O3`, `asm -Os`, `ref -O3`, `ref -Os`), depois CTRU-Light na mesma sequência e por fim ECDH. Na #19, isso foi das 05:10 às 09:12.
- No gráfico de efeito de bateria, as baterias quase coincidem. Mas, além da ordem igual, elas também repetem as entradas (item 2).

**O plano sorteado não foi seguido.** A versão do `run_experiment.py` usada nas baterias #17 a #19 (commit `0e67e73`, 12/11) sorteava as execuções individuais e gravava o resultado em `schedule.json`. O relatório da campanha também descrevia esse arquivo como "cronograma de execução aleatorizado".
- **Só o modo de simulação seguia o sorteio.** No modo bancada, o código percorria `for combo in combos` na ordem fixa da lista, e as execuções de cada configuração rodavam em sequência.
- **Exemplo na #19.**
  - **Plano sorteado:** começa por `kyber512 ref -Os`, `ecdh asm -Os` e `ctru-light asm -O3`.
  - **Execução real:** começou por `kyber512 asm -O3` e seguiu a ordem da lista.
- **Consequência para a reprodução.** O `schedule.json` dessas baterias documenta uma aleatorização que não aconteceu. Quem reproduzir o experimento a partir dele vai supor um desenho diferente do real.

**Por que a aleatorização completa não é possível aqui.** Trocar de configuração exige gravar outro firmware na Flash, e as 12 configurações não cabem juntas nos 48 KB. Então a configuração é um fator difícil de trocar. O desenho adequado é aleatorização restrita, em blocos (*split-plot*):
- **Parcela inteira:** cada bloco é uma gravação de firmware. A ordem dos blocos é sorteada, e cada configuração é dividida em vários blocos intercalados com os das outras.
- **Subparcela:** dentro do bloco, as repetições rodam em sequência. A ordem KeyGen → Encaps → Decaps → MsgCrypt é obrigatória, porque cada operação usa a saída da anterior.

O commit `df201ec` (13/11) implementou esse desenho com `--blocks`, mas com o padrão `--blocks 1` cada configuração ainda roda num bloco único. Só a ordem dos 12 blocos é sorteada.

**Consequências nos dados atuais:**
- **Efeito confundido com o horário.** O efeito de cada configuração fica confundido com o momento em que ela rodou. Com a deriva do item 4, não dá para separar os dois. Isso pesa nas comparações finas (`asm` × `ref`, `-O3` × `-Os`), cujas diferenças são da mesma ordem que a deriva.
- **Mesma posição em todas as baterias.** Como a ordem não muda, uma configuração ocupa sempre a mesma posição na sessão. Por exemplo, o ECDH `ref -Os` roda sempre no fim, depois de cerca de 3 h de placa ligada. Repetir a bateria não desfaz o confundimento.
- **Comparação entre baterias limitada.** Ela mede só a diferença entre sessões, já que a ordem e as entradas se repetem.
- **Replicação superestimada.** Com um bloco por configuração, a diferença entre duas configurações tem só uma réplica real: uma gravação de cada. A ANOVA da seção 8 usa as 150 repetições como resíduo. Essas repetições estimam a variação dentro do bloco, não entre blocos, então os p-valores e IC das comparações entre configurações ficam otimistas.

**Possíveis erros de controle:**
- o plano sorteado foi gravado, mas não executado;
- um bloco por configuração;
- a ordem é sempre a mesma;
- a análise trata as repetições como réplicas independentes da configuração.

**O que fazer:**
- **Ordem.** Rodar as próximas campanhas com `--blocks` maior que 1 (por exemplo, 5 blocos de 30 repetições) e uma `--seed` diferente por campanha.
- **Registro.** Conferir, no `schedule.json` gravado, que a ordem executada (`run_order`, `block_order`) é a mesma do plano.
- **Análise.** Usar um modelo misto, com o bloco como efeito aleatório aninhado na configuração (por exemplo, `lmer(logT ~ alg*var*opt*op + (1|bloco))`). Ou agregar por bloco antes de comparar configurações. Em ambos os casos, a réplica efetiva passa a ser o bloco.
- **Duração dos blocos.** Equilibrar a duração dos blocos entre algoritmos (item 6).
- **Dados antigos.** Corrigir a descrição das baterias #17 a #19 no caderno e no artigo: execução em ordem fixa, sem aleatorização.

### Carga de trabalho e temporalidade (bateria #19)

Script: `delivery/results/.cache/workload.py`, com saída em `workload_out.txt`.

**Carga por bloco.**
- **Ciclo de trabalho:** fração do tempo do bloco em que a janela de medição está ativa.
- **Serial:** fração gasta transferindo chaves e cifras pela UART.

| Configuração | Duração | Ciclo de trabalho | Serial | Intervalo ocioso entre operações | Pausa antes do bloco (gravação) |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Kyber-512 `asm` | 3,3 a 3,5 min | 63% a 64% | 11% a 12% | 51 ms | 21 s |
| Kyber-512 `ref` | 5,3 a 5,5 min | 77% a 78% | 7% | 51 a 52 ms | 41 a 48 s |
| CTRU-Light `asm` | 1,8 min | 35% | 16% a 17% | 51 a 52 ms | 25 a 34 s |
| CTRU-Light `ref` | 2,4 a 2,5 min | 53% a 54% | 11% | 51 ms | 42 a 48 s |
| ECDH `asm` | 33 min | 97% | 0,3% | 51 ms | 22 a 47 s |
| ECDH `ref` | 71 a 72 min | 99% | 0,1% | 51 ms | 66 a 93 s |

**Leitura da tabela:**
- **Intervalo fixo, intensidade variável.** O intervalo entre operações é o mesmo em todo lugar (cerca de 50 ms, o `--interval` do `trigger.py`). Por isso, a intensidade da carga depende do algoritmo: o ECDH deixa o MCU calculando 97% a 99% do tempo, por mais de 1 h, enquanto o CTRU-Light `asm` fica em 35%.
- **MCU nunca dorme.** Entre comandos, o firmware fica num laço de espera em `uart_rx`. Então a diferença entre "calculando" e "ocioso" é de tipo de instrução, não de CPU ligada ou parada. A potência do MCU muda pouco com o ciclo de trabalho.

**Teste do clock do MCU.** O trecho entre a primeira subida dos pulsos de ID e a subida da janela é gerado por `delay_ms_approx`, que tem um número fixo de ciclos por firmware.
- **Medida do clock:** a duração desse trecho no CSV do analisador mede o clock real do MCU em cada operação. Vale cerca de 15,3, 22,1 e 28,9 ms (K, E, D) no `-O3`, e 17,1, 24,7 e 32,3 ms no `-Os`.
- **Comparação:** comparei essa medida com a latência da operação seguinte, nas 10 configurações que têm CSV na #19, usando uma média móvel de 15 operações.

| Medida | Faixa observada |
| :--- | :--- |
| Amplitude da variação do clock dentro do bloco | 0,03% a 0,07% |
| Amplitude da variação da latência dentro do bloco | 0,02% a 0,06% |
| Correlação entre clock e latência (suavizados) | r = +0,42 a +0,98 (≥ 0,55 em 29 de 30 células) |
| Tendência da latência medida (Spearman) | ρ de −0,65 a +0,57 |
| Tendência depois de dividir a latência pelo clock medido | \|ρ\| ≤ 0,1 em 22 de 30 células; o maior é 0,22 |

**Conclusões:**
- **O oscilador explica a deriva.** O clock do MCU varia na mesma amplitude da latência e acompanha a latência ao longo do bloco. Corrigida pelo clock medido, a tendência praticamente some. Exemplos:
  - ECDH `asm -O3` Decaps: ρ = −0,45 cai para +0,08.
  - Kyber `ref -Os` Encaps: ρ = −0,65 cai para +0,08.
  - Kyber `asm -Os` Encaps: ρ = +0,57 cai para 0,00.
- **A carga de trabalho não causa a deriva.**
  - A amplitude é a mesma em blocos de 2 min a 35% de ciclo de trabalho (CTRU-Light) e em blocos de 33 min a 97% (ECDH): de 0,03% a 0,07%.
  - O clock médio de cada bloco difere no máximo ±0,02% entre os blocos da sessão. Não há tendência ao longo das 4 h e nenhuma relação com o ciclo de trabalho: o Kyber `asm -O3` (primeiro bloco, 63%) e o ECDH `asm -O3` (97%) ficam ambos em cerca de −0,02%.
  - A variação é rápida (escala de segundos a minutos), e não um aquecimento cumulativo.
- **Aquecimento no início do bloco.**
  - **Onde aparece:** nas 10 primeiras rodadas do CTRU-Light, a latência é de 0,01% a 0,04% maior que no resto do bloco (Mann-Whitney p < 0,05 em 10 de 12 células).
  - **Mesma causa:** o clock medido também está mais lento nessas rodadas, em 0,01% a 0,04%.
  - **Kyber:** o efeito é desprezível.
  - **ECDH:** aparece em poucas células, até 0,03% no Decaps do `ref -O3`. Essa configuração não tem CSV na #19, então o clock dela não pôde ser conferido.
  - **Origem provável:** o oscilador assentando depois da gravação e do reset. O bloco do CTRU-Light é curto, então essas rodadas pesam mais.
- **Comparações afetadas.** A amplitude da deriva (0,03% a 0,07%) é pequena perto das diferenças entre algoritmos. Mas é da mesma ordem das diferenças finas e da dispersão dentro do modo principal do Kyber e do CTRU-Light.

**Implicações para o protocolo:**
- **Corrigir pelo clock medido.** É possível sem nova coleta: basta dividir cada latência pela razão de clock medida no trecho de ID da mesma operação. Isso também dá ciclos reais, em vez do `cycles_la` nominal (item 10). Vale implementar no `prepare.py` para as campanhas com CSV.
- **Melhorar a referência na próxima campanha.** Emitir, fora da janela, um pulso de referência mais longo e de ciclos conhecidos (por exemplo, 10⁶ ciclos ≈ 50 ms). Junto com a amostragem a 1 MHz ou mais (item 1), isso dá precisão de 0,002% por operação.
- **Não é preciso reduzir a carga por causa da deriva.** Ainda assim, vale padronizar:
  - descartar algumas rodadas de aquecimento;
  - registrar a temperatura do sensor interno;
  - equilibrar a duração dos blocos (item 6).

### 6. Blocos de duração muito diferente (confirmado)

| Configuração (#19) | Duração do bloco |
| :--- | ---: |
| Kyber-512 | 3,3 a 5,5 min |
| CTRU-Light | 1,8 a 2,5 min |
| ECDH `asm` | 33 min |
| ECDH `ref` | 71 a 72 min |

O ECDH fica exposto a uma deriva de 15 a 40 vezes mais longa que os reticulados. Por isso, a sua variância dentro da célula não é comparável com a dos outros algoritmos.

## Kyber-512

Figuras: `4plot_19_kyber512_*.png` (e as das baterias #17 e #18).

**O que os gráficos mostram:**
1. **Picos isolados na sequência.** Em 2% a 8% das rodadas, a latência sobe de forma isolada, sem formar sequências longas.
2. **Picos nas mesmas rodadas.** Nas três operações, os picos caem nas mesmas repetições. Em 74 das 1.320 rodadas lentas, KeyGen, Encaps e Decaps ficaram lentos juntos, e isso nunca aconteceu em uma operação só.
3. **Tamanho do salto.** É de +6,9 ms no `asm` e de +11,9 ms no `ref`.
4. ***Lag* plot em blocos compactos.** O gráfico mostra três ou quatro aglomerados, sem nuvem visível, porque o eixo cobre os dois modos. A dispersão interna de cada modo (cerca de 0,3 a 0,5 ms) é menor que o próprio ponto.
5. **Histograma.** Mostra dois picos separados. O principal ocupa 2 ou 3 barras.
6. **Normal probability plot.** Uma reta quase plana mais um grupo isolado no alto. O Shapiro-Wilk dá p < 10⁻²³.
7. **Rodadas lentas mudam entre configurações.** As posições não se repetem de uma configuração para outra, porque o Kyber já usava a semente do host.

**Interpretação e possíveis erros:**
- **Segundo modo: do algoritmo, não da medição (mecanismo é hipótese).**
  - O KeyGen, o Encaps (que regenera Aᵀ a partir de ρ, presente na chave pública) e o Decaps (que reencripta) expandem a mesma matriz A a partir da mesma semente pública ρ.
  - A expansão usa amostragem por rejeição (`gen_matrix`/`rej_uniform`). Quando ρ exige um bloco extra de SHAKE-128, as três operações ficam mais lentas juntas.
  - O padrão por rodada confirma uma causa ligada à entrada. Ainda não verifiquei no código que se trata de um bloco extra de SHAKE.
  - **Não é outlier.** Excluir esses pontos enviesaria a média.
- **Dispersão do modo principal também vem da entrada (confirmado).** Na mesma rodada, KeyGen e Encaps se correlacionam com r = 0,64 a 0,86. Mesmo depois de remover a deriva, a correlação continua em r = 0,47 a 0,67. O número de candidatos rejeitados varia com ρ.
- **Média do Kyber mistura dois modos.** A proporção de rodadas lentas varia de 7 a 11 em 150 entre configurações da mesma bateria, e de 3 a 12 entre baterias. Assim, parte da diferença entre `asm` e `ref`, ou entre `-O3` e `-Os`, nas médias vem de uma mistura diferente de modos, e não da implementação. O IC da média deveria refletir essa mistura, que vem de uma binomial.
- **Deriva no modo principal.** Ver item 4.
- **Bateria #17 com n = 30.** A tendência forte na #17 (ρ ≈ −0,7) é puxada por 2 picos em 30 execuções, então o teste fica instável com n tão pequeno.

## CTRU-Light

Figuras: `4plot_19_ctru_light_*.png`.

**O que os gráficos mostram:**
1. **Dois modos no KeyGen e no Encaps.** A diferença entre eles é de cerca de 10 ms.
   - **KeyGen:** os dois modos aparecem em proporção quase igual (76 lentas de 150). No *lag* plot, os pares ocupam os quatro cantos.
   - **Encaps:** 37 lentas de 150. O canto lenta → lenta fica vazio (zero pares contra cerca de 79 esperados), e o r1 é de −0,33.
2. **Padrão periódico.** Os dois têm período 4: o KeyGen repete `LLRR` (lenta, lenta, rápida, rápida) e o Encaps repete `RRLR`. O padrão é idêntico em todas as configurações e nas três baterias: sempre 76 e 37 lentas em 150, ou 16 e 7 em 30.
3. **Acoplamento entre operações.** Na mesma rodada, se o KeyGen foi lento, o Encaps nunca é (672 de 672).
4. **Decaps.** Tem um modo só, com faixa de 0,09 a 0,24 ms. A sequência ondula, o *lag* plot é diagonal (r1 de 0,44 a 0,65), e o normal probability plot sobe em degraus de 0,01 ms.
5. **Correlação entre baterias.** O modo principal da mesma repetição se correlaciona entre #18 e #19 com r de 0,1 a 0,4.

**Interpretação e possíveis erros:**
- **Semente fixa (confirmado no código).** O CTRU-Light usava o `randombytes.c` do vendor, um gerador `surf` com semente constante. A cada gravação ou reset, a sequência de chaves recomeçava. Por isso:
  - **Sem amostragem real.** As 150 repetições são as mesmas 150 entradas em toda configuração e bateria. É pseudorreplicação: a variância dentro da célula não estima a variação entre chaves.
  - **Proporção de rejeição sem incerteza.** A fração de rejeição (cerca de 50% no KeyGen, 25% no Encaps) é a fração dessa lista fixa, não uma estimativa com incerteza.
  - **Padrões explicados.** O padrão periódico, o r1 negativo do Encaps e o acoplamento KeyGen × Encaps vêm da sequência fixa, não do hardware.
  - **Igualdade entre baterias inflada.** As baterias parecem iguais porque mediram as mesmas entradas.
  - **Correção.** O commit `6374aca` liga o CTRU-Light ao pool do harness e registra a semente.
- **Custo do gerador dentro da janela.** O `surf` do vendor rodava dentro da janela medida a cada 64 bytes consumidos. Então parte da latência e da variação vinha do gerador de teste, e não do algoritmo. Com a correção, os tempos do KeyGen e do Encaps vão mudar e não serão comparáveis com as campanhas anteriores.
- **Decaps: três fontes somadas.** A dispersão de 0,1 a 0,2 ms soma três componentes:
  - **Entrada:** a correlação entre baterias (r de 0,2 a 0,4) mostra uma parte que se repete.
  - **Deriva:** a ondulação e o r1 positivo (item 4).
  - **Quantização:** de 9 a 24 amostras de 10 µs (item 1).

  Com os dados atuais não dá para separar as três.

## ECDH (micro-ecc, secp256r1)

Figuras: `4plot_19_ecdh_*.png`.

**O que os gráficos mostram:**
1. **Variação contínua.** Diferente dos reticulados, há de 50 a 110 valores distintos e faixa de 3 a 10 ms (cerca de 0,1%). O histograma tem uma forma aproximadamente normal, e o Shapiro-Wilk não rejeita nas células revisadas (p de 0,17 a 0,82).
2. **Sequência com tendência ou ondulação.** O *lag* plot tem a nuvem alongada na diagonal (r1 de 0,26 a 0,55, item 4).
3. **Correlação entre baterias.** O mesmo índice se correlaciona entre #18 e #19 com r de 0,47 a 0,61, porque as chaves são as mesmas.
4. **MsgCrypt.** Alterna entre 0,02 e 0,03 ms, como nos outros algoritmos (item 1).

**Interpretação e possíveis erros:**
- **ECDH `asm` nunca valida (confirmado).** Nas baterias #17 a #19, nenhum dos 510 Decaps do `asm` (330 do `-O3` e 180 do `-Os`) reproduz o segredo do Encaps, e nenhum MsgCrypt decifra. O `ref` valida em 180 de 180 (#17 e #19; a #18 não tem ECDH `ref`).
  - **Tempos inválidos.** Os tempos do `asm` são de um cálculo que não produz o segredo correto. Não servem para comparar `asm` com `ref` nem ECDH com os reticulados.
  - **Causa desconhecida.** Revisei o assembly do micro-ecc para AVR (`asm_avr.inc`, nível 2) e não achei a causa. Uma diferença notável: o AVR compila com `uECC_OPTIMIZATION_LEVEL=2`, enquanto o RP2040 e o script de vendor usam 3.
  - **Diagnóstico na próxima coleta.** O commit `6374aca` registra o código de retorno (`kem_rc`) e confere cada operação contra um P-256 calculado no host (`ecdh_host_check`). Isso aponta qual operação diverge.
- **Semente fixa (confirmado no código).** O ECDH usava o `default_RNG` de `platform-specific.inc`, um gerador congruencial linear com estado inicial fixo, então as chaves se repetiam a cada reset. Isso explica a correlação de 0,47 a 0,61 entre baterias. Também significa que a latência do micro-ecc depende da chave em até cerca de 0,1%.
  - Corrigido em `6374aca`.
- **Blocos longos e deriva.** Ver itens 4 e 6.
- **CSVs do analisador ausentes no ECDH `ref` da #19.** Há 10 CSVs para 12 configurações. O `t_la_ms` existe na telemetria, mas a forma de onda bruta das duas configurações `ref` não foi guardada, então não dá para reprocessar essas configurações.

## Problemas de registro

### 10. `cycles_la` não conta ciclos (confirmado)

O `trigger.py` calcula `cycles_la = largura × 20.000`. É só a latência multiplicada pelo clock nominal, não uma contagem de ciclos. Se o oscilador desvia do valor nominal (item 4), esse valor desvia junto. O texto que trata `cycles_la` como "ciclos exatos" precisa ser corrigido, ou o clock real precisa ser medido (pulsos de ID).

### 11. Decaps sem validação registrada (confirmado; causa a investigar)

No Kyber e no CTRU-Light, de 3 a 4 Decaps por configuração, entre 330 nas baterias #17 a #19, têm `kem_validated` vazio, nem `True` nem `False`. Isso acontece quando o `trigger.py` não tem o segredo do Encaps na sessão ou recebe um payload incompleto. Ainda não identifiquei em quais rodadas.

## Confundimento no fator "variante" do CTRU-Light (confirmado)

As duas variantes do CTRU-Light vêm de pastas diferentes do artefato CHES:

| Variante | Pasta do artefato CHES | Função de hash |
| :--- | :--- | :--- |
| `ref` | `avrC-sha3` | SHA-3/SHAKE (`fips202.c`) |
| `asm` | `avrASM-kred-ascon` | Ascon (`ascon-hash/`) |

A diferença entre `asm` e `ref` do CTRU-Light mistura, portanto, a linguagem (assembly × C) com a primitiva de hash. A razão `ref`/`asm` não mede só o ganho do assembly. O Kyber `ref` (plugin `hybrid-kem-mqtt`) e o Kyber `asm` (`avrASM-montgomery-opt-stack`) também vêm de pastas diferentes. A paridade dessas duas versões ainda não foi conferida. O texto do artigo precisa descrever o fator variante como "implementação do artefato", e não como "C × assembly".

## Informações a coletar para controlar o experimento

Hoje a telemetria registra latência, pilha, validação e, desde o commit `6374aca`, a semente e o código de retorno. Falta registrar:

| Nível | Informação | Para quê | Como |
| :--- | :--- | :--- | :--- |
| Operação | Clock real do MCU | Corrigir a deriva (item 4) e obter ciclos reais | Pulso de referência de ciclos conhecidos (por exemplo, 10⁶) fora da janela; hoje dá para usar o trecho dos pulsos de ID (`la_clock.csv`) |
| Operação | Temperatura do chip | Explicar a deriva do oscilador | Sensor interno (`ADC_MUXPOS_TEMPSENSE`, já usado na entropia) com a calibração `SIGROW.TEMPSENSE0/1`, lido fora da janela e enviado na telemetria |
| Operação | Início e fim no host, e intervalo antes da operação | Carga de trabalho e efeito de arrasto | Já existe `timestamp` (fim); falta o início |
| Operação | Rodada de aquecimento (sim/não) | Separar as rodadas descartadas | Opção `--warmup N` no `run_experiment.py` |
| Bloco | Hash do firmware, commit do git, versão do `avr-gcc`, flags de compilação | Reprodução; hoje o `builds.csv` tem só tamanho e otimização | Gravar no `builds.csv` e no `schedule.json` |
| Bloco | Número de série da placa (`SIGROW.SERNUM0..9`) e contador de gravações | Separar placas e acompanhar o desgaste da Flash | Resposta do comando `P`; registro em `data/flash_ledger.csv` |
| Bloco | Ordem executada e tempo desde a gravação | Conferir a aleatorização e o aquecimento | Comparar `run_order` e `block_order` com o plano a cada campanha (seção 3.3 do caderno) |
| Bloco | Taxa de amostragem do analisador e se o CSV bruto foi guardado | Resolução e possibilidade de reprocessar (faltam CSVs do ECDH `ref` na #19) | Gravar `--la-rate` no `schedule.json`; falhar se o CSV não for salvo |
| Sessão | Temperatura e umidade ambiente | Fator externo da deriva | Sensor externo simples (por exemplo, DS18B20 ou termômetro USB) registrado pelo host a cada bloco |
| Sessão | Tensão de alimentação | O oscilador e a energia dependem dela | Medidor USB em linha, ou divisor resistivo num pino analógico |
| Sessão | Porta e hub USB, máquina host, cabos | Ruído e atraso serial (não afeta a janela, mas afeta a coleta) | Anotar no relatório da campanha |
| Sessão | Corrente no shunt | Energia, métrica prevista no projeto | Pendente desde a etapa parcial |

## Fatores que podem ser variados na execução

| Fator | Níveis possíveis | Situação no projeto | Cuidados |
| :--- | :--- | :--- | :--- |
| Frequência do clock | Do oscilador de 20 MHz com divisor (`CLKCTRL.MCLKCTRLB`): 20; 10 (÷2); 5 (÷4); 3,33 (÷6); 2,5 (÷8); 2 (÷10); 1,67 (÷12); 1,25 (÷16) MHz. Com o fuse `OSCCFG` em 16 MHz: 16, 8, 4, 2,67, 2 MHz... | `main.c` aceita 20, 10 e 5 MHz; o `run_experiment.py` tem `--clocks` | 15 MHz não é possível com o oscilador interno (não há divisor 4/3); exigiria clock externo no pino `EXTCLK`, que no ATmega4809 é o `PA0`, o mesmo pino da janela de medição. Para 16 MHz, o `make flash` precisa parar de gravar `fuse2=0x02`. O `UART` precisa do baud recalculado (o `uart_init` já faz). |
| Tensão de alimentação | 1,8 a 5,5 V, limitada pela frequência: até 5 MHz a partir de 1,8 V, até 10 MHz a partir de 2,7 V, até 20 MHz a partir de 4,5 V | Hoje 5 V pela USB | Exige fonte externa no lugar da USB; frequência e tensão precisam ser combinadas dentro desses limites. Relevante para energia. |
| Otimização do compilador | `-O0`, `-O1`, `-O2`, `-O3`, `-Os`, `-Oz` (GCC ≥ 12), `-Og` | `-O3` e `-Os`; `-O0` numa campanha à parte | `-O0` não compila em várias configurações (Flash e registrador Y) |
| Flags de compilação | `-flto`, `-mcall-prologues` ligado ou desligado, `-mrelax` | Fixas no Makefile | Mudam tamanho e tempo; hoje não são registradas |
| Versão do compilador | `avr-gcc` 7.3 (Ubuntu), 13.2 (Nix) | 13.2 nas campanhas | Precisa ser registrada (`builds.csv`) |
| Implementação | Kyber `asm`: variantes `montgomery-stack`, `montgomery-opt-stack`, `LUT-stack` do artefato CHES; ECDH: `uECC_OPTIMIZATION_LEVEL` de 0 a 4 e `uECC_SQUARE_FUNC` | Uma variante por algoritmo; ECDH `asm` em nível 2 | Ver o confundimento do CTRU-Light (hash) acima |
| Entrada | Sementes aleatórias por operação; sementes pareadas entre configurações | Aleatórias por operação desde `6374aca` | O pareamento exige `--seed-file` (não existe) |
| Tamanho da mensagem do MsgCrypt | 1 a 64 bytes (`--msg`) | 18 bytes, cerca de 20 µs, abaixo da resolução | Para medir o MsgCrypt, usar 64 bytes e amostragem a 1 MHz ou mais |
| Intervalo entre operações | `--interval` do `trigger.py` | 50 ms fixo | Variar permite testar o efeito de arrasto |
| Aquecimento | N rodadas descartadas por bloco | Nenhuma | Proposto: `--warmup` |
| Blocos e repetições | `--blocks`, `-n` | 1 bloco, n = 150 nas últimas baterias | Mais blocos dão mais réplicas reais; ver o desgaste da Flash (cerca de 120 gravações registradas de 10.000) |
| Taxa de amostragem do analisador | Até 24 MHz (`--la-rate`) | 100 kHz | Taxas altas exigem decodificar durante a captura, sem gravar todas as amostras em CSV |
| Temperatura | Ambiente controlada ou variada de propósito (caixa térmica) | Não controlada nem registrada | Mesmo sem controle, registrar |

## O que fazer

| Ação | Resolve | Situação |
| :--- | :--- | :--- |
| Ligar CTRU-Light e ECDH ao pool, com semente registrada e reprodutível | 2, 9 | feito (`6374aca`), falta testar na placa |
| Registrar `kem_rc` e conferir o ECDH no host | 3 | feito (`6374aca`) |
| Coletar 5 rodadas do ECDH `asm` e localizar a operação que diverge; testar `uECC_OPTIMIZATION_LEVEL=3` | 3 | pendente (precisa da placa) |
| Subir a amostragem do analisador para 1 a 2 MHz (resolução de 0,5 a 1 µs), decodificando os pulsos durante a captura em vez de gravar CSV com todas as amostras | 1, 10 | pendente |
| Medir o clock real pelos pulsos de ID (dados existentes) | 4, 10 | feito para a #19 (`workload.py`); confirmou o oscilador |
| Corrigir a latência pelo clock medido no `prepare.py` (campanhas com CSV) | 4, 10 | pendente |
| Pulso de referência longo (10⁶ ciclos) fora da janela, no firmware | 4, 10 | pendente |
| Registrar a temperatura do sensor interno, fora da janela, a cada operação | 4 | pendente |
| Descartar rodadas de aquecimento no início de cada bloco (`--warmup`) | 4 | pendente |
| Rodar com `--blocks` (por exemplo, 5) para sortear e intercalar as configurações | 5 | já existe no `run_experiment.py`, falta usar |
| Analisar com o bloco como efeito aleatório (modelo misto), em vez de usar as repetições como réplicas da configuração | 5 | pendente (caderno) |
| Corrigir a descrição das baterias #17 a #19 (ordem fixa; o `schedule.json` não foi seguido) | 5 | pendente |
| Limitar a duração dos blocos do ECDH (mais blocos com menos repetições) | 6 | pendente |
| Analisar Kyber e CTRU-Light como mistura: tempo de cada modo e proporção de rejeição com IC binomial | 7, 8, 9 | pendente (caderno) |
| Corrigir no caderno e no artigo a descrição "24 MHz" e o significado de `cycles_la` | 1, 10 | pendente |
| Investigar os Decaps sem validação | 11 | pendente |
| Seção 3.3 nos cadernos (`analise.qmd` e `analise.ipynb`) com taxa de amostragem, validação, semente, Kyber, ordem, carga e clock do MCU | 1 a 5, 9 | feito |
| `prepare.py`: extrair `la_clock.csv` dos CSVs do analisador e completar o `timestamp` e o `t_total_ms` da #19, que o `observations.csv` não tinha | 4, 5 | feito |
| Descrever o fator variante do CTRU-Light como "implementação do artefato" (o hash muda entre `ref` e `asm`) | confundimento | pendente |
| Rodar uma nova campanha completa depois das correções; usar #17 a #19 como piloto para dimensionar o n | todos | pendente |
