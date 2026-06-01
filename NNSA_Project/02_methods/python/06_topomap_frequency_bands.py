import mne
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch
from scipy.interpolate import griddata
from matplotlib.patches import Circle
import pandas as pd
import os
from glob import glob

# -------------------------------
# SETTINGS
# -------------------------------
MOVEMENT_FOLDERS = {
    "Eyes Open": "/Users/cooperledoux/Desktop/EEG Kinisiological Movement Project/O_CNN_D/Baseline_Eyes_Open",
    "Eyes Closed": "/Users/cooperledoux/Desktop/EEG Kinisiological Movement Project/O_CNN_D/Baseline_Eyes_Closed",
    "Rest": "/Users/cooperledoux/Desktop/EEG Kinisiological Movement Project/O_CNN_D/Rest",
    "Real Left Fist": "/Users/cooperledoux/Desktop/EEG Kinisiological Movement Project/O_CNN_D/Task1_Real_Left_Fist",
    "Real Right Fist": "/Users/cooperledoux/Desktop/EEG Kinisiological Movement Project/O_CNN_D/Task1_Real_Right_Fist",
    "Imagined Left Fist": "/Users/cooperledoux/Desktop/EEG Kinisiological Movement Project/O_CNN_D/Task2_Imag_Left_Fist",
    "Imagined Right Fist": "/Users/cooperledoux/Desktop/EEG Kinisiological Movement Project/O_CNN_D/Task2_Imag_Right_Fist",
    "Real Both Fists": "/Users/cooperledoux/Desktop/EEG Kinisiological Movement Project/O_CNN_D/Task3_Real_Both_Fists",
    "Imagined Both Fists": "/Users/cooperledoux/Desktop/EEG Kinisiological Movement Project/O_CNN_D/Task4_Imag_Both_Fists",
    "Real Both Feet": "/Users/cooperledoux/Desktop/EEG Kinisiological Movement Project/O_CNN_D/Task3_Real_Both_Feet",
    "Imagined Both Feet": "/Users/cooperledoux/Desktop/EEG Kinisiological Movement Project/O_CNN_D/Task4_Imag_Both_Feet"
}

FREQ_BANDS = {
    "Delta (0.5-4)": (0.5, 4),
    "Theta (4-8)": (4, 8),
    "Alpha (8-13)": (8, 13),
    "Beta (13-30)": (13, 30),
    "Gamma (30-79)": (30, 79),
}

N_PER_SEG = 2048
SMOOTH_WINDOW = 15

# -------------------------------
# HELPER FUNCTIONS
# -------------------------------
def moving_average(x, window_size):
    if len(x) < window_size:
        return x
    return np.convolve(x, np.ones(window_size)/window_size, mode='same')

def normalize(x):
    return (x - np.min(x)) / (np.max(x) - np.min(x) + 1e-12)

def compute_psd_per_channel(file_list):
    """Compute PSD for all channels in all files, return dict {channel: list of PSD arrays}"""
    psd_channels = {}
    for f in file_list:
        try:
            raw = mne.io.read_raw_edf(f, preload=True, verbose=False)
            sfreq = raw.info['sfreq']
            print(f"📊 Sampling rate for {os.path.basename(f)}: {sfreq} Hz (Nyquist: {sfreq/2} Hz)")

        except Exception as e:
            print(f"❌ Error reading {f}: {e}")
            continue

        sfreq = raw.info['sfreq']
        raw.notch_filter(50, verbose=False)
        raw.filter(0.5, 79, fir_design='firwin', verbose=False)

        for ch_idx, ch_name in enumerate(raw.ch_names):
            data = raw.get_data(picks=ch_name)[0]
            freqs, psd = welch(data, fs=sfreq, nperseg=min(N_PER_SEG, len(data)))
            if ch_name not in psd_channels:
                psd_channels[ch_name] = []
            psd_channels[ch_name].append((freqs, psd))
    return psd_channels

def average_band_psd(psd_list, band):
    """Average PSD within a frequency band"""
    band_vals = []
    for freqs, psd in psd_list:
        mask = (freqs >= band[0]) & (freqs <= band[1])
        band_vals.append(np.mean(psd[mask]))
    return np.mean(band_vals)

# -------------------------------
# LOAD CHANNEL POSITIONS
# -------------------------------
pos_file = "/Users/cooperledoux/Desktop/positions.csv"
positions_df = pd.read_csv(pos_file)
channels = positions_df['Channel'].values
x_pos = positions_df['X'].values
y_pos = positions_df['Y'].values

# -------------------------------
# MAIN LOOP
# -------------------------------
band_avg_per_movement = {}  # movement -> band -> channel -> value

for movement, folder in MOVEMENT_FOLDERS.items():
    files = sorted(glob(os.path.join(folder, "*.edf")))
    if not files:
        print(f"⚠️ No EDF files in {folder}")
        continue

    psd_channels = compute_psd_per_channel(files)
    band_avg_per_movement[movement] = {}
    for band_name, band_range in FREQ_BANDS.items():
        band_avg_per_movement[movement][band_name] = []
        for ch in channels:
            if ch in psd_channels:
                avg_val = average_band_psd(psd_channels[ch], band_range)
            else:
                avg_val = 0
            band_avg_per_movement[movement][band_name].append(avg_val)

# -------------------------------
# PLOT TOPOMAPS (Improved layout)
# -------------------------------
grid_x, grid_y = np.mgrid[0:1:200j, 0:1:200j]  # interpolation grid

for band_name in FREQ_BANDS.keys():
    n_movements = len(band_avg_per_movement)
    cols = 3
    rows = int(np.ceil(n_movements / cols))

    # Create figure with extra space on the right for colorbar
    fig, axes = plt.subplots(rows, cols, figsize=(5*cols, 5*rows), constrained_layout=False)
    axes = axes.flatten()

    for idx, (movement, bands) in enumerate(band_avg_per_movement.items()):
        ax = axes[idx]
        values = normalize(np.array(bands[band_name]))
        grid_z = griddata((x_pos, y_pos), values, (grid_x, grid_y), method='cubic')
        mask = (grid_x - 0.5)**2 + (grid_y - 0.5)**2 > 0.45**2
        grid_z[mask] = np.nan

        im = ax.imshow(grid_z.T, origin='lower', extent=(0,1,0,1), cmap='viridis')
        # Head outline
        ax.add_patch(Circle((0.5,0.5), 0.45, fill=False, color='k', lw=2))
        ax.plot([0.5,0.5],[0.95,0.85], color='red', lw=2)  # nose
        ax.plot([0.05,0.05],[0.4,0.6], color='black', lw=2)  # left ear
        ax.plot([0.95,0.95],[0.4,0.6], color='black', lw=2)  # right ear
        ax.scatter(x_pos, y_pos, c='white', s=40, edgecolor='k', zorder=2)

        # Labels and titles
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_aspect('equal')
        ax.set_title(movement, fontsize=12, pad=10)

    # Remove unused subplots
    for i in range(n_movements, len(axes)):
        fig.delaxes(axes[i])

    # Add a single colorbar on the right
    cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])  # [left, bottom, width, height]
    fig.colorbar(im, cax=cbar_ax, orientation='vertical', label=f'{band_name} PSD (µV²/Hz)')

    # Add main title
    fig.suptitle(f"{band_name} Band Activity Topomap", fontsize=18, fontweight='bold', y=0.98)

    # Adjust spacing between subplots and keep titles clear
    plt.subplots_adjust(
        left=0.05,
        right=0.9,   # leave space for colorbar
        top=0.9,
        bottom=0.08,
        hspace=0.5,
        wspace=0.4
    )

    plt.show()
