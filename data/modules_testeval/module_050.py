from typing import List, Dict
import collections

def minimumSubarrayLength(nums: List[int], k: int) -> int:
    ans = len(nums) + 1
    ors = 0
    count = collections.Counter()

    def orNum(ors: int, num: int, count: Dict[int, int]) -> int:
        for i in range(30):
            if (num >> i) & 1:
                count[i] += 1
                if count[i] == 1:
                    ors += 1 << i
        return ors

    def undoOrNum(ors: int, num: int, count: Dict[int, int]) -> int:
        for i in range(30):
            if (num >> i) & 1:
                count[i] -= 1
                if count[i] == 0:
                    ors -= 1 << i
        return ors

    l = 0
    for r, num in enumerate(nums):
        ors = orNum(ors, num, count)

        while ors >= k and l <= r:
            ans = min(ans, r - l + 1)
            ors = undoOrNum(ors, nums[l], count)
            l += 1

    return -1 if ans == len(nums) + 1 else ans