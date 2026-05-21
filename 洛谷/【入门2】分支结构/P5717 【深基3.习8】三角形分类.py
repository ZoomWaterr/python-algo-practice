x,y,z = map(int,input().split())
a,b,c = sorted([x,y,z]) #这一步把两个短边选出来，简化判断！

if a+b <= c :
    print("Not triangle")
else:
    
    if a**2 + b**2 == c**2:
        print("Right triangle")
    elif a**2 + b**2 > c**2:
        print("Acute triangle")
    else:
        print("Obtuse triangle")

    if a == b or b == c or a == c:
        print("Isosceles triangle")
    if a == b == c:
        print("Equilateral triangle")