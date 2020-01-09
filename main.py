import pygame
from random import choice
pygame.init()
size = width, height = 500, 500
screen = pygame.display.set_mode(size)


class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[] for i in range(width)]
        print(self.board)
        for i in range(width):
            for _ in range(height):
                self.board[i].append(choice([0, 1]))
        self.left = 10
        self.top = 10
        self.cell_size = 30
        self.turn = 1

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
                pygame.draw.rect(screen, pygame.Color('white'), rect, 1)

    def get_click(self, pos):
        cell = self.get_cell(pos)
        if cell is not None:
            self.on_click(cell)

    def get_cell(self, pos):
        return self.render(check=pos)

    def on_click(self, cell):
        pass


board = Board(7, 7)
board.set_view(25, 25, 65)
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONUP:
            board.get_click(event.pos)
    board.render()
    pygame.display.flip()
    screen.fill((0, 0, 0))