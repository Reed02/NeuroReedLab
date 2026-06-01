% === Set up paths ===
inputFolder = uigetdir(pwd, 'Select folder with .set EEG files');
desktopPath = fullfile(getenv('HOME'), 'Desktop'); % For Mac
outputBaseFolder = fullfile(desktopPath, 'EEG_Processed_Images2');

% Create output subfolders
originalFolder = fullfile(outputBaseFolder, 'original');
filteredFolder = fullfile(outputBaseFolder, 'filtered');
smoothedFolder = fullfile(outputBaseFolder, 'smoothed');
fftFilteredFolder = fullfile(outputBaseFolder, 'fftFiltered');
fftSmoothedFolder = fullfile(outputBaseFolder, 'fftSmoothed');
fftAverageFolder = fullfile(outputBaseFolder, 'fftAverage');
fftAvgSmoothedFolder = fullfile(outputBaseFolder, 'fftAvgSmoothed');

folders = {originalFolder, filteredFolder, smoothedFolder, ...
           fftFilteredFolder, fftSmoothedFolder, fftAverageFolder, fftAvgSmoothedFolder};

for i = 1:length(folders)
    if ~exist(folders{i}, 'dir')
        mkdir(folders{i});
    end
end

% === Get list of .set files ===
fileList = dir(fullfile(inputFolder, '*.set'));

% === Loop through each .set file ===
for k = 1:length(fileList)
    fileName = fileList(k).name;
    fprintf('Processing %s...\n', fileName);

    EEG = pop_loadset('filename', fileName, 'filepath', inputFolder);
    data = double(EEG.data);
    Fs = EEG.srate;
    t = (0:size(data,2)-1)/Fs;
    nChannels = size(data, 1);

    % === Bandpass filter (14-50 Hz) ===
    bpFilt = designfilt('bandpassiir','FilterOrder',4, ...
             'HalfPowerFrequency1',14,'HalfPowerFrequency2',50, ...
             'SampleRate',Fs);

    % === Smoothing ===
    windowSize = round(0.1 * Fs); % 100 ms
    filtered_data = zeros(size(data));
    smoothed_data = zeros(size(data));

    for ch = 1:nChannels
        filtered_data(ch, :) = filtfilt(bpFilt, data(ch, :));
        smoothed_data(ch, :) = movmean(filtered_data(ch, :), windowSize);
    end

    % === Plot 1: Original ===
    fig1 = figure('Visible','off');
    plot(t, data);
    xlabel('Time (s)'); ylabel('Amplitude (\muV)');
    title(['Original EEG - ', fileName], 'Interpreter', 'none');
    legend(arrayfun(@(x) ['Ch ', num2str(x)], 1:nChannels, 'UniformOutput', false));
    grid on;
    saveas(fig1, fullfile(originalFolder, [fileName(1:end-4), '_original.png'])); close(fig1);

    % === Plot 2: Filtered ===
    fig2 = figure('Visible','off');
    plot(t, filtered_data);
    xlabel('Time (s)'); ylabel('Amplitude (\muV)');
    title(['Filtered EEG (14-50 Hz) - ', fileName], 'Interpreter', 'none');
    legend(arrayfun(@(x) ['Ch ', num2str(x)], 1:nChannels, 'UniformOutput', false));
    grid on;
    saveas(fig2, fullfile(filteredFolder, [fileName(1:end-4), '_filtered.png'])); close(fig2);

    % === Plot 3: Smoothed ===
    fig3 = figure('Visible','off');
    plot(t, smoothed_data);
    xlabel('Time (s)'); ylabel('Amplitude (\muV)');
    title(['Smoothed EEG - ', fileName], 'Interpreter', 'none');
    legend(arrayfun(@(x) ['Ch ', num2str(x)], 1:nChannels, 'UniformOutput', false));
    grid on;
    saveas(fig3, fullfile(smoothedFolder, [fileName(1:end-4), '_smoothed.png'])); close(fig3);

    % === FFT setup ===
    N = size(smoothed_data, 2);
    f = Fs * (0:floor(N/2)) / N;
    fft_all = zeros(nChannels, length(f));

    % === Plot 4: FFT of Filtered ===
    fig4 = figure('Visible','off'); hold on;
    for ch = 1:nChannels
        Y = fft(filtered_data(ch, :));
        P2 = abs(Y / N);
        P1 = P2(1:floor(N/2) + 1);
        P1(2:end-1) = 2 * P1(2:end-1);
        plot(f, P1, 'DisplayName', ['Ch ', num2str(ch)]);
    end
    hold off;
    xlabel('Frequency (Hz)'); ylabel('|Amplitude|');
    title(['FFT of Filtered EEG - ', fileName], 'Interpreter', 'none');
    legend; xlim([0 60]); grid on;
    saveas(fig4, fullfile(fftFilteredFolder, [fileName(1:end-4), '_fft_filtered.png'])); close(fig4);

    % === Plot 5: FFT of Smoothed ===
    fig5 = figure('Visible','off'); hold on;
    for ch = 1:nChannels
        Y = fft(smoothed_data(ch, :));
        P2 = abs(Y / N);
        P1 = P2(1:floor(N/2) + 1);
        P1(2:end-1) = 2 * P1(2:end-1);
        fft_all(ch, :) = P1;
        plot(f, P1, 'DisplayName', ['Ch ', num2str(ch)]);
    end
    hold off;
    xlabel('Frequency (Hz)'); ylabel('|Amplitude|');
    title(['FFT of Smoothed EEG - ', fileName], 'Interpreter', 'none');
    legend; xlim([0 60]); grid on;
    saveas(fig5, fullfile(fftSmoothedFolder, [fileName(1:end-4), '_fft_smoothed.png'])); close(fig5);

    % === Plot 6: Average FFT ===
    avg_fft = mean(fft_all, 1);
    fig6 = figure('Visible','off');
    plot(f, avg_fft, 'k', 'LineWidth', 2);
    xlabel('Frequency (Hz)'); ylabel('Mean |Amplitude|');
    title(['Average FFT of Smoothed EEG - ', fileName], 'Interpreter', 'none');
    grid on; xlim([0 60]);
    saveas(fig6, fullfile(fftAverageFolder, [fileName(1:end-4), '_fft_avg.png'])); close(fig6);

    % === Plot 7: Strongly Smoothed Average FFT ===
    freq_resolution = f(2) - f(1);
    fft_smooth_window_hz = 5;
    fft_smooth_window_pts = round(fft_smooth_window_hz / freq_resolution);
    avg_fft_smoothed = movmean(avg_fft, fft_smooth_window_pts);

    fig7 = figure('Visible','off');
    plot(f, avg_fft_smoothed, 'm', 'LineWidth', 3);
    xlabel('Frequency (Hz)'); ylabel('Strongly Smoothed Mean |Amplitude|');
    title(['Smoothed Avg FFT of Smoothed EEG - ', fileName], 'Interpreter', 'none');
    grid on; xlim([0 60]);
    saveas(fig7, fullfile(fftAvgSmoothedFolder, [fileName(1:end-4), '_fft_avg_smoothed.png'])); close(fig7);

    fprintf('Finished %s\n', fileName);
end

fprintf('All files processed. Results saved to:\n%s\n', outputBaseFolder);
