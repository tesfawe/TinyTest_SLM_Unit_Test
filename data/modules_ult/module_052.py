
FUNCTIONS = ['up', 'down', 'left', 'right']

def find_repeat(directions: list) -> list:
    max_match = 4

    # skip compressed patterns
    start_index = 0
    for start_index, direction in enumerate(directions):
        if direction not in FUNCTIONS:
            break

    # index for first pattern
    end_index = start_index

    # index for second pattern
    second_index = end_index + 2

    # directions matched
    match_count = 0

    # look until all results exhausted
    while second_index < len(directions):
        # compare and move to next character
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
            # found a match
            if match_count > 1:
                end_index -= 1
                break
            # no matching pattern restart check
            else:
                end_index = start_index
                match_count = 0

        second_index += 1

    return directions[start_index: end_index + 1]
