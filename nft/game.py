import pygame, sys
from pygame.math import Vector2
from pygame.locals import K_LEFT, K_RIGHT, QUIT
import numpy as np
<<<<<<< HEAD
from multiprocessing import Queue
from pygame import mixer
=======
 
HEIGHT = 600
WIDTH = 600
FPS = 60
>>>>>>> f08c2b8 (Comments)

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 450
ACC = 0.05
GAMEVOL = 0.4
# k = -(k/m)
FRIC = -0.03
ACC = 0.05

BG_FILE_NAME = "mars.jpg"
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
 
class Checkered(pygame.sprite.Sprite):
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
        checkered_one_hot_array = np.fromfunction(lambda x, y: ( ((x+self.pos.x) // self.spacing) + (y // self.spacing)) % 2, (self.width, self.height))

        # Set low color
        checkered_array = np.full((self.width, self.height, 3), (192, 174, 12))
        # Set high color
        checkered_array[checkered_one_hot_array == 1] = (26, 38, 117)
        self.surf = pygame.surfarray.make_surface(checkered_array)

        # Create Rect object of Surface at bottom of screen
        self.rect = self.surf.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT - (self.height / 2)))
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
<<<<<<< HEAD
    
 
pygame.init()
FramePerSec = pygame.time.Clock()
displaysurface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Game")
=======


pygame.init()
game_time = pygame.time.Clock()
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Training")
>>>>>>> f08c2b8 (Comments)

CheckeredRoad = Checkered(window.get_size()[0], int(HEIGHT/10), int(HEIGHT/10))
MainPlayer = Player()

# Add sprites for future rendering
all_sprites = pygame.sprite.Group()
all_sprites.add(CheckeredRoad)
all_sprites.add(MainPlayer)
 
<<<<<<< HEAD
#displaysurface.fill((228, 217, 255))
displaysurface.fill((0, 0, 0)) #transparent/black bg

x_pos = SCREEN_WIDTH/2 - 10

mixer.music.load(MUSIC_NAME)
mixer.music.play()
mixer.music.set_volume(GAMEVOL)

car = pygame.image.load(CAR_IMAGE)
car = pygame.transform.scale(car, (100, 100))
bg = pygame.image.load(BG_FILE_NAME).convert()
BG_WIDTH = bg.get_width()
BG_HEIGHT = bg.get_height()
bg_x = 0
#bg = pygame.transform.scale(bg, (736 * 1.15, 345 * 1.15))


=======
# Background
window.fill((228, 217, 255))

# Slider x position
x_pos = WIDTH/2 - 10

mouse_pressed = False

>>>>>>> f08c2b8 (Comments)
while True:
    # Handle exit
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    pygame.draw.rect(window, pygame.Color(255, 0, 0), pygame.Rect(0, 0, WIDTH, 50))
    pygame.draw.rect(window, pygame.Color(0, 255, 0), pygame.Rect(x_pos, 0, 20, 50))

    # Handle click slider
    button = pygame.mouse.get_pressed()
<<<<<<< HEAD
    pygame.draw.rect(displaysurface, pygame.Color(255, 0, 0), pygame.Rect(0, 0, SCREEN_WIDTH, 50))
    pygame.draw.rect(displaysurface, pygame.Color(0, 255, 0), pygame.Rect(x_pos, 0, 20, 50))
    if button[0] != 0:
        x, y = pygame.mouse.get_pos()
        if y < 50:
            pygame.draw.rect(displaysurface, pygame.Color(255, 0, 0), pygame.Rect(0, 0, SCREEN_WIDTH, 50))
=======
    if button[0]:
        x, y = pygame.mouse.get_pos()

        # If clicked on slider or slider held
        if y < 50 or mouse_pressed == True:
            mouse_pressed = True

            # Draw slider background
            slider_bg_color = pygame.Color(255, 0, 0)
            slider_bg_rect = pygame.Rect(0, 0, WIDTH, 50)
            pygame.draw.rect(window, slider_bg_color, slider_bg_rect)

            # Handle pixel overflow
>>>>>>> f08c2b8 (Comments)
            if x < 10:
                x_pos = 0
            elif x > SCREEN_WIDTH - 10:
                x_pos = SCREEN_WIDTH - 20
            else:
                x_pos = x - 10
<<<<<<< HEAD
            pygame.draw.rect(displaysurface, pygame.Color(0, 255, 0), pygame.Rect(x_pos, 0, 20, 50))
 
    RATIO = x_pos / (SCREEN_WIDTH - 20)
=======
>>>>>>> f08c2b8 (Comments)

            # Draw slider handle
            slider_handle_color = pygame.Color(0, 255, 0) # Green
            slider_handle_rect = pygame.Rect(x_pos, 0, 20, 50)
            pygame.draw.rect(window, slider_handle_color, slider_handle_rect)

    # Reset slider hold when mouse is released
    else:
        mouse_pressed = False
 
    # Calculate acceleration from slider
    RATIO = x_pos / (WIDTH - 20)
    ACC = RATIO * 0.2
    
    GAMEVOL = ACC * 4 + 0.2
    mixer.music.set_volume(GAMEVOL)

<<<<<<< HEAD
    PT1.move()

    #15 is arbitrary number to control bg scroll speed
    bg_x = bg_x + ACC * 15

    croppedbg = pygame.Surface((SCREEN_WIDTH,BG_HEIGHT))
    if ((bg_x + SCREEN_WIDTH) > BG_WIDTH):
        if (bg_x >= BG_WIDTH): #if it reaches the end of the image reset it to beginning
            bg_x = 0
            croppedbg = bg.subsurface((bg_x, 0, SCREEN_WIDTH, BG_HEIGHT))
        else: #combining part of the end of the image and beginning
            #bg_x = 0
            crop1 = bg.subsurface((bg_x, 0, BG_WIDTH - bg_x, BG_HEIGHT))
            crop2 = bg.subsurface((0, 0, SCREEN_WIDTH - (BG_WIDTH - bg_x), BG_HEIGHT))
            croppedbg.blit(crop1, (0, 0))
            croppedbg.blit(crop2, (BG_WIDTH - bg_x, 0))
    else:
        croppedbg = bg.subsurface((bg_x, 0, SCREEN_WIDTH, BG_HEIGHT))
    #croppedbg = bg.subsurface((bg_x, 0, WIDTH, BG_HEIGHT))
    #displaysurface.blit(bg, (0,50) )
    displaysurface.blit(croppedbg, (0, 50))

    displaysurface.blit(car, (SCREEN_WIDTH/2 - 50, SCREEN_HEIGHT - 135))
    for entity in all_sprites:
        displaysurface.blit(entity.surf, entity.rect)
    #displaysurface.blit(bg, (0,0) )

    
    pygame.display.update()
    FramePerSec.tick(FPS)
=======
    # Handle moving road
    CheckeredRoad.move()

    # Render sprites with blit
    for entity in all_sprites:
        window.blit(entity.surf, entity.rect)
 
    pygame.display.update()
    game_time.tick(FPS)
>>>>>>> f08c2b8 (Comments)
