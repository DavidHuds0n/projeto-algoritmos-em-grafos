import networkx as nx
import matplotlib.pyplot as plt
import random
import time
import heapq

# ==========================================================================
# --- CONFIGURAÇÕES GERAIS DA SIMULAÇÃO E VISUALIZAÇÃO ---
# Altere os valores aqui para ajustar o comportamento do programa.
# ==========================================================================

## --- Arquivos ---
ARQUIVO_LABIRINTO         = 'labirinto.txt'
ARQUIVO_POSICOES          = 'posicoes.txt'

## --- Lógica da Simulação ---
CHANCE_VITORIA_PRISIONEIRO  = 0.01  # 0.01 = 1%

## --- Aparência do Grafo ---
USAR_LAYOUT_DE_GRADE        = True  # True para desenhar em grade (usa posicoes.txt), False para layout automático.
TAMANHO_JANELA              = (12, 8) # (Largura, Altura)
VELOCIDADE_SIMULACAO_SEGUNDOS = 0.2   # Menor = mais rápido

## --- Estilo dos Nós (Círculos) ---
TAMANHO_NO                  = 400
COR_NO_PRISIONEIRO          = 'blue'
COR_NO_MINOTAURO            = 'red'
COR_NO_DESTINO_MINOTAURO    = 'lightcoral'
COR_NO_SAIDA                = 'green'
COR_NO_ENTRADA              = 'cyan'
COR_NO_VISITADO             = '#ADD8E6'
COR_NO_NAO_VISITADO         = '#E0E0E0'

## --- Estilo das Arestas (Linhas) ---
LARGURA_ARESTA_NORMAL       = 1.0
COR_ARESTA_NORMAL           = '#CCCCCC'
LARGURA_ARESTA_CAMINHO      = 2.0
COR_ARESTA_CAMINHO          = 'blue'
ESTILO_ARESTA_CAMINHO       = 'dashed'

## --- Estilo das Fontes e Rótulos ---
TAMANHO_FONTE_NO            = 8
TAMANHO_FONTE_PESO          = 7
COR_FONTE_PESO              = 'dimgray'
POSICAO_LABEL_PESO          = 0.3

# --------------------------------------------------------------------------
# ALGORITMOS EM GRAFOS
# --------------------------------------------------------------------------

def dijkstra(grafo, inicio):
    """
    Implementação do Algoritmo de Dijkstra para encontrar os caminhos mais
    curtos em um grafo ponderado a partir de um nó de início.
    """
    # Passo 1: Inicialização
    # Cria um dicionário para armazenar a distância mínima de 'inicio' até cada vértice.
    # Todos começam com uma distância infinita, pois ainda não foram alcançados.
    distancias = {vertice: float('infinity') for vertice in grafo}
    
    # O nó de início para ele mesmo tem distância 0.
    if inicio not in distancias: return {}, {} 
    distancias[inicio] = 0
    
    # Dicionário que guardará o predecessor de cada vértice no caminho mais curto.
    # Essencial para reconstruir o caminho no final.
    predecessores = {vertice: None for vertice in grafo}
    
    # Fila de prioridades (min-heap) para determinar qual vértice visitar a seguir.
    # Ela armazena tuplas de (distância, vértice), e o heapq sempre nos dará
    # o vértice com a menor distância, garantindo a eficiência do algoritmo.
    fila_prioridade = [(0, inicio)]
    
    # Passo 2: Loop Principal
    # O algoritmo continua enquanto houver vértices na fila para serem processados.
    while fila_prioridade:
        # Pega o vértice da fila com a menor distância.
        dist_atual, vertice_atual = heapq.heappop(fila_prioridade)

        # Otimização: se já encontramos um caminho mais curto para este vértice,
        # podemos ignorar esta entrada na fila (que é de uma iteração anterior).
        if dist_atual > distancias[vertice_atual]:
            continue

        # Passo 3: Relaxamento das Arestas
        # Para o vértice atual, olhamos para todos os seus vizinhos.
        for vizinho, atributos_aresta in grafo.get(vertice_atual, {}).items():
            peso = atributos_aresta['weight']
            
            # Calcula a distância do nó de início até este vizinho, passando pelo vértice atual.
            distancia = dist_atual + peso
            
            # Se encontramos um caminho para o vizinho que é mais curto do que
            # qualquer caminho anteriormente registrado, nós o atualizamos.
            if distancia < distancias[vizinho]:
                distancias[vizinho] = distancia
                predecessores[vizinho] = vertice_atual
                heapq.heappush(fila_prioridade, (distancia, vizinho))
                
    # Retorna os dicionários de distâncias e predecessores.
    return distancias, predecessores

