def actual_exon_numbers(exons):
    exon_list = list()
    if len(exons) < 4 or len(exons) > 12:
        return [0, 0, 0, 0]
    if len(exons) == 4:
        exon_list = list(exons)
    if len(exons) == 5:
        exon_list = map(str, [7, 9, 8, 10])
    if len(exons) == 6:
        exon_list = map(str, [8, 10, 9, 11])
    if len(exons) == 7:
        exon_list = map(str, [9, 11, 10, 12])
    if len(exons) == 8:
        exon_list = [exons[0:2], exons[2:4], exons[4:6], exons[6:8]]
    if len(exons) == 9:
        exon_list = map(str, [97, 99, 98, 100])
    if len(exons) == 10:
        exon_list = map(str, [98, 100, 99, 101])
    if len(exons) == 11:
        exon_list = map(str, [99, 101, 100, 102])
    if len(exons) == 12:
        exon_list = [exons[0:3], exons[3:6], exons[6:9], exons[9:12]]
    return exon_list
