n = int(input())
money = 0
if n <= 150 :
    money = n * 0.4463
elif 151<n<= 400:
    money = 150 * 0.4463 + (n - 150) * 0.4663
else:
    money = 150 * 0.4463 + (400-150) * 0.4663 + (n -400) * 0.5663

print(round(money,1))