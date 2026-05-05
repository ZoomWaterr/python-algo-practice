# n = int(input())

# num = list()
# count = 1

# m = map(int,input().split())
# num.append(m)
# if count > (num.len()):
#     max(num,key=len)
#     print()
# else:
#     print("no")

# n = int(input())
# nums = list(map(int,input().split()))

# count = {}
# for i in nums:
#     count[i] = count.get(i,0) + 1

# for i ,cnt in count.items():
#     if cnt > n / 2:
#         print(i)
#         break
# else:
#     print("no")

n = int(input())    #n个数
nums = list(map(int,input().split()))  #制作N数组

count = {}  #根据题意，数字有对应的出现次数----->创造字典
for i in nums:     #遍历数组中存在的数
    # nums[i] += 1   #检查到存在，记一次数
    count[i] = count.get( i, 0) + 1     #在字典中寻找i对应的值，没有使用后面的默认值
    #现在要考虑是不是比数组数量的一半大

#有说法，现在遍历一下字典中所有的key和value，查一查有没有超过的
for num,cnt in count.items():
    if cnt > n/2:
        print(num)
        break
else:
    print("no")

    






























