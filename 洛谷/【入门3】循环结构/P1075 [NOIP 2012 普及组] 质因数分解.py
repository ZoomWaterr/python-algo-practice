n = int(input())

i = 2

# while i * i <= n:
#     if n % i != 0:
#         i += 1
#     else:
#         ans = n // i
# print(ans)    草，又写bug了，使用while要注意跳出

while i * i <= n:
    if n % i == 0:
        ans = n // i
        break
    i += 1
print(ans)

#这是一个巧妙的质数问题，题中两个质数进行相乘，所以只有唯一解，所以可以进行遍历取余数，如果余数为0，就得到其中那个小的煮熟质数，那么另一个大的直接整出即可求出