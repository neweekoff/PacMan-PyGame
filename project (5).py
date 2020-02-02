import os

import pygame

pygame.init()
size_start = width_start, height_start = 800, 600
screen1 = pygame.display.set_mode(size_start)

# 1 x ghost pacman
size1 = width_all, height_all = 448, 288
size = 32

# 1 x 1 pacman
size2 = width_all2, height_all2 = 700, 775
size22 = 25


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def PrintTwoDimensionalArray(array):
    return "\n".join([" ".join([str(j) for j in i]) for i in array])


def add_ghost():
    for i in range(height):
        for j in range(width):
            if level[i][j] == "%":
                ghost = GhostBlinky(all_sprites, load_image("blinky.png", -1), 2, 2, j * size, i * size)
                Ghosts_sprites.add_internal(ghost)
                return ghost


def check_win():
    flag = True
    for i in range(height):
        for j in range(width):
            if level[i][j] == "$":
                flag = False
                break
    if flag and flag_game_2:
        if pacman.points > pacmanWASD.points:
            end = Player1Win(all_sprites)
        elif pacman.points < pacmanWASD.points:
            end = Player2Win(all_sprites)
        else:
            end = Draw(all_sprites)
    return flag


def check_lose():
    if flag_game_2:
        return
    return ghost.rect == pacman.rect


def generate_lab():
    lab = []
    for line in level:
        cur_line = []
        for el in line:
            if el != "^":
                cur_line.append(0)
            else:
                cur_line.append(-1)
        lab.append(cur_line)
    return lab


def voln(x, y, cur, n, m, lab):
    lab[x][y] = cur
    if y + 1 < m:
        if lab[x][y + 1] == 0 or (lab[x][y + 1] != -1 and lab[x][y + 1] > cur):
            voln(x, y + 1, cur + 1, n, m, lab)
    if x + 1 < n:
        if lab[x + 1][y] == 0 or (lab[x + 1][y] != -1 and lab[x + 1][y] > cur):
            voln(x + 1, y, cur + 1, n, m, lab)
    if x - 1 >= 0:
        if lab[x - 1][y] == 0 or (lab[x - 1][y] != -1 and lab[x - 1][y] > cur):
            voln(x - 1, y, cur + 1, n, m, lab)
    if y - 1 >= 0:
        if lab[x][y - 1] == 0 or (lab[x][y - 1] != -1 and lab[x][y - 1] > cur):
            voln(x, y - 1, cur + 1, n, m, lab)
    return lab


def BlinkyTurn(x, y, n, m, lab):
    cur = lab[x][y]
    if cur == 1:
        return x, y
    if y + 1 < m:
        if lab[x][y + 1] < cur and lab[x][y + 1] != -1:
            return x, y + 1
    if x + 1 < n:
        if lab[x + 1][y] < cur and lab[x + 1][y] != -1:
            cur = lab[x + 1][y]
            return x + 1, y
    if x - 1 >= 0:
        if lab[x - 1][y] < cur and lab[x - 1][y] != -1:
            cur = lab[x - 1][y]
            return x - 1, y
    if y - 1 >= 0:
        if lab[x][y - 1] < cur and lab[x][y - 1] != -1:
            return x, y - 1


# walls
class Wall(pygame.sprite.Sprite):
    wall_image = load_image("wall.png")
    wall_image = pygame.transform.scale(wall_image, (size, size))
    wall_image22 = pygame.transform.scale(wall_image, (size22, size22))

    def __init__(self, group, game='1'):
        super().__init__(group)
        if game == '1':
            self.image = Wall.wall_image
        else:
            self.image = Wall.wall_image22
        self.rect = self.image.get_rect()


