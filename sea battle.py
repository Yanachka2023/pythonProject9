from random import randint


class Dot:  # класс точек на поле
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other): # отвечает за сравнение двух объектов
        return self.x == other.x and self.y == other.y

    def __repr__(self): # отвечает за вывод точек в консоль
        return f"({self.x}, {self.y})"


class BoardException(Exception): # общий класс исключений
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"


class BoardWrongShipException(BoardException): # исключение для размещения кораблей
    pass


class Ship:  # корабль на игровом поле
    def __init__(self, bow, l, o):
        self.bow = bow # точка, где размещен нос корабля
        self.l = l # длина
        self.o = o # направление корабля вертикальное/горизонтальное
        self.lives = l  # количество жизней

    @property
    def dots(self):  # возвращает список всех точек корабля
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot): # показывает попали мы в корабль или нет
        return shot in self.dots


class Board: # игровая доска
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid # определяет нужно ли наше поле скрывать

        self.count = 0  # количество пораженных кораблей

        self.field = [["o"] * size for _ in range(size)] # сетка

        self.busy = []  # хранятся занятые точки (либо кораблем, либо точкой, куда мы стреляли)
        self.ships = []  # список кораблей доски

    def add_ship(self, ship): # ставим корабль на доску

        for d in ship.dots:
            if self.out(d) or d in self.busy: # проверяет что каждая точка корабля не уходит за границы и не занята
                raise BoardWrongShipException() # если это не так, выбрасывается исключение
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d) # запишем точку в список занятых (в списке находится наш корабль или
            # корабли, которые с ним соседствуют)

        self.ships.append(ship) # добавляем список собственных кораблей
        self.contour(ship) # и обводим его по контуру

    def contour(self, ship, verb=False): # обводит корабль по контуру
        near = [       # в данном списке объявлены все точки, вокруг той, в которой мы находимся; описывает сдвиги
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy: # если точка не выходит за границы дочки и не занята
                    # еще, то добавляем ее в список занятых точек и ставим на месте этой точки, точку
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def __str__(self):
        res = ""  # переменная, в которую записывается вся наша доска
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):  # в цикле проходимся по строкам доски, берем индекс нашей доски
            res += f"\n{i + 1} | " + " | ".join(row) + " |"  # выводим номер строки и клетки нашей строки

        if self.hid:  # данный параметр отвечает за то, нужно ли скрывать корабли на доске
            res = res.replace("■", "o") # если ИСТИНА заменяем все символы корабля на пустые символы
        return res

    def out(self, d):  # проверяет, находится ли точка за пределами доски
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))  # если находится- координаты лежат в интервале
        # от 0 до size, если выходит за границы- отрицание условия


    def shot(self, d): # делает выстрел по доске
        if self.out(d): # проверяем выходит ли точка за границы
            raise BoardOutException() # если выходит, выбрасываем исключение

        if d in self.busy: # проверяем занята ли точка
            raise BoardUsedException() # если занята, выбрасываем исключение

        self.busy.append(d)

        for ship in self.ships:  # проходимся в цикле по кораблям, проверяем принадлежит ли точка к какому то кораблю
            if ship.shooten(d):
                ship.lives -= 1
                self.field[d.x][d.y] = "X" # помечаем подбитые корабли
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False # ход больше не нужно делать
                else:
                    print("Корабль подбит!")
                    return True # нужно повторить ход

        self.field[d.x][d.y] = "T" # если ни одни корабль не был поражен
        print("Промах!")
        return False

    def begin(self):
        self.busy = [] # список должен быть обнулен, т.к. мы будем хранить точки, куда игрок стрелял


class Player: # класс игрока в игру
    def __init__(self, board, enemy):
        self.board = board #  доска игрока
        self.enemy = enemy # доска врага

    def ask(self): # "спрашивает" игрока, в какую клетку он делает выстрел
        raise NotImplementedError()

    def move(self): # делает ход в игре
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target) # делаем выстрел по вражеской доске
                return repeat
            except BoardException as e:
                print(e)


class AI(Player): # класс компьютера
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class User(Player): # класс пользователя
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size = 6):
        self.size = size
        pl = self.random_board() # генерируем две случайные доски для компьютера и для игрока
        co = self.random_board()
        co.hid = False

        self.ai = AI(co, pl)   # игрок-компьютер
        self.us = User(pl, co) # игрок-пользователь

    def random_board(self): # генерирует случайную доску
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self): # каждый корабль расставляем на доску
        lens = [3, 2, 2, 1, 1, 1, 1]  # длина кораблей
        board = Board(size = self.size) # создаем доску
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship) # добавляем корабль
                    break
                except BoardWrongShipException:
                    pass
        board.begin() # подготовка доски к игре
        return board

    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")


    def loop(self): # метод с самим игровым циклом
        num = 0
        while True:
            print("-" * 20)
            print("Доска игрока:")
            print(self.us.board)
            print("+" * 20)
            print("Доска компьютера:")
            print(self.ai.board)

            if num % 2 == 0:
                print("-" * 20)
                print("Ходит игрок!")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat: # нужно ли повторить ход
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print("Игрок выиграл!")
                break

            if self.us.board.count == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                break

            num += 1

    def start(self): # запуск игры
        self.greet()
        self.loop()

g= Game()
g.start()






