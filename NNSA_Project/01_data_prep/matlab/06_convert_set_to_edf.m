eeglab;  % Initialize EEGLAB

% Input folder containing EEG_Classification folders
mainFolder = '/Users/cooperledoux/Desktop/EEG_Classification';

% Output folder on Desktop
desktopPath = fullfile(getenv('HOME'), 'Desktop');
outputMasterFolder = fullfile(desktopPath, 'Converted_EDF_Files');

% Create output folder if it doesn't exist
if ~exist(outputMasterFolder, 'dir')
    mkdir(outputMasterFolder);
end

% Get all subfolders in EEG_Classification
folderList = dir(mainFolder);
folderList = folderList([folderList.isdir] & ~ismember({folderList.name}, {'.', '..'}));

% Loop through each subfolder
for k = 1:length(folderList)
    folderName = folderList(k).name;
    inputFolder = fullfile(mainFolder, folderName);
    outputFolder = fullfile(outputMasterFolder, folderName);

    % Create output subfolder
    if ~exist(outputFolder, 'dir')
        mkdir(outputFolder);
    end

    % Find all .set files
    setFiles = dir(fullfile(inputFolder, '*.set'));

    for j = 1:length(setFiles)
        try
            setFile = setFiles(j).name;
            inputPath = fullfile(inputFolder, setFile);

            % Load .set file
            EEG = pop_loadset(inputPath);

            % Clean up channel labels
            for ch = 1:EEG.nbchan
                lbl = EEG.chanlocs(ch).labels;
                lbl = regexprep(lbl, '\s+', '');
                EEG.chanlocs(ch).labels = lbl(1:min(16,end));
            end

            EEG = eeg_checkset(EEG);

            % Save as .edf
            [~, baseName, ~] = fileparts(setFile);
            edfFileName = [baseName, '.edf'];
            outputEDF = fullfile(outputFolder, edfFileName);

            pop_writeeeg(EEG, outputEDF, 'TYPE', 'EDF', 'recordlength', 1);
            fprintf('Converted: %s → %s\n', setFile, edfFileName);

        catch ME
            fprintf('Error converting %s: %s\n', setFile, ME.message);
        end
    end
end
