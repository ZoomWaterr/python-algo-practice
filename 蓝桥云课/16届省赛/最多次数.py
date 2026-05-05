# s = input()
# num = 0
# lens = len(s)
# for i in s:    
#     if "l"in i or "q"in i or "b" in i:
#         word = s[:3]     
#         s.strip(i)
#         # if "lqb"or"lbq"or"qlb"or"qbl"or"blq"or"bql" in word:
# #             num += 1
# #     else:
# #         break
# print(word)



# s = input()
# num = 0
# count = {"l" : 0,"q" : 0,"b" : 0}
# for i in s:
#     if i in count:
#         count[i] += 1
#     else:
#         count = {"l" : 0,"q" : 0,"b" : 0}
#         continue
#     if count["l"] >= 1 and count["q"]>= 1 and count["b"] >= 1:
#         num += 1
#     else:
#         count = {"l" : 0,"q" : 0,"b" : 0}
    
# print(num)

s = input()

word = {"lqb", "lbq", "qlb", "qbl", "blq", "bql"}

count = 0
lens = len(s)
i = 0
while i <= lens-3:
    sub = s[i:i+3]

    if sub in word:
        count += 1  #如果切出来的子串在里面，那就加1lqbblqblqlxqb
        i += 3
    else:
        i += 1
print(count)