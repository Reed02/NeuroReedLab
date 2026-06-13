# Imports
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import mne
import os
from sklearn.model_selection import train_test_split
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
import numpy as np
import json

# Dataset class
class EEGDataset(Dataset):
    def __init__(self, data, labels):
        self.data = data
        self.labels = labels
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        sample = self.data[idx]
        label = self.labels[idx]
        return sample.float(), torch.tensor(label, dtype=torch.long)  # long for CrossEntropyLoss

# Simplified EEG CNN
class SimpleEEGCNN(nn.Module):
    def __init__(self, in_channels, signal_len):
        super(SimpleEEGCNN, self).__init__()
        self.conv1 = nn.Conv1d(in_channels, 8, kernel_size=5)
        self.pool = nn.MaxPool1d(2)
        self.conv2 = nn.Conv1d(8, 16, kernel_size=3)
        
        # Calculate flatten size
        test = torch.zeros(1, in_channels, signal_len)
        x = self.pool(F.relu(self.conv1(test)))
        x = self.pool(F.relu(self.conv2(x)))
        self.flattened = x.view(1, -1).shape[1]

        self.fc1 = nn.Linear(self.flattened, 32)
        self.fc2 = nn.Linear(32, 2)  # 2 classes for CrossEntropyLoss

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# Load EDF files
folder_paths = {
    "Eyes Open": "/Users/cooperledoux/Documents/NNSA Research Project 2024-Summer 2025/Baseline_Eyes_Open",
    "Eyes Closed": "/Users/cooperledoux/Documents/NNSA Research Project 2024-Summer 2025/Baseline_Eyes_Closed",
}
label_map = {"Eyes Open": 0, "Eyes Closed": 1}

raw_files, labels = [], []
for label_name, path in folder_paths.items():
    for file in os.listdir(path):
        if file.endswith(".edf"):
            raw = mne.io.read_raw_edf(os.path.join(path, file), preload=True)
            raw.filter(1.0, 40.0)
            raw.resample(256)
            data = raw.get_data()
            data = (data - data.mean(axis=1, keepdims=True)) / data.std(axis=1, keepdims=True)
            print(f"Loaded EDF file: {file}, shape: {data.shape} → channels: {data.shape[0]}")
            raw_files.append(torch.from_numpy(data))
            labels.append(label_map[label_name])

# Standardize length
min_len = min(x.shape[1] for x in raw_files)
raw_files = [x[:, :min_len] for x in raw_files]

# Train-test split
train_data, test_data, train_labels, test_labels = train_test_split(raw_files, labels, test_size=0.2, stratify=labels)
print("Train class counts:", Counter(train_labels))

# --- Plot 1: Class distribution in train and test ---
plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
sns.countplot(x=train_labels)
plt.title("Train Set Class Distribution")
plt.xlabel("Class")
plt.ylabel("Count")
plt.xticks([0, 1], ["Eyes Open", "Eyes Closed"])

plt.subplot(1, 2, 2)
sns.countplot(x=test_labels)
plt.title("Test Set Class Distribution")
plt.xlabel("Class")
plt.ylabel("Count")
plt.xticks([0, 1], ["Eyes Open", "Eyes Closed"])
plt.tight_layout()
plt.show()

# --- Plot 2: Sample EEG signal plot ---
sample_idx = 0 #0th element from Eyes Open Dataset
sample = raw_files[sample_idx].numpy()
label = labels[sample_idx]

plt.figure(figsize=(20, 12))
for ch in range(sample.shape[0]):  # plot up to 64 channels with offset
    plt.plot(sample[ch] + ch * 10, label=f"Channel {ch+1}")

plt.title(f"Sample EEG Signal (Label: {'Eyes Open' if label == 0 else 'Eyes Closed'})")
plt.xlabel("Time (samples)")
plt.ylabel("Amplitude (offset for clarity)")
plt.tight_layout()
plt.show()

