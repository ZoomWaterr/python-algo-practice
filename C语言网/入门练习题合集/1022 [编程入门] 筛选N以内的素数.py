import math

N = int(input())
for i in range(2,N+1):
    limit = math.sqrt(i)
    for j in range(2,int(limit)+1):   #生成开根号之后需要除以的整数
        if i % j == 0 : #如果范围内的数，能够整除这里面的因子数，那就是
            break
    else:   #神来之笔，语法糖，如果for循环没有被break，那么else就会执行，也就是说这是数是素数
        print(i)
