% % === Load EEGLAB and EEG dataset ===
[ALLEEG, EEG, CURRENTSET, ALLCOM] = eeglab;
EEG = pop_loadset('S001R03_segment_004_T1.set');  
[ALLEEG, EEG, CURRENTSET] = eeg_store(ALLEEG, EEG, 0);

% === Extract data and sampling rate ===
data = double(EEG.data);   % channels x timepoints
Fs = EEG.srate;            % Sampling frequency (Hz)
t = (0:size(data,2)-1)/Fs; % time vector in seconds
nChannels = size(data, 1); % number of EEG channels

% === Bandpass filter from 1 to 50 Hz ===
bpFilt = designfilt('bandpassiir','FilterOrder',4, ...
         'HalfPowerFrequency1',1,'HalfPowerFrequency2',50, ...
         'SampleRate',Fs);

% === Moving average smoothing window ===
windowSize = round(0.1 * Fs); % 50 ms window

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

