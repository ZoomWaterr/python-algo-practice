day = int(input())
coin = 0
#按照整段算,先求整段的和，能够小于整个给定天数
#那这个怎么判断，前几个数的整数和小于给定呢
k = 0   #整段天数
total = 0
while total +(k + 1) <= day:
    k += 1
    total += k  #循环中算出要经历多少个整天数

coin += sum([i**2 for i in range(1,k+1)])#求整段天数的值
last = day - total
coin += last * (k+1)
print(coin)


