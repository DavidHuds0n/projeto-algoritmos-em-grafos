import random
import json
import heapq

# ==========================================================================
# --- CONFIGURAÇÕES DO GERADOR ---
# Altere os valores aqui para gerar labirintos de diferentes tamanhos e
# com diferentes dificuldades iniciais.
# ==========================================================================
LARGURA = 13
ALTURA = 9
DISTANCIA_MINIMA_INICIAL = 15 # Distância mínima (soma de pesos) que o Minotauro deve estar da entrada

# --------------------------------------------------------------------------
# ALGORITMO DE DIJKSTRA
# --------------------------------------------------------------------------
def dijkstra(grafo, inicio):
    """
    Implementação do Algoritmo de Dijkstra para calcular o caminho mais curto
    em um grafo ponderado. Retorna um dicionário com as distâncias.
    """
    distancias = {vertice: float('infinity') for vertice in grafo}
    if inicio not in distancias: return {}
    distancias[inicio] = 0
    fila_prioridade = [(0, inicio)]
    while fila_prioridade:
        dist_atual, vertice_atual = heapq.heappop(fila_prioridade)
        if dist_atual > distancias[vertice_atual]:
            continue
        for vizinho, atributos_aresta in grafo.get(vertice_atual, {}).items():
            peso = atributos_aresta['weight']
            distancia = dist_atual + peso
            if distancia < distancias[vizinho]:
                distancias[vizinho] = distancia
                heapq.heappush(fila_prioridade, (distancia, vizinho))
    return distancias

