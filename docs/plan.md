---
created: 2026-10-17
---
# draft

- ~~Preciso listar o que eu tenho pra fazer no projeto~~
- ~~Preciso organizar qual o nivel de prioridade de cada uma dessas coisas do projeto~~ 
- Preciso definir o que começar primeiro
- ~~Preciso organizar as datas limites para cada uma dessas coisas~~

### Lista
- Organizar o repositorio
- Organizar o codigo
- Definir variaveis do projeto
- Ajustar de que forma o trabalho pode ser reprodutivo
- Organizar Referencias

### Comprar
- Resistor de precisão 1(r) ohm 1%


### Infos Sistem Computacional (SUT)
  Sera utilizado uma devboard Arduino Nano Every, que contem um Microchip ATmega4809 (família megaAVR 0-series, arquitetura AVRxt de 8 bits). 
  - 48 KB Flash, 6 KB SRAM, 256 B EEPROM.
  - Tensão nominal de lógica e alimentação do MCU: 5.0V (regulador on-board MPM3610 converte Vin/USB para 5V).
  - A Nano Every possui um microcontrolador secundário (ATSAMD11D14A) que atua como gravador UPDI e conversor USB-Serial.
  - Single-core, estritamente sequencial (sem hyperthreading, sem execução fora de ordem, sem paralelismo de instruções em nível de hardware).
  - 32 registradores de uso geral de 8 bits (r0 a r31), acessíveis em 1 único ciclo de clock.
  - Os últimos 6 registradores formam 3 pares de ponteiros de 16 bits para indexação indireta de memória: X (r26:r27), Y (r28:r29) e Z (r30:r31).
  - Pipeline: 2 estágios (Fetch e Execute). Enquanto a instrução corrente é executada, a próxima é buscada da Flash. Quase todas as instruções de registradores executam em 1 ciclo de clock. Saltos condicionais (branches) e instruções de acesso à memória (Load/Store) levam de 2 a 3 ciclos.
  - Suporte nativo por hardware apenas para inteiros de 8 bits (adição, subtração, lógica booleana, deslocamento).
  - Multiplicador de Hardware: Multiplicador em silício de 2 registradores de 8 bits gerando resultado de 16 bits em 2 ciclos de clock (MUL, MULS, MULU).
  - Sem suporte a divisão por hardware: Qualquer divisão (e.g., redução modular de polinômios se não for potência de 2) é sintetizada por software via rotinas de shifts sucessivos na avr-libc.
  - Sem FPU (Floating-Point Unit): Qualquer eventual operação em ponto flutuante é emulada via software, gerando explosão de ciclos de clock.
  - Arquitetura Harvard modificada com espaço unificado linear (Unified Memory Mapping


```mermaid
gantt
    dateFormat YYYY-MM-DD
    axisFormat %d/%m
    title Cronograma Completo - Trabalho Final (Parcial: 09/11 | Final: 14/12)

    section Preparação (5 dias)
        Planejamento e organização                  :active, plan, 2026-10-17, 2d
        Setup do toolchain e ambiente               :active, env, after plan, 3d

    section Etapa 2: Parcial (Meta: 09/11)
        Port e execução do algoritmo base           :base_port, after env, 6d
        Instrumentação e setup de medição           :instr, after base_port, 3d
        Coleta preliminar (tendências e métricas)   :crit, prelim, after instr, 5d
        Gráficos preliminares e levantamento de gargalos :ana_pre, after prelim, 2d
        Elaboração dos slides e ensaio parcial      :pres_parcial, after ana_pre, 2d
        Apresentação Parcial (Etapa 2)              :milestone, m_parcial, 2026-11-09, 0d
```


```mermaid
gantt
    dateFormat YYYY-MM-DD
    axisFormat %d/%m
    title Cronograma Completo - Trabalho Final (Parcial: 09/11 | Final: 14/12)

    section Preparação (5 dias)
        Planejamento e organização                  :active, plan, 2026-10-17, 2d
        Setup do toolchain e ambiente               :active, env, after plan, 3d

    section Etapa 2: Parcial (Meta: 09/11)
        Port e execução do algoritmo base           :base_port, after env, 6d
        Instrumentação e setup de medição           :instr, after base_port, 3d
        Coleta preliminar (tendências e métricas)   :crit, prelim, after instr, 5d
        Gráficos preliminares e levantamento de gargalos :ana_pre, after prelim, 2d
        Elaboração dos slides e ensaio parcial      :pres_parcial, after ana_pre, 2d
        Apresentação Parcial (Etapa 2)              :milestone, m_parcial, 2026-11-09, 0d

    section Etapa 3: Execução Final e Artigo (Meta: 14/12)
        Coleta exaustiva de dados                   :crit, coleta_full, after m_parcial, 11d
        Tratamento estatístico e análise crítica    :ana_full, after coleta_full, 6d
        Redação da primeira versão do artigo        :escrita, after ana_full, 10d
        Revisão do artigo e fechamento do texto     :rev, after escrita, 3d
        Elaboração dos slides finais e ensaio       :pres_final, after rev, 4d
        Apresentação Final e Entrega do Artigo      :milestone, m_final, 2026-12-14, 0d
```

```mermaid
gantt
    dateFormat YYYY-MM-DD
    axisFormat %d/%m
    title Cronograma do trabalho final
    section Preparação
        Revisão bibliográfica :done, rev, 2026-03-02, 14d
        Setup do toolchain    :active, env, after rev, 10d
    section Execução
        Port Kyber-512        :port, after env, 14d
        Instrumentação        :instr, after port, 10d
        Coleta de dados       :crit, coleta, after instr, 14d
    section Fechamento
        Análise estatística   :ana, after coleta, 10d
        Escrita do artigo     :esc, after ana, 14d
```

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'fontFamily': 'sans-serif', 'lineColor': '#000000', 'textColor': '#000000'}}}%%
flowchart LR
    %% Classes de alto contraste (Preto, Branco e Vermelho UFRGS)
    classDef hardware fill:#000000,stroke:#000000,stroke-width:2px,color:#ffffff,font-weight:bold;
    classDef rotina fill:#ffffff,stroke:#000000,stroke-width:2px,color:#000000,font-weight:bold;
    classDef medicao fill:#ffffff,stroke:#c8102e,stroke-width:2.5px,color:#c8102e,font-weight:bold;
    classDef metrica fill:#ffffff,stroke:#000000,stroke-width:2px,color:#000000,stroke-dasharray: 4 4;
    classDef pipeline fill:#ffffff,stroke:#000000,stroke-width:2px,color:#000000,font-weight:bold;
    classDef headroom fill:#c8102e,stroke:#000000,stroke-width:2px,color:#ffffff,font-weight:bold;

    subgraph SUT [" Sistema Sob Teste "]
        direction TB
        A["ATmega4809<br/>(6 KB SRAM / 48 KB Flash)"]:::hardware
        B["Rotina Criptográfica<br/>(KeyGen / Encaps / Decaps)"]:::rotina
        A --> B
    end

    %% Instrumentação Física
    B -->|"Trigger GPIO"| C("Osciloscópio"):::medicao
    B -->|"Toggle GPIO"| E("Analisador Lógico"):::medicao
    A -->|"Preenchimento 0xAA"| G("Stack Watermarking"):::medicao

    %% Cálculo das Métricas
    C -->|"Integral de Potência"| D["Energia (µJ)<br/>E = ∫ V · i dt"]:::metrica
    E -->|"Largura de Pulso"| F["Latência / Ciclos<br/>T_exec e K_cycles"]:::metrica
    G -->|"RAMEND - End. Mín."| H["Pico de Pilha<br/>Stack Peak (Bytes)"]:::metrica

    %% Pipeline Snakemake & Análise
    subgraph REPRO [" Automação Linux "]
        SNAKE["Orquestrador Snakemake<br/>(Coleta, Parser e Estatística)"]:::pipeline
    end

    D --> SNAKE
    F --> SNAKE
    H --> SNAKE

    %% Síntese
    SNAKE -.-> I["Margem Sistêmica<br/>Headroom CPU e SRAM"]:::headroom

    %% Força contraste fixo em todas as setas
    linkStyle default stroke:#000000,stroke-width:2px;
    linkStyle 10 stroke:#c8102e,stroke-width:2.5px,stroke-dasharray: 4 4;

