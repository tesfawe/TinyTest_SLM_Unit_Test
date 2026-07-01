def _lcsmatrix(s1, s2):
    m = len(s1)
    n = len(s2) 
    mtx = [[0 for x in range(n)] for y in range(m)]
    for i,c1 in enumerate(s1):
        for j,c2 in enumerate(s2): 
            if c1 == c2 : 
                if i == 0 or j == 0:
                    mtx[i][j] = 1
                else:
                    mtx[i][j] = mtx[i-1][j-1]+1
            else :
                if j == 0: 
                    mtx[i][j] = mtx[i-1][j]
                elif i == 0:
                    mtx[i][j] = mtx[i][j-1]
                else :
                    mtx[i][j] = max(mtx[i][j-1],mtx[i-1][j])
    return mtx
