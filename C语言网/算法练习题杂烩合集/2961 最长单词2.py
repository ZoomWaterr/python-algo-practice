words = input().rstrip(".").split()     #生成字符串，去掉右边的.
long_word = max(words,key = len)
print(long_word)
