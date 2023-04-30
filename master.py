from time import sleep
from random import random
from multiprocessing import Process
from multiprocessing import Pipe

from IPython.display import display, clear_output
import numpy as np
import matplotlib.pyplot as plt
from pylsl import StreamInlet, resolve_stream, resolve_byprop
from scipy.fft import fft, ifft, fftfreq

import pygame, sys
from pygame.math import Vector2
from pygame.locals import K_LEFT, K_RIGHT, QUIT
import numpy as np
 
# generate work
def sender(connection):
    print('Sender: Running', flush=True)
    streams = resolve_stream('type', 'EEG')

    # create a new inlet to read from the stream
    inlet = StreamInlet(streams[0])

    # Parameters
    N = 8
    SLICE = 100
    FS = 250
    df = 1 / FS

    # Our data is stored here
    '''
    t0: [ch1, ch2, ... ch8]
    t1: [ch1, ch2, ... ch8]
    .
    .
    .
    tn: [ch1, ch2, ..., ch8]
    '''
    data = []
    timestamps = []

    file = open('theta.csv', 'w+')
    while True:
        # file.write('n')
        # Get a sample
        '''
        Chunk:
        [[ch1], [ch2], [ch3], ..., [ch8]]
        =>
        [ch1, ch2, ch3, ... ch8]
        '''
        chunk, timestamps = inlet.pull_chunk()

        # We get a valid chunk
        if timestamps:
            # Converts chunk into 
            chunk = list(np.array(chunk).flatten())

            # If we have all channels, add to data time series
            if len(chunk) == N:
                data.append(chunk)

        # If we have at least SLICE number of data points
        if len(data) > SLICE:
            # Circular buffer
            data = data[-SLICE:]

            # Calculation on SLICE-sized buffer
            # y_values = np.mean(np.array(data), axis=0)
            ys = [fft(np.array(data)[:, i])[:SLICE//2] for i in range(N)] # List comprehension + scipy.fft
            
            data_array = np.array(data)
            '''
            ch1: [...]
            ch2: [...]
            ..
            chn: [...]
            '''
            ys = [fft(data_array[:, i])[:SLICE//2] for i in range(N)]
            xs = fftfreq(SLICE, df)[:SLICE//2] # X-axis for FFT, N//2 because complex conjugate symmetry

            '''
            Convert power signal to normalized decibel
            '''
            # ys = [20*np.log10(np.abs(y)/np.max(y)) for y in ys]


            # Performs Theta-band filtering 3-8 Hz
            for i in range(N):
                
                ys[i][xs > 8] = 0
                ys[i][xs < 3] = 0
                ys[i] = ys[i][xs < 8]
                ys[i] -= np.min(ys[i])

            xs = xs[xs < 8]
            
            for i in range(N):
                ys[i] = ys[i][xs > 1]

            xs = xs[xs > 1]

            ys = np.array(ys)
            theta_power = np.abs(np.mean(ys.flatten()))
            file.write(f'{theta_power},')
            # connection.send(theta_power)
    # # generate work
    # for i in range(3):
    #     # generate a value
    #     value = random()
    #     # block
    #     sleep(2)
    #     # send data
    #     connection.send(value)
    # # all done
    # connection.send(None)
    # print('Sender: Done', flush=True)
 
# consume work
def receiver(connection):
    HEIGHT = 450
    WIDTH = 400
    ACC = 0.00

    # k = -(k/m)
    FRIC = -0.03
    FPS = 60

    class Player(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__() 
            self.surf = pygame.Surface((30, 30))
            self.surf.fill((255,255,255))
            self.rect = self.surf.get_rect(center=(WIDTH/2 - 15, HEIGHT - 30))

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

            self.pos = Vector2((WIDTH/2, HEIGHT - (height / 2)))
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
            self.rect = self.surf.get_rect(center=(WIDTH/2, HEIGHT - (self.height / 2)))

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
    print('Receiver: Running', flush=True)
    # # consume work
    # while True:
    #     # get a unit of work
    #     if connection.poll():
    #         item = connection.recv()
    #         # report
    #         print(f'>receiver got {item}', flush=True)
    #         if item is None:
    #             break
    #     # check for stop
    #     print('waiting')
    #     sleep(1)
    # # all done
    pygame.init()
    FramePerSec = pygame.time.Clock()
    displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Game")

    PT1 = Platform(displaysurface.get_size()[0], 60, 60)
    P1 = Player()

    all_sprites = pygame.sprite.Group()
    all_sprites.add(PT1)
    all_sprites.add(P1)
    
    displaysurface.fill((228, 217, 255))

    x_pos = WIDTH/2 - 10
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        
        button = pygame.mouse.get_pressed()
        pygame.draw.rect(displaysurface, pygame.Color(255, 0, 0), pygame.Rect(0, 0, WIDTH, 50))
        pygame.draw.rect(displaysurface, pygame.Color(0, 255, 0), pygame.Rect(x_pos, 0, 20, 50))
        if button[0] != 0:
            x, y = pygame.mouse.get_pos()
            if y < 50:
                pygame.draw.rect(displaysurface, pygame.Color(255, 0, 0), pygame.Rect(0, 0, WIDTH, 50))
                if x < 10:
                    x_pos = 0
                elif x > WIDTH - 10:
                    x_pos = WIDTH - 20
                else:
                    x_pos = x - 10
                pygame.draw.rect(displaysurface, pygame.Color(0, 255, 0), pygame.Rect(x_pos, 0, 20, 50))
    
        RATIO = x_pos / (WIDTH - 20)

        # ACC = RATIO * 0.2
        if connection.poll():
            ACC = connection.recv()/50
            print(ACC)

        PT1.move()
        for entity in all_sprites:
            displaysurface.blit(entity.surf, entity.rect)
    
        pygame.display.update()
        FramePerSec.tick(FPS)
    print('Receiver: Done', flush=True)
 
# create the pipe
conn1, conn2 = Pipe()
# start the sender
sender_process = Process(target=sender, args=(conn2,))
sender_process.start()
# start the receiver
receiver_process = Process(target=receiver, args=(conn1,))
receiver_process.start()
# wait for all processes to finish
sender_process.join()
receiver_process.join()