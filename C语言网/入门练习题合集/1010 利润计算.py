num = int(input())
if num <= 100000 :
    bonus = num * 0.1
elif 100000 < num <= 200000 :
    bonus = 100000 * 0.1 +(num-100000) * 0.075
elif 200000 < num <= 400000:
    bonus = 100000 * 0.1 +100000 * 0.075 + (num - 200000) * 0.05
elif 400000 < num <= 600000 :
    bonus = 100000 * 0.1 +100000 * 0.075 + 200000 * 0.05 + (num - 400000) * 0.03
elif 600000 < num <= 1000000 :
    bonus = 100000 * 0.1 +100000 * 0.075 + 200000 * 0.05 + 200000 * 0.03 + (num - 600000) * 0.015
elif num > 1000000 :
    bonus = 100000 * 0.1 +100000 * 0.075 + 200000 * 0.05 + 200000 * 0.03 + 400000 * 0.015 + (num - 1000000) * 0.01
print(int(bonus))


#大佬写的
l = int(input())
bonus = 0
levels = [
    (100000, 0.10),
    (100000, 0.075),
    (200000, 0.05),
    (200000, 0.03),
    (400000, 0.015),
    (float('inf'), 0.01)
]
remaining = l
for amount, rate in levels:
    if remaining > amount:
        bonus += amount * rate
        remaining -= amount
    else:
        bonus += remaining * rate
        break
print(int(bonus))