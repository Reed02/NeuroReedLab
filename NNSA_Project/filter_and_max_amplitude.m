[ALLEEG, EEG, CURRENTSET, ALLCOM] = eeglab;

% Load dataset
EEG1 = pop_loadset('S001R03_segment_004_T1.set');  
[ALLEEG, EEG1, CURRENTSET] = eeg_store(ALLEEG, EEG1, 0);

% Get data and sampling rate
data = EEG1.data;  % channels x timepoints
Fs = EEG1.srate;
numChannels = size(data, 1);
N = size(data, 2);

% Filter parameters
cutoff = 8; % cutoff frequency (Hz) - eliminates rest frequencies (noise)
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

% Variables to track global max amplitude and corresponding frequency
globalMaxAmp = -Inf;
globalMaxFreq = NaN;
globalMaxChannel = NaN;

figure;
hold on;

for ch = 1:numChannels
    channelData = dataToPlot(ch, :);
    Y = fft(channelData);
    P2 = abs(Y/N);
    P1 = P2(1:floor(N/2)+1);
    P1(2:end-1) = 2*P1(2:end-1);

    % Normalize amplitude to max of 1 per channel for plotting
    P1_norm = P1 / max(P1);

    % Find max amplitude and frequency in original amplitude spectrum (not normalized)
    [chMaxAmp, idxMax] = max(P1);
    chMaxFreq = f(idxMax);

    % Update global max if this channel has a higher amplitude
    if chMaxAmp > globalMaxAmp
        globalMaxAmp = chMaxAmp;
        globalMaxFreq = chMaxFreq;
        globalMaxChannel = ch;
    end

    % Plot normalized spectrum with offset
    offset = (ch - 1) * offsetStep;
    plot(f, P1_norm + offset, 'DisplayName', ['Ch ' num2str(ch)]);
end

hold off;
title('Normalized & Offset Amplitude Spectrum of All Channels (Filtered > 8 Hz)');
xlabel('Frequency (Hz)');
ylabel('Normalized Amplitude + Offset');
xlim([0 Fs/2]);
ylim([-0.5, (numChannels - 1)*offsetStep + 1]);

yticks(0:offsetStep:(numChannels-1)*offsetStep);
yticklabels(arrayfun(@(c) ['Ch ' num2str(c)], 1:numChannels, 'UniformOutput', false));

legend('off');

% Print global max frequency and amplitude
fprintf('Global max amplitude %.4f found at frequency %.2f Hz on channel %d\n', ...
        globalMaxAmp, globalMaxFreq, globalMaxChannel);
