%eeglab;  % Uncomment if you want to launch EEGLAB GUI

% Use current folder where this script is running
edfFolder = pwd;

% Get list of all .edf files in the folder
edfFiles = dir(fullfile(edfFolder, '*.edf'));

for f = 1:length(edfFiles)
    edfFile = edfFiles(f).name;
    [~, nameNoExt, ~] = fileparts(edfFile);
    fprintf('\nProcessing file: %s\n', edfFile);

    % Create a new folder for this file's segments
    segmentFolderName = ['Segment of ', nameNoExt];
    segmentFolderPath = fullfile(edfFolder, segmentFolderName);
    if ~exist(segmentFolderPath, 'dir')
        mkdir(segmentFolderPath);
    end

    % Load EDF file
    EEG = pop_biosig(fullfile(edfFolder, edfFile));
    fs = EEG.srate;
    total_samples = size(EEG.data, 2);

    % Load matching .event file
    eventFile = fullfile(edfFolder, [nameNoExt, '.edf.event']);
    if ~exist(eventFile, 'file')
        warning('Event file not found: %s\nSkipping file...', eventFile);
        continue;
    end

    fid = fopen(eventFile, 'r');
    rawText = fread(fid, '*char')';
    fclose(fid);

    pattern = '(T[0-2])\s*duration:\s*([0-9]+\.[0-9]+)';
    matches = regexp(rawText, pattern, 'tokens');
    if isempty(matches)
        warning('No T0, T1, or T2 events found in: %s\nSkipping file...', eventFile);
        continue;
    end

    % Extract event data
    numEvents = length(matches);
    labels = cell(numEvents, 1);
    durations = zeros(numEvents, 1);
    for i = 1:numEvents
        labels{i} = matches{i}{1};
        durations(i) = str2double(matches{i}{2});
    end
    segment_lengths_samples = round(durations * fs);

    % Adjust final segment if needed
    if sum(segment_lengths_samples) > total_samples
        segment_lengths_samples(end) = total_samples - sum(segment_lengths_samples(1:end-1));
    end

    % Segment and save
    start_idx = 1;
    for i = 1:numEvents
        len = segment_lengths_samples(i);
        end_idx = start_idx + len - 1;
        if end_idx > total_samples
            end_idx = total_samples;
        end

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
end

fprintf('\n✅ All done! Segment folders created in: %s\n', edfFolder);
