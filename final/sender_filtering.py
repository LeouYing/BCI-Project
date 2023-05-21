import numpy as np
from pylsl import StreamInlet, resolve_stream
from scipy.fft import fft, fftfreq
from time import time

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
    SLICE = 1000
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
    start_time = time()
    file_name = f'final_runs/{start_time}.csv'
    file = open(file_name, 'w+')
    while True:
        '''
        Extract a chunk + its timestamps
        from the LSL inlet
        '''
        chunk, timestamps = inlet.pull_chunk() #TODO: this is blocking

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
            data.extend(chunk) #TODO np.append to it to run faster
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