def reconstruir_caminho(predecessores, inicio, fim):
    """
    Reconstrói um caminho a partir de um dicionário de predecessores
    gerado pelo algoritmo de Dijkstra.
    """
    caminho = []
    vertice_atual = fim # Começa pelo fim do caminho.
    
    # Loop que "volta" no tempo, do fim ao início, usando o mapa de predecessores.
    while vertice_atual is not None:
        caminho.append(vertice_atual)
        if vertice_atual == inicio: break # Se chegamos ao início, o caminho está completo.
        vertice_atual = predecessores.get(vertice_atual)
        
    # Como o caminho foi construído de trás para frente, o invertemos para a ordem correta.
    return caminho[::-1]

# --------------------------------------------------------------------------
# CLASSE PARA REPRESENTAR O LABIRINTO
# --------------------------------------------------------------------------
class Labirinto:
    """
    Representa o labirinto, carregando sua estrutura e parâmetros
    a partir de um arquivo de texto.
    """
    def __init__(self, nome_arquivo):
        # Inicializa os atributos do labirinto.
        self.grafo = {}
        self.entrada, self.saida, self.pos_inicial_minotauro = None, None, None
        self.percepcao_minotauro, self.tempo_maximo = 0, 0
        self.num_vertices, self.num_arestas = 0, 0
        
        # Carrega os dados do arquivo de configuração.
        self.carregar_de_arquivo(nome_arquivo)

    def adicionar_aresta(self, u, v, peso):
        """Adiciona uma aresta bidirecional ponderada ao grafo."""
        if u not in self.grafo: self.grafo[u] = {}
        if v not in self.grafo: self.grafo[v] = {}
        # A estrutura {'weight': peso} é usada para compatibilidade com a biblioteca NetworkX.
        self.grafo[u][v] = {'weight': peso}
        self.grafo[v][u] = {'weight': peso}

    def carregar_de_arquivo(self, nome_arquivo):
        """Lê e interpreta o arquivo de texto do labirinto."""
        print(f"Carregando labirinto do arquivo '{nome_arquivo}'...")
        lendo_arestas = False
        with open(nome_arquivo, 'r') as f:
            for linha in f:
                linha = linha.strip()
                # Ignora linhas vazias ou comentários.
                if not linha or linha.startswith('#'): continue
                
                # Ativa o modo de leitura de arestas ao encontrar a tag 'ARESTAS:'.
                if linha.upper() == 'ARESTAS:':
                    lendo_arestas = True; continue
                
                # Se não estiver lendo arestas, processa os parâmetros chave-valor.
                if not lendo_arestas and ':' in linha:
                    chave, valor_str = map(str.strip, linha.split(':', 1))
                    valor = int(valor_str)
                    
                    if chave == 'NUM_VERTICES': self.num_vertices = valor
                    elif chave == 'NUM_ARESTAS': self.num_arestas = valor
                    elif chave == 'ENTRADA': self.entrada = valor
                    elif chave == 'SAIDA': self.saida = valor
                    elif chave == 'MINOTAURO_INICIO': self.pos_inicial_minotauro = valor
                    elif chave == 'PERCEPCAO_DISTANCIA': self.percepcao_minotauro = valor
                    elif chave == 'TEMPO_MAXIMO': self.tempo_maximo = valor
                
                # Se estiver lendo arestas, processa a definição da aresta.
                elif lendo_arestas:
                    u, v, peso = map(int, linha.split())
                    self.adicionar_aresta(u, v, peso)
        print("Labirinto carregado com sucesso!")

