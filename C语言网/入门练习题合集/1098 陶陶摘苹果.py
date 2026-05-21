high = list(map(int,input().split()))
#现在这个东西是列表，怎么把它换成数字呢？
#我靠
tall= int(input())
get = 0
for i in high:
    if tall >= i:   #if tall >= high: 我这个对比错误了，里面的i是数字
        get += 1
    elif tall + 30 >= i :
        get += 1
print(get)