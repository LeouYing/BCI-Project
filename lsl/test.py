import pylsl
from pylsl import StreamInlet, resolve_stream
import matplotlib.pyplot as plt
import numpy as np
from statistics import mean

fs = 250
fft_length = 256

# Set up the plot
plt.ion()  # enable interactive mode
fig, ax = plt.subplots()

labels = ['Delta', 'Theta', 'Alpha', 'Beta', 'Gamma']

# first resolve an EEG stream on the lab network
print("looking for an EEG stream...")
stream = pylsl.resolve_byprop('name', 'eeg')

# create a new inlet to read from the stream
inlet = StreamInlet(stream[0])

buffer_size = 500
timestamps = np.zeros(buffer_size)
data_buffer = np.zeros(buffer_size)

while True:
    chunks, timestamps = inlet.pull_chunk()

    if timestamps:

        averages = [mean(x) for x in zip(*chunks)]

        bandpower = averages

        ax.clear()
        ax.bar(labels, bandpower)
        ax.set_title("Real-time bar graph")
        ax.set_xlabel("brainwave")
        ax.set_ylabel("bandpower")

        plt.pause(0.1)

# Close the plot
# plt.close(fig)