s = input().strip()
ns = s.replace('.','')
rns = ns[::-1]
result = f"{rns[0]}.{rns[1:]}"
print(result)