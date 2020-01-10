import pygame
import random
import os
import time
pygame.init()
SIZE = WIDTH, HEIGHT = 1137, 910
screen = pygame.display.set_mode(SIZE)
CELL_SIZE = 100
WHITE = pygame.Color('white')
BOARD_COLOR = (13, 127, 184)
RED = pygame.Color('red')
FPS = 60
CLOCK = pygame.time.Clock()
MOVESPEED = 10
WAIT = 30
IS_MOVING = False


def load_image(name):
    fullname = os.path.join('A:\Python\PyGameProject\data', name)
    image = pygame.image.load(fullname).convert_alpha()
    return image


class Cursor(pygame.sprite.Sprite):
    def __init__(self, crystals):
        super().__init__(all_sprites)
        self.crystals = crystals
        self.select_first = None
        self.select_second = None
        self.image = pygame.Surface((CELL_SIZE, CELL_SIZE))
        self.rect = pygame.Rect(pygame.mouse.get_pos(), (1, 1))

    def update(self, *args):
        self.rect = pygame.Rect(pygame.mouse.get_pos(), (1, 1))

    def on_click(self, pos):
        board.get_click(pos)
        if not self.select_first:
            for i in pygame.sprite.spritecollide(self, c_sprites, False):
                self.select_first = i
        else:
            if board.switchable:
                for i in pygame.sprite.spritecollide(self, c_sprites, False):
                    self.select_second = i
                self.swithc(self.select_first, self.select_second, pos)
            else:
                self.select_first = self.select_second = None
                board.select_first = board.select_second = None

    def swithc(self, first, second, pos):
        global IS_MOVING
        cell_1 = board.get_cell(pos)
        cell_2 = board.get_cell((self.select_first.rect.left + 5, self.select_first.rect.top + 5))
        target1 = [cell_1[0] * CELL_SIZE + 5, cell_1[1] * CELL_SIZE + 5]
        target2 = [cell_2[0] * CELL_SIZE + 5, cell_2[1] * CELL_SIZE + 5]
        IS_MOVING = True
        self.select_first.target = target1
        self.select_second.target = target2
        if board.get_result():
            self.select_first.target = target2
            self.select_second.target = target1
        else:
            pygame.time.set_timer(WAIT, 500)
        self.select_first = self.select_second = None


class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[] for _ in range(width)]
        for i in range(width):
            for _ in range(height):
                self.board[i].append(1)
        self.left = 5
        self.top = 5
        self.cell_size = CELL_SIZE
        self.fill_board()
        while self.find_three_in_row():
            self.fill_board()
        self.select_first = None
        self.select_second = None
        self.direction = None
        self.switchable = False
        self.undo = None

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
                if self.select_first == (i, j) or self.select_second == (i, j):
                    pygame.draw.rect(screen, RED, rect, 2)
                else:
                    pygame.draw.rect(screen, BOARD_COLOR, rect, 1)

    def get_click(self, pos):
        cell = self.get_cell(pos)
        if cell is not None:
            self.on_click(cell)

    def get_cell(self, pos):
        return self.render(check=pos)

    def on_click(self, cell):
        if not self.select_first:
            self.select_first = cell
        elif self.select_first and cell != self.select_first:
            self.select_second = cell
            self.switch_c()

    def fill_board(self):
        for x in range(self.width):
            for y in range(self.height):
                c_type = random.randint(1, 6)
                self.board[x][y] = c_type
        self.create_sprites()

    def create_sprites(self):
        global c_sprites
        c_sprites.empty()
        for x in range(self.width):
            for y in range(self.height):
                c_type = self.board[x][y]
                Crystal(c_type, (x, y))

    def find_three_in_row(self):
        c_delete = []
        for x in range(self.width):
            for y in range(self.height):
                try:
                    if self.board[x][y] == self.board[x][y + 1] == self.board[x][y + 2] != 0:
                        i = 3
                        try:
                            while self.board[x][y + i] == self.board[x][y]:
                                i += 1
                        except IndexError:
                            pass
                        for k in range(i):
                            c_delete.append([x, y + k])
                except IndexError:
                    pass
                try:
                    if self.board[x][y] == self.board[x + 1][y] == self.board[x + 2][y] != 0:
                        i = 3
                        try:
                            while self.board[x + i][y] == self.board[x][y]:
                                i += 1
                        except IndexError:
                            pass
                        for k in range(i):
                            if [x + k, y] not in c_delete:
                                c_delete.append([x + k, y])
                except IndexError:
                    pass
        return c_delete

    def switch_c(self):
        x1, y1 = self.select_first
        x2, y2 = self.select_second
        for i in range(-1, 2):
            for j in range(-1, 2):
                if (x1 + i, y1 + j) == self.select_second and (i == 0 or j == 0):
                    self.switchable = True
        if self.switchable:
            self.board[x1][y1], self.board[x2][y2] = self.board[x2][y2], self.board[x1][y1]

    def get_result(self):
        x1, y1 = self.select_first
        x2, y2 = self.select_second
        if self.find_three_in_row():
            self.undo = False
        else:
            self.board[x1][y1], self.board[x2][y2] = self.board[x2][y2], self.board[x1][y1]
            self.undo = True
        self.select_first = self.select_second = self.switchable = None
        return self.undo

    def delete_crystals(self):
        global c_sprites, del_c
        for cell in self.find_three_in_row():
            x, y = cell
            DeleteCrystal(x, y)
            self.board[x][y] = 0
        pygame.sprite.groupcollide(c_sprites, del_c, True, True)
        self.board_gravity()

    def board_gravity(self):
        for x in range(self.width):
            for y in range(self.height - 1, -1, -1):
                if y > 0 and self.board[x][y] == 0:
                    self.board[x][y], self.board[x][y - 1] = self.board[x][y - 1], self.board[x][y]
                elif self.board[x][y] == 0:
                    pick = [i for i in range(1, 7)]
                    if x != 0:
                        pick.remove(self.board[x - 1][y])
                    try:
                        pick.remove(self.board[x + 1][y])
                    except IndexError:
                        pass
                    except ValueError:
                        pass
                    i = 0
                    while self.board[x][y + i] == 0:
                        i += 1
                    try:
                        pick.remove(self.board[x][y + i])
                    except ValueError:
                        pass
                    new_c = random.choice(pick)
                    self.board[x][y] = new_c
                    Crystal(new_c, (x, y - 1))

    def find_empty(self):
        empty = False
        for i in range(self.width):
            for j in range(self.height):
                if self.board[i][j] == 0:
                    empty = True
        return empty


