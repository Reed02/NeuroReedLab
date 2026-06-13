# ==================================================================
# 0. Imports
# ==================================================================
import os, json, numpy as np, torch, torch.nn as nn, torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import mne
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from collections import Counter
import matplotlib.pyplot as plt, seaborn as sns

# ------------------------------------------------------------------
# 1. Paths and label map  ▼ EDIT THESE PATHS ONLY ▼
# ------------------------------------------------------------------
folder_paths = {
    "Rest":                      "/Users/cooperledoux/Desktop/O_CNN_D/Rest",
    "Eyes Open":                 "/Users/cooperledoux/Desktop/O_CNN_D/Baseline_Eyes_Open",
    "Eyes Closed":               "/Users/cooperledoux/Desktop/O_CNN_D/Baseline_Eyes_Closed",
    "Right Fist":                "/Users/cooperledoux/Desktop/O_CNN_D/Task1_Real_Right_Fist",
    "Left Fist":                 "/Users/cooperledoux/Desktop/O_CNN_D/Task1_Real_Left_Fist",
    "Imagined Right Fist":       "/Users/cooperledoux/Desktop/O_CNN_D/Task2_Imag_Right_Fist",
    "Imagined Left Fist":        "/Users/cooperledoux/Desktop/O_CNN_D/Task2_Imag_Left_Fist",
    "Both Fists":                "/Users/cooperledoux/Desktop/O_CNN_D/Task3_Real_Both_Fists",
    "Both Feet":                 "/Users/cooperledoux/Desktop/O_CNN_D/Task3_Real_Both_Feet",
    "Imagined Both Fists":       "/Users/cooperledoux/Desktop/O_CNN_D/Task4_Imag_Both_Fists",
    "Imagined Both Feet":        "/Users/cooperledoux/Desktop/O_CNN_D/Task4_Imag_Both_Feet",
}
label_map   = {name: idx for idx, name in enumerate(folder_paths)}
class_names = list(label_map)
n_classes   = len(class_names)            

# ------------------------------------------------------------------
# 2. Dataset wrapper
# ------------------------------------------------------------------
class EEGDataset(Dataset):
    def __init__(self, data, labels):
        self.data, self.labels = data, labels
    def __len__(self):  return len(self.data)
    def __getitem__(self, idx):
        return self.data[idx].float(), torch.tensor(self.labels[idx], dtype=torch.long)

# ------------------------------------------------------------------
# 3. CNN definition
# ------------------------------------------------------------------
class SimpleEEGCNN(nn.Module):
    def __init__(self, in_channels, sig_len, n_classes):
        super().__init__()
        self.conv1 = nn.Conv1d(in_channels, 8,  kernel_size=5)
        self.conv2 = nn.Conv1d(8,           16, kernel_size=3)
        self.pool  = nn.MaxPool1d(2)
        with torch.no_grad():
            x = torch.zeros(1, in_channels, sig_len)
            x = self.pool(F.relu(self.conv1(x)))
            x = self.pool(F.relu(self.conv2(x)))
            flat = x.view(1, -1).shape[1]
        self.fc1 = nn.Linear(flat, 32)
        self.fc2 = nn.Linear(32, n_classes)
    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc1(x))
        return self.fc2(x)

# ------------------------------------------------------------------
# 4. Load & preprocess EDFs
# ------------------------------------------------------------------
raw_files, labels = [], []
for task, path in folder_paths.items():
    for file in os.listdir(path):
        if file.endswith(".edf"):
            raw = mne.io.read_raw_edf(os.path.join(path, file), preload=True, verbose=False)
            raw.filter(1., 40., verbose=False).resample(256, verbose=False)
            data = raw.get_data()
            data = (data - data.mean(1, keepdims=True)) / data.std(1, keepdims=True)
            raw_files.append(torch.from_numpy(data))
            labels.append(label_map[task])
            print(f"[{task:22s}] {file:30s} → {data.shape}")

min_len   = min(x.shape[1] for x in raw_files)
raw_files = [x[:, :min_len] for x in raw_files]

train_d, test_d, train_y, test_y = train_test_split(
    raw_files, labels, test_size=0.2, stratify=labels, random_state=42
)
print("Train counts:", Counter(train_y))

# ------------------------------------------------------------------
# 5. Plots: class distribution
# ------------------------------------------------------------------
def plot_distribution(split_labels, title):
    counts = Counter(split_labels)
    vals   = [counts.get(i,0) for i in range(n_classes)]
    plt.bar(range(n_classes), vals)
    plt.xticks(range(n_classes), class_names, rotation=90)
    plt.title(title); plt.ylabel("Count")

