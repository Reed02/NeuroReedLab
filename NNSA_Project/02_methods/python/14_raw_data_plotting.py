import mne
import torch
import os

folder_path = '/Users/cooperledoux/Desktop/EEG_Machine_Learning_and_Simulation/sourcedata/rawdata/S001'
raw_files = []

#Get all files in the folder
for file_name in os.listdir(folder_path):
    file_path = os.path.join(folder_path, file_name)

    #Check if the file is a supported mne format
    if file_name.endswith('.edf'):
        raw = mne.io.read_raw_edf(file_path)
        raw_files.append(raw)


first_file = raw_files[0]
data = first_file.get_data() #Creates a numpy array
tensor_data = torch.tensor(data, dtype=torch.float32)
print(tensor_data.shape)

first_file.plot(block=True)

