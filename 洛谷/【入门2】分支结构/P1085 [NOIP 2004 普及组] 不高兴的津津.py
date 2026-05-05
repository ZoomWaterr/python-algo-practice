total = 0
for i in range(7):
    a,b = map(int,input().split())
    if total < a + b:
        total = a + b   #将最大的那天求出
        day = i + 1     #这是第几天
if total > 8:
    print(day)
else:
    print(0)