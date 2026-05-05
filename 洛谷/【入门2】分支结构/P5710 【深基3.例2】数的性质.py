x = int(input())

p1 = x % 2 == 0
p2 =  4< x <= 12

a = p1 and p2
u = p1 or p2
b = p1 ^ p2
z = not(p1 or p2)
print(a*1,u*1,b*1,z*1)