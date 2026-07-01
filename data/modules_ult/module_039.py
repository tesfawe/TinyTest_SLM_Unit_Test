def remove_chars(line, chars = ' \t', quotes = '\'\"', comments = None):
    new_line = ''
    quote_stack = ''
    remove_comments = (type(comments) is list) or (type(comments) is str)

    for c in line:

        if remove_comments and len(quote_stack) == 0 and c in comments:
            break

        if len(quote_stack) == 0 and c in chars:
            continue

        if c in quotes:
            if len(quote_stack) == 0 or c != quote_stack[-1]:
                quote_stack += c
            elif len(quote_stack) != 0:
                quote_stack = quote_stack[:-1]

            continue

        new_line += c

    return new_line
