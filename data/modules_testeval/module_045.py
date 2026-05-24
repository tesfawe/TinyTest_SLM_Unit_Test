def numDifferentIntegers(word: str) -> int:
  nums = set()
  curr = []

  def removeLeadingZeros(s):
      index = next((i for i, c in enumerate(s) if c != '0'), -1)
      if index == -1:
          return ['0']
      return s[index:]

  for c in word:
      if c.isdigit():
          curr.append(c)
      elif curr:
          nums.add(''.join(removeLeadingZeros(curr)))
          curr = []

  if curr:
      nums.add(''.join(removeLeadingZeros(curr)))

  return len(nums)