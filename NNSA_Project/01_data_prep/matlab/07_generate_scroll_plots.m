% Start EEGLAB cleanly
[ALLEEG, EEG, CURRENTSET, ALLCOM] = eeglab;

% Base image save location
desktopPath = fullfile(getenv('HOME'), 'Desktop');  % macOS/Linux
% desktopPath = fullfile(getenv('USERPROFILE'), 'Desktop');  % Windows

dstBase = fullfile(desktopPath, 'images');

% Folder names containing .edf files (inside current directory)
taskFolders = {
    'Baseline_Eyes_Open', ...
    'Baseline_Eyes_Closed', ...
    'Rest', ...
    'Task1_Real_Left_Fist', ...
    'Task1_Real_Right_Fist', ...
    'Task3_Real_Both_Fists', ...
    'Task4_Imag_Both_Feet', ...
    'Task4_Imag_Both_Fists', ...
    'Task2_Imag_Left_Fist', ...
    'Task2_Imag_Right_Fist', ...
    'Task3_Real_Both_Feet'
};

for i = 1:length(taskFolders)

    srcFolder = taskFolders{i};
    dstFolder = fullfile(dstBase, srcFolder);

    if ~exist(dstFolder, 'dir')
        mkdir(dstFolder);
    end

    % Find all EDF files
    edfFiles = dir(fullfile(srcFolder, '*.edf'));

    fprintf('\nProcessing folder: %s\n', srcFolder);
    fprintf('Found %d EDF files\n', length(edfFiles));

    for j = 1:length(edfFiles)

        edfFile = edfFiles(j).name;
        [~, baseName, ~] = fileparts(edfFile);

        try

            fprintf('Loading: %s\n', edfFile);

            % Load EDF
            EEG = pop_biosig(fullfile(srcFolder, edfFile));
            EEG.setname = baseName;

            [ALLEEG, EEG, CURRENTSET] = eeg_store(ALLEEG, EEG, 0);

            % Close any existing eegplot windows
            close(findall(0, 'Type', 'figure'));

            % Generate EEG plot
            pop_eegplot(EEG, 1, 1, 1);

            % Allow GUI time to fully render
            pause(2);

            % Find all open figures
            figs = findall(0, 'Type', 'figure');

            if isempty(figs)
                warning('No figure found for %s', edfFile);
                continue;
            end

            % Use most recently created figure
            hFig = figs(1);

            % Force figure background white
            set(hFig, 'Color', 'white');

            % Force all axes backgrounds white
            ax = findall(hFig, 'Type', 'axes');
            for k = 1:length(ax)
                set(ax(k), 'Color', 'white');
            end

            drawnow;

            % Output file
            outFile = fullfile(dstFolder, [baseName '.png']);

            % Export with explicit white background
            exportgraphics( ...
                hFig, ...
                outFile, ...
                'Resolution', 300, ...
                'BackgroundColor', 'white' ...
            );

            fprintf('Saved image: %s\n', outFile);

            % Close figure after saving
            close(hFig);

        catch ME

            fprintf('\nError processing %s\n', edfFile);
            fprintf('%s\n\n', ME.message);

        end

    end

end

disp('All .edf plots saved.');
