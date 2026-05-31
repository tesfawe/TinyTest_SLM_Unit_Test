def check_dead_corner(xanadu, other_objs):
    is_dead = True
    for other_obj in other_objs:
        if xanadu[0] < other_obj[0] or xanadu[1] < other_obj[1]:
            is_dead = False
            break
    if is_dead:
        return True

    is_dead = True
    for other_obj in other_objs:
        if xanadu[0] > other_obj[0] or xanadu[1] < other_obj[1]:
            is_dead = False
            break
    if is_dead:
        return True

    is_dead = True
    for other_obj in other_objs:
        if xanadu[0] < other_obj[0] or xanadu[1] > other_obj[1]:
            is_dead = False
            break
    if is_dead:
        return True

    is_dead = True
    for other_obj in other_objs:
        if xanadu[0] > other_obj[0] or xanadu[1] > other_obj[1]:
            is_dead = False
            break
    if is_dead:
        return True