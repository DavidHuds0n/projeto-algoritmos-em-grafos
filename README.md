# Projeto: Labirinto de Creta

**Disciplina:** Algoritmos em Grafos - CCT/UFCA (2025.1)  
**Professor:** Carlos Vinicius G. C. Lima  
**Autor:** David Hudson Gomes Alves

---

## Descrição do Projeto
Este projeto consiste em uma simulação gráfica baseada no mito do Labirinto de Creta. A aplicação modela o labirinto como um grafo ponderado, onde um Prisioneiro (entrante) deve encontrar a saída antes que seu tempo se esgote ou que seja capturado pelo Minotauro.

A simulação implementa e visualiza algoritmos de grafos clássicos para ditar o comportamento dos personagens, com foco na eficiência e na correta aplicação da teoria vista em sala de aula.

---

## Pré-requisitos
Certifique-se de ter Python 3 instalado. Para instalar as bibliotecas de terceiros necessárias para a visualização, execute o seguinte comando no terminal:
```bash
pip install networkx matplotlib
````

A biblioteca `heapq`, utilizada na implementação de Dijkstra, faz parte da biblioteca padrão do Python e não requer instalação adicional.

-----

## Estrutura dos Arquivos

O repositório está organizado da seguinte forma:

  * `labirinto.py`: Script principal que executa a simulação. Ele carrega a configuração do labirinto, inicializa os personagens, controla o loop de turnos e renderiza a visualização gráfica.
  * `gerador_de_configuracao.py`: Ferramenta para gerar labirintos procedurais. Cria os arquivos `labirinto.txt` e `posicoes.txt` que são utilizados pela simulação principal.
  * `labirinto.txt`: Arquivo de dados que descreve a estrutura do grafo (vértices, arestas, pesos) e os parâmetros da simulação (entrada, saída, tempo, etc.).
  * `posicoes.txt`: Arquivo opcional que mapeia cada vértice do grafo a uma coordenada (x, y), permitindo uma visualização em grade, fiel à estrutura de um labirinto real.
  * `README.md`: Este arquivo, com a documentação do projeto.

-----

## Como Executar

O projeto é composto por dois scripts principais que devem estar na mesma pasta: um gerador de configurações e o simulador principal.

**1. Gerar a Configuração do Labirinto (Opcional, mas recomendado):**
Para criar um novo labirinto aleatório, execute o script `gerador_de_configuracao.py`. Isso criará os arquivos `labirinto.txt` (com a estrutura do grafo) e `posicoes.txt` (para a visualização em grade).

```bash
python gerador_de_configuracao.py
```

> **Customizando a Geração:**
> Você pode facilmente alterar as características do labirinto gerado editando as seguintes constantes no topo do arquivo `gerador_de_configuracao.py`:
>
>   * `LARGURA` e `ALTURA`: Define as dimensões da grade do labirinto.
>   * `DISTANCIA_MINIMA_INICIAL`: Garante que o Minotauro comece a uma distância mínima do jogador, tornando o início do jogo mais justo.

**2. Rodar a Simulação Principal:**
Para iniciar a simulação, execute o script `labirinto.py`. Ele carregará a configuração do `labirinto.txt` e iniciará a visualização gráfica.

```bash
python labirinto.py
```

Uma janela do Matplotlib será aberta, exibindo a simulação em tempo real. O relatório final com os detalhes da execução será impresso no console ao término da simulação.

-----

## Dinâmicas da Simulação

A simulação segue as regras e comportamentos especificados no documento do projeto.

  * **Objetivo do Prisioneiro:** Encontrar o vértice de saída em um tempo máximo `t(G)`, antes de ser capturado pelo Minotauro ou de seus suprimentos acabarem.

  * **Comportamento do Minotauro:**

      * **Patrulha:** Em estado normal, move-se um vértice por turno para destinos aleatórios.
      * **Percepção:** A cada turno, o Minotauro calcula a distância (soma dos pesos das arestas) até o Prisioneiro. Se essa distância for menor ou igual ao parâmetro de percepção `p(G)`, ele detecta o intruso.
      * **Perseguição:** Ao detectar o Prisioneiro, sua velocidade aumenta para **dois vértices por turno**, seguindo o caminho mais curto em direção à sua presa.

  * **Condições de Fim de Jogo:**

      * **Fuga:** O Prisioneiro alcança o nó de saída.
      * **Tempo Esgotado:** O Prisioneiro não consegue escapar dentro do tempo `t(G)`.
      * **Batalha:** Se ambos ocupam o mesmo vértice, o Prisioneiro tem apenas **1% de chance de sobreviver**.

-----

## Implementação dos Algoritmos

Esta seção detalha a lógica por trás dos algoritmos de grafos que governam o comportamento dos personagens.

### Prisioneiro: Exploração com Busca em Profundidade (DFS)

Como o Prisioneiro desconhece o labirinto, sua estratégia de movimento precisava ser de exploração sistemática. A **Busca em Profundidade (DFS)** foi a escolha ideal, simulando perfeitamente a ideia do "novelo de lã".

  * **Estrutura de Dados:** A implementação utiliza uma pilha explícita (`pilha_dfs`) para controlar o percurso. Um conjunto (`visitados`) armazena os nós já visitados para garantir eficiência na consulta (complexidade O(1)).

  * **Lógica de Movimento:**

    1.  **Avançar:** No turno atual, o Prisioneiro olha os vizinhos do vértice onde está (o topo da pilha). Ele se move para o primeiro vizinho que ainda não foi visitado. Este novo vértice é adicionado ao conjunto de visitados e empilhado. Isso equivale a "desenrolar o novelo" em um novo corredor.
    2.  **Retroceder (Backtracking):** Se todos os vizinhos do vértice atual já foram visitados (um beco sem saída), o Prisioneiro remove o vértice atual da pilha (`pop`). Seu próximo movimento será para o novo vértice no topo da pilha, efetivamente retornando pelo caminho já conhecido. Isso simula "recolher o novelo" para tentar outra rota.

### Minotauro: Perseguição com Algoritmo de Dijkstra

O Minotauro conhece todo o mapa e sempre busca o caminho mais eficiente para caçar o Prisioneiro. Para isso, foi implementado o **Algoritmo de Dijkstra**, que calcula o caminho de menor custo (menor soma de pesos das arestas) de um único ponto de origem para todos os outros vértices do grafo.

  * **Estrutura de Dados:** Conforme permitido pelo projeto, a implementação utiliza uma fila de prioridades (min-heap) da biblioteca `heapq`. Isso é crucial para a eficiência do algoritmo, garantindo uma complexidade de tempo de $O((|E| + |V|) \log |V|)$ em vez de $O(|V|^2)$.

  * **Lógica de Funcionamento:**

    1.  **Cálculo de Distâncias:** A cada turno, o Minotauro executa o Dijkstra a partir de sua posição atual. O algoritmo retorna um dicionário com as distâncias mínimas para todos os outros nós. Esse dicionário é usado para verificar se a distância até o Prisioneiro é menor ou igual ao raio de percepção `p(G)`.
    2.  **Reconstrução do Caminho:** Além das distâncias, o algoritmo também retorna um dicionário de `predecessores`, que mapeia cada nó ao seu "pai" no caminho mais curto a partir da origem. Quando o Minotauro inicia a perseguição, uma função auxiliar usa esse dicionário para reconstruir o caminho exato, do Prisioneiro de volta até o Minotauro, que é então percorrido na ordem correta.

-----

## Análise e Discussão dos Resultados

Esta seção aborda a discussão sobre a eficiência e a calibragem dos parâmetros, um dos critérios de avaliação do projeto.

* **Eficiência do Algoritmo de Perseguição (Dijkstra):** A escolha de Dijkstra com uma fila de prioridades (`heapq`) é ideal para o cálculo de caminhos mínimos em grafos ponderados. Esta abordagem garante uma complexidade de tempo eficiente $O((|E| + |V|) \log |V|)$, sendo crucial para a performance da simulação a cada turno, já que o Minotauro precisa recalcular sua rota frequentemente.

* **Eficiência e Adequação da Exploração (DFS):** Para o Prisioneiro, que desconhece o labirinto, a **Busca em Profundidade (DFS)** foi escolhida por ser uma estratégia de exploração completa e sistemática.
    * **Justificativa:** O comportamento recursivo do DFS, explorando um caminho até o fim antes de retroceder (backtracking), alinha-se perfeitamente com a metáfora do "novelo de lã" descrita nos requisitos do projeto. Ele garante que o Prisioneiro explore todo o labirinto sem se perder ou entrar em loops infinitos.
    * **Performance:** A implementação possui complexidade de tempo $O(|V| + |E|)$, que é ótima para percorrer o grafo. O uso de um `set` para registrar os vértices visitados permite consultas em tempo constante (O(1)), mantendo a eficiência máxima da busca. Em comparação, uma busca em largura (BFS) também seria viável e encontraria o caminho com o menor número de arestas, mas o DFS tem um caráter de "se aprofundar no desconhecido" que se encaixa bem tematicamente com a situação do Prisioneiro.

* **Calibragem dos Parâmetros de Entrada:**
    * **`PERCEPCAO_DISTANCIA`:** Este é o parâmetro mais crítico para a dificuldade. Um valor baixo (ex: 3) torna o Minotauro pouco ameaçador, enquanto um valor muito alto (ex: 20) o torna quase onisciente. O valor padrão de `15` provou ser um bom equilíbrio, criando tensão sem tornar a fuga impossível.
    * **`DISTANCIA_MINIMA_INICIAL`:** A implementação no gerador que força o Minotauro a começar longe do prisioneiro é uma melhoria que garante um início de jogo mais justo, dando ao prisioneiro tempo para iniciar sua exploração.
    * **Pesos das Arestas:** A variação de pesos (1 a 5) torna o cálculo de distância do Minotauro mais interessante do que uma simples contagem de passos, validando o uso de Dijkstra em um grafo ponderado.

-----

## Vídeo de Apresentação

[LINK PARA O VÍDEO DE APRESENTAÇÃO](https://youtu.be/c4uL5tWoS-I)
