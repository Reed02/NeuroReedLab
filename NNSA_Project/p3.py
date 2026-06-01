import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.interpolate import griddata
from matplotlib.patches import Circle

# -------------------------------
# Load channel positions
# -------------------------------
pos_file = "/Users/cooperledoux/Desktop/positions.csv"  # CSV with Channel,X,Y
positions_df = pd.read_csv(pos_file)
channels = positions_df['Channel'].values
x_pos = positions_df['X'].values
y_pos = positions_df['Y'].values

# -------------------------------
# Example: normalized_avg_psd dictionary
# Replace with your actual averaged PSD per movement per channel
# normalized_avg_psd = {"Eyes Open": [...], "Eyes Closed": [...], ...}
# Ensure the arrays have length equal to number of channels
# -------------------------------
# For demonstration, generate random PSD values
normalized_avg_psd = {name: np.random.rand(len(channels)) for name in [
    "Eyes Open", "Eyes Closed", "Rest", "Real Left Fist", "Real Right Fist",
    "Imagined Left Fist", "Imagined Right Fist", "Real Both Fists",
    "Imagined Both Fists", "Real Both Feet", "Imagined Both Feet"
]}

# -------------------------------
# Create a grid for interpolation
# -------------------------------
grid_x, grid_y = np.mgrid[0:1:200j, 0:1:200j]  # 200x200 grid

# -------------------------------
# Plot all movements in a grid
# -------------------------------
n_movements = len(normalized_avg_psd)
cols = 3
rows = int(np.ceil(n_movements / cols))

fig, axes = plt.subplots(rows, cols, figsize=(5*cols, 5*rows))
axes = axes.flatten()

for idx, (movement, psd_values) in enumerate(normalized_avg_psd.items()):
    ax = axes[idx]
    
    # Interpolate PSD values
    grid_z = griddata(points=(x_pos, y_pos), values=psd_values,
                      xi=(grid_x, grid_y), method='cubic')
    
    # Mask outside head circle
    mask = (grid_x - 0.5)**2 + (grid_y - 0.5)**2 > 0.45**2
    grid_z[mask] = np.nan
    
    # Plot heatmap
    im = ax.imshow(grid_z.T, origin='lower', extent=(0,1,0,1), cmap='viridis')
    
    # Draw head outline
    ax.add_patch(Circle((0.5,0.5), 0.45, fill=False, color='k', lw=2))  # head
    ax.plot([0.5,0.5],[0.95,0.85], color='red', lw=2)  # nose
    ax.plot([0.05,0.05],[0.4,0.6], color='black', lw=2)  # left ear
    ax.plot([0.95,0.95],[0.4,0.6], color='black', lw=2)  # right ear
    
    # Plot channel points
    ax.scatter(x_pos, y_pos, c='white', s=50, edgecolor='k', zorder=2)
    
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect('equal')
    ax.set_title(movement)

# Remove empty subplots
for i in range(n_movements, len(axes)):
    fig.delaxes(axes[i])

# Colorbar for the entire figure
cbar = fig.colorbar(im, ax=axes.tolist(), shrink=0.8, orientation='vertical', label='PSD (dB)')
plt.tight_layout()
plt.show()
