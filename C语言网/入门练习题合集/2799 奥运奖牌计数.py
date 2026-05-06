# n = int(input())
# medal = list(map(int,input().split()))
# for i in medal:
#     gold = sum(medal[0])
#     silver = sum(medal[1])
#     tong = sum(medal[2])
#
# print(gold,silver,tong,sum(medal),end = " ")

n = int(input())
gold = silver = tong =0

for i in range(n):
    g,s,t= list(map(int,input().split()))#痛点！累加变量 = 累加变量 + 当时值
    gold += g
    silver += s
    tong += t
total = gold + silver + tong
print(gold,silver,tong,total)