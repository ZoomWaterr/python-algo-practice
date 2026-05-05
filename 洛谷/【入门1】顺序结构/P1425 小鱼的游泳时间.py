a,b,c,d = map(int,input().split())

if d - b < 0:
    f = d + 60 -b   #分钟算清楚了
    e = c - 1 -a    #小时算好了
else:
    f = d - b 
    e = c - a

print(e,f)