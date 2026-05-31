def uoc_railfence_encrypt(message, key):

    ciphertext = ''

    # --- IMPLEMENTATION GOES HERE ---

    #for the matrix fence we need rows, columns and hole positions
    rows = key[0]
    holes = key[1]
    
    #we know that we won't need more columns than characters of the message+number of holes (upper limit)
    cols = len(message)+len(holes)
    
    #generate an empty (all zeros) matrix of the required size
    mat = [[0 for x in range(cols)] for y in range(rows)]

    j = 0
    i = 0
    m = 0
    #for all columns and as long as we still have characters to allocate in our fance
    while j < cols and m < len(message):
        pos = (i,j)
        #if the position is not occupied by a hole, then write a character from the message
        if pos not in holes:
            mat[pos[0]][pos[1]] = message[m]
            m += 1
        #impose zig zag behaviour on the row indices to obtain the right positions
        if i==0:
            k = 1
        elif i==(rows-1):
            k = -1
        j += 1
        i += k

    #read the fence elements distinct to 0 by rows to obtain the cyphertext
    for i in range(rows):
        for j in range(cols):
            elem = mat[i][j]
            if elem!=0:
                ciphertext=ciphertext+elem

    # --------------------------------
    return ciphertext