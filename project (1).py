import os

import pygame

pygame.init()
size1 = width_all, height_all = 448, 288
screen = pygame.display.set_mode(size1)
running = True
all_sprites = pygame.sprite.Group()
Eat_sprites = pygame.sprite.Group()
Pacman_sprites = pygame.sprite.Group()
Ghosts_sprites = pygame.sprite.Group()
size = 32
END = False


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
                ghost = GhostBlinky(all_sprites)
                Ghosts_sprites.add_internal(ghost)
                ghost.rect.x = j * size
                ghost.rect.y = i * size
                return ghost


def check_win():
    flag = True
    for i in range(height):
        for j in range(width):
            if level[i][j] == "$":
                flag = False
                break
    return flag


def check_lose():
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

    def __init__(self, group):
        super().__init__(group)
        self.image = Wall.wall_image
        self.rect = self.image.get_rect()


# eat
class Eat(pygame.sprite.Sprite):
    eat_image = load_image("eat.png", -1)
    eat_image = pygame.transform.scale(eat_image, (size, size))

    def __init__(self, group):
        super().__init__(group)
        self.image = Eat.eat_image
        self.rect = self.image.get_rect()

    def update(self, *args):
        if END:
            return
        if pacman.rect.x == self.rect.x and pacman.rect.y == self.rect.y:
            level[self.rect.y // size][self.rect.x // size] = "."
            self.rect.x, self.rect.y = -size, -size


# pac man
class PacMan(pygame.sprite.Sprite):
    pacman_image = load_image("pac.png", -1)
    pacman_image = pygame.transform.scale(pacman_image, (size, size))
    pacman_image_left = pygame.transform.flip(pacman_image, True, False)
    pacman_image_top = pygame.transform.rotate(pacman_image, 90)
    pacman_image_bot = pygame.transform.rotate(pacman_image, 270)

    def __init__(self, group, sheet, columns, rows, x, y):
        super().__init__(group)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.cur_rotation = 0
        self.count = 0
        self.flip = False

    def update(self, *args):
        if END:
            if check_lose():
                self.rect.x = -size
                self.rect.y = -size
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

    def __init__(self, group):
        super().__init__(group)
        self.image = GhostBlinky.ghost_image
        self.rect = self.image.get_rect()
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


file = open(r"data/level1")
level = []

for line in file:
    level += [list(line.strip())]

width = len(level[0])
height = len(level)

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

fps = 100
clock = pygame.time.Clock()
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

# $ - очки
# @ - pac man
# ^ - стены
# % - GhostBlinky

# TO DO LIST
"""
GHOSTS
"""
