def check_dead_corner(xanadu, other_objs):
    # check whether the xanadu is at top right
    is_dead = True
    for other_obj in other_objs:
        if xanadu[0] < other_obj[0] or xanadu[1] < other_obj[1]:
            is_dead = False
            break
    if is_dead:
        return True

    # check whether the xanadu is at top left
    is_dead = True
    for other_obj in other_objs:
        if xanadu[0] > other_obj[0] or xanadu[1] < other_obj[1]:
            is_dead = False
            break
    if is_dead:
        return True

    # check whether the xanadu is at bottom right
    is_dead = True
    for other_obj in other_objs:
        if xanadu[0] < other_obj[0] or xanadu[1] > other_obj[1]:
            is_dead = False
            break
    if is_dead:
        return True

    # check whether the xanadu is at top right
    is_dead = True
    for other_obj in other_objs:
        if xanadu[0] > other_obj[0] or xanadu[1] > other_obj[1]:
            is_dead = False
            break
    if is_dead:
        return True