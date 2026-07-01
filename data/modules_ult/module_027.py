def b_TP_FN_sentence(train):
    tp = 0
    fn = 0
    tmp_t = ""
    tmp_r = ""
    for i in range(len(train)):
        if(train[i][0] != '_'):
            tmp_t += train[i][0]
            tmp_r += train[i][1]
        elif(train[i][0] == '_'):
            if(tmp_t == tmp_r and tmp_t !="" and tmp_r != ""):
                tp += 1
            elif(tmp_t != tmp_r and tmp_t !="" and tmp_r != ""):
                fn += 1
            tmp_r = ""
            tmp_t = ""
    return tp, fn
