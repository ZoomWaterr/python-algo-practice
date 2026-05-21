num = int(input())
def jc(n):
    if n > 1:
        return n * jc(n-1)
    else:
        return 1

sum = 0
for i in range(1, num+1):   #range,代表0到num-1，现在算阶乘要从1开始到num+1结束
    sum += jc(i)
print(sum)