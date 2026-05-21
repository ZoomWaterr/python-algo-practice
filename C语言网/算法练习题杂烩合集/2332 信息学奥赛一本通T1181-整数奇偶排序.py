num = list(map(int,input().split()))
dan = []
shuang = []
for i in num:
    if i % 2 == 1:
       dan.append(i)
       dan.sort() 
       dan.reverse()
    else:
        shuang.append(i)
        shuang.sort()
total = dan + shuang
print(*total)