n = int(input())
# for i in range(N):
#     c = list(map(int,input().split()))
price = []
for i  in range(n):
    price.append(int(input()))

price.sort(reverse=True) #sort是从小到大排列，反过来用reverse=True  这是直接改的原列表
total = 0
for i in range(n):
    if i % 3 != 0:
        total += price[i]

print(total) 


