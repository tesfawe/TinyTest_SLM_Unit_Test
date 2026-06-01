def horizontalMaxs(a):
	max1, max2 = 0,0
	posMax1, posMax2 = 0,0
	for i in range(1,len(a)-1):
		if a[i]>a[i+1] and a[i]>a[i-1]:
			if a[i]>max1:
				max1 = a[i]
				posMax1 = i
	for i in range(1,len(a)-1):
		if a[i]>a[i+1] and a[i]>a[i-1]:		
			if a[i]>max2 and a[i]<max1:
				max2 = a[i]
				posMax2 = i

	return posMax1, max1, posMax2, max2