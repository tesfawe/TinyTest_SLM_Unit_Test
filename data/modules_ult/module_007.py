def uoc_railfence_encrypt(message, key):

    ciphertext = ''

    rows = key[0]
    holes = key[1]
    
    cols = len(message)+len(holes)
    
    mat = [[0 for x in range(cols)] for y in range(rows)]

    j = 0
    i = 0
    m = 0
    while j < cols and m < len(message):
        pos = (i,j)
        if pos not in holes:
            mat[pos[0]][pos[1]] = message[m]
            m += 1
        if i==0:
            k = 1
        elif i==(rows-1):
            k = -1
        j += 1
        i += k

    for i in range(rows):
        for j in range(cols):
            elem = mat[i][j]
            if elem!=0:
                ciphertext=ciphertext+elem

    return ciphertext