```


```mermaid
sequenceDiagram
    autonumber
    participant GW as Gateway / Host (PC)
    participant MCU as ATmega4809 (SUT)
    participant INST as Instrumentação (Osciloscópio / LA)

    Note over MCU,GW: === FASE A: RECEPÇÃO NO MCU (KeyGen + Decaps) ===
    
    GW->>MCU: CMD_START_DOWNLINK
    
    rect rgb(240, 248, 255)
        Note over MCU,INST: Medição 1: KeyGen no MCU
        MCU->>INST: GPIO Window = HIGH
        MCU->>MCU: KeyGen() → (pk_mcu, sk_mcu)
        MCU->>INST: GPIO Window = LOW
    end

    Note over MCU,GW: Troca de I/O (Sem medição)
    MCU->>GW: Envia pk_mcu via Serial
    GW->>GW: Encaps(pk_mcu) → (ct_down, K_down)
    GW->>MCU: Envia ct_down via Serial

    rect rgb(240, 248, 255)
        Note over MCU,INST: Medição 2: Decaps no MCU
        MCU->>INST: GPIO Window = HIGH
        MCU->>MCU: Decaps(sk_mcu, ct_down) → K_down
        MCU->>INST: GPIO Window = LOW
    end
    MCU->>GW: ACK_DOWNLINK_OK + Stack Peak (Fase A)

    Note over MCU,GW: === FASE B: ENVIO A PARTIR DO MCU (Encaps) ===

    Note over GW: GW gera seu próprio par assimétrico:<br/>KeyGen() → (pk_gw, sk_gw)
    GW->>MCU: CMD_START_UPLINK + Envia pk_gw

    rect rgb(240, 255, 240)
        Note over MCU,INST: Medição 3: Encaps no MCU
        MCU->>INST: GPIO Window = HIGH
        MCU->>MCU: Encaps(pk_gw) → (ct_up, K_up)
        MCU->>INST: GPIO Window = LOW
    end

    rect rgb(255, 250, 240)
        Note over MCU,INST: Medição 4: Cifragem de Carga Útil (Opcional)
        MCU->>INST: GPIO Window = HIGH
        MCU->>MCU: AES_CTR(K_up, payload) → payload_cifrado
        MCU->>INST: GPIO Window = LOW
    end

    Note over MCU,GW: Troca de I/O (Sem medição)
    MCU->>GW: Envia [ct_up + payload_cifrado]
    GW->>GW: Decaps(sk_gw, ct_up) → K_up
    GW->>GW: AES_Decrypt(K_up, payload_cifrado)
    MCU->>GW: ACK_UPLINK_OK + Stack Peak (Fase B)
  ```

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'fontFamily': 'sans-serif', 'lineColor': '#000000', 'textColor': '#000000'}}}%%
flowchart LR
    %% Classes de estilo
    classDef hardware fill:#000000,stroke:#000000,stroke-width:2px,color:#ffffff,font-weight:bold;
    classDef fatores fill:#f4f4f4,stroke:#000000,stroke-width:2px,color:#000000,stroke-dasharray: 3 3;
    classDef medicao fill:#ffffff,stroke:#c8102e,stroke-width:2.5px,color:#c8102e,font-weight:bold;
    classDef processamento fill:#ffffff,stroke:#000000,stroke-width:2px,color:#000000,font-weight:bold;
    classDef metricas fill:#c8102e,stroke:#000000,stroke-width:2px,color:#ffffff,font-weight:bold;

    %% Fatores Experimentais (Variáveis Independentes)
    subgraph FAT [" Variáveis Independentes (Fatores) "]
        direction TB
        F1["Algoritmo: ECDH / CTRU / Kyber"]
        F2["Frequência da CPU: 20 / 10 / 5 MHz"]
        F3["Flags do Compilador: -Os vs. -O3"]
    end
    class FAT fatores

    %% SUT
    subgraph SUT [" Sistema Sob Teste (SUT) "]
        direction TB
        MCU["ATmega4809 (Arduino Nano Every)<br/>48 KB Flash / 6 KB SRAM"]:::hardware
        KERNEL["Rotina Criptográfica<br/>(KeyGen / Encaps / Decaps)"]:::hardware
        MCU --> KERNEL
    end

    FAT -->|"Configuração"| SUT

    %% Instrumentação Física (Camada de Aquisição)
    KERNEL -->|"Queda de Tensão no Shunt"| OSC("Osciloscópio Digital<br/>(Amostragem v_shunt)"):::medicao
    KERNEL -->|"Janela Lógica (GPIO HIGH/LOW)"| LA("Analisador Lógico<br/>(Tempo de Borda a Borda)"):::medicao
    MCU -->|"Varredura de Padrão 0xAA"| WM("Stack Watermarking<br/>(Leitura via Firmware/Serial)"):::medicao

    %% Pipeline Snakemake & Análise
    subgraph AUTO [" Automação & Pós-Processamento "]
        direction TB
        PARSER["Orquestrador Snakemake<br/>• Leitura de CSVs<br/>• Integração Numérica: ∫(V·i)dt<br/>• Estatística (Média, IC 95%)"]:::processamento
    end

    OSC -->|"Forma de Onda (CSV)"| PARSER
    LA -->|"Timestamp Δt (CSV)"| PARSER
    WM -->|"Dump de Memória"| PARSER

    %% Métricas Finais (Variáveis Dependentes)
    subgraph OUT [" Métricas Obtidas (Variáveis Dependentes) "]
        direction TB
        M1["Energia por Operação (E_op em µJ)"]:::metricas
        M2["Latência (ms) e Ciclos (K_cycles)"]:::metricas
        M3["Pico de SRAM (Stack Peak em Bytes)"]:::metricas
        M4["Headroom Operacional (CPU e SRAM Livres %)"]:::metricas
    end

    PARSER --> OUT

    %% Ajuste de estilo das conexões
    linkStyle default stroke:#000000,stroke-width:2px;
``` 

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'fontFamily': 'sans-serif', 'lineColor': '#000000', 'textColor': '#000000'}}}%%
flowchart TD
    %% Classes de estilo (Alto contraste com destaque UFRGS)
    classDef setup fill:#f4f4f4,stroke:#000000,stroke-width:2px,color:#000000;
    classDef isolamento fill:#ffffff,stroke:#000000,stroke-width:2px,stroke-dasharray: 4 4,color:#000000;
    classDef orquestra fill:#000000,stroke:#000000,stroke-width:2px,color:#ffffff,font-weight:bold;
    classDef bancada fill:#ffffff,stroke:#c8102e,stroke-width:2.5px,color:#c8102e,font-weight:bold;
    classDef analise fill:#ffffff,stroke:#000000,stroke-width:2px,color:#000000,font-weight:bold;
    classDef saida fill:#c8102e,stroke:#000000,stroke-width:2px,color:#ffffff,font-weight:bold;

    %% 1. Configuração e Isolamento
    subgraph PREP [" 1. Configuração & Isolamento Rigoroso "]
        direction TB
        CFG["Matriz de Fatores (config.yaml)<br/>• Algoritmos: ECDH / CTRU / Kyber<br/>• Otimização: -Os vs. -O3<br/>• Clock: 20 / 10 MHz"]:::setup
        ISO_HW["Isolamento Elétrico & Térmico<br/>• Bateria Li-Ion 18650 dedicada<br/>• Shunt de precisão calibrado (1 Ω)<br/>• Intervalo de repouso (Cool-down)"]:::isolamento
        ISO_FW["Isolamento do Firmware<br/>• Desativação de interrupções (cli)<br/>• I/O de 1 ciclo via VPORTx.OUT<br/>• Sem chamadas de I/O na janela"]:::isolamento
    end

    %% 2. Orquestração e Reprodutibilidade
    subgraph ORQ [" 2. Automação e Execução Fatorial (Snakemake) "]
        direction TB
        BUILD["Compilação Parametrizada<br/>(avr-gcc + dump avr-size)"]:::setup
        FLASH["Gravação Automática<br/>(avrdude via UPDI)"]:::setup
        DOE["Planejamento Experimental (DoE)<br/>• N = 30 iterações por fator<br/>• Ordem de execução randomizada"]:::orquestra
        BUILD --> FLASH --> DOE
    end

    PREP --> ORQ

    %% 3. Janela de Execução e Coleta
    subgraph ACQ [" 3. Bancada de Aquisição e Disparo "]
        direction TB
        TRIG["Disparo Serial Host/MCU<br/>(Sem buffer serial no trigger)"]:::bancada
        PWM["Stack Watermarking<br/>(Padrão 0xAA)"]:::bancada
        OSC["Osciloscópio Digital<br/>(Forma de onda v_shunt)"]:::bancada
        LA["Analisador Lógico (sigrok-cli)<br/>(Largura do pulso GPIO)"]:::bancada
    end

    DOE -->|"Inicia Ensaio"| TRIG
    TRIG --> PWM
    TRIG --> OSC
    TRIG --> LA

    %% 4. Pós-processamento e Estatística
    subgraph STAT [" 4. Tratamento Estatístico e Métricas "]
        direction TB
        RAW["Armazenamento de Dados Brutos<br/>(CSVs com hash git e metadados)"]:::analise
        INTEG["Integração Numérica e Cálculo<br/>• Energia: E = ∫ V·i dt<br/>• Latência e Ciclos reais<br/>• Pico de Pilha (RAMEND - mín)"]:::analise
        TRAT["Análise Estatística Robusta<br/>• Média amostral<br/>• Intervalo de Confiança (CI 95%)<br/>• Detecção e auditoria de outliers"]:::analise
        RAW --> INTEG --> TRAT
    end

    OSC -->|"Curva v(t)"| RAW
    LA -->|"Timestamps"| RAW
    PWM -->|"Dump Pilha"| RAW

    %% 5. Artefatos Finais
    subgraph OUT [" 5. Artefatos Científicos Finais "]
        TAB["Tabelas Finais Agregadas<br/>(summary_table.csv)"]:::saida
        FIG["Gráficos com Barras de Erro<br/>(Curvas Trade-off, PDF vetorial)"]:::saida
    end

    TRAT --> TAB
    TRAT --> FIG

    %% Ajuste dos links
    linkStyle default stroke:#000000,stroke-width:2px;
