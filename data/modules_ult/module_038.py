def rsplit_longest_suffix(uname, suffixes):
    minindex = len(uname)
    for suffix in suffixes:
        # FIXME: prevent suffix from starting with '_'?
        index = len(uname) - len(suffix)
        if index == 0 and uname == suffix:
            return None, suffix
        elif index > 0 and index < minindex and uname[index:] == suffix \
             and uname[index-1] == '_':
            minindex = index
    if minindex < len(uname):
        if minindex <= 1:
            return None, uname[minindex:]
        else:
            return uname[:minindex-1], uname[minindex:]
    else:
        return uname, None
