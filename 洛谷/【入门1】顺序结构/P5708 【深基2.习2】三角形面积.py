import math
a,b,c = map(float,input().split())
p = 0.5*(a+b+c)
S = math.sqrt(p*(p-a)*(p-b)*(p-c))
print(round(S,1))