class DeleteCrystal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(del_c)
        left = x * CELL_SIZE + 10
        top = y * CELL_SIZE + 10
        self.rect = pygame.Rect((left, top), (1, 1))


class MovePoint(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(move_point)
        left = x
        top = y + CELL_SIZE
        self.rect = pygame.Rect((left, top), (MOVESPEED, MOVESPEED))


c_images = {1: load_image('1.png'),
            2: load_image('2.png'),
            3: load_image('3.png'),
            4: load_image('4.png'),
            5: load_image('5.png'),
            6: load_image('6.png')}
c_sprites = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
del_c = pygame.sprite.Group()
move_point = pygame.sprite.GroupSingle()
background = pygame.sprite.GroupSingle()


class BackGround(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(background)
        self.image = load_image('background.png')
        self.image = pygame.transform.scale(self.image, SIZE)
        self.rect = self.image.get_rect()


class Crystal(pygame.sprite.Sprite):
    def __init__(self, c_type, pos):
        super().__init__(c_sprites)
        self.pos = pos
        self.image = c_images[c_type]
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))
        self.rect = self.image.get_rect().move(pos[0] * CELL_SIZE + 5, pos[1] * CELL_SIZE + 5)
        self.target = None

    def update(self):
        global IS_MOVING, IS_FALLING
        if self.target and IS_MOVING:
            if self.rect.x < self.target[0]:
                self.rect.move_ip(MOVESPEED, 0)
            elif self.rect.x > self.target[0]:
                self.rect.move_ip(-MOVESPEED, 0)
            elif self.rect.y < self.target[1]:
                self.rect.move_ip(0, MOVESPEED)
            elif self.rect.y > self.target[1]:
                self.rect.move_ip(0, -MOVESPEED)
            else:
                self.target = None
        elif self.rect.y <= 8 * CELL_SIZE and not IS_MOVING:
            global move_point
            c_under = MovePoint(self.rect.left, self.rect.top)
            if not pygame.sprite.spritecollideany(c_under, c_sprites):
                self.rect.move_ip(0, MOVESPEED)
            move_point.empty()


board = Board(9, 9)
running = True
BackGround()
cursor = Cursor(Crystal)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                cursor.on_click(event.pos)
        if event.type == WAIT:
            board.delete_crystals()
            IS_MOVING = False
            # board.board_gravity()
            # pygame.time.set_timer(WAIT, 0)
    if board.find_empty():
        board.board_gravity()
    c_sprites.update()
    all_sprites.update()
    background.draw(screen)
    board.render()
    c_sprites.draw(screen)
    pygame.display.flip()
    CLOCK.tick(FPS)
