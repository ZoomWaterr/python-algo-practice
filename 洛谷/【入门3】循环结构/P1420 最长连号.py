n = int(input())
num = list(map(int,input().split()))

#最长连号?
cnt = 1 #新学的 current 现在的，当前的
ans = 1 # answer 答案
for i in range(n-1) :
    if num[i] + 1 == num[i + 1]:
        cnt += 1
    else:
        cnt = 1

    ans = max(cnt,ans) #这是把目前见过的最长长度和当前长度相比，留下更大的那个

print(ans)

