import pygame
import sys
from options import *
from game import *

"""
False: blanc
True: noir
"""

# setup
pygame.init()
clock = pygame.time.Clock()

# screen
screen = pygame.display.set_mode((screen_width, screen_height))

# game
grid = Game()
grid.load("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
grid.sound = True

# GAME LOOP
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()
            grid.click(pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            pos = pygame.mouse.get_pos()
            grid.right_click(pos)
        if event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            grid.release(pos)
    screen.fill((0, 0, 0))
    grid.tick()
    grid.draw(screen)
    pygame.display.flip()
    clock.tick(60)