```

```mermaid
stateDiagram-v2
    [*] --> IDLE : Inicialização (Setup UART + GPIO)
    
    IDLE --> PREP_DOWNLINK : Recebe CMD_START_DOWNLINK
    PREP_DOWNLINK --> EXEC_KEYGEN : Watermark SRAM (0xAA)
    EXEC_KEYGEN --> SEND_PK : GPIO=HIGH → KeyGen() → GPIO=LOW
    SEND_PK --> WAIT_CT : Envia pk_mcu via Serial
    WAIT_CT --> EXEC_DECAPS : Recebe ct_down
    EXEC_DECAPS --> REPORT_DOWN : GPIO=HIGH → Decaps() → GPIO=LOW
    REPORT_DOWN --> IDLE : Envia ACK e Leitura da Pilha

    IDLE --> PREP_UPLINK : Recebe CMD_START_UPLINK (com pk_gw)
    PREP_UPLINK --> EXEC_ENCAPS : Watermark SRAM (0xAA)
    EXEC_ENCAPS --> EXEC_AES : GPIO=HIGH → Encaps() → GPIO=LOW
    EXEC_AES --> SEND_TELEMETRY : GPIO=HIGH → AES() → GPIO=LOW
    SEND_TELEMETRY --> REPORT_UP : Envia ct_up + payload
    REPORT_UP --> IDLE : Envia ACK e Leitura da Pilha
