char = input()
for i in char:
    if  ord('A') <= ord(i) <= ord('Z'):
        i = chr(ord(i) + 32)
    print(i,end = "")
#chr()将ascii码转成字符，ord()由ascii码转成数字
print(char.lower())
print(input().lower())
