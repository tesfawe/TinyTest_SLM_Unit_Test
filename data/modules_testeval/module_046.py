from typing import List

def validPath(n: int, edges: List[List[int]], source: int, destination: int) -> bool:
    parent = list(range(n))
    rank = [0] * n

    def find(u: int) -> int:
        if parent[u] != u:
            parent[u] = find(parent[u])
        return parent[u]

    def union(u: int, v: int) -> None:
        root_u = find(u)
        root_v = find(v)

        if root_u == root_v:
            return

        if rank[root_u] < rank[root_v]:
            parent[root_u] = root_v
        elif rank[root_u] > rank[root_v]:
            parent[root_v] = root_u
        else:
            parent[root_u] = root_v
            rank[root_v] += 1

    for u, v in edges:
        union(u, v)

    return find(source) == find(destination)