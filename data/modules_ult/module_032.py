def checkFormulas(arguments, formulaTuple, state):
	for formula in formulaTuple:
		if len(formula) == 1 and formula[0] not in state:
			return False
		if len(formula) == 2\
			and (formula[0] not in state or arguments[formula[1]] not in state[formula[0]]):
			return False
		if len(formula) == 3\
			and (formula[0] not in state or (arguments[formula[1]], arguments[formula[2]]) not in state[formula[0]]):
			return False
	return True
