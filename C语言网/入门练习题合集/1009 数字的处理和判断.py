#给出一个不多于5位的整数，要求 1、求出它是几位数 2、分别输出每一位数字 3、按逆序输出各位数字，例如原数为321,应输出123

num = input()
count = len(num)    #现在num是字符串，count代表字符串的长度，取巧求数位
print(count)
for i in num :
    print(i,end=' ')
print()
print(num[::-1])