def decode_address_entry(string, sort=False):

    sections = string.split(":")
    sec_len = len(sections)

    if sec_len > 3:
        print("Error in string ", string)
        return []

    # do everything backwards
    # asics
    asics = []
    if sec_len == 3 and len(sections[2]) > 0:
        _asics = sections[2].split(",")
        asics = [int(a)-1 for a in _asics if int(a) in range(1, 3)]
    else:
        asics = [0, 1]

    # asics
    cables = []
    if sec_len >= 2 and len(sections[1]) > 0:
        _cables = sections[1].split(",")
        cables = [int(c)-1 for c in _cables if int(c) in range(1, 4)]
    else:
        cables = [0, 1, 2]

    # check address
    address = sections[0]
    if len(address) == 6:
        if address[0:2] != "0x":
            print("Incorrect address in string: ", string)
            return []
    elif len(address) == 4:
        address = "0x" + address
    else:
        print("Incorrect address in string: ", string)
        return []

    if sort:
        tup = [[x] + [y] + [z] for x in [address, ] for y in cables for z in asics]
    else:
        tup = [[x] + [y] + [z] for x in [address, ] for z in asics for y in cables]

    return tup