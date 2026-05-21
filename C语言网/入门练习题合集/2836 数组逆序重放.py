s = input()
num = list(map(int,input().split()))
# for i in num[::-1] :
#     print(i,end = " ")
print(' '.join(map(str,num[::-1])))
