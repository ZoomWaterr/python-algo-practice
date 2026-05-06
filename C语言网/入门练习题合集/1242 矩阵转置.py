n  = int(input())
new_list = []
for i in range(n):
    row = list(map(int,input().split()))
    new_list.append(row)

for i in range(n):
    for j in range(n):
        print(new_list[j][i],end = " ")
    print()