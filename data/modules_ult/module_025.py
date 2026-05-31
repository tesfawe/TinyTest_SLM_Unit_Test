
FUNCTIONS = ['up', 'down', 'left', 'right']

def find_repeat(directions: list) -> list:
    max_match = 4
    start_index = 0
    for start_index, direction in enumerate(directions):
        if direction not in FUNCTIONS:
            break

    end_index = start_index
    second_index = end_index + 2
    match_count = 0

    while second_index < len(directions):
        if directions[end_index] == directions[second_index] \
                and directions[end_index] not in FUNCTIONS \
                and directions[second_index] not in FUNCTIONS:
            match_count += 1
            if match_count == max_match:
                break
            if end_index >= second_index - match_count + 1:
                match_count -= 1
                break
            else:
                end_index += 1
        else:
            if match_count > 1:
                end_index -= 1
                break
            else:
                end_index = start_index
                match_count = 0

        second_index += 1

    return directions[start_index: end_index + 1]
