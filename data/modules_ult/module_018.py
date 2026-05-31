def _normalized_vcf(chr, pos, ref, alt):
    for i in range(max(len(ref), len(alt))):
        _ref = ref[i] if i < len(ref) else None
        _alt = alt[i] if i < len(alt) else None
        if _ref is None or _alt is None or _ref != _alt:
            break

    if _ref is None and _alt is None:
        raise ValueError('"ref" and "alt" cannot be the same: {}'.format(
            (chr, pos, ref, alt)
        ))

    _pos = int(pos)
    if _ref is None or _alt is None:
        _pos = _pos + i - 1
        _ref = ref[i - 1:]
        _alt = alt[i - 1:]
    else:
        _pos = _pos + i
        _ref = ref[i:]
        _alt = alt[i:]

    return chr, _pos, _ref, _alt