% Load EEGLAB and dataset
[ALLEEG, EEG, CURRENTSET, ALLCOM] = eeglab;
EEG1 = pop_loadset('S001R03_segment_004_T1.set');  
[ALLEEG, EEG1, CURRENTSET] = eeg_store(ALLEEG, EEG1, 0);

% Plot raw EEG with all channels using EEGLAB GUI style
%figure(1);
%pop_eegplot(EEG1, 1, 1, 1);

% Extract data and sampling rate
data = EEG1.data;          % channels x timepoints
fs = EEG1.srate;           % sampling rate in Hz
[num_channels, num_samples] = size(data);

% Parameters for sliding window FFT
window_length_sec = 1;      % Window length in seconds
window_length_samples = window_length_sec * fs;

step_size_sec = 0.1;        % Step size in seconds
step_size_samples = step_size_sec * fs;

num_windows = floor((num_samples - window_length_samples) / step_size_samples) + 1;

% Frequency band limits
freq_low = 8;   % Hz (minimum)
freq_high = 80; % Hz (maximum)

% Preallocate dominant frequency matrix: channels x windows
max_freqs_all = zeros(num_channels, num_windows);
times = zeros(1, num_windows);

% Compute dominant frequency over time for each channel
for ch = 1:num_channels
    for i = 1:num_windows
        start_idx = (i-1)*step_size_samples + 1;
        end_idx = start_idx + window_length_samples - 1;
        segment = data(ch, start_idx:end_idx);
        
        % Compute FFT
        Y = fft(segment);
        L = length(segment);
        P2 = abs(Y/L);
        P1 = P2(1:floor(L/2)+1);
        P1(2:end-1) = 2*P1(2:end-1);
        
        f = fs*(0:(L/2))/L;
        
        % Find indices within [freq_low, freq_high]
        valid_idx = find(f >= freq_low & f <= freq_high);
        
        % Find max amplitude frequency within valid range
        [~, max_rel_idx] = max(P1(valid_idx));
        max_idx = valid_idx(max_rel_idx);
        max_freqs_all(ch, i) = f(max_idx);
        
        % Time vector (same for all channels)
        if ch == 1
            times(i) = (start_idx + end_idx) / (2*fs);
        end
    end
end

% Plot all channels' dominant frequency on one plot with vertical offsets
figure(2);
hold on;
colors = lines(num_channels);  % Distinct colors for channels

offset = freq_high + 10;  % Vertical offset between channels (adjust as needed)

for ch = 1:num_channels
    % Offset the dominant frequency values by channel index
    plot(times, max_freqs_all(ch, :) + (ch-1)*offset, 'Color', colors(ch, :), 'LineWidth', 1.5);
end
hold off;

xlabel('Time (seconds)');
ylabel('Dominant Frequency + Offset');
title(['Dominant Frequency (' num2str(freq_low) '-' num2str(freq_high) ' Hz) Over Time with Offsets']);
yticks((0:num_channels-1)*offset + freq_low + (freq_high-freq_low)/2);
yticklabels(arrayfun(@(x) ['Ch ' num2str(x)], 1:num_channels, 'UniformOutput', false));
grid on;
