from random import randint


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'Dot({self.x}, {self.y})'


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку!"


class BoardWrongShipException(BoardException):
    pass


class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l

    @property
    def dots(self):
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

    def shooten(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid

        self.count = 0  # количество пораженнных кораблей

        self.field = [['0'] * size for _ in range(size)]  # сетка

        self.busy = []  # точки
        self.ships = []  # список кораблей доски

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "0")
        return res

    def out(self, d):  # проверяет точку за пределами доски
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))  # координаты лежат от 0 до size

    def contour(self, ship, verb=False):  # добавляет корабль на доску
        near = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0),
                (1, 1)]  # обьявлены все точки вокруг той, в которой находимся, 0,0 точка в которой МЫ
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = 'T'
                    self.busy.append(cur)

    def add_ship(self, ship):  # проверяет точки корабля, на выход за границу и не занята ли точка
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()  # если это не так, то исключение
        for d in ship.dots:
            self.field[d.x][d.y] = "■"  # точки корабля
            self.busy.append(d)  # точки в которых находятся корабли или соседствующие точки (занятые точки)

        self.ships.append(ship)  # добавляем список собственных кораблей
        self.contour(ship)  # и обводим их по контору

    def shot(self, d):  # делает выстрел
        if self.out(d):  # проверяем точку на выход за границу доски
            raise BoardOutException()  # если да, то выбрасываем исключение

        if d in self.busy:  # проверяем точку на занятость
            raise BoardUsedException()  # если да, то выбрасываем исключение

        self.busy.append(d)  # если точка была не занята, то теперь занимаем ее

        for ship in self.ships:
            if ship.shooten(d):  # если корабл прострелен
                ship.lives -= 1  # то уменьшаем кол-во жизней 1
                self.field[d.x][d.y] = "X"  # ставим Х, значит корабль поражен
                if ship.lives == 0:  # если у корабля кончились жизни
                    self.count += 1  # прибавляем к щетчику уничтоженный кораблей +1
                    self.contour(ship, verb=True)  # обводим его по контуру
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")  # если кол-во дизней не 0, то выводим сообщение
                    return True  # и говорим о повторе хода

        self.field[d.x][d.y] = "T"  # если корабль не был поражен
        print("Мимо!")  # выводим сообщение
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):  # просто передаются 2 доски
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError

    def move(self):  # пытаемся сделать выстрел
        while True:
            try:
                target = self.ask()  # даем координы для выстрела
                repeat = self.enemy.shot(target)  # выполняем выстрел
                return repeat  # если выстрел прошел хорошо, то возвращаем повтор хода
            except BoardException as e:  # если прошел плохо, то выбрасываем исключение и цикл продолжается
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1}{d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()  #

            if len(cords) != 2:  # запрашиваем координаты и проверяем введены ли ДВЕ координаты!
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):  # проверяем, что это числа
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)  # проверяем эту точку, вычитаем 1(еденицу)


class Game:
    def __init__(self, size=6):  # объявляем размер доски
        self.size = size
        pl = self.random_board()  # генерируем доску для компьютера
        co = self.random_board()  # генерируем доску для игрока
        co.hid = True  # для компьютера скрываем корабли

        self.ai = AI(co, pl)  # создаем двух игроков
        self.us = User(pl, co)  # передав им доски созданные ниже в классе try_board

    def try_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]  # список длины кораблей
        board = Board(size=self.size)  # сама доска
        attempts = 0  # попытки поставить корабль
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:  # если попыток больше 2000, то возвращаем пустую доску
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:  # try добавления корабля
                    board.add_ship(ship)
                    break  # если все хророшо, то ебсконечный цикл закончится
                except BoardWrongShipException:  # если нет, то выбрасывается исключение и продолжаем итерацию заново
                    pass

        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def greet(self):
        print("--------------------")
        print("  Приветствуем  Вас  ")
        print("   в замечательной  ")
        print("        игре        ")
        print("     морской бой    ")
        print("--------------------")
        print(" формат вводА: X Y  ")
        print(" X - номер строки   ")
        print(" Y - номер столбца  ")

    def loop(self):
        num = 0  # номер хода
        while True:  # выводим доски
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            print("-" * 20)
            if num % 2 == 0:  # если номер хода четный, то ходит пользователь
                print("Ходит пользователь:")
                repeat = self.us.move()
            else:  # если нет, то ходи компьютер
                print("Ходит компьютер:")
                repeat = self.ai.move()

            if repeat:
                num -= 1

            if self.ai.board.count == 7:  # кол-во пораженых кораблей равно 7
                print("-"*20)
                print("Пользователь выиграл!")
                break

            if self.us.board.count == 7:
                print("-"*20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
