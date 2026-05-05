import sys
import math
# 填上你觉得需要的其他模块

def main():
    T = int(input())
    if T == 1:
        # 粘贴问题 1 的主函数代码
        print("I love Luogu!")
    elif T == 2:
        # 粘贴问题 2 的主函数代码
        print(2 + 4, 10 - 2 - 4)
    elif T == 3:
        # 请自行完成问题 3 的代码
        print(14 // 4)
        print(14 // 4 * 4)
        print(14-(14 // 4)*4)
        pass
    elif T == 4:
        # 请自行完成问题 4 的代码
        print(round(500/3,3))
        pass
    elif T == 5:
        # 请自行完成问题 5 的代码
        print(round((260+220)/(12+20)))
        pass
    elif T == 6:
        # 请自行完成问题 6 的代码
        digital = math.sqrt(6**2 + 9**2)
        print(round(digital,4))
        pass
    elif T == 7:
        # 请自行完成问题 7 的代码
        print(110)
        print(110-20)
        print(0)
        pass
    elif T == 8:
        # 请自行完成问题 8 的代码
        pi = 3.141593
        r = 5
        print(round(2*r*pi,4))
        print(round(pi * r**2,4))
        print(round(pi * r**3 *4 / 3,3))
        pass
    elif T == 9:
        # 请自行完成问题 9 的代码
        print((((1+1)*2+1)*2+1)*2)
        pass
    elif T == 10:
        # 请自行完成问题 10 的代码
        # x是每分钟增加任务 y是原本拥有的任务
        x = (8*30 -10*6)/(30-6)
        y = 8*30 - x*30
        n = (y + x*10) / 10
        print(round(n))
        pass
    elif T == 11:
        # 请自行完成问题 11 的代码
        time = 100/3
        print(round(time,4))
        pass
    elif T == 12:
        # 请自行完成问题 12 的代码
        print(13)
        print("R")
        pass
    elif T == 13:
        # 请自行完成问题 13 的代码
        pi = 3.141593
        total = ((pi* 4**3)+(pi* 10**3))*4/3
        a = total**(1/3)
        print(round(a))
        pass
    elif T == 14:
        # 请自行完成问题 14 的代码
        for money in range(1,111):
                peo = 10+(110-money)
                if money * peo == 3500:
                    print(round(money))
                    break
        pass

if __name__ == "__main__":
    main()