# --------------------------------------------------------------------------
# CLASSES DOS PERSONAGENS
# --------------------------------------------------------------------------
class Prisioneiro:
    """Representa o Prisioneiro e sua lógica de movimento de exploração (DFS)."""
    def __init__(self, pos_inicial):
        self.posicao_atual = pos_inicial
        self.caminho_percorrido = [pos_inicial] # Log de todos os vértices visitados em ordem.
        self.visitados = {pos_inicial}          # Conjunto de vértices únicos já visitados.
        self.pilha_dfs = [pos_inicial]          # Pilha para a lógica de backtracking do DFS.

    def mover(self, labirinto):
        """
        Executa um passo de movimento usando uma estratégia de Busca em Profundidade (DFS)
        para explorar o labirinto de forma sistemática.
        """
        if not self.pilha_dfs: return

        # O topo da pilha sempre representa a posição atual na exploração.
        pos_atual_dfs = self.pilha_dfs[-1]
        
        # Passo 1: Tenta Explorar um Novo Caminho
        # Procura por um vizinho não visitado em ordem numérica (para ser determinístico).
        for vizinho in sorted(labirinto.grafo.get(pos_atual_dfs, {}).keys()):
            if vizinho not in self.visitados:
                # Se encontrou um vizinho novo, avança:
                self.visitados.add(vizinho)              # 1. Marca como visitado.
                self.pilha_dfs.append(vizinho)             # 2. Empilha o novo vértice ("desenrola o novelo").
                self.posicao_atual = vizinho             # 3. Move o personagem.
                self.caminho_percorrido.append(self.posicao_atual)
                return                                   # 4. Termina a lógica para este turno.
        
        # Passo 2: Faz o Backtracking (Retorno)
        # Se o loop 'for' terminar, não há vizinhos não visitados (beco sem saída).
        self.pilha_dfs.pop() # "Recolhe o novelo de lã", removendo a posição atual da pilha.
        
        # Move o personagem para a posição anterior (o novo topo da pilha).
        if self.pilha_dfs:
            self.posicao_atual = self.pilha_dfs[-1]
            self.caminho_percorrido.append(self.posicao_atual)

class Minotauro:
    """Representa o Minotauro e sua lógica de patrulha e perseguição."""
    def __init__(self, pos_inicial):
        self.posicao_atual = pos_inicial
        self.perseguindo = False
        self.vivo = True
        self.caminho_patrulha = [] # Armazena o caminho a ser seguido na patrulha.

    def mover(self, labirinto, pos_prisioneiro):
        """Executa a lógica de movimento do Minotauro para um turno."""
        if not self.vivo: return

        # Fase 1: Percepção
        # Usa Dijkstra para saber a distância até o prisioneiro.
        distancias, predecessores = dijkstra(labirinto.grafo, self.posicao_atual)
        dist_ate_prisioneiro = distancias.get(pos_prisioneiro, float('inf'))
        perseguindo_agora = dist_ate_prisioneiro <= labirinto.percepcao_minotauro
        
        # Fase 2: Decisão de Movimento (Perseguição ou Patrulha)
        if perseguindo_agora:
            # Lógica de Perseguição
            if not self.perseguindo:
                print(f"!!! MINOTAURO DETECTOU O PRISIONEIRO a uma distância de {dist_ate_prisioneiro} !!!")
            self.perseguindo, self.caminho_patrulha = True, [] # Abandona a patrulha
            caminho_perseguicao = reconstruir_caminho(predecessores, self.posicao_atual, pos_prisioneiro)
            
            # Move-se dois vértices por turno durante a perseguição.
            if len(caminho_perseguicao) > 2: self.posicao_atual = caminho_perseguicao[2]
            elif len(caminho_perseguicao) > 1: self.posicao_atual = caminho_perseguicao[1]
        
        else:
            # Lógica de Patrulha Inteligente
            if self.perseguindo: print("Minotauro perdeu o rastro.")
            self.perseguindo = False
            
            # Se a patrulha terminou ou não existe, cria uma nova.
            if not self.caminho_patrulha or len(self.caminho_patrulha) <= 1:
                todos_os_nos = list(labirinto.grafo.keys())
                if len(todos_os_nos) > 1:
                    nos_candidatos = [n for n in todos_os_nos if n != self.posicao_atual]
                    destino_patrulha = random.choice(nos_candidatos)
                else: destino_patrulha = self.posicao_atual
                
                _, pred_patrulha = dijkstra(labirinto.grafo, self.posicao_atual)
                self.caminho_patrulha = reconstruir_caminho(pred_patrulha, self.posicao_atual, destino_patrulha)

            # Move-se um passo ao longo do caminho de patrulha.
            if self.caminho_patrulha and len(self.caminho_patrulha) > 1:
                self.posicao_atual = self.caminho_patrulha[1]
                self.caminho_patrulha.pop(0) # Remove a posição antiga da lista.
            else:
                self.caminho_patrulha = []

