def make_similar(nums, target):
    odd_nums = sorted([n for n in nums if n & 1])
    even_nums = sorted([n for n in nums if not n & 1])
    odd_target = sorted([t for t in target if t & 1])
    even_target = sorted([t for t in target if not t & 1])
    odd_diff = sum(abs(a - b) for a, b in zip(odd_nums, odd_target))
    even_diff = sum(abs(a - b) for a, b in zip(even_nums, even_target))
    return (odd_diff + even_diff) // 4