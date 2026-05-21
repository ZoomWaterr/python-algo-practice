a,b,c = map(int,input().split())

order = input()
A,B,C = sorted([a,b,c])

turn = {'A': A,'B' : B,'C': C}

print(f"{turn[order[0]]} {turn[order[1]]} {turn[order[2]]}")
