def count_leading_digits_var2(numd):

    # Initialize the repartition by ones to avoid division by zero error further ahead
    f=[1, 1, 1, 1, 1, 1, 1, 1, 1]
    
    for i in numd:
        c = str(int(i))[0]
        if c == '1':
            f[0] += 1
        elif c == '2':
            f[1] += 1;
        elif c == '3':
            f[2] += 1;
        elif c == '4':
            f[3] += 1;
        elif c == '5':
            f[4] += 1;
        elif c == '6':
            f[5] += 1;
        elif c == '7':
            f[6] += 1;
        elif c == '8':
            f[7] += 1;
        elif c == '9':
            f[8] += 1;
          
    return f
