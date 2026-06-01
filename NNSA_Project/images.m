% Start EEGLAB cleanly
[ALLEEG, EEG, CURRENTSET, ALLCOM] = eeglab;

% Base image save location
desktopPath = fullfile(getenv('HOME'), 'Desktop');  % macOS/Linux
% desktopPath = fullfile(getenv('USERPROFILE'), 'Desktop');  % Windows
dstBase = fullfile(desktopPath, 'images');

% Folder names containing .edf files (inside current directory)
taskFolders = {
    'Baseline_Eyes_Open', 
    'Baseline_Eyes_Closed', 
    'Rest', 
    'Task1_Real_Left_Fist', 
    'Task1_Real_Right_Fist', 
    'Task3_Real_Both_Fists', 
    'Task4_Imag_Both_Feet',
    'Task4_Imag_Both_Fists',
    'Task2_Imag_Left_Fist',
    'Task2_Imag_Right_Fist',
    'Task3_Real_Both_Feet'
};

figNum = 1;

for i = 1:length(taskFolders)
    srcFolder = taskFolders{i};  % relative to current directory
    dstFolder = fullfile(dstBase, srcFolder);  % where we will save the image

    if ~exist(dstFolder, 'dir')
        mkdir(dstFolder);
    end

    % List all .edf files in the subfolder
    edfFiles = dir(fullfile(srcFolder, '*.edf'));

    for j = 1:length(edfFiles)
        edfFile = edfFiles(j).name;
        [~, baseName, ~] = fileparts(edfFile);

        try
            % Load EDF file
            EEG = pop_biosig(fullfile(srcFolder, edfFile));
            EEG.setname = baseName;
            [ALLEEG, EEG, CURRENTSET] = eeg_store(ALLEEG, EEG, 0);

            % Plot EEG
            figure(figNum);
            clf;
            pop_eegplot(EEG, 1, 1, 1);  % interactive-style plot

            % Give time to render GUI figure
            pause(2);

            % Save figure
            outFile = fullfile(dstFolder, [baseName '.png']);
            exportgraphics(gcf, outFile, 'Resolution', 300);
            close(gcf);

            fprintf('Saved image: %s\n', outFile);
            figNum = figNum + 1;

        catch ME
            fprintf('Error processing %s: %s\n', edfFile, ME.message);
        end
    end
end

disp('All .edf plots saved.');