plt.figure(figsize=(12,5))
plt.subplot(1,2,1); plot_distribution(train_y, "Train Distribution")
plt.subplot(1,2,2); plot_distribution(test_y,  "Test Distribution")
plt.tight_layout(); plt.show()

# ------------------------------------------------------------------
# 6. DataLoaders, model, optimiser
# ------------------------------------------------------------------
batch_size = 4
train_loader = DataLoader(EEGDataset(train_d, train_y), batch_size, shuffle=True)
test_loader  = DataLoader(EEGDataset(test_d,  test_y),  batch_size)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model  = SimpleEEGCNN(train_d[0].shape[0], min_len, n_classes).to(device)
criterion, optimizer = nn.CrossEntropyLoss(), optim.Adam(model.parameters(), lr=.0001)

# ------------------------------------------------------------------
# 7. Training loop
# ------------------------------------------------------------------
epochs, train_losses = 1000, []
for ep in range(1, epochs+1):
    model.train(); run=0.
    for x,y in train_loader:
        x,y = x.to(device), y.to(device)
        optimizer.zero_grad()
        loss = criterion(model(x), y)
        loss.backward(); optimizer.step()
        run += loss.item()
    train_losses.append(run/len(train_loader))
    print(f"Epoch {ep:02d}/{epochs}   loss={train_losses[-1]:.4f}")

plt.figure(); plt.plot(range(1,epochs+1), train_losses, marker='o')
plt.title("Training Loss"); plt.xlabel("Epoch"); plt.ylabel("Loss"); plt.grid(); plt.show()

# ------------------------------------------------------------------
# 8. Evaluation
# ------------------------------------------------------------------
model.eval(); correct=total=0; preds_all=[]; true_all=[]
with torch.no_grad():
    for x,y in test_loader:
        x,y = x.to(device), y.to(device)
        preds = model(x).argmax(1)
        correct += (preds==y).sum().item(); total += y.size(0)
        preds_all.extend(preds.cpu()); true_all.extend(y.cpu())
acc = 100*correct/total
print(f"Test accuracy: {acc:.2f}%")

cm = confusion_matrix(true_all, preds_all)
plt.figure(figsize=(9,7))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=class_names, yticklabels=class_names)
plt.title("Confusion Matrix"); plt.xlabel("Predicted"); plt.ylabel("True")
plt.xticks(rotation=45); plt.yticks(rotation=0); plt.tight_layout(); plt.show()

# ------------------------------------------------------------------
# 9. Probability histograms (one subplot per class)
# ------------------------------------------------------------------
probs_by_class = [[] for _ in range(n_classes)]
with torch.no_grad():
    for x,_ in test_loader:
        x = x.to(device)
        probs = torch.softmax(model(x), dim=1).cpu().numpy()
        for row in probs:
            for i,p in enumerate(row):
                probs_by_class[i].append(p)

cols = 4
rows = int(np.ceil(n_classes/cols))
plt.figure(figsize=(cols*4, rows*3))
for i in range(n_classes):
    plt.subplot(rows, cols, i+1)
    plt.hist(probs_by_class[i], bins=15, alpha=0.7)
    plt.title(class_names[i]); plt.xticks([0,0.5,1]); plt.yticks([])
plt.suptitle("Predicted‑probability distributions (test set)")
plt.tight_layout(rect=[0,0,1,0.96]); plt.show()

# ------------------------------------------------------------------
# 10. Quick inference on a new EDF (optional)
# ------------------------------------------------------------------
file_path = "/Users/cooperledoux/Documents/NNSA Research Project 2024-Summer 2025/Test_File/S046R01.edf"
if os.path.isfile(file_path):
    raw = mne.io.read_raw_edf(file_path, preload=True, verbose=False)
    raw.filter(1.,40., verbose=False).resample(256, verbose=False)
    data = raw.get_data()
    data = (data - data.mean(1,keepdims=True)) / data.std(1,keepdims=True)
    tensor = torch.from_numpy(data)[:, :min_len].unsqueeze(0).float().to(device)
    with torch.no_grad():
        probs = torch.softmax(model(tensor), dim=1)[0]
    pred = probs.argmax().item()
    print("Inference →", class_names[pred])
    json.dump({"predicted_class": class_names[pred]}, open("predicted_class.json","w"))
