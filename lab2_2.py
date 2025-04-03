# 1. Считываем строку с клавиатуры
s = input("Введите строку: ")

# 2. Находим максимальную последовательность 'g'
max_len = 0
current_len = 0

for char in s:
    if char == 'g':
        current_len += 1
        if current_len > max_len:
            max_len = current_len
    else:
        current_len = 0

print(f"Максимальная длина последовательности 'g': {max_len}")

# 3. Заменяем все точки на '!' без использования replace()
result = []
for char in s:
    if char == '.':
        result.append('!')
    else:
        result.append(char)
modified_s = ''.join(result)

print("Строка после замены точек на '!':")
print(modified_s)