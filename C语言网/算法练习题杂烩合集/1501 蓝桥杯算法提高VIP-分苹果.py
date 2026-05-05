#使用差分数组
N,M = map(int,input().split())

d=[0] * (N+2)#开辟出差分数组，

for _ in range(M):
    L,R,C = map(int,input().split())
    d[L] += C
    d[R + 1] -= C   #使用数组记录变化量

for i in range(1,N+1):   #使用前缀和还原数组情况
    d[i] += d[i-1]

print(*d[1:N+1])
