#[[a,b],[c,d] ]
study = []
level = []
angry = 0
for i in range(7):
    nums = list(map(int, input().split()))
    study.append(nums)  #接收7天的时间
#目前这个study是双重列表，
for up,down in study:
    angry = up + down - 8
    if angry < 0:
        angry = 0
    level.append(angry)

if max(level) > 0:
    print(level.index(max(level)) + 1)
else:
    print(0)

#简单直接的解法
hour_max = day = 0
for i in range(1,8):
    hour1,hour2 = map(int,input().split())
    hour_all = hour1 + hour2
    if hour_all > 8:
        if hour_all > hour_max:
            hour_max = hour_all
            day = i
print(day)