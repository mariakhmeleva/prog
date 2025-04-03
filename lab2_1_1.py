#1/1
# x = input('Введите число: ')
# y = input('Введите число: ')
# z = input('Введите число: ')

# try:
#     x = int(x)
#     y = int(y)
#     z = int(z)
#     print('Минимальное число:', min(x, y, z))
# except ValueError:
#     print('Вы ввели не число')
#1/2
numbers = []
for _ in range(3):
    user_input = input('Введите число: ')
    try:
        number = int(user_input)
    except ValueError:
        print('Вы ввели не число')
        number = None 
    numbers.append(number)

filtered_numbers = []
for num in numbers:
    if num is not None and 1 <= num < 50:
        filtered_numbers.append(num)

print('Ваши числа входящие в промежуток 1-50:', filtered_numbers)