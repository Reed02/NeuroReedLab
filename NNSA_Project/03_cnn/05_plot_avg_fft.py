import scipy.io
import matplotlib.pyplot as plt

# Path to your .mat file
mat_file = '/Users/cooperledoux/Desktop/O_CNN_D_2/Baseline_Eyes_Closed/S001R02_avgFFT.mat'

# Load the .mat file
mat_contents = scipy.io.loadmat(mat_file)

# Extract variables
avg_fft = mat_contents['avg_fft_row'].flatten()
frequencies = mat_contents['f'].flatten()

# Plot
plt.figure(figsize=(8,5))
plt.plot(frequencies, avg_fft, 'k-', linewidth=2)
plt.xlabel('Frequency (Hz)')
plt.ylabel('Mean Amplitude')
plt.title('Average FFT')
plt.xlim([0, 60])
plt.grid(True)
plt.show()
