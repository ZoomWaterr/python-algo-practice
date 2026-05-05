w,h,v = map(int,input().split())


for i in range(1,h+1):
    print("Q"*w)
for j in range(1,w+1):
    print("Q" * (w + v))