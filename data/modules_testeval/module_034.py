from typing import List

def findRedundantDirectedConnection(edges: List[List[int]]) -> List[int]:
    parent = list(range(len(edges) + 1))
    rank = [0] * (len(edges) + 1)

    def find(u: int) -> int:
        if parent[u] != u:
            parent[u] = find(parent[u])
        return parent[u]

    def unionByRank(u: int, v: int) -> bool:
        i = find(u)
        j = find(v)

        if i == j:
            return False

        if rank[i] < rank[j]:
            parent[i] = j
        elif rank[i] > rank[j]:
            parent[j] = i
        else:
            parent[i] = j
            rank[j] += 1

        return True

    ids = [0] * (len(edges) + 1)
    nodeWithTwoParents = 0

    for _, v in edges:
        ids[v] += 1
        if ids[v] == 2:
            nodeWithTwoParents = v

    def check(skippedEdgeIndex: int) -> List[int]:
        nonlocal parent, rank

        parent = list(range(len(edges) + 1))
        rank = [0] * (len(edges) + 1)

        for i, edge in enumerate(edges):
            if i == skippedEdgeIndex:
                continue

            if not unionByRank(edge[0], edge[1]):
                return edge

        return []

    if nodeWithTwoParents == 0:
        return check(-1)

    for i in reversed(range(len(edges))):
        _, v = edges[i]

        if v == nodeWithTwoParents:
            if not check(i):
                return edges[i]