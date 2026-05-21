high = list(map(int,input().split()))

tall = int(input())
get = 0
for i in high:

    if tall >= i or tall + 30 >= i:
        get += 1

print(get)