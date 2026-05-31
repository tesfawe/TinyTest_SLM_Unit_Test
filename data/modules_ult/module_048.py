def featurize_finance(investment, average_money):

	#newVec = [0, 0, 0, 0, 0, 0, 0, 0]
	newVec = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

	if investment == 0: money = average_money
	else: money = investment

	if   money < 1*10**5: newVec[0]=1
	elif money < 5*10**5: newVec[1]=1
	elif money < 1*10**6: newVec[2]=1
	elif money < 5*10**6: newVec[3]=1
	elif money < 1*10**7: newVec[4]=1
	elif money < 5*10**7: newVec[5]=1
	elif money < 1*10**8: newVec[6]=1
	elif money < 5*10**8: newVec[7]=1
	elif money < 1*10**9: newVec[8]=1
	else: newVec[9]=1

	return newVec