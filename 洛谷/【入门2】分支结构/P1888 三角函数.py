import math

a,b,c = map(int,input().split())

x,y,z = sorted([a,b,c])
g = math.gcd(x,z)

print(f"{x//g}/{z//g}")