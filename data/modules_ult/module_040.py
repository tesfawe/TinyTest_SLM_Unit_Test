def compute_range(nums, distance):
    less, equal = 0, 0
    a, b = 0, 0  # a, b are the extremes of the segment of less distances
    c, d = 0, 0  # c, d are the extremes of the segment of less/equal distances
    prev = None
    for num in nums[:-1]:
        if num != prev:
            while c < len(nums) and nums[c] + distance < num: c += 1
            a = c
            while a < len(nums) and nums[a] + distance == num: a += 1
            while b < len(nums) - 1 and nums[b + 1] - distance < num: b += 1
            d = b
            while d < len(nums) - 1 and nums[d + 1] - distance == num: d += 1
        prev = num

        less += b - a
        equal += d - c

    return max(0, less/2), equal/2
