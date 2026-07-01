def make_dp(arr, n, value):
    dp = [[False for i in range(value+1)] for j in range(n+1)]
    
    for i in range(n+1):
        for j in range(value+1):
            if j ==0:
                dp[i][j] = True
            elif i == 0:
                dp[i][j] = False
            else:
                if dp[i-1][j]:
                    dp[i][j] = True
                elif j >=arr[i-1]:
                    if dp[i-1][j-arr[i-1]]:
                        dp[i][j] = True
    return dp
