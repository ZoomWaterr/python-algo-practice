num = int(input())

arr = [0] * (num + 2)

arr[1] = arr[2] = 1
for i in range(3,num+1):
    arr[i] = arr[i-1] + arr[i-2]

print(arr[num])
