def next_point_in_8_neigh(b, c):
    if c[0]-1 == b[0] and c[1]+1 == b[1]:
        return (b[0], b[1]-1)
    if c[0] == b[0] and c[1]+1 == b[1]:
        return (b[0]-1, b[1]-1)
    if c[0]+1 == b[0] and c[1]+1 == b[1]:
        return (b[0]-1, b[1])
    if c[0]+1 == b[0] and c[1] == b[1]:
        return (b[0]-1, b[1]+1)
    if c[0]+1 == b[0] and c[1]-1 == b[1]:
        return (b[0], b[1]+1)
    if c[0] == b[0] and c[1]-1 == b[1]:
        return (b[0]+1, b[1]+1)
    if c[0]-1 == b[0] and c[1]-1 == b[1]:
        return (b[0]+1, b[1])
    if c[0]-1 == b[0] and c[1] == b[1]:
        return (b[0]+1, b[1]-1)