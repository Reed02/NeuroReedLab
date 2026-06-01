% === Load EEGLAB and EEG dataset ===
[ALLEEG, EEG, CURRENTSET, ALLCOM] = eeglab;
EEG = pop_loadset('S001R03_segment_006_T1.set');  
[ALLEEG, EEG, CURRENTSET] = eeg_store(ALLEEG, EEG, 0);

% === Extract data and sampling rate ===
data = double(EEG.data);   % channels x timepoints
Fs = EEG.srate;            % Sampling frequency (Hz)
t = (0:size(data,2)-1)/Fs; % time vector in seconds
nChannels = size(data, 1); % number of EEG channels

% === Bandpass filter from 1 to 50 Hz ===
bpFilt = designfilt('bandpassiir','FilterOrder',4, ...
         'HalfPowerFrequency1',14,'HalfPowerFrequency2',50, ...
         'SampleRate',Fs);

% === Moving average smoothing window ===
windowSize = round(0.1 * Fs); % 100 ms window

% === Prepare storage for filtered and smoothed signals ===
filtered_data = zeros(size(data));
smoothed_data = zeros(size(data));

for ch = 1:nChannels
    % Apply bandpass filter
    filtered_data(ch, :) = filtfilt(bpFilt, data(ch, :));
    
    % Apply moving average smoothing
    smoothed_data(ch, :) = movmean(filtered_data(ch, :), windowSize);
end

% === Plot 1: Original signals (all channels) ===
figure;
plot(t, data);
xlabel('Time (s)');
ylabel('Amplitude (\muV)');
title('All Channels - Original EEG Signals');
legend(arrayfun(@(x) ['Ch ', num2str(x)], 1:nChannels, 'UniformOutput', false));
grid on;

% === Plot 2: Filtered signals (1-50 Hz) ===
figure;
plot(t, filtered_data);
xlabel('Time (s)');
ylabel('Amplitude (\muV)');
title('All Channels - Filtered EEG Signals (1-50 Hz)');
legend(arrayfun(@(x) ['Ch ', num2str(x)], 1:nChannels, 'UniformOutput', false));
grid on;

% === Plot 3: Smoothed signals ===
figure;
plot(t, smoothed_data);
xlabel('Time (s)');
ylabel('Amplitude (\muV)');
title('All Channels - Smoothed EEG Signals');
legend(arrayfun(@(x) ['Ch ', num2str(x)], 1:nChannels, 'UniformOutput', false));
grid on;

% === Plot 4: FFT of Filtered signals ===
figure;
N = size(filtered_data, 2);      
f = Fs * (0:floor(N/2)) / N;     

hold on;
for ch = 1:nChannels
    Y = fft(filtered_data(ch, :));
    P2 = abs(Y / N);             
    P1 = P2(1:floor(N/2) + 1);   
    P1(2:end-1) = 2 * P1(2:end-1);
    
    plot(f, P1, 'DisplayName', ['Ch ', num2str(ch)]);
end
hold off;
xlabel('Frequency (Hz)');
ylabel('|Amplitude|');
title('FFT of Filtered EEG Signals (All Channels)');
legend;
xlim([0 60]);
grid on;

% === Plot 5: FFT of Smoothed signals ===
figure;
N = size(smoothed_data, 2);      
f = Fs * (0:floor(N/2)) / N;     

hold on;
for ch = 1:nChannels
    Y = fft(smoothed_data(ch, :));
    P2 = abs(Y / N);             
    P1 = P2(1:floor(N/2) + 1);   
    P1(2:end-1) = 2 * P1(2:end-1);
    
    plot(f, P1, 'DisplayName', ['Ch ', num2str(ch)]);
end
hold off;
xlabel('Frequency (Hz)');
ylabel('|Amplitude|');
title('FFT of Smoothed EEG Signals (All Channels)');
legend;
xlim([0 60]);
grid on;

% === Plot 6: Average FFT of Smoothed EEG Signals Across All Channels ===
N = size(smoothed_data, 2);
f = Fs * (0:floor(N/2)) / N;

% Compute FFT for all channels and store them
fft_all = zeros(nChannels, length(f));

for ch = 1:nChannels
    Y = fft(smoothed_data(ch, :));
    P2 = abs(Y / N);
    P1 = P2(1:floor(N/2) + 1);
    P1(2:end-1) = 2 * P1(2:end-1);
    
    fft_all(ch, :) = P1;
end

% Take mean across all channels
avg_fft = mean(fft_all, 1);

% Plot
figure;
plot(f, avg_fft, 'k', 'LineWidth', 2);
xlabel('Frequency (Hz)');
ylabel('Mean |Amplitude|');
title('Average FFT of Smoothed EEG Signals (All Channels)');
grid on;
xlim([0 60]);

% === Plot 7: Very Strongly Smoothed Average FFT of Smoothed EEG Signals ===

% Frequency resolution
freq_resolution = f(2) - f(1);

% Large smoothing window (e.g., 10 Hz)
fft_smooth_window_hz = 5;  

% Convert Hz to number of points
fft_smooth_window_pts = round(fft_smooth_window_hz / freq_resolution);

% Apply moving average smoothing with a large window
avg_fft_strongly_smoothed = movmean(avg_fft, fft_smooth_window_pts);

% Plot
figure;
plot(f, avg_fft_strongly_smoothed, 'm', 'LineWidth', 3);
xlabel('Frequency (Hz)');
ylabel('Strongly Smoothed Mean |Amplitude|');
title('Strongly Smoothed Average FFT of Smoothed EEG Signals (All Channels)');
grid on;
xlim([0 60]);
