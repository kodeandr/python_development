class Solution:
    def findMaxLength(self, nums: List[int]) -> int:
        max_len = 0
        n = len(nums)

        for start in range(n):
            zeroes = 0
            ones = 0
            for end in range(start, n):
                if nums[end] == 1:
                    ones += 1
                else:
                    zeroes += 1
            
            if zeroes == ones:
                current_len = end - start + 1
                if current_len > max_len:
                    max_len = current_len
    return max_len
