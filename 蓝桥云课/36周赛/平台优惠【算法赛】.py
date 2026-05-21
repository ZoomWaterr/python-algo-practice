N = int(input())
num = list(map(int,input().split()))

total = sum(num)
lens = len(num)

if lens >= 3:
    num.sort(reverse=True)  #从大到小排序
    for i in num:
        
        total -= num[2:lens:3]
print(total)
        
