n = int(input())
num = list(map(int,input().split()))

time = 0

#哦哦我懂了，应该造一个新数组，放对比过的数字，新数字对旧数组进行遍历，遇到比自己小的就加一
new = []

for i in range(n):  # i = 当前这条鱼
    count = 0       #记录有多少鱼不如当前这条
    for j in range(i):  # j = 左边的每一条鱼
        if num[j] < num[i]:
            count += 1
    new.append(count)

print(*new)