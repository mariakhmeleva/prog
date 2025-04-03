#1/1
x, y, z = input('Введите число '), input('Введите число '), input('Введите число    ')
try:
    x = int(x)
    y = int(y)
    z = int(z)
    print('Минимальное число ',min(x,y,z))
except:
    print('Вы ввели не число')

