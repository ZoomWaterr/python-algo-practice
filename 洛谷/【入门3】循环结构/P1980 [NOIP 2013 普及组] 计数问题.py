# n,x = map(int,input().split())
# nums = []
# for i in range(1,n+1):
#     nums.append(i)

# char = str(nums)
# total = char.find('x')
# print(total)
n,x = map(int,input().split())
count = 0

target = str(x)

for i in range(1,n + 1):
    count += str(i).count(target) 

print(count)

# 使用通用工具  count()
# 就能很好的解决这个问题