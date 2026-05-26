n = int(input())

num = list(map(int,input().split()))

num.remove(max(num))
num.remove(min(num))

ans = sum(num)/len(num)

print(f"{ans:.2f}")