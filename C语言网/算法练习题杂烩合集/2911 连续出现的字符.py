k = int(input())
s = input()
current = s[0]
count = 1

if count >= k:
    print(current)
else:
    for i in range(1,len(s)):
        if s[i] == current:
            count += 1
            if count >= k:
                print(current)
                break
        else:
            current = s[i]
            count = 1
    else:
        print("No")
