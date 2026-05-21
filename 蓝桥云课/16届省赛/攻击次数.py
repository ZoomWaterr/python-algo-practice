bl = 2025
turn = 1
while bl > 0:
   bl -= 5
   if turn % 2 == 1:
      bl -= 15
   else:
      bl -= 2
   if turn % 3 == 1:
      bl -= 2
   if turn % 3 == 2:
      bl -= 10
   if turn % 3 == 0:
      bl -= 7
   if bl <= 0:
      break
   turn += 1
print(turn)
         