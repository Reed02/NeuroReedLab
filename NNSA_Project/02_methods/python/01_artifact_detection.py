import mne
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter1d

# -------------------------------
# SETTINGS
# -------------------------------
OVERLAP = False  # True = overlapping, False = stacked
SMOOTH_WINDOW = 2000
THRESHOLD_FACTOR = 3.0

# -------------------------------
# File paths (6 files)
# -------------------------------
edf_files = [
    "/Users/cooperledoux/Desktop/S001R01.edf",  # Eyes Open 1
    "/Users/cooperledoux/Desktop/S001R02.edf",  # Eyes Closed 1
    "/Users/cooperledoux/Desktop/S002R01.edf",  # Eyes Open 2
    "/Users/cooperledoux/Desktop/S002R02.edf",  # Eyes Closed 2
    "/Users/cooperledoux/Desktop/S003R01.edf",  # Eyes Open 3
    "/Users/cooperledoux/Desktop/S003R02.edf"   # Eyes Closed 3
]

# -------------------------------
# Load and preprocess all files
# -------------------------------
channel_name = 'FC5'  # preferred channel
processed_data = []

for f in edf_files:
    raw = mne.io.read_raw_edf(f, preload=True, verbose=False)

    # pick consistent channel
    ch = channel_name if channel_name in raw.ch_names else raw.ch_names[0]

    # filter 1-40 Hz
    raw.filter(1., 40., fir_design='firwin', verbose=False)

    # extract data & convert to µV
    data, times = raw[ch]
    data = data[0] * 1e6

    # Gaussian smoothing
    smoothed = gaussian_filter1d(data, sigma=10)

    # Normalize
    norm = (smoothed - np.mean(smoothed)) / np.std(smoothed)

    # Very smooth moving average
    ma = np.convolve(norm, np.ones(SMOOTH_WINDOW)/SMOOTH_WINDOW, 'same')

    # Artifact detection
    threshold = THRESHOLD_FACTOR * np.std(ma)
    artifact_mask = np.abs(ma) > threshold

    # Count artifact segments
    num_artifacts = np.sum(np.diff(artifact_mask.astype(int)) == 1)

    processed_data.append({
        'file': f.split('/')[-1],
        'times': times,
        'ma': ma,
        'artifact_mask': artifact_mask,
        'num_artifacts': num_artifacts
    })

    print(f"{f.split('/')[-1]}: {num_artifacts} artifacts detected.")

# -------------------------------
# Plotting
# -------------------------------
if OVERLAP:
    plt.figure(figsize=(14,6))
    colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown']
    for idx, d in enumerate(processed_data):
        plt.plot(d['times'], d['ma'], label=d['file'], color=colors[idx], linewidth=2)
        plt.fill_between(d['times'], d['ma'], where=d['artifact_mask'], color=colors[idx], alpha=0.25)
    plt.title(f"EEG Artifact Trends (Overlapping) - Channel {channel_name}")
    plt.xlabel("Time (s)")
    plt.ylabel("Smoothed Amplitude (a.u.)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
else:
    fig, axs = plt.subplots(len(processed_data), 1, figsize=(14, 2.5*len(processed_data)), sharex=True)
    colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown']
    for idx, d in enumerate(processed_data):
        axs[idx].plot(d['times'], d['ma'], color=colors[idx], linewidth=2)
        axs[idx].fill_between(d['times'], d['ma'], where=d['artifact_mask'], color=colors[idx], alpha=0.25)
        axs[idx].set_title(f"{d['file']} - Artifacts: {d['num_artifacts']}")
        axs[idx].set_ylabel("Smoothed Amplitude")
        axs[idx].grid(True, alpha=0.3)
    axs[-1].set_xlabel("Time (s)")
    plt.suptitle(f"EEG Artifact Trends (Stacked) - Channel {channel_name}", fontsize=14)
    plt.tight_layout(rect=[0,0,1,0.96])
    plt.show()
