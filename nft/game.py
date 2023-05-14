import pygame, sys
from pygame.math import Vector2
from pygame.locals import K_LEFT, K_RIGHT, QUIT
import numpy as np
from multiprocessing import Queue
from pygame import mixer

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
ACC = 0.05
GAMEVOL = 0.4
# k = -(k/m)
FRIC = -0.03
FPS = 60

BG_FILE_NAME = "test1_resize.jpg"
MUSIC_NAME = "cruxgamemusic.mp3"
CAR_IMAGE = "roller-coaster-car.png"

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.surf = pygame.Surface((30, 30))
        #self.surf.fill((255,255,255))
        self.surf.set_colorkey((0,0,0)) #transparent block
        self.rect = self.surf.get_rect(center=(SCREEN_WIDTH/2 - 15, SCREEN_HEIGHT - 30))
        

        self.pos = Vector2((10, 385))
        self.vel = Vector2(0, 0)
        self.acc = Vector2(0, 0)
 
class Platform(pygame.sprite.Sprite):
    def __init__(self, width, height, spacing):
        super().__init__()
        # self.surf = pygame.Surface((WIDTH, 20))
        # self.surf.fill((255,0,0))

        self.width = width
        self.height = height
        self.spacing = spacing

        self.pos = Vector2((SCREEN_WIDTH/2, SCREEN_HEIGHT - (height / 2)))
        self.vel = Vector2(0, 0)
        self.acc = Vector2(0, 0)

        self.construct_grid()

    def construct_grid(self):
        # Construct checkered array
        #checkered_one_hot_array = np.fromfunction(lambda x, y: ( ((x+self.pos.x) // self.spacing) + (y // self.spacing)) % 2, (self.width, self.height))

        # Set low color
        #checkered_array = np.full((self.width, self.height, 3), (192, 174, 12))
        # Set high color
        #checkered_array[checkered_one_hot_array == 1] = (26, 38, 117)
        #self.surf = pygame.surfarray.make_surface(checkered_array)

        # Create Rect object of Surface at bottom of screen
        #self.rect = self.surf.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT - (self.height / 2)))
        
        self.surf = pygame.Surface((SCREEN_WIDTH, 60))
        self.surf = self.surf.convert_alpha()
        self.surf.fill((0,0,0,0)) #transparent surface

        
        for i in range(0, SCREEN_WIDTH + 180, 60): #180 is 3 extra trakcs so track loads on time, 60 is spacing between tracks
            smallrect = pygame.Surface((10 , 60)) #each individual brown track 10 x 60
            smallrect.fill((84, 61, 70)) 
            self.surf.blit(smallrect, (i - self.pos.x, 0)) 
        railrect = pygame.Surface((SCREEN_WIDTH, 10)) #rail of track
        railrect.fill((201, 185, 185))
        self.surf.blit(railrect, (0, 0))
        self.rect = self.surf.get_rect(topleft = (0, SCREEN_HEIGHT - 60))

    def move(self):
        self.acc = Vector2(0,0)
    
        # Set initial acceleration
        # pressed_keys = pygame.key.get_pressed()            
        # if pressed_keys[K_LEFT]:
        #     self.acc.x = -ACC
        # if pressed_keys[K_RIGHT]:
        #     self.acc.x = ACC
        self.acc.x = ACC
        
        # dt = 1

        # a = a_0 - kv
        self.acc.x += self.vel.x * FRIC

        # v = v_0 + a*dt
        self.vel += self.acc

        # x = x_0 + v*dt + 0.5*a*dt^2
        self.pos += self.vel + 0.5 * self.acc

        # Reset position
        if self.pos.x > 2*self.spacing:
            self.pos.x -= 2*self.spacing
        
        self.construct_grid()
    

pygame.init()

displaysurface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Game")

displaysurface.fill((0, 0, 0)) #transparent/black bg

startfont = pygame.font.SysFont("comicsans", 15)
starttext = startfont.render("Click anywhere on screen to start.", True, (255, 255, 255))
displaysurface.blit(starttext, (SCREEN_WIDTH / 2 - 120, SCREEN_HEIGHT / 2))

pygame.display.update()

while True: #start screen
    start_signal = False
    for ev in pygame.event.get():
        if ev.type == pygame.MOUSEBUTTONDOWN: 
            start_signal = True
            break
        if ev.type == QUIT:
            pygame.quit()
            sys.exit()
    if start_signal:
        break

