import re

def calc_query_pos_from_cigar(cigar, strand):

    cigar_ops = [[int(op[0]), op[1]] for op in re.findall('(\d+)([A-Za-z])', cigar)]

    order_ops = cigar_ops
    if not strand: 
        order_ops = order_ops[::-1]

    qs_pos = 0
    qe_pos = 0
    q_len = 0

    for op_position in range(len(cigar_ops)):
        op_len = cigar_ops[op_position][0]
        op_type = cigar_ops[op_position][1]

        if op_position == 0 and ( op_type == 'H' or op_type == 'S' ):
            qs_pos += op_len
            qe_pos += op_len
            q_len += op_len
        elif op_type == 'H' or op_type == 'S':
            q_len += op_len
        elif op_type == 'M' or op_type == 'I' or op_type == 'X':
            qe_pos += op_len
            q_len += op_len

    return qs_pos, qe_pos