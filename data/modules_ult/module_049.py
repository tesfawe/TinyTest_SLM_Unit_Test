def stoprec_analysis_rltnshp(stoprecrange, analysisrange):
    rec_in = stoprecrange[0]
    rec_out = stoprecrange[1]
    a_start = analysisrange[0]
    a_end = analysisrange[1]
    
    if (rec_in > rec_out):
        return 'backwards'
    elif (a_start <= rec_in < a_end) and (a_start <= rec_out < a_end):
        return 'inner'
    elif (a_start <= rec_in < a_end) and (rec_out >= a_end):
        return 'right'
    elif (rec_in < a_start) and (a_start <= rec_out < a_end):
        return 'left'
    elif (rec_in < a_start) and (rec_out >= a_end):
        return 'outer'
    else:
        return 'none'
