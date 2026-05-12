import math
n = int(input())

sqrt5 = math.sqrt(5)

left = ((1 + sqrt5) / 2 ) ** n
right = ((1 - sqrt5) / 2 ) ** n
fn = (left - right) / sqrt5
print(f"{fn:.2f}")