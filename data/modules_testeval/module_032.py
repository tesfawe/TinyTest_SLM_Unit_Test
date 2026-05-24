from typing import List

def findNumberOfLIS(nums: List[int]) -> int:
  ans = 0
  maxLength = 0
  length = [1] * len(nums)
  count = [1] * len(nums)

  for i, num in enumerate(nums):
    for j in range(i):
      if nums[j] < num:
        if length[i] < length[j] + 1:
          length[i] = length[j] + 1
          count[i] = count[j]
        elif length[i] == length[j] + 1:
          count[i] += count[j]

  for i, l in enumerate(length):
    if l > maxLength:
      maxLength = l
      ans = count[i]
    elif l == maxLength:
      ans += count[i]

  return ans