# eat
class Eat(pygame.sprite.Sprite):
    eat_image = load_image("eat.png", -1)
    eat_image = pygame.transform.scale(eat_image, (size, size))
    eat_image22 = pygame.transform.scale(eat_image, (size22, size22))

    def __init__(self, group, game='1'):
        super().__init__(group)
        if game == '1':
            self.image = Eat.eat_image
        else:
            self.image = Eat.eat_image22
        self.rect = self.image.get_rect()

    def update(self, *args):
        if END:
            return
        if pacman.rect.x == self.rect.x and pacman.rect.y == self.rect.y:
            level[self.rect.y // size][self.rect.x // size] = "."
            self.rect.x, self.rect.y = -size, -size
            pacman.points += 1
        elif flag_game_2 and (pacmanWASD.rect.x == self.rect.x and pacmanWASD.rect.y == self.rect.y):
            level[self.rect.y // size][self.rect.x // size] = "."
            self.rect.x, self.rect.y = -size, -size
            pacmanWASD.points += 1


# pac man
class PacMan(pygame.sprite.Sprite):
    '''pacman_image = load_image("pac.png", -1)
    pacman_image = pygame.transform.scale(pacman_image, (size, size))
    pacman_image_left = pygame.transform.flip(pacman_image, True, False)
    pacman_image_top = pygame.transform.rotate(pacman_image, 90)
    pacman_image_bot = pygame.transform.rotate(pacman_image, 270)'''

    def __init__(self, group, sheet, columns, rows, x, y, game='1'):
        super().__init__(group)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.cur_rotation = 0
        self.count = 0
        self.flip = False
        self.points = 0

    def update(self, *args):
        if END:
            if check_lose():
                self.rect.x = -size
                self.rect.y = -size
            else:
                self.image = self.frames[1]
            return
        if args:
            event = args[0]
            if event.type == 3:
                if event.key == pygame.K_RIGHT:
                    if self.move("r"):
                        self.rect.x += size
                        self.rect.x = self.rect.x % (width * size)
                    self.cur_rotation = 0
                    self.flip = False
                elif event.key == pygame.K_LEFT:
                    if self.move("l"):
                        self.rect.x -= size
                        self.rect.x = self.rect.x % (width * size)
                    self.flip = True
                elif event.key == pygame.K_UP:
                    if self.move("u"):
                        self.rect.y -= size
                        self.rect.y = self.rect.y % (height * size)
                    self.cur_rotation = 90
                    self.flip = False
                elif event.key == pygame.K_DOWN:
                    if self.move("d"):
                        self.rect.y += size
                        self.rect.y = self.rect.y % (height * size)
                    self.flip = False
                    self.cur_rotation = 270
                Eat_sprites.update()
        self.count += 1
        if not self.count % (fps // 12):
            self.count = 0
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            if self.flip:
                self.image = pygame.transform.flip(self.frames[self.cur_frame], True, False)
            else:
                self.image = pygame.transform.rotate(self.frames[self.cur_frame], self.cur_rotation)

    def move(self, direction):
        if direction == "r":
            return level[self.rect.y // size][(self.rect.x // size + 1) % width] != "^"
        elif direction == "l":
            return level[self.rect.y // size][self.rect.x // size - 1] != "^"
        elif direction == "d":
            return level[(self.rect.y // size + 1) % height][self.rect.x // size] != "^"
        elif direction == "u":
            return level[self.rect.y // size - 1][self.rect.x // size] != "^"

    def cut_sheet(self, sheet, columns, rows):
        sheet = pygame.transform.scale(sheet, (size * columns, size * rows))
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))


class PacManWASD(pygame.sprite.Sprite):
    '''pacman_image = load_image("pac.png", -1)
    pacman_image = pygame.transform.scale(pacman_image, (size, size))
    pacman_image_left = pygame.transform.flip(pacman_image, True, False)
    pacman_image_top = pygame.transform.rotate(pacman_image, 90)
    pacman_image_bot = pygame.transform.rotate(pacman_image, 270)'''

    def __init__(self, group, sheet, columns, rows, x, y):
        super().__init__(group)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.cur_rotation = 0
        self.count = 0
        self.flip = True
        self.points = 0

    def update(self, *args):
        if END:
            if check_lose():
                self.rect.x = -size
                self.rect.y = -size
            else:
                self.image = self.frames[1]
            return
        if args:
            event = args[0]
            if event.type == 3:
                if event.key == pygame.K_d:
                    if self.move("r"):
                        self.rect.x += size
                        self.rect.x = self.rect.x % (width * size)
                    self.cur_rotation = 0
                    self.flip = False
                elif event.key == pygame.K_a:
                    if self.move("l"):
                        self.rect.x -= size
                        self.rect.x = self.rect.x % (width * size)
                    self.flip = True
                elif event.key == pygame.K_w:
                    if self.move("u"):
                        self.rect.y -= size
                        self.rect.y = self.rect.y % (height * size)
                    self.cur_rotation = 90
                    self.flip = False
                elif event.key == pygame.K_s:
                    if self.move("d"):
                        self.rect.y += size
                        self.rect.y = self.rect.y % (height * size)
                    self.flip = False
                    self.cur_rotation = 270
                Eat_sprites.update()
        self.count += 1
        if not self.count % (fps // 12):
            self.count = 0
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            if self.flip:
                self.image = pygame.transform.flip(self.frames[self.cur_frame], True, False)
            else:
                self.image = pygame.transform.rotate(self.frames[self.cur_frame], self.cur_rotation)

    def move(self, direction):
        if direction == "r":
            return level[self.rect.y // size][(self.rect.x // size + 1) % width] != "^"
        elif direction == "l":
            return level[self.rect.y // size][self.rect.x // size - 1] != "^"
        elif direction == "d":
            return level[(self.rect.y // size + 1) % height][self.rect.x // size] != "^"
        elif direction == "u":
            return level[self.rect.y // size - 1][self.rect.x // size] != "^"

    def cut_sheet(self, sheet, columns, rows):
        sheet = pygame.transform.scale(sheet, (size * columns, size * rows))
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))


class EndWin(pygame.sprite.Sprite):
    End_image = load_image("end_win.jpg")
    End_image = pygame.transform.scale(End_image, (width_all, height_all))

    def __init__(self, group):
        super().__init__(group)
        self.image = EndWin.End_image
        self.rect = self.image.get_rect()
        self.rect.x = -width_all
        self.rect.y = 0

    def update(self, *args):
        if self.rect.x < 0:
            self.rect.x += 1


class GhostBlinky(pygame.sprite.Sprite):
    ghost_image = load_image("blinky1.png", -1)
    ghost_image = pygame.transform.scale(ghost_image, (size, size))

    def __init__(self, group, sheet, columns, rows, x, y):
        super().__init__(group)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(x, y)
        self.count = 0

    def update(self, *args):
        if END:
            return
        self.count += 1
        if not self.count % (fps // 3):
            lab = voln(pacman.rect.y // size, pacman.rect.x // size, 1, height_all // size, width_all // size,
                       generate_lab())
            self.rect.y, self.rect.x = BlinkyTurn(self.rect.y // size, self.rect.x // size, height_all // size,
                                                  width_all // size, lab)
            self.rect.x *= size
            self.rect.y *= size
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]

    def cut_sheet(self, sheet, columns, rows):
        sheet = pygame.transform.scale(sheet, (size * columns, size * rows))
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))


class EndLose(pygame.sprite.Sprite):
    End_image = load_image("game_over.jpg")
    End_image = pygame.transform.scale(End_image, (width_all, height_all))

    def __init__(self, group):
        super().__init__(group)
        self.image = EndLose.End_image
        self.rect = self.image.get_rect()
        self.rect.x = -width_all
        self.rect.y = 0

    def update(self, *args):
        if self.rect.x < 0:
            self.rect.x += 1


class Player1Win(pygame.sprite.Sprite):
    Player1win = load_image("win1.png", -1)
    Player1win = pygame.transform.scale(Player1win, (width_all2, height_all2))

    def __init__(self, group):
        super().__init__(group)
        self.image = Player1Win.Player1win
        self.rect = self.image.get_rect()
        self.rect.x = -width_all2
        self.rect.y = 0

    def update(self, *args):
        if self.rect.x < 0:
            self.rect.x += 5


class Player2Win(pygame.sprite.Sprite):
    Player2win = load_image("win2.png", -1)
    Player2win = pygame.transform.scale(Player2win, (width_all2, height_all2))

    def __init__(self, group):
        super().__init__(group)
        self.image = Player2Win.Player2win
        self.rect = self.image.get_rect()
        self.rect.x = -width_all2
        self.rect.y = 0

    def update(self, *args):
        if self.rect.x < 0:
            self.rect.x += 5


class Draw(pygame.sprite.Sprite):
    draw = load_image("draw.png", -1)
    draw = pygame.transform.scale(draw, (width_all, height_all))

    def __init__(self, group):
        super().__init__(group)
        self.image = Draw.draw
        self.rect = self.image.get_rect()
        self.rect.x = -width_all
        self.rect.y = 0

    def update(self, *args):
        if self.rect.x < 0:
            self.rect.x += 1


class ButtonGame1(pygame.sprite.Sprite):
    Button = load_image("button.jpg", -1)
    Button = pygame.transform.scale(Button, (400, 200))

    def __init__(self, group):
        super().__init__(group)
        self.image = ButtonGame1.Button
        self.rect = self.image.get_rect()

    def update(self, *args):
        global running1, Button_game_1
        if args and args[0].type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(args[0].pos):
            running1 = False
            Button_game_1.rect.x = -Button_game_1.rect.w
            Button_game_1.rect.y = -Button_game_1.rect.h
            Button_game_2.rect.x = -Button_game_1.rect.w
            Button_game_2.rect.y = -Button_game_1.rect.h
            game_1()


class ButtonGame2(pygame.sprite.Sprite):
    Button = load_image("button1.jpg", -1)
    Button = pygame.transform.scale(Button, (400, 200))

    def __init__(self, group):
        super().__init__(group)
        self.image = ButtonGame2.Button
        self.rect = self.image.get_rect()

    def update(self, *args):
        global running1, Button_game_2, flag_game_2
        if args and args[0].type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(args[0].pos):
            running1 = False
            Button_game_1.rect.x = -Button_game_1.rect.w
            Button_game_1.rect.y = -Button_game_1.rect.h
            Button_game_2.rect.x = -Button_game_1.rect.w
            Button_game_2.rect.y = -Button_game_1.rect.h

            flag_game_2 = True
            game_2()


class ButtonQuit(pygame.sprite.Sprite):
    Button = load_image("quit.png", -1)
    Button = pygame.transform.scale(Button, (60, 30))

    def __init__(self, group):
        super().__init__(group)
        self.image = ButtonQuit.Button
        self.rect = self.image.get_rect()

    def update(self, *args):
        global running, running1
        if args and args[0].type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(args[0].pos):
            running = False


def game_1():
    global level, END, width_all, height_all, width, height, running, size, all_sprites, \
        Ghosts_sprites, Eat_sprites, Pacman_sprites, screen, pacman, ghost, fps, clock, end_lose, end_win

    screen = pygame.display.set_mode(size1)

    file = open(r"data/level1")
    level = []
    for line in file:
        level += [list(line.strip())]
    width = len(level[0])
    height = len(level)

    all_sprites = pygame.sprite.Group()
    Eat_sprites = pygame.sprite.Group()
    Pacman_sprites = pygame.sprite.Group()
    Ghosts_sprites = pygame.sprite.Group()

    fps = 100
    clock = pygame.time.Clock()
    END = False
    end_lose = False
    end_win = False
    running = True

    for i in range(height):
        for j in range(width):
            if level[i][j] == "^":
                sprite = Wall(all_sprites)
                sprite.rect.x, sprite.rect.y = j * size, i * size
            elif level[i][j] == "$":
                sprite = Eat(all_sprites)
                Eat_sprites.add_internal(sprite)
                sprite.rect.x, sprite.rect.y = j * size, i * size
            elif level[i][j] == "@":
                pacman = PacMan(all_sprites, load_image("pac1.png", -1), 5, 1, j * size, i * size)
                Pacman_sprites.add_internal(pacman)
                pacman.rect.x, pacman.rect.y = j * size, i * size

    ghost = add_ghost()
    quit_button = ButtonQuit(all_sprites)

    all_sprites.update()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            all_sprites.update(event)
        screen.fill((0, 0, 0))
        all_sprites.update()
        all_sprites.draw(screen)
        pygame.display.flip()
        if not END:
            if check_win() or check_lose():
                END = True
                if check_win():
                    end_win = EndWin(all_sprites)
                else:
                    end_lose = EndLose(all_sprites)
        clock.tick(fps)


def game_2():
    global level, END, width_all2, height_all2, width, height, running, size, all_sprites, \
        Ghosts_sprites, Eat_sprites, Pacman_sprites, screen, pacman, pacmanWASD, \
        fps, clock, end_lose, end_win, flag_game_2, level_to_play

    screen = pygame.display.set_mode(size2)
    size = size22
    file = open(r"data/level1x1")
    level = []
    for line in file:
        level += [list(line.strip())]
    width = len(level[0])
    height = len(level)

    all_sprites = pygame.sprite.Group()
    Eat_sprites = pygame.sprite.Group()
    Pacman_sprites = pygame.sprite.Group()

    fps = 100
    clock = pygame.time.Clock()
    END = False
    end_lose = False
    end_win = False
    running = True

    for i in range(height):
        for j in range(width):
            if level[i][j] == "^":
                sprite = Wall(all_sprites, '2')
                sprite.rect.x, sprite.rect.y = j * size22, i * size22
            elif level[i][j] == "$":
                sprite = Eat(all_sprites, '2')
                Eat_sprites.add_internal(sprite)
                sprite.rect.x, sprite.rect.y = j * size22, i * size22
            elif level[i][j] == "@":
                pacman = PacMan(all_sprites, load_image("pac1 for 1x1.png", -1), 5, 1, j * size22, i * size22)
                Pacman_sprites.add_internal(pacman)
                pacman.rect.x, pacman.rect.y = j * size22, i * size22
            elif level[i][j] == "&":
                pacmanWASD = PacManWASD(all_sprites, load_image("pac2 for 1x1.png", -1), 5, 1, j * size22, i * size22)
                Pacman_sprites.add_internal(pacmanWASD)
                pacmanWASD.rect.x, pacmanWASD.rect.y = j * size22, i * size22

    quit_button = ButtonQuit(all_sprites)

    all_sprites.update()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            all_sprites.update(event)
        screen.fill((0, 0, 0))
        all_sprites.update()
        all_sprites.draw(screen)
        pygame.display.flip()
        if not END:
            if check_win():
                END = True
        clock.tick(fps)


def main():
    global size_start, width_start, height_start, screen1, running1, \
        Buttons_sprites, Button_game_1, Button_game_2, flag_game_2

    running1 = True

    Buttons_sprites = pygame.sprite.Group()

    Button_game_1 = ButtonGame1(Buttons_sprites)
    Button_game_1.rect.x = width_start // 2 - Button_game_1.rect.w // 2
    Button_game_1.rect.y = height_start // 3 - Button_game_1.rect.h // 1.5

    Button_game_2 = ButtonGame2(Buttons_sprites)
    Button_game_2.rect.x = width_start // 2 - Button_game_2.rect.w // 2
    Button_game_2.rect.y = height_start // 2

    flag_game_2 = False

    while running1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running1 = False
            Buttons_sprites.update(event)
        screen1.fill((0, 0, 0))
        Buttons_sprites.draw(screen1)
        pygame.display.flip()


main()

# $ - очки
# @ - pacman
# ^ - стены
# % - GhostBlinky
# & - pacmanWASD
