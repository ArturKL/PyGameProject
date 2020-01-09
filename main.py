import pygame
import random
import os
pygame.init()
SIZE = WIDTH, HEIGHT = 1137, 910
screen = pygame.display.set_mode(SIZE)
CELL_SIZE = 100
WHITE = pygame.Color('white')
BOARD_COLOR = (13, 127, 184)


def load_image(name):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname).convert_alpha()
    return image


class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[] for i in range(width)]
        for i in range(width):
            for _ in range(height):
                self.board[i].append(random.choice([0, 1]))
        self.left = 10
        self.top = 10
        self.cell_size = 30
        self.turn = 1
        Crystal(1, (0, 0))
        Crystal(2, (1, 0))
        Crystal(3, (2, 0))
        Crystal(4, (3, 0))
        Crystal(5, (4, 0))
        Crystal(6, (5, 0))

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, check=False):
        for i in range(self.width):
            for j in range(self.height):
                x = self.left + self.cell_size * i
                y = self.top + self.cell_size * j
                if check:
                    if x <= check[0] <= x + self.cell_size and y <= check[1] <= y + self.cell_size:
                        return i, j
                rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                pygame.draw.rect(screen, BOARD_COLOR, rect, 1)

    def get_click(self, pos):
        cell = self.get_cell(pos)
        if cell is not None:
            self.on_click(cell)

    def get_cell(self, pos):
        return self.render(check=pos)

    def on_click(self, cell):
        pass


c_images = {1: load_image('1.png'),
            2: load_image('2.png'),
            3: load_image('3.png'),
            4: load_image('4.png'),
            5: load_image('5.png'),
            6: load_image('6.png')}
c_sprites = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()


class BackGround(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)
        self.image = load_image('background.png')
        self.image = pygame.transform.scale(self.image, SIZE)
        self.rect = self.image.get_rect()


class Crystal(pygame.sprite.Sprite):
    def __init__(self, c_type, pos):
        super().__init__(c_sprites)
        self.image = c_images[c_type]
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))
        self.rect = self.image.get_rect().move(pos[0] * CELL_SIZE + 5, pos[1] * CELL_SIZE + 5)


board = Board(9, 9)
board.set_view(5, 5, CELL_SIZE)
running = True
BackGround()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONUP:
            board.get_click(event.pos)
    all_sprites.draw(screen)
    board.render()
    c_sprites.draw(screen)
    pygame.display.flip()
