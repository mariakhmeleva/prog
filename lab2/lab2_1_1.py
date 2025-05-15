#1/1
x = input('Введите число: ')
y = input('Введите число: ')
z = input('Введите число: ')

try:
    x = int(x)
    y = int(y)
    z = int(z)
    print('Минимальное число:', min(x, y, z))
except ValueError:
    print('Вы ввели не число')
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

#1/3
try:
    number = float(input('Введите число: '))
    for i in range(1, 11):
        print(f'{number} * {i} = {number * i}')
except ValueError:
    print('Ошибка: вы ввели не число')

#1/4
print("Вводите числа по одному. Для завершения введите пустую строку:")

total_sum = 0  # Сумма чисел
count = 0      # Количество чисел

while True:
    num_input = input()  # Ждём ввода числа
    
    # Проверка на завершение ввода
    if num_input == "":
        break
    
    # Проверка и обработка числа
    try:
        number = int(num_input)
        total_sum += number
        count += 1
    except ValueError:
        print("Ошибка: введите целое число или пустую строку для завершения!")

# Вывод результатов
if count == 0:
    print("Вы не ввели ни одного числа!")
else:
    print(f"Сумма чисел: {total_sum}")
    print(f"Количество чисел: {count}")
