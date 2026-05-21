a,b,c = map(int,input().split())
pf = 0
total = sum(range(1,a+1))
for i in range(1,b+1):
    pf += i **2
fenmu = 0
for i in range(1,c+1):
    fenmu += 1/i
all = total + pf + fenmu
print(f"{all:.2f}")


A = sum(range(1,a + 1))
B = sum([i **2 for i in range(1,b + 1)])
C = sum([1/i for i in range(1,c + 1)])
print(f"{(A+B+C):.2f}")