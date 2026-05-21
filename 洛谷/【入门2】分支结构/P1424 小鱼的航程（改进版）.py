# x,n = map(int,input().split())

# if 6-x > 0:
#     thisday = 6-x
# elif 6 - x == 0:
#     nextday = 1
# else:
#     nextday = 2
# # 先算第一个星期的天数

# first = thisday * 250
# last = 8 - x    #这是第一周所占有的天数
# normal = (n - last) // 7 * 5 * 250 + (n - last) % 7 * 250 + first
# print(normal)

#使用数学手法写得自己思维不清楚，不如下面的直接暴力

x,n = map(int,input().split())

gather = 0

for i in range(1,n+1):
    if x != 6 and x != 7:
        gather += 250
    x += 1
    if x > 7:
        x = 1
print(gather)