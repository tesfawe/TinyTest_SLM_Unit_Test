def x0x1_after_extraction(x0o: int, x1o: int, x0e: int, x1e: int):

    if x0e >= x0o and x0e <= x1o:
        x0 = 0
    elif x0e <= x0o:
        x0 = x0o - x0e
    elif x0e >= x0o:
        x0 = 0

    if x1e >= x0o and x1e <= x1o:
        x1 = x1e - x0e
    elif x1e > x1o:
        x1 = x1o - x0e

    try:
        if x0 < 0 or x1 < 0 or x0 == x1:
            return None, None
        else:
            return x0, x1
    except UnboundLocalError:
        return None, None
