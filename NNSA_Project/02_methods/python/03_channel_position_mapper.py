import mne
import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import csv

# -----------------------------
# Load one EDF to get channel names
# -----------------------------
edf_file = filedialog.askopenfilename(title="Select one EDF file", filetypes=[("EDF files", "*.edf")])
if not edf_file:
    raise RuntimeError("No EDF file selected.")

raw = mne.io.read_raw_edf(edf_file, preload=True, verbose=False)
channel_names = raw.ch_names

# -----------------------------
# GUI class
# -----------------------------
class ChannelMapperGUI:
    def __init__(self, root, channel_names):
        self.root = root
        self.root.title("EEG Channel Mapper")
        self.channel_names = channel_names
        self.text_objs = {}  # store matplotlib text objects
        self.drag_data = {"x": 0, "y": 0, "item": None}

        # Left frame: channel list + save button
        self.frame_left = tk.Frame(root)
        self.frame_left.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        self.listbox = tk.Listbox(self.frame_left, selectmode=tk.SINGLE, height=20)
        self.scrollbar = tk.Scrollbar(self.frame_left, orient=tk.VERTICAL)
        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.listbox.yview)
        self.listbox.pack(side=tk.LEFT, fill=tk.Y)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        for ch in self.channel_names:
            self.listbox.insert(tk.END, ch)

        self.save_button = tk.Button(self.frame_left, text="Save Positions", command=self.save_positions)
        self.save_button.pack(pady=10)

        # Right frame: head canvas
        self.frame_right = tk.Frame(root)
        self.frame_right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.fig, self.ax = plt.subplots(figsize=(6,6))
        self.ax.axis("off")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_right)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.draw_head_outline()
        self.canvas.mpl_connect("button_press_event", self.on_click)
        self.canvas.mpl_connect("motion_notify_event", self.on_drag)
        self.canvas.mpl_connect("button_release_event", self.on_release)

    # -----------------------------
    # Draw head circle, nose, ears
    # -----------------------------
    def draw_head_outline(self):
        self.ax.clear()
        # head
        head = plt.Circle((0.5,0.5), 0.45, fill=False, linewidth=2)
        self.ax.add_patch(head)
        # nose (top center)
        self.ax.plot([0.5,0.5],[0.95,0.85], color='red', linewidth=2)
        # ears
        self.ax.plot([0.05,0.05],[0.4,0.6], color='black', linewidth=2)
        self.ax.plot([0.95,0.95],[0.4,0.6], color='black', linewidth=2)
        self.ax.set_xlim(0,1)
        self.ax.set_ylim(0,1)
        self.ax.set_aspect('equal')
        self.canvas.draw()

    # -----------------------------
    # Mouse click
    # -----------------------------
    def on_click(self, event):
        if event.inaxes != self.ax:
            return
        # add new channel
        selection = self.listbox.curselection()
        if not selection:
            return
        ch_name = self.listbox.get(selection[0])
        if ch_name in self.text_objs:
            return
        txt = self.ax.text(event.xdata, event.ydata, ch_name, fontsize=9,
                           ha='center', va='center', picker=True,
                           bbox=dict(facecolor='yellow', alpha=0.5))
        self.text_objs[ch_name] = txt
        self.canvas.draw()
        self.drag_data["item"] = txt
        self.drag_data["x"] = event.xdata
        self.drag_data["y"] = event.ydata

    # -----------------------------
    # Mouse drag
    # -----------------------------
    def on_drag(self, event):
        if self.drag_data["item"] is None or event.inaxes != self.ax:
            return
        self.drag_data["item"].set_position((event.xdata, event.ydata))
        self.canvas.draw()

    # -----------------------------
    # Mouse release
    # -----------------------------
    def on_release(self, event):
        self.drag_data["item"] = None

    # -----------------------------
    # Save positions to CSV
    # -----------------------------
    def save_positions(self):
        if not self.text_objs:
            messagebox.showwarning("No channels", "No channel positions to save.")
            return
        file_path = filedialog.asksaveasfilename(title="Save channel positions",
                                                 defaultextension=".csv",
                                                 filetypes=[("CSV files","*.csv")])
        if not file_path:
            return
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Channel","X","Y"])
            for ch, txt_obj in self.text_objs.items():
                x, y = txt_obj.get_position()
                writer.writerow([ch, x, y])
        messagebox.showinfo("Saved", f"Channel positions saved to {file_path}")


# -----------------------------
# Run GUI
# -----------------------------
root = tk.Tk()
gui = ChannelMapperGUI(root, channel_names)
root.mainloop()
