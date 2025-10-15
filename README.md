# Projeto: Labirinto de Creta
**Disciplina:** Algoritmos em Grafos - CCT/UFCA (2025.1)  
**Professor:** Carlos Vinicius G. C. Lima  
**Autor:** David Hudson Gomes Alves

## Descrição do Projeto
Este projeto consiste em uma simulação gráfica e interativa baseada no mito do Labirinto de Creta. A aplicação modela o labirinto como um grafo ponderado, onde um Prisioneiro (entrante) deve encontrar a saída antes que seu tempo se esgote ou que seja capturado pelo Minotauro.

A simulação implementa e visualiza algoritmos de grafos clássicos para ditar o comportamento dos personagens:
* **Busca em Profundidade (DFS):** Utilizada pelo Prisioneiro, que desconhece o labirinto, para explorá-lo de forma sistemática. Sua memória e a capacidade de retornar por caminhos já feitos simulam o uso de um "novelo de lã".
* **Algoritmo de Dijkstra:** Empregado pelo Minotauro, que conhece todo o mapa, para calcular o caminho mais curto (baseado na soma dos pesos das arestas) até o Prisioneiro, permitindo uma perseguição inteligente e eficaz.

---

## Pré-requisitos
Certifique-se de ter Python 3 instalado. Para instalar as bibliotecas de terceiros necessárias para a visualização, execute o seguinte comando no terminal:
```bash
pip install networkx matplotlib
````

A biblioteca `heapq`, utilizada na implementação de Dijkstra, faz parte da biblioteca padrão do Python e não requer instalação adicional.

-----

## Como Executar

O projeto é composto por dois scripts principais que devem estar na mesma pasta: um gerador de configurações e o simulador principal.

**1. Gerar a Configuração do Labirinto (Opcional, mas recomendado):**
Para criar um novo labirinto aleatório, execute o script `gerador_de_configuracao.py`. Isso criará os arquivos `labirinto.txt` (com a estrutura do grafo) e `posicoes.txt` (para a visualização em grade).

```bash
python gerador_de_configuracao.py
```

**2. Rodar a Simulação Principal:**
Para iniciar a simulação, execute o script `labirinto.py`. Ele carregará a configuração do `labirinto.txt` e iniciará a visualização gráfica.

```bash
python labirinto.py
```

Uma janela do Matplotlib será aberta, exibindo a simulação em tempo real. O relatório final com os detalhes da execução será impresso no console ao término da simulação.

-----

## Funcionalidades e Dinâmicas Implementadas

  * **Geração Procedural:** O `gerador_de_configuracao.py` cria arquivos `labirinto.txt` que descrevem a topologia do grafo, incluindo número de vértices e arestas, pesos, e parâmetros da simulação, conforme solicitado.
  * **Movimentação Inteligente:**
      * **Prisioneiro:** Move-se um vértice por vez e, em caso de encontro com o Minotauro, há uma batalha com 1% de chance de sobrevivência. Se encontrar a saída, o prisioneiro escapa.
      * **Minotauro:** Em modo normal, move-se um vértice por vez através de uma "Patrulha Inteligente". Ao detectar o prisioneiro (a uma distância `p(G)`), passa a persegui-lo movendo-se dois vértices por turno pelo caminho mínimo.
  * **Visualização Detalhada:** A interface gráfica exibe em tempo real:
      * A posição do Prisioneiro e do Minotauro.
      * O "novelo de lã" do Prisioneiro (caminho já percorrido).
      * O caminho de patrulha futuro do Minotauro e seu nó de destino.
      * Os nós já visitados pelo Prisioneiro.
      * Os pesos de todas as arestas.

-----

## Análise e Discussão dos Resultados

Esta seção aborda a discussão sobre a eficiência e a calibragem dos parâmetros, um dos critérios de avaliação do projeto.

  * **Eficiência dos Algoritmos:** A escolha de Dijkstra com uma fila de prioridades (`heapq`) é ideal para o cálculo de caminhos mínimos em grafos ponderados. Esta abordagem garante uma complexidade de tempo eficiente, sendo crucial para a performance da simulação a cada turno. O uso de `heapq` está de acordo com as permissões do projeto para uso de estruturas de dados clássicas.

  * **Calibragem dos Parâmetros de Entrada:**

      * **`PERCEPCAO_DISTANCIA`:** Este é o parâmetro mais crítico para a dificuldade. Um valor baixo (ex: 3) torna o Minotauro pouco ameaçador, enquanto um valor muito alto (ex: 20) o torna quase onisciente. O valor padrão de `8` provou ser um bom equilíbrio, criando tensão sem tornar a fuga impossível.
      * **`DISTANCIA_MINIMA_INICIAL`:** A implementação no gerador que força o Minotauro a começar longe do prisioneiro é uma melhoria que garante um início de jogo mais justo, dando ao prisioneiro tempo para iniciar sua exploração.
      * **Pesos das Arestas:** A variação de pesos (1 a 5) torna o cálculo de distância do Minotauro mais interessante do que uma simples contagem de passos, validando o uso de Dijkstra em um grafo ponderado.

-----

## Vídeo de Apresentação

`[LINK PARA O VÍDEO DE APRESENTAÇÃO]`
