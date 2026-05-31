
def move_gain(match, i, m, nm, weight_dict, match_num_dict, match_num):
    cur_m = (i, nm)
    old_m = (i, m)
    new_match = match[:]
    new_match[i] = nm
    if tuple(new_match) in match_num_dict:
        return match_num_dict[tuple(new_match)] - match_num
    gain = 0
    if cur_m in weight_dict:
        gain += weight_dict[cur_m][-1]
        for k in weight_dict[cur_m]:
            if k == -1:
                continue
            elif match[k[0]] == k[1]:
                gain += weight_dict[cur_m][k]
    if old_m in weight_dict:
        gain -= weight_dict[old_m][-1]
        for k in weight_dict[old_m]:
            if k == -1:
                continue
            elif match[k[0]] == k[1]:
                gain -= weight_dict[old_m][k]
    match_num_dict[tuple(new_match)] = match_num + gain
    return gain
