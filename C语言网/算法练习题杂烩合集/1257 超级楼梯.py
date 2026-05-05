N = int(input())
arr = [0] * 42        # 修正3：固定够大
arr[1] = 1            # 初始条件：第一级，一种走法
arr[2] = 1            # 初始条件：第二级，一种走法
for _ in range(N):
    M = int(input())
    # step = M -1     # 修正2：删掉这行！
    for i in range(3, M+1):
        arr[i] = arr[i-1] + arr[i-2]
    print(arr[M])     # 输出arr[M]
