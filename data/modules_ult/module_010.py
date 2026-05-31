def maximal_matching_pairs(string):
    n = len(string)
    for x in range(0, n - 1):
        for l in range(int((n - x)/2) + 1, 0, -1):
            c = string[x:x+l]
            y = string.find(c, x + 1)

            if y == -1 or y < x + l:
                continue

            if (y + l < n and x + l < y and string[x+l] == string[y+l]) or \
               (x - 1 >= 0 and x + l < y and string[x-1] == string[y-1]):
                continue

            if any(string[x:x+l+i] == string[y-i:y+l]
                   for i in range(1, (y - x - l)/2 + 1)):
                continue

            if any(string[x-i:x+l] == string[y:y+l+i]
                   for i in range(1, max(x, n - y - l) + 1)):
                continue

            yield x, y, l