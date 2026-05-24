from typing import List
import math

def maximumStrongPairXor(nums: List[int]) -> int:
    max_num = max(nums)
    max_bit = int(math.log2(max_num)) if max_num > 0 else 0

    children = []
    mins = []
    maxs = []

    def new_node():
        children.append([-1, -1])
        mins.append(math.inf)
        maxs.append(-math.inf)
        return len(children) - 1

    root = new_node()

    def insert(num: int) -> None:
        node = root

        for i in range(max_bit, -1, -1):
            bit = (num >> i) & 1

            if children[node][bit] == -1:
                children[node][bit] = new_node()

            node = children[node][bit]
            mins[node] = min(mins[node], num)
            maxs[node] = max(maxs[node], num)

    def getMaxXor(x: int) -> int:
        max_xor = 0
        node = root

        for i in range(max_bit, -1, -1):
            bit = (x >> i) & 1
            toggle_bit = bit ^ 1

            toggle_node = children[node][toggle_bit]

            if (
                toggle_node != -1
                and maxs[toggle_node] > x
                and mins[toggle_node] <= 2 * x
            ):
                max_xor |= 1 << i
                node = toggle_node
            elif children[node][bit] != -1:
                node = children[node][bit]
            else:
                return 0

        return max_xor

    for num in nums:
        insert(num)

    return max(getMaxXor(num) for num in nums)