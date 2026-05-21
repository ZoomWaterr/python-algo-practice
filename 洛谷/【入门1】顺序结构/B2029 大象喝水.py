h,r = map(int,input().split())
pi = 3.14
basic = 20000

tong =(basic + (pi * r**2 * h ) - 1) // (pi * r**2 * h )
print(round(tong))