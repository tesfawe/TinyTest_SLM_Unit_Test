
def get_intersect_point(v1, v2, width, height):
    x1, y1, x2, y2 = *v1, *v2
    if x2 - x1 == 0:
        k = None
    else:
        k = (y2 - y1) / (x2 - x1)
    if k is not None:
        b = y1 - k * x1
        x_max, x_min = max(x1, x2), min(x1, x2)
        y_max, y_min = max(y1, y2), min(y1, y2)

        if b >= 0 and b <= y_max and b >= y_min:
            return [0, round(b)]

        y_right = width * k + b
        if y_right >= 0 and y_right <= y_max and y_right >= y_min:
            return [width, round(y_right)]

        x_top = (-1) * b / k
        if x_top >= 0 and x_top <= x_max and x_top >= x_min:
            return [round(x_top), 0]

        x_bot = (height - b) / k
        if x_bot >= 0 and x_bot <= x_max and x_bot >= x_min:
            return [round(x_bot), height]

    return None
