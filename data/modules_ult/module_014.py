def initiate_board():

    board_dict = {}
    ran = range(-3, 4)
    for (q, r) in [(q, r) for q in ran for r in ran if -q - r in ran]:
        if q == -3 and r >= 0:
            board_dict[(q, r)] = "red"
        elif q >= 0 and r == -3:
            board_dict[(q, r)] = "green"
        elif q+r == 3:
            board_dict[(q, r)] = "blue"

    return board_dict