```

```mermaid
stateDiagram-v2
    [*] --> IDLE : Inicialização (Setup UART + GPIO)
    
    %% --- FLUXO DOWNLINK ---
    IDLE --> PREP_DOWNLINK : Recebe CMD_START_DOWNLINK
    PREP_DOWNLINK --> EXEC_KEYGEN : Watermark SRAM (0xAA)
    
    state EXEC_KEYGEN {
        [*] --> High_KeyGen : VPORT.OUT = HIGH
        note right of High_KeyGen
            • Analisador Lógico: Captura t0
            • Osciloscópio: Dispara trigger e amostra v_shunt(t)
        end note
        High_KeyGen --> Low_KeyGen : Executa KeyGen()
        Low_KeyGen --> [*] : VPORT.OUT = LOW (Fim da janela)
    }

    EXEC_KEYGEN --> SEND_PK
    SEND_PK --> WAIT_CT : Envia pk_mcu via Serial
    WAIT_CT --> EXEC_DECAPS : Recebe ct_down

    state EXEC_DECAPS {
        [*] --> High_Decaps : VPORT.OUT = HIGH
        note right of High_Decaps
            • Analisador Lógico: Captura t0
            • Osciloscópio: Amostra v_shunt(t)
        end note
        High_Decaps --> Low_Decaps : Executa Decaps()
        Low_Decaps --> [*] : VPORT.OUT = LOW (Fim da janela)
    }

    EXEC_DECAPS --> REPORT_DOWN
    
    state REPORT_DOWN {
        [*] --> Varredura_SRAM : Calcula Stack Peak (RAMEND - mín)
        Varredura_SRAM --> Envio_Telemetria : Envia ACK + Stack Peak via UART
        Envio_Telemetria --> [*]
    }

    REPORT_DOWN --> IDLE : Coleta serial gravada no Host

    %% --- FLUXO UPLINK ---
    IDLE --> PREP_UPLINK : Recebe CMD_START_UPLINK (com pk_gw)
    PREP_UPLINK --> EXEC_ENCAPS : Watermark SRAM (0xAA)

    state EXEC_ENCAPS {
        [*] --> High_Encaps : VPORT.OUT = HIGH
        note right of High_Encaps
            • Analisador Lógico: Mede latência
            • Osciloscópio: Amostra energia do Encaps
        end note
        High_Encaps --> Low_Encaps : Executa Encaps()
        Low_Encaps --> [*] : VPORT.OUT = LOW
    }

    EXEC_ENCAPS --> EXEC_AES

    state EXEC_AES {
        [*] --> High_AES : VPORT.OUT = HIGH
        High_AES --> Low_AES : Executa AES_CTR()
        Low_AES --> [*] : VPORT.OUT = LOW
    }

    EXEC_AES --> SEND_TELEMETRY : Envia ct_up + payload cifrado
    SEND_TELEMETRY --> REPORT_UP : Envia Stack Peak do Uplink via UART
    REPORT_UP --> IDLE : Coleta concluída

    %% --- TRATAMENTO DOS DADOS NO HOST ---
    note right of IDLE
        PÓS-PROCESSAMENTO NO HOST (Linux):
        1. Snakemake consolida CSVs do osciloscópio e analisador
        2. Integração da potência: E_op = ∫ V·i dt
        3. Cálculo de ciclos, Headroom e IC 95%
    end note
