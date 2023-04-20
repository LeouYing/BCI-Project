from IPython.display import display, clear_output
import numpy as np
import matplotlib.pyplot as plt
from pylsl import StreamInlet, resolve_stream, resolve_byprop
from scipy.fft import fft, ifft, fftfreq

print("looking for an EEG stream...")
streams = resolve_byprop('name', 'bci', timeout=2.5)
print(len(streams))

fig = plt.figure()
ax = fig.add_subplot(111)

# create a new inlet to read from the stream
inlet = StreamInlet(streams[0])
N = 8
data = []

while True:
    chunk, timestamps = inlet.pull_chunk()

    if timestamps:
        data.extend(chunk)
    # print(data.shape)
    if len(data) > 500:
        data = data[-500:]

        # Sample count
        N = len(data)
        # Sampling rate
        fs = 250

        # Sample spacing (inverse of sampling rate)
        df = 1/fs

        '''
        FFT and frequency time scale
        Halve the frequency domain due to real-time signal conjugate symmetry
        '''
        data_array = np.array(data)
        # print(data_array.shape)


        yfs = [fft(data_array[:, i])[:N//2] for i in range(8)]
        xf = fftfreq(N, df)[:N//2]
        # xf = xf[xf > 3]
        # xf = xf[xf < 8]

        '''
        Convert power signal to normalized decibel
        '''
        yf_plot = [20*np.log10(np.abs(yf)/np.max(yf)) for yf in yfs]
        # print(yf_plot[0])
        for i in range(8):
            yf_plot[i] -= yf_plot[i][0]
            # yf_plot[i] = yf_plot[i][xf > 3]
            
            yf_plot[i][xf > 8] = 0
            yf_plot[i][xf < 3] = 0
            yf_plot[i] = yf_plot[i][xf < 8]
            # yf_plot[i] = yf_plot[i][xf > 2]
            # yf_plot[i] = yf_plot[i][:len(xf)]

        # xf = xf[xf > 3]
        xf = xf[xf < 8]
        # xf = xf[xf > 2]

        ax.clear()
        
        # ax.plot(data)
        # ax.set_ylim(-30, 30)
        ax.set_ylim(-80, 80)
        # print(yf_plot.shape)

        for i in range(8):
            ax.plot(xf, yf_plot[i], label=f'Ch{i}')
        display(fig)
        ax.legend()
        clear_output(wait=True)
    # plt.pause(0.1)
