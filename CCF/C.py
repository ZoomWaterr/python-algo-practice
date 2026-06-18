n = int(input())

if n == 0:
    print("0")
else:
    digits = []
    while n > 0:
        r = n % 3
        if r == 0:
            digits.append('0')
        elif r == 1:
            digits.append('o')
        else:
            digits.append('O')
        n //= 3
    print('.'.join(digits))