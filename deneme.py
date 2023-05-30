import numpy as np
import matplotlib.pyplot as plt

# Generate a sample time domain signal
time = np.linspace(0, 1, 1000)  # Time values from 0 to 1 with 1000 samples
frequency = 10  # Frequency of the signal in Hz
amplitude = 1  # Amplitude of the signal
signal = amplitude * np.sin(2 * np.pi * frequency * time)  # Generate a sine wave signal

# Perform Fourier Transform (DFT)
signal_freq = np.fft.fft(signal)

# Calculate the corresponding frequency values
sampling_frequency = 1 / (time[1] - time[0])  # Sampling frequency based on time spacing
freq = np.fft.fftfreq(len(signal), d=1/sampling_frequency)

# Plot the frequency domain representation
plt.plot(freq, np.abs(signal_freq))
plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude')
plt.title('Frequency Domain Representation')
plt.show()
