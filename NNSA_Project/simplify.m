[ALLEEG, EEG, CURRENTSET, ALLCOM] = eeglab;

% Load dataset
EEG1 = pop_loadset('S001R03_segment_002_T2.set');  
[ALLEEG, EEG1, CURRENTSET] = eeg_store(ALLEEG, EEG1, 0);

% Get data and sampling rate
data = EEG1.data;  % channels x timepoints
Fs = EEG1.srate;
numChannels = size(data, 1);
N = size(data, 2);

% Filter parameters
cutoff = 8; % cutoff frequency (Hz) This elimiates rest frequencies(or noise)
order = 4; % filter order

% Design highpass Butterworth filter
[b,a] = butter(order, cutoff/(Fs/2), 'high');

% Initialize filtered data matrix
filteredData = zeros(size(data));

% Apply zero-phase filtering (filtfilt) to each channel
for ch = 1:numChannels
    filteredData(ch, :) = filtfilt(b, a, double(data(ch, :)));
end

% Data to use for FFT and plotting
dataToPlot = filteredData;

% Frequency vector for plotting (up to Nyquist frequency)
f = Fs*(0:(floor(N/2)))/N;

offsetStep = 0.1;  % vertical offset between channel plots

figure;
hold on;

for ch = 1:numChannels
    channelData = dataToPlot(ch, :);
    Y = fft(channelData);
    P2 = abs(Y/N);
    P1 = P2(1:floor(N/2)+1);
    P1(2:end-1) = 2*P1(2:end-1);

    % Normalize amplitude to max of 1 per channel
    P1 = P1 / max(P1);

    % Plot with offset to separate channels vertically
    offset = (ch - 1) * offsetStep;
    plot(f, P1 + offset, 'DisplayName', ['Ch ' num2str(ch)]);
end

hold off;
title('Normalized & Offset Amplitude Spectrum of All Channels (Filtered > 12 Hz)');
xlabel('Frequency (Hz)');
ylabel('Normalized Amplitude + Offset');
xlim([0 Fs/2]);
ylim([-0.5, (numChannels - 1)*offsetStep + 1]);

yticks(0:offsetStep:(numChannels-1)*offsetStep);
yticklabels(arrayfun(@(c) ['Ch ' num2str(c)], 1:numChannels, 'UniformOutput', false));

legend('off');
