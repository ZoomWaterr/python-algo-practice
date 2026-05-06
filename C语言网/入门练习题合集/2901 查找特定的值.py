s = input()
num = list(map(int,input().split()))
that_num = int(input())
if that_num in num :
    print(num.index(that_num)+1)
else:
    print(-1)