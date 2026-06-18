l,m = map(int,input().split())

tree = [True] * (l + 1)  # l+1 棵树：位置 0 到 l

for i in range(m):
    u,v = map(int,input().split())
    for j in range(u,v+1):
        tree[j] = False
print(sum(tree))
#这题使用布尔数组
#使用查分数组也能解

l,m = map(int,input().split())
diff = [0] * (l + 2)  # l+1 棵树：位置 0 到 l 多加一个，避免超出

for _ in range(m):
    u,v = map(int,input().split())
    diff[u] += 1
    diff[v + 1] -= 1

ans = 0 #答案
cur = 0 #当前数
for i in range(l+1):
    cur += diff[i]
    if cur == 0:
        ans += 1
print(ans)
