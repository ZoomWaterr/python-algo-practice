#1 4 3 2    3
#1 2 4 3    2
#1 2 3 4    1

n = int(input())
nums = list(map(int,input().split()))
count = 0
for i in range(n):
    for j in range(n-1-i):
        if nums[j] > nums[i]:
            print("")
            nums[i] ,nums[i+1] = nums[j+1],nums[j]
            count += 1
print(count)
