def countTime(time: str) -> int:
  ans = 1
  if time[3] == '?':
    ans *= 6
  if time[4] == '?':
    ans *= 10

  if time[0] == '?' and time[1] == '?':
    return ans * 24
  if time[0] == '?':
    if time[1] < '4':
      return ans * 3
    else:
      return ans * 2
  if time[1] == '?':
    if time[0] == '2':
      return ans * 4
    else:
      return ans * 10
  return ans
