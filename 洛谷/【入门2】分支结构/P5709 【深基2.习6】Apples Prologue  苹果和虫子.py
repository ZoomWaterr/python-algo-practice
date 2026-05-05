import math
m,t,s = map(int,input().split())
if t == 0:
    print(0)
else:
    eaten = math.ceil(s/t)
    aw = m -eaten   
    print(max(aw,0))    #如果吃的比所有的还多，那就输出0.这里是保底