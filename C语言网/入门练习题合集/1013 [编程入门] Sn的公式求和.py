#求Sn=a+aa+aaa+…+aa…aaa（有n个a）之值，其中a是一个数字，为2。 例如，n=5时=2+22+222+2222+22222，n由键盘输入。
num = int(input())
a = 2
current = 0
total = 0
for i in range(num):
    current = current * 10 + a
    total += current
print(total)