# --------------------------------------------------------------------------
# FUNÇÕES AUXILIARES
# --------------------------------------------------------------------------
def carregar_posicoes(nome_arquivo, nos_do_grafo):
    """
    Lê o arquivo de posições para o layout visual do grafo.
    Se a configuração USAR_LAYOUT_DE_GRADE for False, ou se o arquivo não for
    encontrado, retorna um layout automático.
    """
    # Verifica o toggle de configuração para o tipo de layout.
    if not USAR_LAYOUT_DE_GRADE:
        print("Usando layout automático (spring_layout) por configuração.")
        return nx.spring_layout(nx.Graph(nos_do_grafo), seed=42)

    # Tenta carregar o arquivo de layout em grade.
    posicoes = {}
    try:
        with open(nome_arquivo, 'r') as f:
            for linha in f:
                partes = linha.split(); posicoes[int(partes[0])] = (float(partes[1]), float(partes[2]))
        print("Layout em grade carregado a partir do arquivo 'posicoes.txt'.")
    except FileNotFoundError:
        # Fallback para o layout automático caso o arquivo não exista.
        print(f"Aviso: Arquivo '{nome_arquivo}' não encontrado. Usando layout automático.")
        return nx.spring_layout(nx.Graph(nos_do_grafo), seed=42)
    
    return posicoes

