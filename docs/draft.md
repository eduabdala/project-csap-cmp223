## Etapas

- Ter um problema bem definido


## Problema?:
- algoritimos PQC atuais necessitam de uma grande quantidade de recursos, essa elevada quantidade de recursos necessarios dificulta a aplicabilidade em sistemas mais restritos e em sua grande parte legados, atualização de hardware é algo custoso a se fazer.

→ Problema bem definido é meio caminho andado
- Uma boa parte do esforço deve ser gasto na definição clara do problema
- Compreender profundamente o sistema e o problema antes de modelar
- Investir tempo em formular a questão certa

## Objetivo:
- objetivo é definir qual o limite da aplicabilidade dos algoritimos de criptografia pos quantica em sistemas embarcados


## Possiveis Assuntos:

- Kyber-512 contra o CTRU-Light

- analyses energetic consume in restrict embedded sistems using NIST Pos-quantum cryptography


## Questionamentos

- não seria interessante fazer a comparação dos algoritimos pqc com versãoes atuais para medir o custo computacional em relação ao que ja vem sendo utilizado atualmente, comparando ou usando por exemplo AES-128 como baseline de custo energetico e ciclos de clock entre outras metricas (talvez não nesse momento que o projeto ja esta quase todo planejado)
    - Comparar a PQC com a CC dificultaria ou agregaria de que forma?? 
        Acredito que possa ser interessante ver a diferença real entre o que ja se entendia como criptografia e o que vem a ser chamado de PQC.

- adicionar uma tabela das metricas e seus respectivos calculos

- Quais algoritimos serão comparados??
    (Tomar cuidado pois não faz sentido comprar algoritimos de propositos distintos como se fossem a mesma coisa)

- adiconar linha do tempo da nist

- Qual o objeto computacional??
    - o objeto computacional a ser analisado sera os algoritimos PQC rodando em um ambiente restrito como o Atmega4809.

- Quais são as metricas?
    - As metricas serão
        - Consumo energetico por operação criptografica (keygem, encap, decap)
        - Uso de Stack
        - Tempo de execução dessas operações
        - Tamanho dos binarios gerados
        - Margem operacional do sistema (quanto da perte criptografica vai ocupar na flash e quanto ficaria disponivel para ser utilizado em sensoriamento e etc)

- Quais são as variaveis? quais delas podem ser modificadas para analisar como o sistema se comporta em diferentes tipos de ambientes?

- Quais  o tipo de analise? de que maneira as metricas serão medidas?
    - A ideia principal seria seguir com Medição, fazer todo o processo de captura de metricas via osciloscopio e analisador logico e integrar a um pipeline com uma rotina pre definida para coleta e tratamento de dado.
    - Mas se possivel fazer uma analise mista entre Simulação e Medição, capaturando toda a parte de ciclos de clock, uso de stack, tempo de execução e demais metricas e comparando com a aplicação real

- Quais os parametros configuraveis desse projeto?
    - A otimização de compilação
    - O tamanhos dos dados cifrados
    - A quantidade de dados recebidos e decifrados

- Onde se quer chegar com esse trabalho??
    - validar principalmente a aplicabilidades dessas novas familias de algoritimos criptograficos em sistemas restristos sem abrir mão da usabilidade dele ou no caso o avaliar a margem operacional sistemica que seria justamente o quanto restaria para as demais tarefas 

- De que forma esse trabalho se tornara reprodutivo?

- Qual sera a carga de trabalho?
    - As cargas de trabalho serão:
        - ?


#### Tendo esses e outras duvidas acima sanadas, atualizar o ppt.


## tabela de metricas por algoritimo

-