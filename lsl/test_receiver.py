from time import sleep
from random import random

import numpy as np
import matplotlib.pyplot as plt
from pylsl import StreamInlet, resolve_stream, resolve_byprop
from scipy.fft import fft, ifft, fftfreq

fig = plt.figure()
ax = fig.add_subplot(111)

print('Receiving data', flush=True)
streams = resolve_stream('type', 'EEG')

# create a new inlet to read from the stream
inlet = StreamInlet(streams[0])

# Parameters
N = 8
SLICE = 1000
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
        # If we have all channels, add to data time series
        if chunk:
            data.extend(chunk)

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

        '''
        Do FFT on data
        '''
        ys = [fft(data_array[:, i])[:SLICE//2] for i in range(N)]
        xs = fftfreq(SLICE, df)[:SLICE//2] # X-axis for FFT, N//2 because complex conjugate symmetry

        '''
        Perform Theta-band filtering 3-8 Hz (simple rect function)
        '''
        rect_filter = np.where((xs >= 3) & (xs <= 8))
        xs = np.take(xs, rect_filter)
        print(xs)
        
        for i in range(N):
            ys[i] = np.take(ys[i], rect_filter).flatten()

        ax.clear()
        for i in range(8):
            ax.plot(xs, ys[i], label=f'Ch{i}')
        ax.legend()
        plt.show()
        input()