def desenhar_labirinto(labirinto, prisioneiro, minotauro, posicoes_layout, turno, posicao_batalha=None, resultado_final=""):
    """Renderiza um frame da simulação usando Matplotlib."""
    plt.clf() # Limpa o frame anterior.
    G = nx.Graph(labirinto.grafo)
    
    # Desenha os elementos visuais em camadas.
    nx.draw_networkx_edges(G, pos=posicoes_layout, edge_color=COR_ARESTA_NORMAL, width=LARGURA_ARESTA_NORMAL)
    
    # Desenha o "novelo de lã" do prisioneiro.
    if len(prisioneiro.caminho_percorrido) > 1:
        arestas_do_caminho = list(zip(prisioneiro.caminho_percorrido, prisioneiro.caminho_percorrido[1:]))
        nx.draw_networkx_edges(G, pos=posicoes_layout, edgelist=arestas_do_caminho, edge_color=COR_ARESTA_CAMINHO, width=LARGURA_ARESTA_CAMINHO, style=ESTILO_ARESTA_CAMINHO)
        
    # Desenha o caminho de patrulha do Minotauro.
    if not minotauro.perseguindo and len(minotauro.caminho_patrulha) > 1:
        arestas_patrulha = list(zip(minotauro.caminho_patrulha, minotauro.caminho_patrulha[1:]))
        nx.draw_networkx_edges(G, pos=posicoes_layout, edgelist=arestas_patrulha, edge_color=COR_NO_MINOTAURO, width=1.5, style='dotted')

    # Determina o nó de destino da patrulha para destaque.
    destino_minotauro = None
    if not minotauro.perseguindo and minotauro.caminho_patrulha:
        destino_minotauro = minotauro.caminho_patrulha[-1]

    # Define a cor de cada nó com base no estado atual da simulação.
    cores_nos = []
    for node in G.nodes():
        # Lógica especial para colorir o nó da batalha no frame final.
        if node == posicao_batalha:
            if "Vitória milagrosa" in resultado_final: cores_nos.append(COR_NO_PRISIONEIRO); continue
            elif "derrotado" in resultado_final: cores_nos.append(COR_NO_MINOTAURO); continue
        
        # Define a cor com base na hierarquia de prioridade.
        if node == prisioneiro.posicao_atual: cores_nos.append(COR_NO_PRISIONEIRO)
        elif minotauro.vivo and node == minotauro.posicao_atual: cores_nos.append(COR_NO_MINOTAURO)
        elif node == labirinto.saida: cores_nos.append(COR_NO_SAIDA)
        elif node == labirinto.entrada: cores_nos.append(COR_NO_ENTRADA)
        elif node == destino_minotauro: cores_nos.append(COR_NO_DESTINO_MINOTAURO)
        elif node in prisioneiro.visitados: cores_nos.append(COR_NO_VISITADO)
        else: cores_nos.append(COR_NO_NAO_VISITADO)
        
    # Desenha os nós e seus rótulos.
    nx.draw_networkx_nodes(G, pos=posicoes_layout, node_color=cores_nos, node_size=TAMANHO_NO)
    nx.draw_networkx_labels(G, pos=posicoes_layout, font_size=TAMANHO_FONTE_NO, font_weight='bold')
    
    # Desenha os rótulos de peso nas arestas.
    pesos = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos=posicoes_layout, edge_labels=pesos, font_size=TAMANHO_FONTE_PESO, font_color=COR_FONTE_PESO, label_pos=POSICAO_LABEL_PESO)
    
    # Atualiza os títulos da janela e do gráfico.
    plt.title(f"Turno: {turno} | Tempo Restante: {labirinto.tempo_maximo - turno}")
    titulo_janela = f"Simulação: Labirinto de Creta | Turno {turno} de {labirinto.tempo_maximo}"
    plt.gcf().canvas.manager.set_window_title(titulo_janela)
    
    # Renderiza o frame e pausa a execução para criar a animação.
    plt.draw()
    plt.pause(VELOCIDADE_SIMULACAO_SEGUNDOS)

def imprimir_relatorio_final(resultado, tempo_restante, prisioneiro, turno_final, turno_deteccao, turno_batalha, caminho_perseguicao):
    """Exibe o relatório final da simulação no console."""
    print("\n" + "="*40 + "\n--- RELATÓRIO FINAL DA SIMULAÇÃO ---\n" + "="*40)
    print(f"Resultado: {resultado}")
    print(f"Turno Final: {turno_final}")
    print(f"Tempo Restante: {tempo_restante}")
    print(f"\nSequência de vértices visitados pelo prisioneiro ({len(prisioneiro.caminho_percorrido)} passos):")
    print(" -> ".join(map(str, prisioneiro.caminho_percorrido)))
    
    # Exibe informações de detecção e perseguição, se ocorreram.
    if turno_deteccao is not None:
        print(f"\nO Minotauro detectou o prisioneiro no turno: {turno_deteccao}")
        print("Caminho percorrido pelo Minotauro durante a perseguição:")
        print(" -> ".join(map(str, caminho_perseguicao)))
        if turno_batalha is not None:
            print(f"A batalha ocorreu no turno: {turno_batalha}")
    else:
        print("\nO Minotauro nunca detectou o prisioneiro.")
    print("="*40)

