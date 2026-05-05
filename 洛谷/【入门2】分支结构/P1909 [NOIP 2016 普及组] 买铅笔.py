import math
n = int(input())
money = float('inf')
for i in range(3):
    num,price = map(int,input().split())
    count = math.ceil(n/num)    #现在要解决一个问题，就是怎么把第一个钱数保存下俩，与其他的对比
    
    if money > count * price:   
        money = count * price

print(money)


#另一种写法 把所有的钱数存到列表中，使用列表方法直接找出最小！

n = int(input())
costs = []

for i in range(3):
    num,price = map(int,input().split())
    costs.append(math.ceil(n/num) * price)
print(min(costs))