n = int(input())
S = 0
def jc(x):
    if x == 1:
        return 1
    if x > 1:
        return x * jc(x-1)
    
for i in range(1,n+1):
    num = jc(i)
    S += num

print(S)