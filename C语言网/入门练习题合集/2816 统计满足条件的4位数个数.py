n = int(input())
num = list(map(int,input().split()))
bingo = 0
for i in num :
    n1 = i // 1000
    n2 = (i % 1000) // 100  #百位
    n3 = (i % 100) //10 #十位
    n4 = i % 10
    if n4 - n1 - n3 - n2 > 0 :
        bingo +=1
print(bingo)