from curses.ascii import isalpha

char = input()
letter = 0  #字母
digit = 0  #数字
space = 0   #空格
others = 0  #其他
for i in char :
    if i.isalpha():
        letter += 1
    elif i.isdigit():
        digit += 1
    elif i.isspace():
        space += 1
    else:
        others += 1
print(f"{letter} {digit} {space} {others}")


# 这个题关键在于调用Python内置方法
# i.isalpha() 判断i是否为字母
# i.isdigit() 判断i是否为数字
# i.isspace() 判断i是否为空格
#也可以用ascii码的区间判断
# ord(i)  是核心，可以获取对应的ascii码
