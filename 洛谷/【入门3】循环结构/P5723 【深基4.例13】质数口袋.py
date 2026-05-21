L = int(input())

def is_prime(n):
    if n < 2 :
        return False
    for i in range(2,n):
        if n % i == 0:  #只要有一个能整出n那就不是质数
            return False
    
    return True

sum_p = 0   #质数和
count = 0   #质数的个数
num = 2     #从2开始判断

while True:
    if is_prime(num):
        if sum_p + num <= L:
            sum_p += num
            count += 1
            print(num)
        else:
            break
    num += 1
print(count)