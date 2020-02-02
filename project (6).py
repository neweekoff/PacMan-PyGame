import os

import pygame

pygame.init()
size1 = width, height = 224, 288
screen = pygame.display.set_mode(size1)
running = True
all_sprites = pygame.sprite.Group()
size = 32


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
    eat_image = load_image("eat.png")
    eat_image = pygame.transform.scale(eat_image, (size, size))

    def __init__(self, group):
        super().__init__(group)
        self.image = Eat.eat_image
        self.rect = self.image.get_rect()

    def update(self, *args):
        if pacman.rect.x == self.rect.x and pacman.rect.y == self.rect.y:
            self.rect.x, self.rect.y = -size, -size


# pac man
class PacMan(pygame.sprite.Sprite):
    pacman_image = load_image("pac.png")
    pacman_image = pygame.transform.scale(pacman_image, (size, size))
    pacman_image_left = pygame.transform.flip(pacman_image, True, False)
    pacman_image_top = pygame.transform.rotate(pacman_image, 90)
    pacman_image_bot = pygame.transform.rotate(pacman_image, 270)

    def __init__(self, group):
        super().__init__(group)
        self.image = PacMan.pacman_image
        self.rect = self.image.get_rect()

    def update(self, *args):
        event = args[0]
        if event.type == 3:
            if event.key == pygame.K_RIGHT:
                if self.move("r"):
                    self.rect.x += size
                    self.rect.x = self.rect.x % (width * size)
                    self.image = PacMan.pacman_image
            elif event.key == pygame.K_LEFT:
                if self.move("l"):
                    self.rect.x -= size
                    self.rect.x = self.rect.x % (width * size)
                    self.image = PacMan.pacman_image_left
            elif event.key == pygame.K_UP:
                if self.move("u"):
                    self.rect.y -= size
                    self.rect.y = self.rect.y % (height * size)
                    self.image = PacMan.pacman_image_top
            elif event.key == pygame.K_DOWN:
                if self.move("d"):
                    self.rect.y += size
                    self.rect.y = self.rect.y % (height * size)
                    self.image = PacMan.pacman_image_bot

    def move(self, direction):
        if direction == "r":
            return level[self.rect.y // size][(self.rect.x // size + 1) % width] != "^"
        elif direction == "l":
            return level[self.rect.y // size][self.rect.x // size - 1] != "^"
        elif direction == "d":
            return level[(self.rect.y // size + 1) % height][self.rect.x // size] != "^"
        elif direction == "u":
            if self.rect.y >= size:
                return level[self.rect.y // size - 1][self.rect.x // size] != "^"


file = open(r"data/level1")
level = []

for line in file:
    level += [line.strip()]

width = len(level[0])
height = len(level)

for i in range(height):
    for j in range(width):
        if level[i][j] == "^":
            sprite = Wall(all_sprites)
            sprite.rect.x, sprite.rect.y = j * size, i * size
        elif level[i][j] == "$":
            sprite = Eat(all_sprites)
            sprite.rect.x, sprite.rect.y = j * size, i * size
        elif level[i][j] == "@":
            pacman = PacMan(all_sprites)
            pacman.rect.x, pacman.rect.y = j * size, i * size

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        all_sprites.update(event)
    screen.fill((0, 0, 0))
    all_sprites.draw(screen)
    pygame.display.flip()

# $ - очки
# @ - pac man


# TO DO LIST
"""
SCORE
ANIMATION w/ROTATE(переменная отвечает за текущий градус rotate)
WIN/LOSE
GHOSTS
"""
