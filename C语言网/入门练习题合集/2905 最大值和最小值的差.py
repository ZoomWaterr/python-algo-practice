M = int(input())
#怎么对列表产生占位呢
nums = list(map(int,input().split()))
print(max(nums) - min(nums))
