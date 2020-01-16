import pygame
import random
import os
import sys
pygame.init()
SIZE = WIDTH, HEIGHT = 1137, 810
screen = pygame.display.set_mode(SIZE)
CELL_SIZE = 100
WHITE = pygame.Color('white')
BOARD_COLOR = (13, 127, 184)
RED = pygame.Color('red')
FPS = 120
CLOCK = pygame.time.Clock()
MOVESPEED = 10
WAIT = 30
IS_MOVING = False
STARTSCREEN = True
SETTINGS = False
TEXTLCOLOR = (184, 32, 111)
BUTTONCOLOR = (76, 165, 85)
SCORE = 0
GRAVITY = 0.5
pygame.mixer.music.load('data\music.mp3')
CRYSTALBREAKSOUND = pygame.mixer.Sound('data\sound.wav')
CRYSTALBREAKSOUND.set_volume(0.2)
pygame.mixer.music.set_volume(0.5)
MUSICVOLUME = int(pygame.mixer.music.get_volume() * 100)
pygame.mixer.music.play(1)


def load_image(name):
    fullname = os.path.join('data', name)
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
        if pygame.sprite.spritecollide(self, buttons, False):
            button = pygame.sprite.spritecollide(self, buttons, False)[0]
            button.on_click()
        else:
            board.get_click(pos)
            if not self.select_first:
                for i in pygame.sprite.spritecollide(self, c_sprites, False):
                    self.select_first = i
            else:
                if board.switchable:
                    for i in pygame.sprite.spritecollide(self, c_sprites, False):
                        self.select_second = i
                    self.switch(pos)
                else:
                    self.select_first = self.select_second = None
                    board.select_first = board.select_second = None

    def switch(self, pos):
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
        global SCORE
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
        while self.find_three_in_row(False):
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
                    pygame.draw.rect(screen, RED, rect, 4)
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

    def find_three_in_row(self, count_score):
        global SCORE
        c_delete = []
        for x in range(self.width):
            for y in range(self.height):
                try:
                    if self.board[x][y] == self.board[x][y + 1] == self.board[x][y + 2] != 0:
                        if count_score:
                            SCORE += 30
                        i = 3
                        try:
                            while self.board[x][y + i] == self.board[x][y]:
                                if count_score:
                                    SCORE += 10 * i
                                i += 1
                        except IndexError:
                            pass
                        for k in range(i):
                            c_delete.append([x, y + k])
                except IndexError:
                    pass
                try:
                    if self.board[x][y] == self.board[x + 1][y] == self.board[x + 2][y] != 0:
                        if count_score:
                            SCORE += 30
                        i = 3
                        try:
                            while self.board[x + i][y] == self.board[x][y]:
                                if count_score:
                                    SCORE += 10 * i
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
        if self.find_three_in_row(False):
            self.undo = False
        else:
            self.board[x1][y1], self.board[x2][y2] = self.board[x2][y2], self.board[x1][y1]
            self.undo = True
        self.select_first = self.select_second = self.switchable = None
        return self.undo

    def delete_crystals(self):
        global c_sprites, del_c
        if self.find_three_in_row(False):
            CRYSTALBREAKSOUND.play()
        for cell in self.find_three_in_row(True):
            x, y = cell
            DeleteCrystal(x, y)
            if self.board[x][y] != 0:
                create_particles((x * CELL_SIZE + 50, y * CELL_SIZE + 50), self.board[x][y])
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
buttons = pygame.sprite.Group()
move_point = pygame.sprite.GroupSingle()
background = pygame.sprite.GroupSingle()
particles = pygame.sprite.Group()


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
        global IS_MOVING
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
        elif self.rect.y <= 7 * CELL_SIZE and not IS_MOVING:
            global move_point
            c_under = MovePoint(self.rect.left, self.rect.top)
            if not pygame.sprite.spritecollideany(c_under, c_sprites):
                self.rect.move_ip(0, MOVESPEED)
            move_point.empty()


screen_rect = (0, 0, WIDTH, HEIGHT)


class Particle(pygame.sprite.Sprite):
    def __init__(self, pos, dx, dy, c_type):
        self.particle = [load_image(f'{c_type}.png')]
        for scale in (5, 10, 20):
            self.particle.append(pygame.transform.scale(self.particle[0], (scale, scale)))
        self.particle.pop(0)
        super().__init__(particles)
        self.image = random.choice(self.particle)
        self.rect = self.image.get_rect()

        self.velocity = [dx, dy]
        self.rect.x, self.rect.y = pos

        self.gravity = GRAVITY

    def update(self):
        self.velocity[1] += self.gravity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if not self.rect.colliderect(screen_rect):
            self.kill()


