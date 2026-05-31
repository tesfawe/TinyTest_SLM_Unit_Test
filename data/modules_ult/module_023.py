def windows_k_distinct(x, k):
    dist, i, j = 0, 0, 0                # dist = |{x[i], ..., x[j-1]}|
    occ = {xi: 0 for xi in x}           # number of occurrences in x[i:j]
    while j < len(x):
        while dist == k:                # move start of interval
            occ[x[i]] -= 1              # update counters
            if occ[x[i]] == 0:
                dist -= 1
            i += 1
        while j < len(x) and (dist < k or occ[x[j]]):
            if occ[x[j]] == 0:          # update counters
                dist += 1
            occ[x[j]] += 1
            j += 1                      # move end of interval
        if dist == k:
            yield (i, j)                # one interval found