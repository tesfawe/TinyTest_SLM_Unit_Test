from typing import List

def findRedundantConnection(edges: List[List[int]]) -> List[int]:
    id = list(range(len(edges) + 1))
    rank = [0] * (len(edges) + 1)

    def find(u: int) -> int:
        if id[u] != u:
            id[u] = find(id[u])
        return id[u]

    def unionByRank(u: int, v: int) -> bool:
        i = find(u)
        j = find(v)

        if i == j:
            return False

        if rank[i] < rank[j]:
            id[i] = j
        elif rank[i] > rank[j]:
            id[j] = i
        else:
            id[i] = j
            rank[j] += 1

        return True

    for edge in edges:
        u, v = edge
        if not unionByRank(u, v):
            return edge