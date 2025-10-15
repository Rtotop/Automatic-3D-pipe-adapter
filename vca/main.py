from adapter import generate_stl

if __name__ == '__main__':
    print("Параметры цилиндра большого в мм")
    print("диаметр внешний в мм")
    d_cylinder1 = int(input())
    print("длина в мм")
    len_cylinder = int(input())
    # Параметры цилиндров
    # c = 20
    # z = 1
    # x = 10
    print("Параметры цилиндра малого")
    print("диаметр внешний")
    d_cylinder2 = int(input())
    print("Параметры цилиндра всех")
    print("толщина стенок")
    thickness = int(input())
    # Параметры цилиндров
    # x2 = 5
    # z2 = 1
    # c2 = 20
    # Создаем конус между цилиндрами
    generate_stl(d_cylinder1, d_cylinder2, thickness, len_cylinder)
