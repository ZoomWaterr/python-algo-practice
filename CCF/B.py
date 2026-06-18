t = int(input())

for _ in range(t):
    x1, y1, z1 = map(int, input().split())
    x2, y2, z2 = map(int, input().split())

    if x1 != x2:
        print(">" if x1 > x2 else "<")
    elif y1 != y2:
        print(">" if y1 > y2 else "<")
    elif z1 != z2:
        print(">" if z1 > z2 else "<")
    else:
        print("=")
