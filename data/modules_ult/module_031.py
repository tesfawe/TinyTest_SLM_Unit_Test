
def locate_alignment(Qseq, Sseq, Qstart, resMatch=False):
    if resMatch:
        matchPos = [i for i, ch in enumerate(Qseq) if i < len(Sseq) and (ch != '-') and (Sseq[i] == ch)]
    else:
        matchPos = [i for i, ch in enumerate(Qseq) if i < len(Sseq) and (ch != '-') and (Sseq[i] != '-')]
    gapPos = [i for i, ch in enumerate(Qseq) if i < len(Sseq) and ch == '-']
    if len(gapPos) == 0:
        return [pos + Qstart for pos in matchPos]
    else:
        numGaps = [len([g for g in gapPos if g < pos]) for pos in matchPos]
        return [pos + Qstart - gaps for pos, gaps in zip(matchPos, numGaps)]
