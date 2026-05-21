char = input()
hole = {} #定义了一个空字典
for i in char:
    if i in hole:
        hole[i] += 1
    else:
        hole[i] = 1
# print(max(hole,key = hole.get),hole[max(hole,key = hole.get)])
#优化
best = max(hole,key = hole.get)
print(best,hole[best])

#key 可以传给max一个工具，让他以这个东西来对比大小