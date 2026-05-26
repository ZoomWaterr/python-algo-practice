# num = list(map(int,input().split()))
num = [int(input())  for _ in range(12)] #这才是面对一列进行输入的方法
# 每月增加300， 月初剩的钱+300 - 预计花销 ——> 剩下的大于整百，存到妈妈手上
#                                      ——>  剩下的不足整百，存下来，当现金，和下个月的一起
mama = 0    #在妈妈手里的钱
cash = 0    #手里现有的钱
for i in range(12):
    
    extramoney = cash + 300 - num[i]    #每个月除去计划能剩下来的钱

    if extramoney < 0:
        print(-(i + 1))
        break
    if extramoney // 100 > 0:
        mama += (extramoney // 100) * 100 #存上整百的数
        extramoney -= (extramoney // 100) * 100 #去掉存的钱
        cash = extramoney  #到下个月手里剩的钱
    else:
        cash = extramoney
else:
    print(int(mama* 1.2) + cash)


#==========================================================分割线，更优解法

num = [int(input()) for _ in range(12)]

mama = 0
cash = 0

for i in range(12):
    cash += 300 - num[i]

    if cash < 0:
        print(-(i + 1))
        break
    
    mama += cash // 100 * 100   #// 100 负责数“有几个整百”
    cash %= 100                 #% 100 负责留下“不到一百的部分”
else:
    print(int(mama * 1.2) + cash) 
# x // K   # 能分出多少组 K
# x % K    # 分完以后还剩多少