# --------------------------------------------------------------------------
# FUNÇÕES DE GERAÇÃO
# --------------------------------------------------------------------------
def criar_labirinto_em_grade(largura, altura):
    """
    Gera uma representação de labirinto em uma matriz 2D (grade) usando
    o algoritmo Recursive Backtracker.
    """
    if largura % 2 == 0: largura += 1
    if altura % 2 == 0: altura += 1
    grade = [['#' for _ in range(largura)] for _ in range(altura)]
    pilha = []
    inicio_x, inicio_y = random.randrange(1, largura, 2), random.randrange(1, altura, 2)
    grade[inicio_y][inicio_x] = ' '
    pilha.append((inicio_x, inicio_y))
    while pilha:
        x, y = pilha[-1]
        vizinhos = []
        for dx, dy in [(0, -2), (0, 2), (-2, 0), (2, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < largura and 0 <= ny < altura and grade[ny][nx] == '#':
                vizinhos.append((nx, ny))
        if vizinhos:
            prox_x, prox_y = random.choice(vizinhos)
            grade[(y + prox_y) // 2][(x + prox_x) // 2] = ' '
            grade[prox_y][prox_x] = ' '
            pilha.append((prox_x, prox_y))
        else:
            pilha.pop()
    grade[1][0] = 'E'
    grade[altura - 2][largura - 1] = 'S'
    return grade

def gerar_arquivos_de_configuracao(grade):
    """
    Converte a grade 2D em um grafo e salva os arquivos 'labirinto.txt' e
    'posicoes.txt' para a simulação.
    """
    mapa_coords_para_id = {}
    mapa_id_para_coords = {}
    
    # Numera apenas os caminhos (' '), garantindo que a entrada em (1,1) seja o vértice 1.
    entrada_coords = (1, 1)
    entrada_id = 1
    mapa_coords_para_id[entrada_coords] = entrada_id
    mapa_id_para_coords[entrada_id] = entrada_coords
    
    id_vertice_atual = 2
    for y in range(len(grade)):
        for x in range(len(grade[0])):
            if grade[y][x] == ' ':
                coords = (x, y)
                if coords not in mapa_coords_para_id:
                    mapa_coords_para_id[coords] = id_vertice_atual
                    mapa_id_para_coords[id_vertice_atual] = coords
                    id_vertice_atual += 1

    saida_id = mapa_coords_para_id.get((len(grade[0]) - 2, len(grade) - 2))

    # Constrói a estrutura do grafo e a lista de arestas
    grafo = {}
    arestas_str = []
    arestas_set = set()
    for coords, u_id in mapa_coords_para_id.items():
        if u_id not in grafo: grafo[u_id] = {}
        x, y = coords
        for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            vizinho_coords = (x + dx, y + dy)
            if vizinho_coords in mapa_coords_para_id:
                v_id = mapa_coords_para_id[vizinho_coords]
                aresta_ordenada = tuple(sorted((u_id, v_id)))
                if aresta_ordenada in arestas_set:
                    continue
                peso = random.randint(1, 5)
                if v_id not in grafo: grafo[v_id] = {}
                grafo[u_id][v_id] = {'weight': peso}
                grafo[v_id][u_id] = {'weight': peso}
                arestas_str.append(f"{u_id} {v_id} {peso}")
                arestas_set.add(aresta_ordenada)

    # Filtra os nós para garantir a distância mínima inicial do Minotauro
    distancias_da_entrada = dijkstra(grafo, entrada_id)
    nos_possiveis = list(mapa_id_para_coords.keys())
    if entrada_id: nos_possiveis.remove(entrada_id)
    if saida_id: nos_possiveis.remove(saida_id)
    
    nos_validos_para_minotauro = [
        no for no in nos_possiveis 
        if distancias_da_entrada.get(no, 0) >= DISTANCIA_MINIMA_INICIAL
    ]
    
    if nos_validos_para_minotauro:
        minotauro_inicio = random.choice(nos_validos_para_minotauro)
    else: # Fallback para labirintos pequenos
        minotauro_inicio = random.choice(nos_possiveis)
    
    # Salva o arquivo de configuração do labirinto com formatação melhorada
    with open('labirinto.txt', 'w') as f:
        f.write("# ============================================\n")
        f.write("# ARQUIVO DE CONFIGURAÇÃO DO LABIRINTO DE CRETA\n")
        f.write("# Gerado automaticamente.\n")
        f.write("# ============================================\n\n")
        
        num_vertices = len(mapa_id_para_coords)
        num_arestas = len(arestas_str)
        f.write("# --------------------------------------------\n")
        f.write("# PARÂMETROS GERAIS DO GRAFO\n")
        f.write("# --------------------------------------------\n")
        f.write(f"NUM_VERTICES: {num_vertices}\n")
        f.write(f"NUM_ARESTAS: {num_arestas}\n\n")
        
        f.write("# --------------------------------------------\n")
        f.write("# PARÂMETROS DA SIMULAÇÃO\n")
        f.write("# --------------------------------------------\n")
        f.write(f"ENTRADA: {entrada_id}\n")
        f.write(f"SAIDA: {saida_id}\n")
        f.write(f"MINOTAURO_INICIO: {minotauro_inicio}\n")
        f.write("PERCEPCAO_DISTANCIA: 8\n")
        f.write("TEMPO_MAXIMO: 150\n\n")

        f.write("# --------------------------------------------\n")
        f.write("# DEFINIÇÃO DAS ARESTAS (u, v, peso)\n")
        f.write("# --------------------------------------------\n")
        f.write("ARESTAS:\n")
        f.write("\n".join(arestas_str))
            
    # Salva o arquivo com as posições para a visualização
    with open('posicoes.txt', 'w') as f:
        for id_node, coords in mapa_id_para_coords.items():
            f.write(f"{id_node} {coords[0]} {-coords[1]}\n")

    print("Arquivos de configuração 'labirinto.txt' e 'posicoes.txt' gerados com sucesso!")

# --- EXECUÇÃO DO GERADOR ---
if __name__ == "__main__":
    grade_labirinto = criar_labirinto_em_grade(LARGURA, ALTURA)
    gerar_arquivos_de_configuracao(grade_labirinto)