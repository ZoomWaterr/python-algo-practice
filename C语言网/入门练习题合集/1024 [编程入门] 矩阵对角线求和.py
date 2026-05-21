#求一个3×3矩阵对角线元素之和。
double = []
for i in range(3):
    row = list(map(int,input().split()))
    double.append(row)  #这里的double矩阵是二维的

sum1 = double[0][0]+double[1][1]+double[2][2]
sum2 = double[0][2]+double[1][1]+double[2][0]
print(sum1,sum2)