# --------------------------------------------------------------------------
# LOOP PRINCIPAL DA SIMULAÇÃO
# --------------------------------------------------------------------------
def main():
    """Função principal que orquestra a execução da simulação."""
    # Inicialização: Carrega o labirinto e os personagens.
    try:
        labirinto = Labirinto(ARQUIVO_LABIRINTO)
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{ARQUIVO_LABIRINTO}' não encontrado. Execute o 'gerador_de_configuracao.py' primeiro.")
        return

    prisioneiro = Prisioneiro(labirinto.entrada)
    minotauro = Minotauro(labirinto.pos_inicial_minotauro)
    
    # Inicialização das variáveis de log para o relatório final.
    resultado_final = ""
    turno_deteccao, turno_batalha, posicao_batalha = None, None, None
    caminho_perseguicao_minotauro = []
    
    posicoes_layout = carregar_posicoes(ARQUIVO_POSICOES, labirinto.grafo)
    
    # Configuração da janela Matplotlib para modo interativo.
    plt.ion(); plt.figure(figsize=TAMANHO_JANELA); turno = 0

    # Loop principal, executado a cada turno da simulação.
    for turno in range(1, labirinto.tempo_maximo + 1):
        
        # Lógica de movimento dos personagens.
        prisioneiro.mover(labirinto)
        minotauro.mover(labirinto, prisioneiro.posicao_atual)
        
        # Registra os dados de log do turno atual.
        if minotauro.perseguindo and minotauro.vivo:
            if turno_deteccao is None: turno_deteccao = turno
            caminho_perseguicao_minotauro.append(minotauro.posicao_atual)
            
        # Lógica de encontro e batalha.
        if minotauro.vivo and minotauro.posicao_atual == prisioneiro.posicao_atual:
            turno_batalha, posicao_batalha = turno, minotauro.posicao_atual
            print("\n--- ENCONTRO! UMA BATALHA SE INICIA! ---")
            if random.random() <= CHANCE_VITORIA_PRISIONEIRO:
                resultado_final = "Vitória milagrosa! O Prisioneiro derrotou o Minotauro!"
                print(f"Resultado da Batalha: {resultado_final}"); minotauro.vivo = False
            else:
                resultado_final = "O Prisioneiro foi derrotado e devorado pelo Minotauro."
                print(f"Resultado da Batalha: {resultado_final}")
                # Desenha o frame da derrota antes de encerrar o loop.
                desenhar_labirinto(labirinto, prisioneiro, minotauro, posicoes_layout, turno, posicao_batalha, resultado_final)
                break
        
        # Desenha o estado atual do labirinto.
        desenhar_labirinto(labirinto, prisioneiro, minotauro, posicoes_layout, turno, posicao_batalha, resultado_final)

        # Condição de vitória do prisioneiro.
        if prisioneiro.posicao_atual == labirinto.saida:
            resultado_final = "O Prisioneiro encontrou a saída e escapou!"; break

    # Se o loop terminar por tempo, define o resultado final.
    if not resultado_final:
        resultado_final = "O tempo acabou! O Prisioneiro não conseguiu escapar."
    
    # Gera o relatório de texto no console.
    imprimir_relatorio_final(
        resultado=resultado_final,
        tempo_restante=labirinto.tempo_maximo - turno,
        prisioneiro=prisioneiro,
        turno_final=turno,
        turno_deteccao=turno_deteccao,
        turno_batalha=turno_batalha,
        caminho_perseguicao=caminho_perseguicao_minotauro
    )
    
    print("\nSimulação encerrada. A janela final mostra o último estado. Feche-a para terminar.")
    
    # Mantém a janela final aberta até que o usuário a feche.
    plt.ioff()
    plt.show()

# Ponto de entrada do script.
if __name__ == '__main__':
    main()