def string_contrast(ss):
    s = [item + 'q' for item in ss if item is not None]
    short = min(s, key=len)
    for ib in range(len(short)):
        if not all([mc[ib] == short[ib] for mc in s]):
            preidx = ib
            break
    else:
        preidx = 0
    for ib in range(len(short)):
        ie = -1 * (ib + 1)
        if not all([mc[ie] == short[ie] for mc in s]):
            sufidx = ie + 1
            break
    else:
        sufidx = -1 * (len(short))

    miditer = iter([mc[preidx:sufidx] for mc in s])
    prefix = short[:preidx]
    suffix = short[sufidx:-1]
    middle = ['' if mc is None else next(miditer) for mc in ss]

    return prefix, suffix, middle