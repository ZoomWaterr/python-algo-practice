n,k = map(int,input().split())

can = []
no = []
for i in range(1,n+1):
    if i % k == 0:
        can.append(i)
    else:
        no.append(i)

A = round(sum(can)/len(can),1)
B = round(sum(no)/len(no),1)

print(A,B)