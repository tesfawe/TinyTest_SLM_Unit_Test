def tr_tet_tr_oct_cubo_coord_test(x, y, z):  # dist2 = 4
    x = abs(x) % 6
    y = abs(y) % 6
    z = abs(z) % 6
    if x > 3:
        x = 6-x
    if y > 3:
        y = 6-y
    if z > 3:
        z = 6-z
    dist2 = x**2 + y**2
    return ((z % 6 == 0 and (dist2 == 2 or dist2 == 8)) or
            (z % 6 == 1 and (dist2 == 1 or dist2 == 13)) or
            (z % 6 == 2 and (dist2 == 4 or dist2 == 10)) or
            (z % 6 == 3 and dist2 == 5))
