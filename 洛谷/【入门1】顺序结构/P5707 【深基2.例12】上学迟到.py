import math
s,v = map(float,input().split())
# 这是需要花费的时间
time = math.ceil(s/v) + 10
# 8:00换成分钟，求出出发时间
start_time = 8 * 60 - time

# 跨天处理，如果是负数，就加上一天的分钟数1440
if start_time < 0 :
    start_time += 24 * 60

hour = start_time // 60
minute = start_time % 60

print(f"{hour:02d}:{minute:02d}")