# Dataloaders
batch_size = 4
train_loader = DataLoader(EEGDataset(train_data, train_labels), batch_size=batch_size, shuffle=True)
test_loader = DataLoader(EEGDataset(test_data, test_labels), batch_size=batch_size)

# Training setup
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = SimpleEEGCNN(train_data[0].shape[0], min_len).to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# --- Training loop with loss collection for Plot 3 ---
epochs = 50
train_losses = []

for epoch in range(epochs):
    running_loss = 0.0
    model.train()
    for inputs, labels_batch in train_loader:
        inputs, labels_batch = inputs.to(device), labels_batch.to(device)
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels_batch)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()
    avg_loss = running_loss / len(train_loader)
    train_losses.append(avg_loss)
    print(f"Epoch {epoch+1} - Train Loss: {avg_loss:.4f}")

# --- Plot 3: Training Loss Curve ---
plt.figure()
plt.plot(range(1, epochs+1), train_losses, marker='o')
plt.title("Training Loss per Epoch")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.grid(True)
plt.show()

# --- Testing and metrics ---
correct, total = 0, 0
all_preds = []
all_labels = []

model.eval()
with torch.no_grad():
    for inputs, labels_batch in test_loader:
        inputs, labels_batch = inputs.to(device), labels_batch.to(device)
        outputs = model(inputs)
        _, preds = torch.max(outputs, 1)
        total += labels_batch.size(0)
        correct += (preds == labels_batch).sum().item()
        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels_batch.cpu().numpy())

print(f"Test Accuracy: {100 * correct / total:.2f}%")

# --- Plot 4: Confusion Matrix ---
cm = confusion_matrix(all_labels, all_preds)
plt.figure(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=["Eyes Open", "Eyes Closed"], yticklabels=["Eyes Open", "Eyes Closed"])
plt.ylabel('True Label')
plt.xlabel('Predicted Label')
plt.title("Confusion Matrix on Test Set")
plt.show()

# --- Plot 5: Class Probability Histogram ---
probs_list = []

model.eval()
with torch.no_grad():
    for inputs, _ in test_loader:
        inputs = inputs.to(device)
        outputs = model(inputs)
        probs = torch.softmax(outputs, dim=1)[:, 1]  # probability of "Eyes Closed"
        probs_list.extend(probs.cpu().numpy())

plt.figure()
plt.hist(probs_list, bins=20, alpha=0.7)
plt.title("Predicted Probability Distribution for 'Eyes Closed' Class on Test Set")
plt.xlabel("Probability")
plt.ylabel("Number of Samples")
plt.show()

# --- Test on new EDF file ---
file_path = "/Users/cooperledoux/Documents/NNSA Research Project 2024-Summer 2025/Test_File/S046R01.edf"
raw = mne.io.read_raw_edf(file_path, preload=True)
raw.filter(1., 40.)
raw.resample(256)
data = raw.get_data()
data = (data - data.mean(axis=1, keepdims=True)) / data.std(axis=1, keepdims=True)

# Crop to correct length
tensor_data = torch.from_numpy(data).float()
tensor_data = tensor_data[:, :min_len]  # Use min_len instead of undefined signal_length
tensor_data = tensor_data.unsqueeze(0).to(device)  # Add batch dimension

# Inference
with torch.no_grad():
    logits = model(tensor_data)
    probs = torch.softmax(logits, dim=1)
    prob_closed = probs[0, 1].item()  # Probability of class 1 (Eyes Closed)
    predicted_class = torch.argmax(probs, dim=1).item()

label_map = {0: "Eyes Open", 1: "Eyes Closed"}
print(f"Predicted class: {label_map[predicted_class]}")
print(f"Probability of Eyes Closed: {prob_closed:.4f}")





# Save predicted class to a JSON file
result = {"predicted_class": label_map[predicted_class]}
with open("predicted_class.json", "w") as f:
    json.dump(result, f)
