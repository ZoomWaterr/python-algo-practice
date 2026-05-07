n = int(input())

#第一行生成n个数，第二行n-1个数---> 个数 = n-i+1    常用
count = 1
for i in range(1,n+1):  #控制层数
    for j in range(n-i+1):
        print(f"{count:02d}",end="")
        count += 1
    print()