import os
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader, random_split
import pyedflib
from scipy.signal import spectrogram
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
from tqdm import tqdm

# === File paths for labeled EDF data ===
DATA_FOLDERS = {
    "Eyes Open": "/Users/cooperledoux/Desktop/Baseline_Eyes_Open",
    "Eyes Closed": "/Users/cooperledoux/Desktop/Baseline_Eyes_Closed",
    "Open_and_Close_left_or_right_fist": "/Users/cooperledoux/Desktop/Open_and_Close_left_or_right_fist",
    "Imagine_Opening_and_Closing_left_or_right_fist": "/Users/cooperledoux/Desktop/Imagine_Opening_and_Closing_left_or_right_fist",
}

LABEL_MAP = {label: idx for idx, label in enumerate(DATA_FOLDERS.keys())}
LABELS = list(LABEL_MAP.keys())

# === Convert EDF to Spectrogram ===
def edf_to_spectrogram(file_path, target_size=(64, 64)):
    f = pyedflib.EdfReader(file_path)
    signal = f.readSignal(0)
    fs = f.getSampleFrequency(0)
    f._close()

    freqs, times, Sxx = spectrogram(signal, fs=fs, nperseg=256, noverlap=128)
    Sxx = np.log1p(Sxx)

    Sxx_resized = np.zeros(target_size)
    h, w = min(Sxx.shape[0], target_size[0]), min(Sxx.shape[1], target_size[1])
    Sxx_resized[:h, :w] = Sxx[:h, :w]

    return torch.tensor(Sxx_resized).float().unsqueeze(0)  # shape [1, H, W]

# === Dataset Class ===
class EDFDataset(Dataset):
    def __init__(self, folder_dict, target_size=(64, 64)):
        self.samples = []
        self.target_size = target_size

        for label, path in folder_dict.items():
            label_idx = LABEL_MAP[label]
            for fname in os.listdir(path):
                if fname.endswith(".edf"):
                    full_path = os.path.join(path, fname)
                    self.samples.append((full_path, label_idx))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        file_path, label = self.samples[idx]
        spec_tensor = edf_to_spectrogram(file_path, self.target_size)
        return spec_tensor, label

# === 2D CNN Model with BatchNorm and Dropout ===
class EDF2DCNN(nn.Module):
    def __init__(self, num_classes):
        super(EDF2DCNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 16, 3, padding=1)
        self.bn1 = nn.BatchNorm2d(16)
        self.conv2 = nn.Conv2d(16, 32, 3, padding=1)
        self.bn2 = nn.BatchNorm2d(32)
        self.dropout = nn.Dropout(0.5)
        self.fc1 = nn.Linear(32 * 16 * 16, num_classes)

    def forward(self, x):
        x = F.relu(self.bn1(self.conv1(x)))     # [B, 16, 64, 64]
        x = F.max_pool2d(x, 2)                   # [B, 16, 32, 32]
        x = F.relu(self.bn2(self.conv2(x)))     # [B, 32, 32, 32]
        x = F.max_pool2d(x, 2)                   # [B, 32, 16, 16]
        x = torch.flatten(x, 1)                  # Flatten batch dim
        x = self.dropout(x)
        x = self.fc1(x)                          # [B, num_classes]
        return x

# === Train & Eval Functions ===
def train(model, loader, optimizer, criterion, device):
    model.train()
    total_loss = 0
    correct = 0
    for x, y in tqdm(loader, desc="Training"):
        x, y = x.to(device), y.to(device)
        optimizer.zero_grad()
        out = model(x)
        loss = criterion(out, y)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
        correct += (out.argmax(1) == y).sum().item()
    return total_loss / len(loader), correct / len(loader.dataset)

def evaluate(model, loader, criterion, device):
    model.eval()
    total_loss = 0
    correct = 0
    all_preds = []
    all_labels = []
    with torch.no_grad():
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            out = model(x)
            loss = criterion(out, y)
            total_loss += loss.item()
            correct += (out.argmax(1) == y).sum().item()
            all_preds.extend(out.argmax(1).cpu().numpy())
            all_labels.extend(y.cpu().numpy())
    return total_loss / len(loader), correct / len(loader.dataset), all_preds, all_labels

# === Main with Early Stopping, LR Scheduler and Checkpointing ===
def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dataset = EDFDataset(DATA_FOLDERS)

    # Split data
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_set, val_set = random_split(dataset, [train_size, val_size])

    train_loader = DataLoader(train_set, batch_size=4, shuffle=True)
    val_loader = DataLoader(val_set, batch_size=4)

    model = EDF2DCNN(num_classes=len(LABEL_MAP)).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-4, weight_decay=1e-4)
    criterion = nn.CrossEntropyLoss()
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=3, verbose=True)

    epochs = 30  # increased max epochs to give model more room
    patience = 10  # early stopping patience
    best_val_loss = float('inf')
    patience_counter = 0

    train_losses, val_losses = [], []
    train_accuracies, val_accuracies = [], []

    best_model_path = "best_edf_model.pth"

    for epoch in range(1, epochs + 1):
        print(f"\nEpoch {epoch}/{epochs}")
        train_loss, train_acc = train(model, train_loader, optimizer, criterion, device)
        val_loss, val_acc, _, _ = evaluate(model, val_loader, criterion, device)

        train_losses.append(train_loss)
        val_losses.append(val_loss)
        train_accuracies.append(train_acc)
        val_accuracies.append(val_acc)

        print(f"Train Loss: {train_loss:.4f}, Acc: {train_acc:.4f}")
        print(f"Val   Loss: {val_loss:.4f}, Acc: {val_acc:.4f}")

        # Step the scheduler with validation loss
        scheduler.step(val_loss)

        # Early stopping check
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            torch.save(model.state_dict(), best_model_path)
            print(f"✅ New best model saved with val loss: {best_val_loss:.4f}")
        else:
            patience_counter += 1
            print(f"Patience counter: {patience_counter}/{patience}")
            if patience_counter >= patience:
                print(f"⏹ Early stopping triggered after {patience} epochs without improvement.")
                break

    # Load best model for evaluation and plotting
    model.load_state_dict(torch.load(best_model_path))

    # === Plot Loss and Accuracy ===
    epochs_range = range(1, len(train_losses) + 1)

    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.plot(epochs_range, train_losses, label='Train Loss', marker='o')
    plt.plot(epochs_range, val_losses, label='Val Loss', marker='o')
    plt.title("Loss Over Epochs")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend()
    plt.grid(True)

    plt.subplot(1, 2, 2)
    plt.plot(epochs_range, train_accuracies, label='Train Accuracy', marker='o')
    plt.plot(epochs_range, val_accuracies, label='Val Accuracy', marker='o')
    plt.title("Accuracy Over Epochs")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.savefig("training_plots.png")
    plt.show()

    # === Confusion Matrix ===
    _, _, preds, labels = evaluate(model, val_loader, criterion, device)
    cm = confusion_matrix(labels, preds)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=LABELS)
    disp.plot(xticks_rotation=45, cmap='Blues')
    plt.title("Validation Confusion Matrix")
    plt.tight_layout()
    plt.savefig("confusion_matrix.png")
    plt.show()


if __name__ == "__main__":
    main()
