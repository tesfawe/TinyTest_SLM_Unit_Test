def point_box_relation(u, vbox):
    uy, ux = u
    vy0, vx0, vy1, vx1 = vbox
    if (ux < vx0 and uy <= vy0) or (ux == vx0 and uy == vy0):
        relation = 0  # 'left-above'
    elif vx0 <= ux < vx1 and uy <= vy0:
        relation = 3  # 'above'
    elif (vx1 <= ux and uy < vy0) or (ux == vx1 and uy == vy0):
        relation = 8  # 'right-above'
    elif vx1 <= ux and vy0 <= uy < vy1:
        relation = 7  # 'right-of'
    elif (vx1 < ux and vy1 <= uy) or (ux == vx1 and uy == vy1):
        relation = 9  # 'right-below'
    elif vx0 < ux <= vx1 and vy1 <= uy:
        relation = 6  # 'below'
    elif (ux <= vx0 and vy1 < uy) or (ux == vx0 and uy == vy1):
        relation = 1  # 'left-below'
    elif ux <= vx0 and vy0 < uy <= vy1:
        relation = 2  # 'left-of'
    elif vx0 < ux < vx1 and vy0 < uy < vy1:
        relation = 4  # 'inside'
    else:
        relation = None
    return relation