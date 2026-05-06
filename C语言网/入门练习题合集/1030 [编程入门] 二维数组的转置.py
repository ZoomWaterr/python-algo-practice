#写一个函数，使给定的一个二维数组（3×3）转置，即行列互换。
new_list = []
for i in range(3):
    row = list(map(int,input().split()))    #构建列表，3个数字
    new_list.append(row)    #把这个列表存到二维列表里

for i in range(3):
    for j in range(3):
        print(new_list[j][i],end = " ")
    print()
#解题关键在于行列互换！



