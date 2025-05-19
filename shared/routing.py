from collections import deque

def calculate_route(start_id: str, end_id: str, graph: dict[str, set[str]]) -> list[str] | None:
    """
    Находит кратчайший маршрут от start_id до end_id в графе graph.
    graph: dict где ключ - agent_id, значение - множество соседних agent_id.
    Возвращает список agent_id маршрута или None, если маршрута нет.
    """
    if start_id == end_id:
        return [start_id]

    if start_id not in graph or end_id not in graph:
        return None

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
                if neighbor not in visited:
                    new_path = list(path)
                    new_path.append(neighbor)
                    queue.append(new_path)

    return None
