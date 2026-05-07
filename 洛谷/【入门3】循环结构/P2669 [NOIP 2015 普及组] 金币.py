k = int(input())

total = 0   #总金币
n = 1       #第几批

while k > 0:
    if k >= n:   #剩余的天数够完整的一轮
        total += n * n
        k -= n
    else:
        total += k * n
        k = 0
    n += 1

print(total)