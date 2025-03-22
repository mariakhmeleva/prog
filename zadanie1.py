# #1
# #Ввод 
# num1 = float(input("Введите первое число: "))
# num2 = float(input("Введите второе число: "))
# num3 = float(input("Введите третье число: "))
# # Нахождение мин. числа
# min_num = min(num1, num2, num3)

# print(f"Минимальное число: {min_num}")

#2 
# Ввод
num1 = float(input("Введите первое число: "))
num2 = float(input("Введите второе число: "))
num3 = float(input("Введите третье число: "))

# Проверка и вывод
print("Числа, попадающие в интервал [1, 50]:")
for num in [num1, num2, num3]:
    if 1 <= num <= 50:
        print(num)