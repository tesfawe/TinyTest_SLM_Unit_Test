def longestNonWildcardSubsequence(opCodes, mask=None):
    start = 1
    end = 0
    if not mask:
        mask = "1"*len(opCodes[0])
    for x in range(len(mask)):
        for y in range(x, len(mask)):
            rangeGood = True
            for op in opCodes:
                for i in range(x, y+1):
                    if op[i] == "*" or mask[i] == "*":
                        rangeGood = False
                        break
                if not rangeGood:
                    break
            if rangeGood:
                if y-x > end-start:
                    end = y
                    start = x

    mask = [ c for c in mask ]

    for i in range(start, end+1):
        mask[i] = "*"

    return start, end, ''.join(mask)