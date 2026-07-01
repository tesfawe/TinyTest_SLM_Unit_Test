def dinamic(a, b):

    dp = [[0 for i in range(len(b))] for j in range(len(a))]

    for i in range(0, len(a)):
        for j in range(0, len(b)):
            if i == 0:
                if a[i] == b[j] and dp[i][j] == 0:
                    dp[i][j] = 1
                else:
                    dp[i][j] = 0
            elif j == 0:
                if a[i] == b[j] and dp[i][j] == 0:
                    dp[i][j] = 1
                else:
                    dp[i][j] = 0
            elif a[i] == b[j]:
                dp[i][j] = 1 + dp[i-1][j-1]
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])

    return dp
