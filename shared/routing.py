from collections import deque

def calculate_route(start_id: str, end_id: str, peers: dict[str, tuple]) -> list[str] | None:
    """
    Находит кратчайший маршрут от start_id до end_id в графе peers.
    peers: dict где ключ - agent_id, значение - (ip, port)
    Возвращает список agent_id маршрута или None, если маршрута нет.
    """
    if start_id == end_id:
        return [start_id]

    # Граф: у каждого пира — соседи
    # Для простоты считаем, что каждый peer связан с каждым (полносвязная сеть),
    # но в будущем можно расширить до реального графа с соседями.
    # Для демонстрации — просто смотрим peers.keys()
    
    # Формируем граф соседств (на будущее)
    graph = {}
    for agent in peers.keys():
        # Предположим, что каждый агент видит всех пиров (полносвязь)
        graph[agent] = set(peers.keys()) - {agent}

    # Если start или end нет в peers, маршрута нет
    if start_id not in graph or end_id not in graph:
        return None

    # BFS для поиска кратчайшего пути
    queue = deque([[start_id]])
    visited = set()

    while queue:
        path = queue.popleft()
        node = path[-1]
        if node == end_id:
            return path

        if node not in visited:
            visited.add(node)
            neighbors = graph.get(node, set())
            for neighbor in neighbors:
                new_path = list(path)
                new_path.append(neighbor)
                queue.append(new_path)

    # Если путь не найден
    return None
