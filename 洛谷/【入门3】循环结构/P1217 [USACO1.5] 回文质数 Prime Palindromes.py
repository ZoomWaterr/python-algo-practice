a,b = map(int,input().split())

def is_prime(n):
    if n < 2:
         return False
    for i in range(2,n):
        if n % i == 0:
            return False
    return True

def is_hw(n):
    s = str(n)
    if s == s[::-1]:
        return True
    else:
        return False


for i in range(a,b+1):
    if is_prime(i) and is_hw(i) :
            print(i)
#这个写的基础代码，没有优化，能ac但是会超时