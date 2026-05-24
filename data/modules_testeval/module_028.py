from typing import List

def findCircleNum(isConnected: List[List[int]]) -> int:
    n = len(isConnected)
    count = n
    id = list(range(n))
    rank = [0] * n

    def find(u: int) -> int:
        if id[u] != u:
            id[u] = find(id[u])
        return id[u]

    def unionByRank(u: int, v: int) -> None:
        nonlocal count

        i = find(u)
        j = find(v)

        if i == j:
            return

        if rank[i] < rank[j]:
            id[i] = j
        elif rank[i] > rank[j]:
            id[j] = i
        else:
            id[i] = j
            rank[j] += 1

        count -= 1

    for i in range(n):
        for j in range(i, n):
            if isConnected[i][j] == 1:
                unionByRank(i, j)

    return count