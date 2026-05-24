from typing import List

def setZeroes(matrix: List[List[int]]) -> None:
  m = len(matrix)
  n = len(matrix[0])
  shouldFillFirstRow = 0 in matrix[0]
  shouldFillFirstCol = 0 in list(zip(*matrix))[0]

  for i in range(1, m):
    for j in range(1, n):
      if matrix[i][j] == 0:
        matrix[i][0] = 0
        matrix[0][j] = 0

  for i in range(1, m):
    for j in range(1, n):
      if matrix[i][0] == 0 or matrix[0][j] == 0:
        matrix[i][j] = 0

  if shouldFillFirstRow:
    matrix[0] = [0] * n

  if shouldFillFirstCol:
    for row in matrix:
      row[0] = 0
