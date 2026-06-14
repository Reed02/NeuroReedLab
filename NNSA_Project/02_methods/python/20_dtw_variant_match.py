import mne
import numpy as np
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d
from fastdtw import fastdtw
import warnings

warnings.filterwarnings("ignore")  # Clean output

file_paths = [
    "/Users/cooperledoux/Desktop/O_CNN_D/Baseline_Eyes_Open/S001R01.edf",
    "/Users/cooperledoux/Desktop/O_CNN_D/Baseline_Eyes_Open/S002R01.edf",
    "/Users/cooperledoux/Desktop/O_CNN_D/Baseline_Eyes_Open/S003R01.edf",
    "/Users/cooperledoux/Desktop/O_CNN_D/Baseline_Eyes_Open/S004R01.edf",
    "/Users/cooperledoux/Desktop/O_CNN_D/Baseline_Eyes_Open/S005R01.edf",
    "/Users/cooperledoux/Desktop/O_CNN_D/Baseline_Eyes_Open/S006R01.edf",
    "/Users/cooperledoux/Desktop/O_CNN_D/Baseline_Eyes_Open/S007R01.edf",
    "/Users/cooperledoux/Desktop/O_CNN_D/Baseline_Eyes_Open/S008R01.edf",
    "/Users/cooperledoux/Desktop/O_CNN_D/Baseline_Eyes_Open/S009R01.edf",
    "/Users/cooperledoux/Desktop/O_CNN_D/Baseline_Eyes_Open/S010R01.edf",
]

def get_data(raw, channel='Cz'):
    raw_copy = raw.copy()
    if channel in raw.info['ch_names']:
        raw_copy.pick([channel])
        data = raw_copy.get_data()[0]
    else:
        raw_copy.pick('eeg')
        data = raw_copy.get_data().mean(axis=0)
    return data

def generate_variants(sig, num_variants=10, peak_shift_std=20, peak_height_std=0.5, peak_width_std=3):
    variants = []
    peaks, properties = find_peaks(sig, height=None, distance=20)
    
    for _ in range(num_variants):
        variant = np.copy(sig)
        for peak_idx in peaks:
            shift = int(np.random.normal(0, peak_shift_std))
            new_peak_idx = np.clip(peak_idx + shift, 0, len(sig)-1)
            
            height_factor = 1 + np.random.normal(0, peak_height_std)
            width_factor = 1 + np.random.normal(0, peak_width_std)
            
            # Clamp width_factor to minimum 0.1 to avoid invalid sigma
            width_factor = max(width_factor, 0.1)
            
            # Modify peak height
            variant[new_peak_idx] = variant[new_peak_idx] * height_factor
            
            window = int(20 * width_factor)
            window = max(window, 3)  # minimum window size
            half_win = window // 2
            
            start = max(new_peak_idx - half_win, 0)
            end = min(new_peak_idx + half_win, len(sig))
            
            # Apply gaussian smoothing with sigma = width_factor (must be positive float)
            variant[start:end] = gaussian_filter1d(variant[start:end], sigma=width_factor)
        variants.append(variant)
    return variants

def scalar_dist(x, y):
    return abs(x - y)

def compute_similarity(sig1, sig2, method="dtw", max_len=5000):
    sig1 = np.ravel(sig1).astype(float)
    sig2 = np.ravel(sig2).astype(float)
    min_len = min(len(sig1), len(sig2), max_len)
    sig1 = sig1[:min_len]
    sig2 = sig2[:min_len]

    if method == "dtw":
        distance, _ = fastdtw(sig1, sig2, dist=scalar_dist)
        similarity = 1 / (1 + distance)
        return similarity
    elif method == "correlation":
        corr = np.corrcoef(sig1, sig2)[0, 1]
        return corr
    else:
        raise ValueError("Unknown method")

print("🔍 Loading EEG data...")
eeg_data_list = [mne.io.read_raw_edf(path, preload=True, verbose=False) for path in file_paths]
main_signals = [get_data(raw) for raw in eeg_data_list]

num_variants = 20
similarity_threshold = 0.8
similarity_method = "dtw"

print("🔍 Generating variants for each main signal...")
all_variants = [generate_variants(sig, num_variants=num_variants,
                                  peak_shift_std=40, peak_height_std=0.8, peak_width_std=5)
                for sig in main_signals]

print("🔍 Performing cross-comparison...")
n = len(main_signals)
pattern_indices = []

for i in range(n):
    main_sig = main_signals[i]
    main_variants = all_variants[i]
    matches = 0

    for j in range(n):
        if i == j:
            continue
        other_sig = main_signals[j]
        sim_main = compute_similarity(main_sig, other_sig, method=similarity_method)
        if sim_main >= similarity_threshold:
            matches += 1
            continue

        variant_matches = False
        for variant in main_variants:
            sim = compute_similarity(other_sig, variant, method=similarity_method)
            if sim >= similarity_threshold:
                variant_matches = True
                break
        if variant_matches:
            matches += 1

    if matches >= n // 2:
        pattern_indices.append(i)

print("\n📊 Summary of Matches:")
if pattern_indices:
    print(f"✔ Pattern detected in {len(pattern_indices)} main EEG files (≥ {similarity_threshold*100:.0f}% similarity with others or variants):")
    for idx in pattern_indices:
        print(f"  - {file_paths[idx]}")
else:
    print("✘ No consistent pattern detected at the given similarity threshold.")

trash_indices = set(range(n)) - set(pattern_indices)
if trash_indices:
    print(f"\n🗑 'Trash' EEG plots (do not match pattern):")
    for idx in trash_indices:
        print(f"  - {file_paths[idx]}")
