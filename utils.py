def remove_quoted_text(twext):
    result = ""
    in_quotes = False
    for c in twext:
        if c is '"':
            in_quotes = not in_quotes
            continue
        if not in_quotes:
            result = result + c
    # Quotations were mismatched! Return original string.
    if in_quotes is True:
        return twext
    return result
    