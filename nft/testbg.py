import pygame
import math

pygame.init()

clock = pygame.time.Clock()
FPS = 60

SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 418

#create game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("test bg")

#load image
bg = pygame.image.load("testnight.jpg").convert()
bg_width = bg.get_width()
#define game variables
scroll = 0
tiles = math.ceil(SCREEN_WIDTH  / bg_width) + 1
#game loop

#screen.blit(bg,(0,0))
#crop = pygame.Surface((0, 0))
crop = pygame.Surface((1000, 500))
crop1 = bg.subsurface((1000, 0, 500, 418))
crop2 = bg.subsurface((0, 0, 500, 418))
#crop = crop1.copy()
crop.blit(crop1, (0, 0))
crop.blit(crop2, (500, 0))

screen.blit(crop, (0,0))
pygame.display.update()
run = True
while run:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      run = False
while run:

  clock.tick(FPS)
  #draw scrolling background
  for i in range(0, tiles):
    screen.blit(bg, (i * bg_width + scroll, 0))

  #scroll background
  scroll -= 5

  #reset scroll
  if abs(scroll) > bg_width:
    scroll = 0

  #event handler
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      run = False

  pygame.display.update()
pygame.quit()