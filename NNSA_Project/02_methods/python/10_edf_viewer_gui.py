import tkinter as tk
from tkinter import filedialog, messagebox
import mne
import numpy as np
import matplotlib.pyplot as plt

class EEGViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EEG File Viewer")

        self.file_paths = []
        self.check_vars = []

        # Upload button
        self.upload_btn = tk.Button(root, text="Upload EEG Files", command=self.upload_files)
        self.upload_btn.pack(pady=10)

        # Frame to hold checkboxes
        self.checkbox_frame = tk.Frame(root)
        self.checkbox_frame.pack(pady=10)

        # Plot button
        self.plot_btn = tk.Button(root, text="Plot Selected", command=self.plot_selected)
        self.plot_btn.pack(pady=10)

    def upload_files(self):
        files = filedialog.askopenfilenames(
            title="Select EEG EDF files",
            filetypes=[("EDF files", "*.edf"), ("All files", "*.*")]
        )
        if not files:
            return

        self.file_paths = list(files)
        self.refresh_checkboxes()

    def refresh_checkboxes(self):
        # Clear old widgets
        for widget in self.checkbox_frame.winfo_children():
            widget.destroy()
        self.check_vars = []

        for fp in self.file_paths:
            var = tk.IntVar(value=0)
            cb = tk.Checkbutton(self.checkbox_frame, text=fp.split('/')[-1], variable=var)
            cb.pack(anchor='w')
            self.check_vars.append(var)

    def get_data(self, raw, channel='Cz'):
        raw_copy = raw.copy()
        if channel in raw.info['ch_names']:
            raw_copy.pick([channel])
            data = raw_copy.get_data()[0]
        else:
            raw_copy.pick('eeg')
            data = raw_copy.get_data().mean(axis=0)
        return data, raw.info['sfreq']

    def plot_selected(self):
        selected_files = [fp for fp, var in zip(self.file_paths, self.check_vars) if var.get() == 1]
        if not selected_files:
            messagebox.showinfo("No Selection", "Please select at least one EEG file to plot.")
            return

        for path in selected_files:
            try:
                raw = mne.io.read_raw_edf(path, preload=True, verbose=False)
                data, sfreq = self.get_data(raw)
                times = np.arange(len(data)) / sfreq

                plt.figure(figsize=(10, 4))
                plt.plot(times, data)
                plt.title(f"EEG Signal - {path.split('/')[-1]}")
                plt.xlabel("Time (s)")
                plt.ylabel("Amplitude (µV)")
                plt.grid(True)
                plt.tight_layout()
            except Exception as e:
                messagebox.showerror("Error Loading File", f"Failed to load or plot {path}.\nError: {e}")

        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = EEGViewerApp(root)
    root.mainloop()
