n = input()

if n == "0":
    print(0)
elif n[0] == "-":
    num = n[1:]
    num = num.rstrip('0')
    print("-"+num[::-1])
else:
    n = n.rstrip('0')
    print(n[::-1])