```

```mermaid
stateDiagram-v2
    [*] --> IDLE : Inicialização (Setup UART + VPORT)

    %% Disparo KeyGen
    IDLE --> PREP_KEYGEN : CMD_KEYGEN recebido
    PREP_KEYGEN --> PREP_KEYGEN : Preenche SRAM (0xAA)
    PREP_KEYGEN --> PULSE_ID_1 : Emite 1 pulso identificador (1 µs)
    PULSE_ID_1 --> EXEC_KEYGEN : VPORT = HIGH (t0)
    EXEC_KEYGEN --> END_KEYGEN : KeyGen() termina → VPORT = LOW (t1)
    END_KEYGEN --> IDLE : Transmite Stack Peak & pk via UART

    %% Disparo Encaps
    IDLE --> PREP_ENCAPS : CMD_ENCAPS recebido
    PREP_ENCAPS --> PREP_ENCAPS : Preenche SRAM (0xAA)
    PREP_ENCAPS --> PULSE_ID_2 : Emite 2 pulsos identificadores
    PULSE_ID_2 --> EXEC_ENCAPS : VPORT = HIGH (t0)
    EXEC_ENCAPS --> END_ENCAPS : Encaps() termina → VPORT = LOW (t1)
    END_ENCAPS --> IDLE : Transmite Stack Peak & ct via UART

    %% Disparo Decaps
    IDLE --> PREP_DECAPS : CMD_DECAPS recebido
    PREP_DECAPS --> PREP_DECAPS : Preenche SRAM (0xAA)
    PREP_DECAPS --> PULSE_ID_3 : Emite 3 pulsos identificadores
    PULSE_ID_3 --> EXEC_DECAPS : VPORT = HIGH (t0)
    EXEC_DECAPS --> END_DECAPS : Decaps() termina → VPORT = LOW (t1)
    END_DECAPS --> IDLE : Transmite Stack Peak & confirmação via UART
```