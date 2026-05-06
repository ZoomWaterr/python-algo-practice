N = int(input())
def jc(n):
    if n == 1 or n == 0:
        return 1
    else:
        return n*jc(n-1)
print(jc(N))
