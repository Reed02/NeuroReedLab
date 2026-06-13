import mne
import numpy as np

# Path to your EDF file
edf_file = '/Users/cooperledoux/Documents/NNSA Research Project 2024-Summer 2025/EEG_Machine_Learning_and_Simulation/sourcedata/rawdata/S001/S001R01.edf'

# Load EDF file
raw = mne.io.read_raw_edf(edf_file, preload=True, verbose=False)

# Get data as numpy array (channels x timepoints)
data, times = raw.get_data(return_times=True)

# Convert all data to microvolts (µV), assuming input is in volts
data_uV = data * 1e6

# Calculate stats
means_uV = np.mean(data_uV, axis=1)
mins_uV = np.min(data_uV, axis=1)
maxs_uV = np.max(data_uV, axis=1)

# Print results
for ch_name, ch_mean, ch_min, ch_max in zip(raw.ch_names, means_uV, mins_uV, maxs_uV):
    print(f"Channel {ch_name}: Mean = {ch_mean:.2f} µV | Min = {ch_min:.2f} µV | Max = {ch_max:.2f} µV")
