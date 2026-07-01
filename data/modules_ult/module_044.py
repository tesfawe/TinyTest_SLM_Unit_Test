def cigar_prefix_length(cigar, reference_bases):
		ref_pos = 0
		query_pos = 0
		for op, length in cigar:
			if op in (0, 7, 8):  # M, X, =
				ref_pos += length
				query_pos += length
				if ref_pos >= reference_bases:
					return (reference_bases, query_pos + reference_bases - ref_pos)
			elif op == 2:  # D
				ref_pos += length
				if ref_pos >= reference_bases:
					return (reference_bases, query_pos)
			elif op == 1:  # I
				query_pos += length
			elif op == 4 or op == 5:  # soft or hard clipping
				pass
			else:
				# TODO it should be possible to handle the N operator (ref. skip)
				assert False
		assert ref_pos < reference_bases
		return (ref_pos, query_pos)
