This Project Is a Continuation and Enhancement Upon my NNSA Open Source EEG Classificaion Project


This projects methodology is inspired by:
Alazrai, Rami, Hisham Alwanni, and Mohammad I. Daoud.
"EEG-based BCI System for Decoding Finger Movements withiin the Same Hand."
Neuroscience Letters, 2019.
DOI: 10.1016/j.neulet.2018.12.045

Their study showed a hierarchical EEG based classification system capable of decoding 12 finger movements
within the same hand using an 11 channel EEG system and a two layer SVM framework with time frequency features
dervied from the Choi Williams Distribution

GOAL:
This project will explore whether the core ideas from the Alazrai et al. (2019) BCI framework can be adapted to a low cost wearable
EEG device (Muse 2) under severe constrains in:
- Channel count (11 -> 4 electrodes)
- Spatial Resolution
- Signal Quality
- Computational Complexity
Rather than replicating full 12 class decoding, this will focus on:
Robust, real-time motor intent decoding under wearable EEG constraints.

SYSTEM OVERVIEW
The original paper uses a two layer classification system:
- Layer 1: Finger Identification
- Layer 2: Movement Type Per Finger
- Features: Choi-Williams time-frequency distribution + entropy based measures
- Classifier: SVM based hierarchical model

This project modifies the pipeline as follows:
- EEG device: Muse 2 (4 channels)
- Feature extraction: bandpwer + Hjorth parameters
- Classifier: lightweight ML models (SVM/LDA/Random Forest)
- Task Complexity: Reduced class motor intent decoding
- Output: real time control signals for robotic hand

HARDWARE
- EEG Device: Muse 2
- Robotic Hand: Hiwonder uHand

METHODOLOGY
1. Data Acquisition
EEG signals are recorded using Muse 2 at los channel frontal/temporal sites. Signals are sampled and segmented into short time windows (1-2 seconds) for analysis.

2. Preprocessing
- Bandpass filter: 1-40 Hz
- Notch filter: 50/60 Hz (noise removal)
- Z-score normalization per session
- Sliding window segmentation

3. Feature Extraction
Instead of high complexity time frequency analysis (e.g., Choi-Williams Distribution used in the original study), this project uses:
- Bandpower (delta, theta, alpha, beta)
- Log-variance per channel
- Hjorth parameters (activity, mobility, complexity)
These features are chosen for their robustness in low-density EEG systems and suitability for real time processing

4. Classification Strategy
The origiinal hierarchical SVM system is adapted into a simplified two stage pipeline:
Layer 1: Movement Detection
- Rest vs Movement
Layer 2: Intent Classification
- Thumb intent
- Index intent
- Grip intent
This preserves the hierarchical decision structure while reducing class complexity to match signal limitations

5. Control Output
Classifier outputs are mapped to robotic actions:
- Thumb intent -> thumb actuation
- Index Intent -> Index actuation
- Grip Intent -> Full hand closure
A smoothing filter (majority vote over recent predictions) is used to stabilize real time control signals.


EXPECTED PERFORMANCE
System                    Classes                  Accuracy                     Notes

Alazrai et al. (2019)     12 finger movements      ~65-85%                      high-density EEG

This project              3-4 intents              subject-dependent (~50-80%)  wearable EEG constraint


KEY DESIGN DECISIONS (IMPORTANT)
1. Reduction of classification complexity
The original 12-class system is not feasible unser 4 channel EEG due to overlapping motor representations and reduced spatial resolution

2. Replacement of CWD wuth spectral features
Choi-William Distribution provides high-resolution time-frequency analysis but is computationally expensive and sensitive to noise in werable EEG settings.

3. Use of hierarchical classification
A layered decision structure is retained because it improves robustness and reduces classification ambiguity in low SNR environments.

SCIENTIFIC CONTRIBUTION

This project does not aim to replicate full resolution finger decoding. Instead, it investigates:
  - how far hierarchical motor intent decoding can be preserved under severe EEG hardware constraints.

FUTURE WORK
- Improve feature extraction using CSP or Riemannian geometry methods
- Replace classical ML with lightweight CNNs on spectrograms
- Improve cross-subject generalization
- Integrate adaptive calibration per user

CITATION
Alazrai, Rami, Hisham Alwanni, and Mohammad I. Daoud.
"EEG-based BCI System for Decoding Finger Movements within the Same Hand."
Neuroscience Letters, vol. 698, 2019, pp. 113–120.
https://doi.org/10.1016/j.neulet.2018.12.045


