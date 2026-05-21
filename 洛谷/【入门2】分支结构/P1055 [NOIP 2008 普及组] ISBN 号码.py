s = input()
s = s.replace("-","")   #把横杠去掉替换成没东西

total = 0
n = 1
for i in s[:-1:] :
    i = int(i)
    total += i * n
    n += 1

shibie = total % 11
if shibie == 10:
    shibie = 'X'
if str(shibie) == s[-1]:
    print("Right")
else:
    print(f"{s[0]}-{s[1:4]}-{s[4:9]}-{shibie}")
