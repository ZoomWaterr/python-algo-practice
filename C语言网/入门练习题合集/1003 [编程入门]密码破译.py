s = input()
result = ""
for i in s:
    new_word = chr(ord(i) + 4)  #这个地方是精华    ord()把字符转化成ascll值   chr()再把ascll转成字符
    result += new_word
print(result)