def windows_k_distinct(x, k):
    dist, i, j = 0, 0, 0            
    occ = {xi: 0 for xi in x}          
    while j < len(x):
        while dist == k:                
            occ[x[i]] -= 1         
            if occ[x[i]] == 0:
                dist -= 1
            i += 1
        while j < len(x) and (dist < k or occ[x[j]]):
            if occ[x[j]] == 0:     
                dist += 1
            occ[x[j]] += 1
            j += 1                      
        if dist == k:
            yield (i, j)              