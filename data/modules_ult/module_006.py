def point_box_relation(u, vbox):
    uy, ux = u
    vy0, vx0, vy1, vx1 = vbox
    if (ux < vx0 and uy <= vy0) or (ux == vx0 and uy == vy0):
        relation = 0  
    elif vx0 <= ux < vx1 and uy <= vy0:
        relation = 3 
    elif (vx1 <= ux and uy < vy0) or (ux == vx1 and uy == vy0):
        relation = 8 
    elif vx1 <= ux and vy0 <= uy < vy1:
        relation = 7  
    elif (vx1 < ux and vy1 <= uy) or (ux == vx1 and uy == vy1):
        relation = 9  
    elif vx0 < ux <= vx1 and vy1 <= uy:
        relation = 6  
    elif (ux <= vx0 and vy1 < uy) or (ux == vx0 and uy == vy1):
        relation = 1  
    elif ux <= vx0 and vy0 < uy <= vy1:
        relation = 2  
    elif vx0 < ux < vx1 and vy0 < uy < vy1:
        relation = 4 
    else:
        relation = None
    return relation