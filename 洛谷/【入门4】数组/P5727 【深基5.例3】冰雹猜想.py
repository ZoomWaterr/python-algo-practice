
# while n % 2 == 1:
#     if n == 1:
#         break
#     n = n * 3 + 1
#     if n % 2 ==0:
#         n /= 2
    
# print(n)
n = int(input())
num = [n]
while n != 1:
   
   if n % 2 == 1:
      n = n *3 + 1
   else:
      n //= 2
   num.append(n)
print(*num[::-1])