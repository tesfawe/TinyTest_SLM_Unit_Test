def is_degree_in_degree_range(degree_a, degree_b, degree_c):
    degrees_omni = [degree_a, degree_b, degree_c]

    for x in range(len(degrees_omni)):
        if degrees_omni[x] > 180 or degrees_omni[x] <= -180:
            degrees_omni[x] = -180 * (((degrees_omni[x] // 180) % 2) * degrees_omni[x]/abs(degrees_omni[x])) + (degrees_omni[x] % 180)

    degree_a = degrees_omni[0]
    degree_b = degrees_omni[1]
    degree_c = degrees_omni[2]

    clockwise = degree_a
    counterclock = degree_b

    if clockwise > counterclock:
        if degree_c <= clockwise and degree_c >= counterclock:
            return True
    elif clockwise < counterclock and clockwise <= 0 and counterclock > 0:
        if degree_c >= counterclock or degree_c <= clockwise:
            return True
    return False