import heapq
import sys

def solve():
    input = sys.stdin.read
    data = sys.stdin.read().split()
    
    idx = 0
    n = int(data[idx]); idx += 1
    m = int(data[idx]); idx += 1
    s = int(data[idx]); idx += 1
    t = int(data[idx]); idx += 1
    C = int(data[idx]); idx += 1
    
    # Создаем список смежности
    graph = [[] for _ in range(n + 1)]
    
    for _ in range(m):
        u = int(data[idx]); idx += 1
        v = int(data[idx]); idx += 1
        length = int(data[idx]); idx += 1
        cost_val = int(data[idx]); idx += 1
        graph[u].append((v, length, cost_val))
    
    # Инициализация двумерного массива расстояний
    INF = 10**18
    dist = [[INF] * (C + 1) for _ in range(n + 1)]
    dist[s][0] = 0
    
    # Очередь с приоритетом: (время, вершина, стоимость)
    pq = []
    heapq.heappush(pq, (0, s, 0))
    
    while pq:
        current_time, u, current_cost = heapq.heappop(pq)
        
        # Если это не актуальное состояние, пропускаем
        if current_time > dist[u][current_cost]:
            continue
        
        # Перебираем всех соседей
        for v, length, cost_val in graph[u]:
            new_cost = current_cost + cost_val
            new_time = current_time + length
            
            # Проверяем бюджетное ограничение
            if new_cost <= C and new_time < dist[v][new_cost]:
                dist[v][new_cost] = new_time
                heapq.heappush(pq, (new_time, v, new_cost))
    
    # Находим минимальное время достижения t в рамках бюджета
    answer = INF
    for cost in range(C + 1):
        if dist[t][cost] < answer:
            answer = dist[t][cost]
    
    if answer == INF:
        print(-1)
    else:
        print(answer)

if __name__ == "__main__":
    solve()