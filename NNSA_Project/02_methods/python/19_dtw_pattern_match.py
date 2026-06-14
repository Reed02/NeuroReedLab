import mne
import numpy as np
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


# -----------------------------
# Extract EEG signal
# -----------------------------
def get_data(raw, channel='Cz'):
    raw_copy = raw.copy()

    # Prefer specific channel if available
    if channel in raw.info['ch_names']:
        raw_copy.pick([channel])
        data = raw_copy.get_data()[0]
    else:
        # fallback: average all EEG channels
        raw_copy.pick('eeg')
        data = raw_copy.get_data().mean(axis=0)

    return data


# -----------------------------
# EEG similarity (NO DTW)
# -----------------------------
def compute_similarity(sig1, sig2, max_len=5000):
    sig1 = np.ravel(sig1).astype(float)
    sig2 = np.ravel(sig2).astype(float)

    # align length
    min_len = min(len(sig1), len(sig2), max_len)
    sig1 = sig1[:min_len]
    sig2 = sig2[:min_len]

    # normalize (critical for EEG)
    sig1 = (sig1 - np.mean(sig1)) / (np.std(sig1) + 1e-8)
    sig2 = (sig2 - np.mean(sig2)) / (np.std(sig2) + 1e-8)

    # normalized cross-correlation
    corr = np.correlate(sig1, sig2, mode='full')

    similarity = np.max(corr) / min_len

    return similarity


# -----------------------------
# Load EEG files
# -----------------------------
print("🔍 Loading EEG data...")

eeg_data_list = [
    mne.io.read_raw_edf(path, preload=True, verbose=False)
    for path in file_paths
]

main_signals = [get_data(raw) for raw in eeg_data_list]


# -----------------------------
# Pairwise comparison
# -----------------------------
similarity_threshold = 0.8
n = len(main_signals)
pattern_indices = []

print("🔍 Comparing EEG files pairwise...")

for i in range(n):
    matches = 0

    for j in range(n):
        if i == j:
            continue

        sim = compute_similarity(main_signals[i], main_signals[j])

        if sim >= similarity_threshold:
            matches += 1

    # must match at least half the dataset
    if matches >= n // 2:
        pattern_indices.append(i)


# -----------------------------
# Results
# -----------------------------
print("\n📊 Summary of Matches:")

if pattern_indices:
    print(f"✔ Pattern detected in {len(pattern_indices)} EEG files "
          f"(≥ {similarity_threshold*100:.0f}% similarity with ≥50% of others):")

    for idx in pattern_indices:
        print(f"  - {file_paths[idx]}")
else:
    print("✘ No consistent pattern detected at the given similarity threshold.")


trash_indices = set(range(n)) - set(pattern_indices)

if trash_indices:
    print("\n🗑 Non-matching EEG files:")
    for idx in trash_indices:
        print(f"  - {file_paths[idx]}")
