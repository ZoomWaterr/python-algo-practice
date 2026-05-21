# n = int(input())
# char = ["2","0","2","6"]
# word = []
# for i in range(n):
    
#     if i <= 4:
#         word += char[i]
#     if i >= 4:
#         print()

s = "2026"      #直接定义字符串
n = int(input())
for i in range(1, n + 1):   
    print((s * (i // 4 + 1))[:i])   
    #s * 多长才能够这个东西切，4以内：// 4 等于0 加一等于需要一个，后面的是列表切片(第一个为开始，省略后自动从第一个开始)


n = int(input())
base = "2026"

for i in range(1, n + 1):
    line = ""
    for j in range(i):
        line += base[j % 4]
    print(line)