sentence = input()
new_s = sentence.split()
# 现在是把这个按照空格分成列表
rollback = []
for char in new_s:
    rollback.append(char[::-1]) #列表里存的都是反转之后的单词

result = ' '.join(rollback)
print(result)