%eeglab;  % Uncomment if you want to launch EEGLAB GUI

%% Paths setup
baseFolder   = pwd;                                         % current folder with S001...S109
desktopPath  = fullfile(getenv('HOME'), 'Desktop');
masterFolder = fullfile(desktopPath, 'EEG_Segments');      % master folder on Desktop
if ~exist(masterFolder, 'dir'), mkdir(masterFolder); end

%% Get subject folders
subjectFolders = dir(fullfile(baseFolder, 'S*'));
subjectFolders = subjectFolders([subjectFolders.isdir]);

%% Loop over subjects
for s = 1:length(subjectFolders)
    subjectPath = fullfile(baseFolder, subjectFolders(s).name);

    % Find EDF files
    edfFiles = dir(fullfile(subjectPath, '*.edf'));
    if isempty(edfFiles)
        warning('No .edf files found in %s. Skipping.', subjectPath);
        continue;
    end

    % Process each EDF file in this subject folder
    for f = 1:length(edfFiles)
        edfFile = edfFiles(f).name;
        [~, nameNoExt] = fileparts(edfFile);
        fprintf('\n🔄 Processing %s in %s\n', edfFile, subjectFolders(s).name);

        % Create output folder for this file's segments inside master folder
        segmentFolderName = ['Segment of ', nameNoExt];
        segmentFolderPath = fullfile(masterFolder, segmentFolderName);
        if ~exist(segmentFolderPath, 'dir'), mkdir(segmentFolderPath); end

        % Load EDF
        EEG = pop_biosig(fullfile(subjectPath, edfFile));
        fs = EEG.srate;
        total_samples = size(EEG.data, 2);

        % Load matching .event file
        eventFile = fullfile(subjectPath, [nameNoExt, '.edf.event']);
        if ~exist(eventFile, 'file')
            warning('Event file not found: %s. Skipping file...', eventFile);
            continue;
        end

        fid = fopen(eventFile, 'r');
        rawText = fread(fid, '*char')';
        fclose(fid);

        % Use your requested pattern:
        pattern = '(T[0-2])\s*duration:\s*([0-9]+\.[0-9]+)';
        matches = regexp(rawText, pattern, 'tokens');
        if isempty(matches)
            warning('No T0, T1, or T2 events found in: %s. Skipping file...', eventFile);
            continue;
        end

        % Extract labels and durations
        numEvents = length(matches);
        labels = cell(numEvents, 1);
        durations = zeros(numEvents, 1);
        for i = 1:numEvents
            labels{i} = matches{i}{1};
            durations(i) = str2double(matches{i}{2});
        end
        segment_lengths_samples = round(durations * fs);

        % Adjust last segment if total length exceeded
        if sum(segment_lengths_samples) > total_samples
            segment_lengths_samples(end) = total_samples - sum(segment_lengths_samples(1:end-1));
        end

        % Segment and save each
        start_idx = 1;
        for i = 1:numEvents
            len = segment_lengths_samples(i);
            end_idx = min(start_idx + len - 1, total_samples);

            EEG_seg = EEG;
            EEG_seg.data = EEG.data(:, start_idx:end_idx);
            EEG_seg.pnts = size(EEG_seg.data, 2);
            EEG_seg.xmax = EEG_seg.pnts / fs;
            EEG_seg.times = EEG.times(start_idx:end_idx);
            EEG_seg.trials = 1;

            segFilename = sprintf('%s_segment_%03d_%s.set', nameNoExt, i, labels{i});
            segPath = fullfile(segmentFolderPath, segFilename);
            pop_saveset(EEG_seg, 'filename', segPath);

            start_idx = end_idx + 1;
            if start_idx > total_samples
                break;
            end
        end

        fprintf('✅ Done: segments saved in %s\n', segmentFolderPath);
    end
end

fprintf('\n🎉 All done! Segments saved inside: %s\n', masterFolder);
