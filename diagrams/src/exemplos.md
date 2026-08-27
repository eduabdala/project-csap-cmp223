# Diagramas — CMP223

Cada bloco `mermaid` vira um arquivo em `diagrams/out/`.
O nome sai do comentário `<!-- diagrama: nome -->` logo antes do bloco.

Classes de estilo disponíveis (sufixo `:::`): `destaque`, `alerta`, `neutro`.

---

<!-- diagrama: metodologia-hibrida -->

```mermaid
flowchart LR
    A[Objeto de estudo<br/>Kyber-512 / CTRU-Light] --> B{Metodologia<br/>híbrida}
    B --> C[Simulação<br/>cycle-accurate]
    B --> D[Medição física<br/>bare-metal]
    C --> E[Contagem de ciclos<br/>sem intrusão]
    D --> F[Energia por operação<br/>latência real]
    E --> G[Análise de<br/>desempenho]
    F --> G

    B:::destaque
    G:::destaque
    E:::neutro
    F:::neutro
```

---

<!-- diagrama: fluxo-kem -->

```mermaid
sequenceDiagram
    participant MCU as ATmega4809
    participant GW as Gateway
    MCU->>MCU: KeyGen (pk, sk)
    MCU->>GW: pk
    GW->>GW: Encaps(pk) → (ct, K)
    GW-->>MCU: ct
    MCU->>MCU: Decaps(sk, ct) → K
    Note over MCU,GW: Segredo K compartilhado
```

---

<!-- diagrama: orcamento-sram -->

```mermaid
pie showData title Orçamento de SRAM (6 KB)
    "Kyber-512 (stack peak)" : 3200
    "Stack RTOS + MQTT" : 1400
    "Buffers de sensor" : 700
    "Headroom livre" : 844
```

---

<!-- diagrama: cronograma -->

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

---

<!-- diagrama: ciclos-por-operacao -->

```mermaid
xychart
    title "Ciclos de clock por operação (k-cycles)"
    x-axis ["KeyGen", "Encaps", "Decaps"]
    y-axis "k-cycles" 0 --> 4000
    bar [2650, 3100, 3480]
    bar [1180, 1420, 1560]
```
