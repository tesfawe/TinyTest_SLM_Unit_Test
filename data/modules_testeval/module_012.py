from typing import List

def getSkyline(buildings: List[List[int]]) -> List[List[int]]:
    def merge(left: List[List[int]], right: List[List[int]]) -> List[List[int]]:
        ans = []
        i = 0
        j = 0
        leftY = 0
        rightY = 0

        while i < len(left) and j < len(right):
            if left[i][0] < right[j][0]:
                leftY = left[i][1]
                addPoint(ans, left[i][0], max(left[i][1], rightY))
                i += 1
            else:
                rightY = right[j][1]
                addPoint(ans, right[j][0], max(right[j][1], leftY))
                j += 1

        while i < len(left):
            addPoint(ans, left[i][0], left[i][1])
            i += 1

        while j < len(right):
            addPoint(ans, right[j][0], right[j][1])
            j += 1

        return ans

    def addPoint(ans: List[List[int]], x: int, y: int) -> None:
        if ans and ans[-1][0] == x:
            ans[-1][1] = y
            return

        if ans and ans[-1][1] == y:
            return

        ans.append([x, y])

    n = len(buildings)

    if n == 0:
        return []

    if n == 1:
        left, right, height = buildings[0]
        return [[left, height], [right, 0]]

    left = getSkyline(buildings[:n // 2])
    right = getSkyline(buildings[n // 2:])

    return merge(left, right)