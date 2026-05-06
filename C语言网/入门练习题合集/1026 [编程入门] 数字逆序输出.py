#输入10个数字，然后逆序输出。
number = list(map(int,input().split()))
# print(number[::-1])
#进坑里了，现在我有了倒序的列表，怎么用纯数字接空格的格式输出呢？
for i in number[::-1]:
    print(i,end = " ")
#我真是他妈的天才