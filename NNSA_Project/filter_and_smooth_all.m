% === Set up paths ===
inputFolder = uigetdir(pwd, 'Select folder with .set EEG files');
%desktopPath = fullfile(getenv('USERPROFILE'), 'Desktop');  % Windows
desktopPath = fullfile(getenv('HOME'), 'Desktop'); %mac
outputBaseFolder = fullfile(desktopPath, 'EEG_Processed_Images');

% Create output subfolders
originalFolder = fullfile(outputBaseFolder, 'original');
filteredFolder = fullfile(outputBaseFolder, 'filtered');
smoothedFolder = fullfile(outputBaseFolder, 'smoothed');
if ~exist(originalFolder, 'dir'), mkdir(originalFolder); end
if ~exist(filteredFolder, 'dir'), mkdir(filteredFolder); end
if ~exist(smoothedFolder, 'dir'), mkdir(smoothedFolder); end

% === Get list of .set files ===
fileList = dir(fullfile(inputFolder, '*.set'));

% === Loop through each .set file ===
for k = 1:length(fileList)
    fileName = fileList(k).name;
    fprintf('Processing %s...\n', fileName);
    
    % Load dataset
    EEG = pop_loadset('filename', fileName, 'filepath', inputFolder);
    
    % Extract data and sampling rate
    data = double(EEG.data);   % channels x timepoints
    Fs = EEG.srate;
    t = (0:size(data,2)-1)/Fs;
    nChannels = size(data, 1);
    
    % Bandpass filter 1-50 Hz
    bpFilt = designfilt('bandpassiir','FilterOrder',4, ...
             'HalfPowerFrequency1',1,'HalfPowerFrequency2',50, ...
             'SampleRate',Fs);
    
    % Smoothing
    windowSize = round(0.05 * Fs);
    filtered_data = zeros(size(data));
    smoothed_data = zeros(size(data));
    
    for ch = 1:nChannels
        filtered_data(ch, :) = filtfilt(bpFilt, data(ch, :));
        smoothed_data(ch, :) = movmean(filtered_data(ch, :), windowSize);
    end
    
    % === Plot and Save Original ===
    fig1 = figure('Visible','off');
    plot(t, data);
    xlabel('Time (s)'); ylabel('Amplitude (\muV)');
    title(['Original EEG - ', fileName], 'Interpreter', 'none');
    legend(arrayfun(@(x) ['Ch ', num2str(x)], 1:nChannels, 'UniformOutput', false));
    grid on;
    saveas(fig1, fullfile(originalFolder, [fileName(1:end-4), '_original.png']));
    close(fig1);
    
    % === Plot and Save Filtered ===
    fig2 = figure('Visible','off');
    plot(t, filtered_data);
    xlabel('Time (s)'); ylabel('Amplitude (\muV)');
    title(['Filtered EEG (1-50 Hz) - ', fileName], 'Interpreter', 'none');
    legend(arrayfun(@(x) ['Ch ', num2str(x)], 1:nChannels, 'UniformOutput', false));
    grid on;
    saveas(fig2, fullfile(filteredFolder, [fileName(1:end-4), '_filtered.png']));
    close(fig2);
    
    % === Plot and Save Smoothed ===
    fig3 = figure('Visible','off');
    plot(t, smoothed_data);
    xlabel('Time (s)'); ylabel('Amplitude (\muV)');
    title(['Smoothed EEG - ', fileName], 'Interpreter', 'none');
    legend(arrayfun(@(x) ['Ch ', num2str(x)], 1:nChannels, 'UniformOutput', false));
    grid on;
    saveas(fig3, fullfile(smoothedFolder, [fileName(1:end-4), '_smoothed.png']));
    close(fig3);
    
    fprintf('Finished %s\n', fileName);
end

fprintf('All files processed. Results saved to:\n%s\n', outputBaseFolder);
