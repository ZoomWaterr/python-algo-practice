n = int(input())


# for i in range(1,n*n + 1): #输出1到n方
#     while line <= n:
#         line = 0
#         line += 1
#         print(i)
#     else:
#         print() #自己不过脑子写的狗屎代码

num = 1

for i in range(n):  #二维输出要用双层循环
    for j in range(n):
        print(f"{num:02d}",end="")
        num += 1
    print()

print()

num = 1

for i in range(1,n + 1):
    print(" " * ((n - i) * 2),end="")

    for j in range(i):
        print(f"{num:02d}",end = "")
        num += 1
    print()