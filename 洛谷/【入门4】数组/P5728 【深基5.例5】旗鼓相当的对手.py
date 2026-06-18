N = int(input())

chinese = [0] * N
math = [0] * N
english = [0] * N
total = [0] * N

ans = 0
for i in range(N):
    chinese[i],math[i],english[i] = map(int,input().split())
    total[i] = chinese[i]+math[i]+english[i]

for i in range(N):
    for j in range(i+1,N):
        if abs(chinese[i]-chinese[j])<= 5 and abs(math[i]-math[j])<= 5 and abs(english[i]-english[j])<= 5 and abs(total[i]-total[j])<= 10:
            ans += 1

print(ans)