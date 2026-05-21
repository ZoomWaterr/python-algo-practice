s = float(input())

 #第一步2m
total = 2   #总长
step = 1    #步数
next_step = 2 * 0.98

while True:
    if s <= 2:
        print(1)
        break
    elif total < s:     #小于需要的总长代表没完呢
        total += next_step
        next_step *= 0.98   #精髓持续更新下一步的长度
        step += 1
    else:   #代表大于目标了
        print(step)
        break

    #我这个题做的真棒，中间那个替换下一步的迭代相当棒