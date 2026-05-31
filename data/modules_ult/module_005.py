def _remove_strings(code):
    removed_string = ""
    is_string_now = None

    for i in range(0, len(code)-1):
        append_this_turn = False

        if code[i] == "'" and (i == 0 or code[i-1] != '\\'):
            if is_string_now == "'":
                is_string_now = None

            elif is_string_now is None:
                is_string_now = "'"
                append_this_turn = True

        elif code[i] == '"' and (i == 0 or code[i-1] != '\\'):
            if is_string_now == '"':
                is_string_now = None

            elif is_string_now is None:
                is_string_now = '"'
                append_this_turn = True

        if is_string_now is None or append_this_turn:
            removed_string += code[i]

    return removed_string