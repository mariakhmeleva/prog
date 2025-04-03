import sys

# 1. Чтение массива из параметров командной строки
if len(sys.argv) < 2:
    print("Ошибка: не указаны элементы массива")
    sys.exit(1)

try:
    arr = [int(x) for x in sys.argv[1:]]
except ValueError:
    print("Ошибка: все элементы должны быть целыми числами")
    sys.exit(1)

# 2. Поиск наибольшего четного элемента
max_even = None
for num in arr:
    if num % 2 == 0:
        if max_even is None or num > max_even:
            max_even = num

if max_even is not None:
    print(f"Наибольший четный элемент: {max_even}")
else:
    print("В массиве нет четных элементов")

# 3. Поиск четных чисел < 10 и вывод в порядке возрастания
small_evens = []
for num in arr:
    if num % 2 == 0 and num < 10:
        small_evens.append(num)

# Сортировка пузырьком (без использования встроенной sort)
n = len(small_evens)
for i in range(n):
    for j in range(0, n-i-1):
        if small_evens[j] > small_evens[j+1]:
            small_evens[j], small_evens[j+1] = small_evens[j+1], small_evens[j]

if small_evens:
    print("Четные числа меньше 10 в порядке возрастания:", end=" ")
    for num in small_evens:
        print(num, end=" ")
    print()
else:
    print("Четных чисел меньше 10 нет")