PT1 = Platform(displaysurface.get_size()[0], 60, 60)
P1 = Player()

all_sprites = pygame.sprite.Group()
all_sprites.add(PT1)
all_sprites.add(P1)
 
#displaysurface.fill((228, 217, 255))


FramePerSec = pygame.time.Clock()
x_pos = SCREEN_WIDTH/2 - 10

mixer.music.load(MUSIC_NAME)
mixer.music.play(-1) #repeats infintely
mixer.music.set_volume(GAMEVOL)

car = pygame.image.load(CAR_IMAGE)
car = pygame.transform.scale(car, (100, 100))
#car_width = car.get_width()
#car_height = car.get_height()
#print ("car: ", car_width, car_height)

bg = pygame.image.load(BG_FILE_NAME).convert()
BG_WIDTH = bg.get_width()
BG_HEIGHT = bg.get_height()
#print("BG: ", BG_WIDTH, BG_HEIGHT)

bg_x = 0

score = 0
font = pygame.font.SysFont("comicsans", 15)

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    
    button = pygame.mouse.get_pressed()
    pygame.draw.rect(displaysurface, pygame.Color(255, 0, 0), pygame.Rect(0, 0, SCREEN_WIDTH, 50))
    pygame.draw.rect(displaysurface, pygame.Color(0, 255, 0), pygame.Rect(x_pos, 0, 20, 50))
    if button[0] != 0:
        x, y = pygame.mouse.get_pos()
        if y < 50:
            pygame.draw.rect(displaysurface, pygame.Color(255, 0, 0), pygame.Rect(0, 0, SCREEN_WIDTH, 50))
            if x < 10:
                x_pos = 0
            elif x > SCREEN_WIDTH - 10:
                x_pos = SCREEN_WIDTH - 20
            else:
                x_pos = x - 10
            pygame.draw.rect(displaysurface, pygame.Color(0, 255, 0), pygame.Rect(x_pos, 0, 20, 50))
 
    RATIO = x_pos / (SCREEN_WIDTH - 20)

    #ACC = RATIO * 0.2
    ACC = RATIO * 0.3

    GAMEVOL = ACC * 4 + 0.2
    mixer.music.set_volume(GAMEVOL)

    PT1.move()

    #15 is arbitrary number to control bg scroll speed
    bg_x = bg_x + ACC * 15

    #score based directly off acc
    score = score + ACC
    
    txtsurf = font.render("Score: " + str(round(score, 1)), True, (255, 255, 255))


    if ((bg_x + SCREEN_WIDTH) > BG_WIDTH):
        if (bg_x >= BG_WIDTH): #if it reaches the end of the image reset it to beginning
            bg_x -= BG_WIDTH
            croppedbg = pygame.Surface((SCREEN_WIDTH,BG_HEIGHT))
            croppedbg = bg.subsurface((bg_x, 0, SCREEN_WIDTH, BG_HEIGHT))
            displaysurface.blit(croppedbg, (0, 50))
        else: #combining part of the end of the image and beginning
            croppedbg1 = pygame.Surface((SCREEN_WIDTH,BG_HEIGHT))
            croppedbg1 = bg.subsurface((bg_x, 0, BG_WIDTH - bg_x, BG_HEIGHT))			
            croppedbg2 = pygame.Surface((SCREEN_WIDTH,BG_HEIGHT))
            croppedbg2 = bg.subsurface((0, 0, SCREEN_WIDTH - (BG_WIDTH - bg_x), BG_HEIGHT))			
            displaysurface.blit(croppedbg1, (0, 50))
            displaysurface.blit(croppedbg2, (BG_WIDTH - bg_x, 50))
    else:
        croppedbg = bg.subsurface((bg_x, 0, SCREEN_WIDTH, BG_HEIGHT))
        displaysurface.blit(croppedbg, (0, 50))

    displaysurface.blit(car, (SCREEN_WIDTH/2 - 50, SCREEN_HEIGHT - 135))
    for entity in all_sprites:
        displaysurface.blit(entity.surf, entity.rect)
    #displaysurface.blit(bg, (0,0) )

    displaysurface.blit(txtsurf, (SCREEN_WIDTH - 110, 60))

    pygame.display.update()
    FramePerSec.tick(FPS)
    
    
