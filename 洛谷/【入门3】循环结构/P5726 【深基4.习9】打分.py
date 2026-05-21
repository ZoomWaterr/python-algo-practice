n = int(input())

num = list(map(int,input().split()))

num = num.pop(max(num))
num = num.pop(min(num))

ans = sum(num)/len(num)

print(round(ans,2))