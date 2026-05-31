def formatTime(time_diff: int):
    if time_diff < 0:  
        return "ERROR: Negative timeDiff"

    response = ["", "0 hours", "0 minutes", "0 seconds"]
    m, s = divmod(time_diff, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)

    if d == 1: response[0] = "1 day"
    elif d > 1: response[0] = "{} days".format(d)

    if h == 1: response[1] = "1 hour"
    elif h > 1: response[1] = "{} hours".format(h)

    if m == 1: response[2] = "1 minute"
    elif m > 1: response[2] = "{} minutes".format(m)

    if s == 1: response[3] = "1 second"
    elif s > 1: response[3] = "{} seconds".format(s)

    return response