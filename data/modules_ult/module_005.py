def get_allen_relation(duration1, duration2):

    is1, ie1 = duration1
    is2, ie2 = duration2

    if is2-1 == ie1:
        return 'meets'
    elif is1-1 == ie2:
        return 'metby'

    elif is1 == is2 and ie1 == ie2:
        return 'equal'

    elif is2 > ie1:
        return 'before'
    elif is1 > ie2:
        return 'after'

    elif ie1 >= is2 and ie1 <= ie2 and is1 <= is2:
        return 'overlaps'
    elif ie2 >= is1 and ie2 <= ie1 and is2 <= is1:
        return 'overlapped_by'
    elif is1 >= is2 and ie1 <= ie2:
        return 'during'
    elif is1 <= is2 and ie1 >= ie2:
        return 'contains'
    elif is1 == is2 and ie1 < ie2:
        return 'starts'
    elif is1 == is2 and ie1 > ie2:
        return 'started_by'
    elif ie1 == ie2 and is2 < is1:
        return 'finishes'
    elif ie1 == ie2 and is2 > is1:
        return 'finished_by'