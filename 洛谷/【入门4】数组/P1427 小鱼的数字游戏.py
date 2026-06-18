# num = list(map(int,input().split()))

# new = num(reversed = True)

# print(new)

num = list(map(int,input().split()))

num.pop() #括号内填入下标，默认删除最后一个数

new = num[::-1]
print(*new)