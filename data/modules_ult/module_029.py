def time_in_swiss_german(hour: int, minute: int) -> str:
    if hour < 6:
        period_of_day = "znacht"
    elif 6 <= hour < 12:
        period_of_day = "am morge"
    elif hour == 12:
        period_of_day = "am mittag"
    elif hour < 18:
        period_of_day = "am namittag"
    elif hour < 22:
        period_of_day = "am abig"
    else:
        period_of_day = "znacht"

    if hour == 0:
        clock_hour = 12
    elif hour > 12:
        clock_hour = hour - 12
    else:
        clock_hour = hour
    hour_suffix = "i" if clock_hour > 3 else ""

    if minute == 0:
        return f"{clock_hour}{hour_suffix} {period_of_day}"

    stated_hour = clock_hour if minute < 25 else clock_hour + 1

    if minute == 15:
        minute_part = "viertel ab"
    elif minute == 30:
        minute_part = "halbi"
    elif minute == 45:
        minute_part = "viertel vor"
    elif minute < 25:
        minute_part = f"{minute} ab"
    elif 25 <= minute < 30:
        minute_part = f"{30 - minute} vor halbi"
    elif 30 < minute <= 39:
        minute_part = f"{minute - 30} ab halbi"
    else:
        minute_part = f"{60 - minute} vor"

    result = f"{minute_part} {stated_hour}{hour_suffix} {period_of_day}"

    return result