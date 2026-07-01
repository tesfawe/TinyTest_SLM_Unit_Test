def edit_modified_distance_dp(pattern,text):

    dp_matrix = [[0 for _ in range(len(text)+1)] for _ in range(len(pattern)+1)]
    for v in range(len(pattern)+1): dp_matrix[v][0] = v
    for h in range(len(text)+1): dp_matrix[0][h] = h
    # Compute DP Matrix
    for h in range(1,len(text)+1):
        for v in range(1,len(pattern)+1):
            dp_matrix[v][h]=min(dp_matrix[v - 1][h - 1] + (0 if pattern[v - 1] == text[h - 1] else 1),
            dp_matrix[v][h - 1] + 1,dp_matrix[v - 1][h] + 1)
            if v > 1 and h > 1 and pattern[v-1] == text[h - 2] and pattern[v - 2] == text[h-1]: # The tranposition condition.
                dp_matrix[v][h] = min(dp_matrix[v][h], dp_matrix[v - 2][h - 2] + 1)
    
    return dp_matrix
