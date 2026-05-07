# k = int(input())

# def sn(x):
#     if x == 1:
#         return 1
#     if x > 1:
#         return x + 1/(x-1)

# while True:
#     y = sn()

k = int(input())

sn = 0.0
n = 0

while True:
    n += 1
    sn += 1/n
    if sn > k:
        print(n)
        break
    