import mne
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch
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
CHANNEL_INDEX = 0
FREQ_RANGE = (0.5, 79)
N_PER_SEG = 2048
SMOOTH_WINDOW = 15
DB_MIN, DB_MAX = -10, 20
MATCH_THRESHOLD = 80  # %
DEVIATION_TOL = 0.15  # 15%

# -------------------------------
# HELPER: Moving average smoother
# -------------------------------
def moving_average(x, window_size):
    if len(x) < window_size:
        return x
    return np.convolve(x, np.ones(window_size)/window_size, mode='same')

# -------------------------------
# HELPER: Normalize to fixed dB range
# -------------------------------
def normalize_db_curve(curve, min_val=DB_MIN, max_val=DB_MAX):
    curve_min = np.min(curve)
    curve_max = np.max(curve)
    if curve_max == curve_min:
        return np.full_like(curve, min_val)
    scaled = (curve - curve_min) / (curve_max - curve_min)
    return scaled * (max_val - min_val) + min_val

# -------------------------------
# HELPER: Compute PSD and interpolate to common freq
# -------------------------------
def compute_group_psd_fixed_freq(file_list, common_freqs=None):
    psd_stack = []
    for f in file_list:
        try:
            raw = mne.io.read_raw_edf(f, preload=True, verbose=False)
        except Exception as e:
            print(f"❌ Error reading {f}: {e}")
            continue

        sfreq = raw.info['sfreq']
        raw.notch_filter(freqs=50, verbose=False)

        try:
            raw.filter(FREQ_RANGE[0], FREQ_RANGE[1], fir_design='firwin', verbose=False)
        except ValueError:
            # fallback filter length for short signals
            raw.filter(FREQ_RANGE[0], FREQ_RANGE[1], fir_design='firwin', filter_length='auto', verbose=False)

        ch_name = raw.ch_names[CHANNEL_INDEX]
        data = raw.get_data(picks=ch_name)[0]

        if len(data) < 2:
            print(f"⚠️ Skipping file {f}: too short")
            continue

        freqs, psd = welch(data, fs=sfreq, nperseg=min(N_PER_SEG, len(data)))
        mask = (freqs >= FREQ_RANGE[0]) & (freqs <= FREQ_RANGE[1])
        freqs = freqs[mask]
        psd_db = 10 * np.log10(psd[mask] + 1e-12)

        if common_freqs is not None:
            psd_db = np.interp(common_freqs, freqs, psd_db)
            freqs = common_freqs

        psd_stack.append(psd_db)

    if len(psd_stack) == 0:
        return None, None, None

    psd_stack = np.array(psd_stack)
    mean_psd = np.mean(psd_stack, axis=0)
    smooth_psd = moving_average(mean_psd, SMOOTH_WINDOW)
    normalized_psd = normalize_db_curve(smooth_psd, DB_MIN, DB_MAX)
    return freqs, psd_stack, normalized_psd

# -------------------------------
# HELPER: Compute percentage match
# -------------------------------
def percentage_match(y1, y2):
    matches = 0
    for v1, v2 in zip(y1, y2):
        if v1 == 0 and v2 == 0:
            matches += 1
            continue
        if v1 != 0:
            deviation = abs(v1 - v2) / abs(v1)
            if deviation <= DEVIATION_TOL:
                matches += 1
    return matches / len(y1) * 100

# -------------------------------
# MAIN PROCESS
# -------------------------------
psd_data = {}
normalized_avg_psd = {}

# Step 0: Define common frequency axis
first_folder = list(MOVEMENT_FOLDERS.values())[0]
first_files = sorted(glob(os.path.join(first_folder, "*.edf")))
if not first_files:
    raise RuntimeError(f"No EDF files found in {first_folder}. Check the folder path.")

common_freqs, _, _ = compute_group_psd_fixed_freq(first_files)
if common_freqs is None:
    raise RuntimeError("Failed to define common frequency axis.")

# Step 1: Compute PSDs for all folders
for name, folder in MOVEMENT_FOLDERS.items():
    files = sorted(glob(os.path.join(folder, "*.edf")))
    if not files:
        print(f"⚠️ Warning: No EDF files found in {folder}")
        continue

    freqs, psd_stack, normalized_psd = compute_group_psd_fixed_freq(files, common_freqs=common_freqs)
    if psd_stack is None:
        print(f"⚠️ Skipping {name}: no valid PSD computed")
        continue

    psd_data[name] = psd_stack

# Step 2: Find matched datasets within each folder
matched_indices = {}
for name, stack in psd_data.items():
    n_files = stack.shape[0]
    folder_matches = set()
    for i in range(n_files):
        for j in range(i + 1, n_files):
            match_percent = percentage_match(stack[i], stack[j])
            if match_percent >= MATCH_THRESHOLD:
                folder_matches.add(i)
                folder_matches.add(j)
    matched_indices[name] = list(folder_matches)
    print(f"{name}: {len(folder_matches)} matched files out of {n_files}")

# Step 3: Compute averages of matched files
for name, indices in matched_indices.items():
    if indices:
        matched_stack = psd_data[name][indices]
        avg_psd = np.mean(matched_stack, axis=0)
        avg_psd_smooth = moving_average(avg_psd, SMOOTH_WINDOW)
        normalized_avg_psd[name] = normalize_db_curve(avg_psd_smooth, DB_MIN, DB_MAX)
    else:
        normalized_avg_psd[name] = None

# Step 4: Plot overlapping averages
plt.figure(figsize=(12, 6))
colors = ['blue', 'orange', 'green', 'red', 'purple', 'brown']

for idx, (name, avg_psd) in enumerate(normalized_avg_psd.items()):
    if avg_psd is not None:
        plt.plot(common_freqs, avg_psd, label=name,
                 color=colors[idx % len(colors)], linewidth=2)

plt.title("Averaged Matched PSDs Across Folders")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Power (dB)")
plt.ylim(DB_MIN, 0)
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()
