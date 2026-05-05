N = int(input())
nums = list(map(int,input().split()))
count = 0
for i in range(N):
    for j in range(i):
        if nums[j] > nums[i]:
            count += 1
print(count)            
        