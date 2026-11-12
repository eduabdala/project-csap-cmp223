%%{init: {'theme': 'base', 'themeVariables': { 'fontFamily': 'sans-serif', 'lineColor': '#000000', 'textColor': '#000000'}}}%%
flowchart LR
    %% Classes de alto contraste oficiais UFRGS (Preto, Branco, Cinza e Vermelho #c8102e)
    classDef setup fill:#f4f4f4,stroke:#000000,stroke-width:2px,stroke-dasharray: 4 4,color:#000000;
    classDef orquestra fill:#ffffff,stroke:#000000,stroke-width:2px,color:#000000,font-weight:bold;
    classDef bancada fill:#000000,stroke:#c8102e,stroke-width:2.5px,color:#ffffff,font-weight:bold;
    classDef processamento fill:#ffffff,stroke:#000000,stroke-width:2px,color:#000000;
    classDef saida fill:#c8102e,stroke:#000000,stroke-width:2px,color:#ffffff,font-weight:bold;

    %% 1. Configuração e DoE
    subgraph S1 [" 1. Configuração & DoE "]
        direction TB
        A1["Matriz Fatorial 3×2×2×3"]
        A2["Ordem Randomizada (DoE)"]
        A3["N = 30 iterações por fator"]
        A1 --> A2 --> A3
    end
    class S1 setup;

    %% 2. Build & Flash
    subgraph S2 [" 2. Build & Gravação "]
        direction TB
        B1["Compilação avr-gcc 13<br/>(-Os vs. -O3)"]
        B2["Métricas avr-size<br/>(Flash / RAM)"]
        B3["Gravação avrdude UPDI<br/>(fuse2 @ 20 MHz)"]
        B1 --> B2 --> B3
    end
    class S2 orquestra;

    %% 3. Bancada Física (SUT)
    subgraph S3 [" 3. Bancada Física (SUT) "]
        direction TB
        C1["ATmega4809 (20 MHz)"]
        C2["Janela GPIO PA0 (VPORT)"]
        C3["Stack Watermarking (0xAA)"]
        C4["Analisador Lógico (24 MHz)"]
        C1 --> C2 --> C3 --> C4
    end
    class S3 bancada;

    %% 4. Pós-Processamento
    subgraph S4 [" 4. Pós-Processamento "]
        direction TB
        D1["Extração de Pulso Δt<br/>(Livre de ruído UART)"]
        D2["Pareamento 1:1<br/>(LA ↔ Telemetria)"]
        D3["Validação Criptográfica<br/>(KEM & Shared Secret)"]
        D1 --> D2 --> D3
    end
    class S4 processamento;

    %% 5. Métricas Finais
    subgraph S5 [" 5. Métricas Finais "]
        direction TB
        E1["Latência pura (ms)"]
        E2["Pico de Pilha (Bytes)"]
        E3["Flash ROM e Margens"]
        E4["Modelagem ANOVA & Jain"]
        E1 --> E2 --> E3 --> E4
    end
    class S5 saida;

    %% Conexões do Pipeline
    S1 -->|"Planejamento"| S2
    S2 -->|"Firmware HEX"| S3
    S3 -->|"Sinais Físicos"| S4
    S4 -->|"Dados Tratados"| S5

    %% Ajuste do estilo das setas
    linkStyle default stroke:#000000,stroke-width:2px;
