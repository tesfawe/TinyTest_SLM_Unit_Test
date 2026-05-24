def minCut(s: str) -> int:
  n = len(s)
  isPalindrome=[]
  for _ in range(n):
    isPalindrome.append([True] * n)
  dp = [n] * n

  for l in range(2, n + 1):
    i = 0
    for j in range(l - 1, n):
      isPalindrome[i][j] = s[i] == s[j] and isPalindrome[i + 1][j - 1]
      i += 1

  for i in range(n):
    if isPalindrome[0][i]:
      dp[i] = 0
      continue

    for j in range(i):
      if isPalindrome[j + 1][i]:
        dp[i] = min(dp[i], dp[j] + 1)

  return dp[-1]
