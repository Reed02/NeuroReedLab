import mne
import matplotlib.pyplot as plt
import os
import numpy as np

# === Folder containing your EDF files ===
edf_folder = '/Users/cooperledoux/Desktop/Converted_EDF_Files/Task1_Real_Left_Fist'

# === Specific EDF files to plot ===
edf_filenames = [
    'S001R03_segment_004_T1.edf',
    'S001R03_segment_006_T1.edf',
    'S001R03_segment_012_T1.edf',
    'S001R03_segment_014_T1.edf',
    'S001R03_segment_018_T1.edf'
]

for filename in edf_filenames:
    edf_path = os.path.join(edf_folder, filename)

    if not os.path.exists(edf_path):
        print(f"⚠️ File not found: {edf_path}")
        continue

    # Load EEG data
    raw = mne.io.read_raw_edf(edf_path, preload=True, verbose=False)
    raw.pick('eeg')  # Use new-style picking
    raw.set_eeg_reference('average', projection=False)  # Optional average referencing

    data, times = raw.get_data(return_times=True)
    data = data * 1e6  # Convert to µV

    ch_names = raw.ch_names

    data = data[::-1]
    ch_names = ch_names[::-1]

    n_channels = len(ch_names)

    # === Use a small constant offset (adjust if needed) ===
    offset = 80  # in µV

    # Create new figure for each file
    plt.figure(figsize=(15, 6))

    for ch in range(n_channels):
        plt.plot(times, data[ch] + ch * offset, label=ch_names[ch])

    plt.title(f'EEG: {filename}')
    plt.xlabel('Time (s)')
    plt.ylabel('EEG Amplitude (µV) + offset')
    plt.yticks([])
    plt.legend(loc='upper right', fontsize='x-small', ncol=2)
    plt.grid(True)
    plt.tight_layout()
    plt.show()
