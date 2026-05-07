L = int(input())

def is_prime(n):
    if n < 2 :
        return False
    for i in range(2,n):
        if n % i == 0:  #只要有一个能整出n那就不是质数
            return False
    
    return True

while True:
    