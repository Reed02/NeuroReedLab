%eeglab;  % Uncomment if you want to launch EEGLAB GUI

desktopPath = fullfile(getenv('HOME'), 'Desktop');

% Define folder to save EEG segments
saveFolder = fullfile(desktopPath, 'EEG_Segments');

% Create the folder if it doesn't exist
if ~exist(saveFolder, 'dir')
    mkdir(saveFolder);
end

% Load EDF file
EEG = pop_biosig('S001R03.edf');

fs = EEG.srate;             % sampling rate
total_samples = size(EEG.data, 2);

% --- Load event labels and durations as before ---
filename = 'S001R03.edf.event';  % your event file

% Open event file and read text
fid = fopen(filename, 'r');
rawText = fread(fid, '*char')';
fclose(fid);

% Extract labels and durations with regex
pattern = '(T[0-2])\s*duration:\s*([0-9]+\.[0-9]+)';
matches = regexp(rawText, pattern, 'tokens');
if isempty(matches)
    error('No T0, T1, or T2 events with durations were found.');
end

numEvents = length(matches);
labels = cell(numEvents, 1);
durations = zeros(numEvents, 1);

for i = 1:numEvents
    labels{i} = matches{i}{1};
    durations(i) = str2double(matches{i}{2});
end

% Calculate samples for each segment based on durations
segment_lengths_samples = round(durations * fs);

% Check if sum of all segment lengths exceeds data length
if sum(segment_lengths_samples) > total_samples
    warning('Sum of event durations exceeds EEG data length. Truncating last segment.');
    % Optionally truncate last segment to fit EEG data length exactly
    segment_lengths_samples(end) = total_samples - sum(segment_lengths_samples(1:end-1));
end

% Initialize starting sample index
start_idx = 1;

for i = 1:numEvents
    len = segment_lengths_samples(i);
    end_idx = start_idx + len - 1;
    
    % Safety check in case end_idx goes beyond data length
    if end_idx > total_samples
        end_idx = total_samples;
    end
    
    % Extract segment
    EEG_seg = EEG;
    EEG_seg.data = EEG.data(:, start_idx:end_idx);
    EEG_seg.pnts = size(EEG_seg.data, 2);
    EEG_seg.xmax = EEG_seg.pnts / fs;
    EEG_seg.times = EEG.times(start_idx:end_idx);
    EEG_seg.trials = 1;
    
    % Save segment with label and number in filename
    filename_set = sprintf('segment_%03d_%s.set', i, labels{i});
    fullpath = fullfile(saveFolder, filename_set);
    
    pop_saveset(EEG_seg, 'filename', fullpath);
    
    % Update start index for next segment
    start_idx = end_idx + 1;
    
    % Stop if we reached end of data
    if start_idx > total_samples
        break
    end
end
