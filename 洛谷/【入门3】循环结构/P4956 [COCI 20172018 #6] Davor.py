N = int(input())

weekmoney = N // 52
weekday = 0
# sum(range(7)) = 21
for X in range(100,0,-1):  #让X尽量的大
    remainder = weekmoney - 7 * X #7*X + 21*K = weekmoney
    if remainder % 21 == 0 and remainder > 0:     #remainder = 剩余量
        K = remainder // 21
        print(X)
        print(K)
        break

