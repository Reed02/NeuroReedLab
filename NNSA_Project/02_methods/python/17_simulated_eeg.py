import random
import matplotlib.pyplot as plt

# --- EEG Channel statistics: name -> (mean, min, max) ---
stats = {
    "Fc5": (-0.76, -232, 397),
    "Fc3": (2.04, -233, 310),
    "Fc1": (2.08, -231, 281),
    "Fcz": (2.85, -238, 257),
    "Fc2": (1.46, -238, 249),
    "Fc4": (3.06, -227, 229),
    "Fc6": (1.75, -222, 244),
    "C5": (-1.89, -190, 350),
    "C3": (2.36, -207, 269),
    "C1": (0.19, -201, 244),
    "Cz": (2.39, -202, 227),
    "C2": (2.69, -211, 219),
    "C4": (-1.22, -190, 206),
    "C6": (-0.63, -162, 183),
    "Cp5": (-0.46, -177, 276),
    "Cp3": (-0.17, -190, 246),
    "Cp1": (-0.78, -190, 241),
    "Cpz": (-0.65, -194, 221),
    "Cp2": (-0.12, -181, 204),
    "Cp4": (-0.50, -171, 187),
    "Cp6": (1.35, -143, 191),
    "Fp1": (-8.76, -518, 597),
    "Fpz": (-7.78, -496, 564),
    "Fp2": (-8.69, -507, 596),
    "Af7": (-10.70, -487, 559),
    "Af3": (-9.14, -470, 553),
    "Afz": (-2.96, -327, 380),
    "Af4": (-4.73, -379, 455),
    "Af8": (-6.51, -501, 565),
    "F7": (-2.35, -309, 493),
    "F5": (-5.62, -347, 448),
    "F3": (-1.67, -275, 313),
    "F1": (-0.14, -270, 322),
    "Fz": (-0.84, -268, 309),
    "F2": (-0.45, -273, 305),
    "F4": (-0.87, -272, 309),
    "F6": (-1.16, -301, 342),
    "F8": (-1.78, -240, 371),
    "Ft7": (-2.38, -231, 404),
    "Ft8": (-0.86, -153, 229),
    "T7": (1.94, -198, 363),
    "T8": (1.75, -142, 198),
    "T9": (-1.71, -173, 341),
    "T10": (-0.10, -78, 141),
    "Tp7": (0.14, -169, 318),
    "Tp8": (-0.70, -101, 149),
    "P7": (-0.86, -176, 281),
    "P5": (1.08, -181, 262),
    "P3": (1.31, -201, 251),
    "P1": (-0.59, -204, 247),
    "Pz": (-0.19, -185, 230),
    "P2": (0.80, -171, 227),
    "P4": (-1.17, -162, 214),
    "P6": (-1.80, -146, 191),
    "P8": (-1.03, -149, 180),
    "Po7": (0.79, -200, 265),
    "Po3": (-2.02, -205, 259),
    "Poz": (-0.28, -197, 249),
    "Po4": (1.03, -187, 210),
    "Po8": (1.23, -206, 232),
    "O1": (-0.63, -239, 262),
    "Oz": (-1.15, -213, 264),
    "O2": (-0.32, -216, 227),
    "Iz": (-0.57, -192, 231),
}

# --- Generation parameters ---
n_points = 15616
typ_step = 0.05
step_std = 0.02
momentum = 0.8
pull_strength = 0.02

# --- Time series generator function ---
def make_series(mu, lo, hi):
    series = [mu]
    prev_dt = 0.0
    for _ in range(n_points - 1):
        d_rand = random.gauss(typ_step, step_std)
        if random.random() < 0.5:
            d_rand = -d_rand
        pull = (mu - series[-1]) * pull_strength
        dt = momentum * prev_dt + (1 - momentum) * (d_rand + pull)
        nxt = max(lo, min(hi, series[-1] + dt))
        series.append(nxt)
        prev_dt = dt
    return series

# --- Generate data for all channels ---
channels = {name: make_series(mu, lo, hi) for name, (mu, lo, hi) in stats.items()}

channel_order = [
    "Fc5", "Fc3", "Fc1", "Fcz", "Fc2", "Fc4", "Fc6",
    "C5", "C3", "C1", "Cz", "C2", "C4", "C6",
    "Cp5", "Cp3", "Cp1", "Cpz", "Cp2", "Cp4", "Cp6",
    "Fp1", "Fpz", "Fp2",
    "Af7", "Af3", "Afz", "Af4", "Af8",
    "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
    "Ft7", "Ft8",
    "T7", "T8", "T9", "T10",
    "Tp7", "Tp8",
    "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
    "Po7", "Po3", "Poz", "Po4", "Po8",
    "O1", "Oz", "O2",
    "Iz"
]

offset_step = 5  # small offset for stacking

plt.figure(figsize=(16, 14))

num_channels = len(channel_order)

yticks = []
ytick_labels = []

for i, name in enumerate(channel_order):
    data = channels[name]
    data_min, data_max = min(data), max(data)
    norm_data = [(x - data_min) / (data_max - data_min) for x in data]
    scaled_data = [x * 4 for x in norm_data]
    offset_data = [x + (num_channels - 1 - i) * offset_step for x in scaled_data]
    plt.plot(offset_data, label=name, alpha=0.7, linewidth=0.8)
    
    # Set yticks in the middle of each channel’s offset band
    yticks.append((num_channels - 1 - i) * offset_step + 2)  # 2 is midpoint of [0,4] scaled range
    mu = stats[name][0]  # channel mean in µV
    ytick_labels.append(f"{name} ({mu:.1f} µV)")

plt.title("Simulated EEG Traces for All Channels")
plt.xlabel("Sample Index")
plt.ylabel("Mean uV Per Channel")
plt.yticks(yticks, ytick_labels, fontsize=7)
plt.legend(ncol=4, fontsize='small', loc='upper right')
plt.tight_layout()
plt.show()

