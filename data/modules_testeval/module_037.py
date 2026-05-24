import math
from typing import List

def minStickers(stickers: List[str], target: str) -> int:
  maxMask = 1 << len(target)
  dp = [math.inf] * maxMask
  dp[0] = 0

  for mask in range(maxMask):
    if dp[mask] == math.inf:
      continue
    for sticker in stickers:
      superMask = mask
      for c in sticker:
        for i, t in enumerate(target):
          if c == t and not (superMask >> i & 1):
            superMask |= 1 << i
            break
      dp[superMask] = min(dp[superMask], dp[mask] + 1)

  return -1 if dp[-1] == math.inf else dp[-1]
