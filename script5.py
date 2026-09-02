User= input("Введите ваше имя: ")
Budget= int(input("Введите ваш бюджет: "))
Price=int(input("Введите цену товара: "))
Sale =int(input("Введите скидку (%): "))
count = Budget // Price
rest = Budget % Price
discount_price = Price * (1-Sale/100)
print("Пользователь:",User)
print("Количество товаров без скидки",count)
print("Остаток денег",rest)
print("Цена 1 товара со скидко",discount_price)