def create_particles(position, c_type):
    particle_count = 5
    numbers = range(-5, 6)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers), c_type)


class Button(pygame.sprite.Sprite):
    def __init__(self, text, pos, size, tip):
        super().__init__(buttons)
        self.image = pygame.Surface(size)
        self.image.fill(BUTTONCOLOR)
        font = pygame.font.SysFont('arial', 40)
        font.set_bold(1)
        self.text = font.render(text, 1, TEXTLCOLOR)
        self.image.blit(self.text, (10, 5))
        self.rect = self.image.get_rect()
        self.rect.move_ip(pos)
        self.type = tip

    def on_click(self):
        global STARTSCREEN, board, SCORE, SETTINGS, MUSICVOLUME
        if self.type == 'endless':
            STARTSCREEN = False
        elif self.type == 'exit':
            pygame.quit()
            sys.exit()
        elif self.type == 'home':
            STARTSCREEN = True
            SETTINGS = False
        elif self.type == 'reset':
            board = Board(9, 8)
            SCORE = 0
        elif self.type == 'settings':
            SETTINGS = True
            STARTSCREEN = False
        elif self.type == 'plus':
            if MUSICVOLUME < 100:
                MUSICVOLUME += 10
                pygame.mixer.music.set_volume(MUSICVOLUME / 100)

        elif self.type == 'minus':
            if MUSICVOLUME > 0:
                MUSICVOLUME -= 10
                pygame.mixer.music.set_volume(MUSICVOLUME / 100)


class Score:
    def __init__(self):
        self.draw_score = pygame.Surface((205, 90))
        self.font = pygame.font.SysFont('arial', 72)
        self.font.set_bold(1)
        self.score = 0

    def update(self):
        self.draw_score.fill(BUTTONCOLOR)
        self.score = SCORE
        text = self.font.render(str(self.score), 1, TEXTLCOLOR)
        self.draw_score.blit(text, (5, 5))
        screen.blit(self.draw_score, (930, 5))


board = Board(9, 8)
running = True
BackGround()
cursor = Cursor(Crystal)


def start_screen():
    global STARTSCREEN, TEXTLCOLOR, board, SCORE, score
    buttons.empty()
    SCORE = 0
    font = pygame.font.SysFont('thaoma', 150)
    font.set_bold(1)
    game_name = font.render('Crystal Rush', 1, TEXTLCOLOR)
    screen.fill((0, 0, 0))
    background.draw(screen)
    screen.blit(game_name, (170, 290))
    Button('Бесконечный режим', (350, 400), (400, 55), 'endless')
    Button('      Настройки', (350, 470), (400, 55), 'settings')
    Button('         Выход', (350, 540), (400, 55), 'exit')
    buttons.draw(screen)
    STARTSCREEN = True
    pygame.display.flip()
    while STARTSCREEN:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                cursor.on_click(event.pos)
        all_sprites.update()
    buttons.empty()
    Button('В Меню', (930, 200), (205, 50), 'home')
    Button('Сбросить', (930, 260), (205, 50), 'reset')
    board = Board(9, 8)
    score = Score()


def settings():
    global STARTSCREEN, SETTINGS, MUSICVOLUME
    buttons.empty()
    font1 = pygame.font.SysFont('thaoma', 150)
    font1.set_bold(1)
    font2 = pygame.font.SysFont('arial', 40)
    font2.set_bold(1)
    Button('Громкость музыки: ', (150, 300), (370, 50), 'empty')
    Button('-', (530, 300), (50, 50), 'minus')
    Button('+', (660, 300), (50, 50), 'plus')
    Button('В Меню', (480, 500), (180, 50), 'home')
    while SETTINGS:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                cursor.on_click(event.pos)
        screen.fill((0, 0, 0))
        background.draw(screen)
        all_sprites.update()
        settings_text = font1.render('Настройки', 1, TEXTLCOLOR)
        volume = font2.render(str(MUSICVOLUME), 1, TEXTLCOLOR)
        screen.blit(settings_text, (250, 80))
        screen.blit(volume, (590, 300))
        buttons.draw(screen)
        pygame.display.flip()

    STARTSCREEN = True


start_screen()
while running:
    score = Score()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                cursor.on_click(event.pos)
        if event.type == WAIT:
            board.delete_crystals()
            IS_MOVING = False
    if board.find_empty():
        board.board_gravity()

    if SETTINGS:
        settings()
    if STARTSCREEN:
        start_screen()
    c_sprites.update()
    all_sprites.update()
    background.draw(screen)
    score.update()
    board.render()
    buttons.draw(screen)
    c_sprites.draw(screen)
    particles.update()
    particles.draw(screen)
    pygame.display.flip()
    CLOCK.tick(FPS)
