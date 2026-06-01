% === Set up paths ===
inputFolder = uigetdir(pwd, 'Select folder with .edf EEG files');
desktopPath = fullfile(getenv('HOME'), 'Desktop'); % For Mac
outputFolder = fullfile(desktopPath, 'EEG_FFT_Average_MAT');

if ~exist(outputFolder, 'dir')
    mkdir(outputFolder);
end

% === Get list of .edf files ===
fileList = dir(fullfile(inputFolder, '*.edf'));

% === Loop through each .edf file ===
for k = 1:length(fileList)
    fileName = fileList(k).name;
    fprintf('Processing %s...\n', fileName);

    % Load EDF file using EEGLAB's biosig plugin
    EEG = pop_biosig(fullfile(inputFolder, fileName));
    data = double(EEG.data);
    Fs = EEG.srate;
    nChannels = size(data, 1);

    % === Bandpass filter (14-50 Hz) ===
    bpFilt = designfilt('bandpassiir', 'FilterOrder', 4, ...
                        'HalfPowerFrequency1', 14, 'HalfPowerFrequency2', 50, ...
                        'SampleRate', Fs);

    % === Smoothing ===
    windowSize = round(0.1 * Fs); % 100 ms
    filtered_data = zeros(size(data));
    smoothed_data = zeros(size(data));

    for ch = 1:nChannels
        filtered_data(ch, :) = filtfilt(bpFilt, data(ch, :));
        smoothed_data(ch, :) = movmean(filtered_data(ch, :), windowSize);
    end

    % === FFT computation ===
    N = size(smoothed_data, 2);
    f = Fs * (0:floor(N/2)) / N;
    fft_all = zeros(nChannels, length(f));

    for ch = 1:nChannels
        Y = fft(smoothed_data(ch, :));
        P2 = abs(Y / N);
        P1 = P2(1:floor(N/2) + 1);
        P1(2:end-1) = 2 * P1(2:end-1);
        fft_all(ch, :) = P1;
    end

    % === Average FFT across channels ===
    avg_fft = mean(fft_all, 1);   % 1 x length(f)

    % === Save average FFT and frequency vector as .mat ===
    baseName = fileName(1:end-4);
    saveFile = fullfile(outputFolder, [baseName, '_avgFFT.mat']);
    avg_fft_row = avg_fft(:)'; % ensure row vector

    save(saveFile, 'avg_fft_row', 'f');

    fprintf('Finished %s\n', fileName);
end

fprintf('All files processed. Average FFT .mat files saved to:\n%s\n', outputFolder);
