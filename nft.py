from time import sleep
from random import random
from multiprocessing import Process
from multiprocessing import Pipe

import numpy as np
import matplotlib.pyplot as plt
from pylsl import StreamInlet, resolve_stream
from scipy.fft import fft, fftfreq

import pygame, sys
from pygame.math import Vector2
from pygame.locals import QUIT
 
# generate work
def sender(connection):
    print('Sender: Running', flush=True)
    streams = resolve_stream('type', 'EEG')

    '''
    Grabs the LSL stream inlet

    No need to modify this
    '''
    inlet = StreamInlet(streams[0])

    '''
    Modify these parameters to change the behavior

    N: Number of channels

    SLICE: Number of samples stored in the buffer to perform FFT
        Note: larger values have more frequency resolution,
        but may lead to a performance slowdown
        since FFT is an O(n log n) operation

    FS: Sampling rate
        Note: this is defined in the Cyton hardware spec
        Do not change this

    df: This is the frequency resolution
        Basically, this is the space between every
        sample in the frequency spectrum
    '''
    N = 8
    SLICE = 100
    FS = 250
    df = 1 / FS

    '''
    Data list looks like this:

    data =
    [
        [ch1, ch2, ... ch8]
        [ch1, ch2, ... ch8]
        .
        .
        .
        [ch1, ch2, ..., ch8]
    ]

    It is a time series list of 8 channels per sample
    See below for more information
        The data structure looks a lot like the received chunk
    '''
    data = []
    timestamps_data = []

    '''
    Open a CSV file for logging
    '''
    file = open('theta.csv', 'w+')
    while True:
        '''
        Extract a chunk + its timestamps
        from the LSL inlet
        '''
        chunk, timestamps = inlet.pull_chunk()

        '''
        Chunk currently looks like this:

        chunk =
        [
            [ch1, ch2, ch3, ..., chN]
            [ch1, ch2, ch3, ..., chN]
            .
            .
            .
            [ch1, ch2, ch3, ..., chN]
        ]

        It is k x N array, 
            where k = # of samples
            and N = # of channels

        It's simply a time series array
            with each time sample containing N
            values for each channel
        
        Here, we use N = 8 for 8 channels
        '''

        # If we get a valid chunk, extend our data
        if timestamps and chunk:
            data.extend(chunk)
            timestamps_data.extend(timestamps)

        '''
        We use "data" as a circular buffer to perform FFT on
        https://en.wikipedia.org/wiki/Circular_buffer

        As new samples are added, we simply push out the old samples

        Think of this buffer as a conveyer belt with limited length
            As more stuff is put on at the beginning of the queue,
            The old stuff at the end of the queue will fall off
        '''
        # If we have at least SLICE number of data points
        if len(data) > SLICE:
            '''
            This operation removes all old values

            This grabs the last SLICE number of samples, 
            effectively deleting the old data
            '''
            data = data[-SLICE:]

            '''
            Do FFT on data

            After doing the FFT on each of N channels, 
                we now have a list of N arrays, one for each channel

            Each of N arrays contains the frequency spectrum of that channel

            Here is the data structure:

            ys =
            [
                CH1 FFT 1D array
                CH2 FFT 1D array
                .
                .
                .
                CHN FFT 1D array
            ]

            Each CH_i FFT 1D array contains up to SLICE//2 values
            For example, if SLICE = 100,
                We only have 50 sample points on our frequency spectrum

            By increasing SLICE, we get more samples,
                effectively increasing our resolution (perhaps at a cost of performance?)

            Note: we only have SLICE/2 due to complex conjugate symmetry with real-valued signals + Nyquist
                Read here: https://brianmcfee.net/dstbook-site/content/ch06-dft-properties/Conjugate-Symmetry.html#why-does-this-matter

                Our sampling rate is 250 Hz. Due to Nyquist Theorem, we can only sample up to 125 Hz without aliasing
                This effectively halves our relevant frequency spectrum

                Coupled with the fact that our signal is real-valued, we only need to look at half the spectrum
            '''
            data_array = np.array(data)
            ys = [fft(data_array[:, i])[:SLICE//2] for i in range(N)] # FFT on each channel
            xs = fftfreq(SLICE, df)[:SLICE//2] # X-axis for FFT, N//2 because complex conjugate symmetry

            '''
            Perform Theta-band band-pass filtering 3-8 Hz

            We implement a band-pass filter with a simple rectangle function
            
            Our rectangle simply removes frequencies greater than or less than its bounds
            '''
            rect_filter = np.where((xs >= 3) & (xs <= 8))
            xs = np.take(xs, rect_filter)
            
            for i in range(N):
                ys[i] = np.take(ys[i], rect_filter).flatten()

            '''
            Calculate theta power (mean value of FFT -> absolute value to remove complex #s)

            Perform Min-Max normalization on each channel

            This reduces the effect of a really strong channel on the overall theta band mean


            '''
            # Lambda function to map to each channel
            min_max_normal = lambda array: (array - np.min(array)) / (np.max(array) - np.min(array))

            # Map the normalization function to each channel
            ys = list(map(min_max_normal, ys))

            # Convert back to numpy array for ez calculations
            ys = np.array(ys)

            # Calculate mean value across all channels
            theta_power = np.mean(np.abs(ys.flatten()))

            '''
            Log our theta power in a file
            '''
            file.write(f'{theta_power},')

            '''
            Send data through the pipe to the game
            '''
            connection.send(theta_power)
 
def receiver(connection):
    '''
    General game parameters

    HEIGHT: height of the screen
    
    WIDTH: width of the screen

    ACC: acceleration of the player sprite (or platform beneath)
        Note: this is set by the received theta band power

    FRIC: factor to slow down the player + limit max speed
        Also does a cool slowdown effect when ACC = 0

    FPS: graphics rendering speed
    '''
    HEIGHT = 450
    WIDTH = 400
    ACC = 0.00

    # k = -(k/m)
    FRIC = -0.03
    FPS = 60

    '''
    Player sprite (currently a white box)
    '''
    class Player(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__() 
            self.surf = pygame.Surface((30, 30))
            self.surf.fill((255,255,255))
            self.rect = self.surf.get_rect(center=(WIDTH/2 - 15, HEIGHT - 30))

            self.pos = Vector2((10, 385))
            self.vel = Vector2(0, 0)
            self.acc = Vector2(0, 0)
    
    '''
    Platform sprite (currently 1D checkered pattern)
    '''
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

    '''
    Basic game setup
    '''
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

    while True:
        '''
        Read user input if they want to exit
        '''
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        # This polls the pipe to check if there is data to be read
        if connection.poll():
            '''
            Read the theta band power from the pipe
            We divide by an arbitrary value to scale it down

            The received theta band power serves as our linear acceleration here
            - The game functions with acceleration proportional to theta-band power

            We can also use a logistic function to reduce the impact
            of extreme values: f(received value) => new acceleration
            '''
            ACC = connection.recv()/10
            print(f'ACC = {ACC}')

        '''
        Move the player sprite according to the physics parameters
        '''
        PT1.move()
        for entity in all_sprites:
            displaysurface.blit(entity.surf, entity.rect)
    
        '''
        Update the game graphics
        '''
        pygame.display.update()
        FramePerSec.tick(FPS)
 
if __name__ == '__main__':
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