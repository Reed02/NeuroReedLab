import mne
import numpy as np
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

def scalar_dist(x, y):
    return abs(x - y)

def compute_similarity(sig1, sig2, max_len=5000):
    sig1 = np.ravel(sig1).astype(float)
    sig2 = np.ravel(sig2).astype(float)
    min_len = min(len(sig1), len(sig2), max_len)
    sig1 = sig1[:min_len]
    sig2 = sig2[:min_len]

    distance, _ = fastdtw(sig1, sig2, dist=scalar_dist)
    similarity = 1 / (1 + distance)
    return similarity

print("🔍 Loading EEG data...")
eeg_data_list = [mne.io.read_raw_edf(path, preload=True, verbose=False) for path in file_paths]
main_signals = [get_data(raw) for raw in eeg_data_list]

similarity_threshold = 0.8
n = len(main_signals)
pattern_indices = []

print("🔍 Comparing main EEG files pairwise...")

for i in range(n):
    matches = 0
    for j in range(n):
        if i == j:
            continue
        sim = compute_similarity(main_signals[i], main_signals[j])
        if sim >= similarity_threshold:
            matches += 1
    if matches >= n // 2:  # Similar to at least half the others
        pattern_indices.append(i)

print("\n📊 Summary of Matches:")
if pattern_indices:
    print(f"✔ Pattern detected in {len(pattern_indices)} main EEG files (≥ {similarity_threshold*100:.0f}% similarity with ≥50% of other files):")
    for idx in pattern_indices:
        print(f"  - {file_paths[idx]}")
else:
    print("✘ No consistent pattern detected at the given similarity threshold.")

trash_indices = set(range(n)) - set(pattern_indices)
if trash_indices:
    print(f"\n🗑 'Trash' EEG plots (do not match pattern):")
    for idx in trash_indices:
        print(f"  - {file_paths[idx]}")
