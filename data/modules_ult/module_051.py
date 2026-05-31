
COMP_OVL = "Complete overlap"
NO_OVL = "No overlap"

def cal_overlap_neg_strand(s1, e1, s2, e2):

    overlap = None

    len1 = abs(e1 - s1)
    len2 = abs(e2 - s2)

    min_len = min(len1, len2)

    # seq2 within seq1 region - this may match the partial overlap case
    if s1 > s2 and e1 < e2:
        overlap = COMP_OVL

    # no overlap, seq1 before seq2
    elif s1 > s2 and e1 >= s2:
        overlap = NO_OVL

    # partial overlap, seq1 before seq2
    elif s1 >= s2 and s2 > e1 and e1 >= e2:
        overlap = float(s2 - e1 + 1) / float(min_len)

    # seq1 within seq2 region
    elif s2 > s1 and e1 > e2:
        overlap = COMP_OVL

    # no overlap, seq2 before seq1
    elif s2 > s1 and e2 >= s1:
        overlap = NO_OVL

    # partial overlap, seq2 before seq1
    elif s2 >= s1 and s1 > e2 and e2 >= e1:
        overlap = float(s1 - e2 + 1) / float(min_len)

    return overlap
