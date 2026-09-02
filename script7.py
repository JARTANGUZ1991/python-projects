secret = 7
while secret == 7 :
  Number = int(input("Enter number: "))
  if Number > secret:
      print(" Enough, Try Again")
  elif Number < secret:
          print("Not Enough, Try Again")
  else:
          print("You Win, Good girl")
          break

