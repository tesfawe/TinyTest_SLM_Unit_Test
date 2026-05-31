def coordinate_sorter(start, stop, ascending_list):
	if len(ascending_list) == 0:
		#print('1st IF')
		return 0
	else:
		for current_index in range(0, len(ascending_list)):

			if start == stop and start in range(int(ascending_list[current_index]['coordinates']['start']), int(ascending_list[current_index]['coordinates']['stop'])+1):
				#print('2nd IF')
				return current_index

			elif start == stop and stop >= int(ascending_list[current_index]['coordinates']['stop']) and current_index+1 == len(ascending_list):
				#print('3rd IF')
				return current_index+1

			elif stop >= int(ascending_list[current_index]['coordinates']['stop']) and current_index+1 == len(ascending_list):
				#print('4th IF')
				return current_index+1