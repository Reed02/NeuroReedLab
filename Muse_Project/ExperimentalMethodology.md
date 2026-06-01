EXPERIMENTAL DESIGN

This project investigates whether motor-intent decoding techniques inspired by Alazrai et al. (2019) can be adapted to a low cost wearable EEG device (Muse 2) for real-time robotic hand control. The original study utilized an 11-channel BioSemiActiveTwo EEG system and successfully classified twelve finger movements within the same hand using a hierarchical classification framework. Due to the reduced spatial resolution of the Muse 2 headset, this project begins with a simplified classification problem consisting of three classes:

1. Rest
2. Thumb flexion/extension
3. Index finger flexion/extension

The objective of the initial experiment is to determine whether these classes can be reliably distinguished using only four Muse 2 EEG channels.

______________________________________________________________________________________________________________________________________

SUBJECT PREPARATION

The experiment is performed by a single subject. Prior to data collection, the Muse 2 headset is fitted according to manufacturer recommendations and electrode quality is verified using the MuseLSL visualization tools.

This subject is instructed to:

- Remain awake and alert.
- Avoid caffeine immediately before recording sessions when possible.
- Avoid vigorous exercise immediately before recording session.
- Remove distractions from the recording environment.
- Silence electronic devices.

All recording sessions are performed in the same room and under similar environmental conditions whenever possible.

______________________________________________________________________________________________________________________________________


SEATING AND POSTURE

The subject is seated in a fixed chair with back support positioned at a desk.

During recording:

- The subject's back remains in contact with the chair backrest.
- Feet remain flat on the floor.
- Legs remain uncrossed.
- The head remains upright and oriented forward.
- The subject does not intentionally lean forward or recline during trials.

This posture is maintained throughout the recording session to reduce movement related artifacts.

______________________________________________________________________________________________________________________________________


ARM AND HAND POSITION

The right arm is used for all movement trials.

The right forearm rests completely on a solid surface and remains supported throughout the experiment.

THe wrist is positioned near the edge of the solid surface while the hand extends slighly beyond the edge.

THe hand remains in a pronated position throughout all trials:

- Palm facing downward
- Back of the hand facing upward.

The forearm, elbow, shoulder, and torso are kept stationary during data collection.

Only the instructed finger is allowed to move.


______________________________________________________________________________________________________________________________________

VISUAL FIXATION

To reduce eye movement artifacts, the subject maintains visual fixation on a stationary target positioned approximately at eye level.

The fixation target remains visible throughout the recording session.

The subject keeps both eyes open during all trials.

Eye closure is avoided becuase it can substantially alter alpha band EEG activity and introduce unwanted variability into the recordings.

______________________________________________________________________________________________________________________________________

BREATHING AND FACIAL ACTIVITY

The subject is instructed to breath normally throughout all recording sessions.

No attempt is made to consciously alter breathing rate or depth.

The subject is instructed to:

- Avoid speaking.
- Avoid jaw clenching.
- Avoid excessive swallowing.
- Avoid eyebrow moevements.
- Avoid facial expressions.

These precautions are taken because facial muscle activity can produce electrical signals that are significantly larger than the EEG activity of interest.

______________________________________________________________________________________________________________________________________

MOVEMENT PROTOCOL

Finger movements are performed at a controlled pace.

Each movement consists of repeated flexion and extension cycles at approximately one cycle per second.

______________________________________________________________________________________________________________________________________

THUMB TRIALS

During thumb trials:

- Only one thumb moves.
- The thumb repeatedly flexes and extends.
- The wrist remains stationary.
- The remaining fingers remain relaxed.

______________________________________________________________________________________________________________________________________

INDEX FINGER TRIALS

During index finger trials:

- Only the index finger moves.
- The index finger repeatedly flexes and extends.
- The wrist remains stationary.
- The remaining fingers remain relaxed.

Movement amplitude is kept as consistent as possible across all repetitions.

______________________________________________________________________________________________________________________________________


TRIAL STRUCTURE

Each trial follows the same sequency:

Stage                    Duration

Baseline Rest            2 seconds

Visual Cue               1 second

Movement Period          3 seconds

Recovery Rest            2 seconds

Total trial duration: 8 seconds.

Visual cues are displayed on a computer screen to indicate the upcoming task.

Examples of visual cues include:

- Rest
- Thumb
- Index

______________________________________________________________________________________________________________________________________

TRIAL RANDOMIZATION

Trials are presented in randomized order.

Thumb and index movements are not grouped into separate recording blocks.

Randomization is used to reduce:

- Fatigue-related effects
- Adaptation effects
- Temporal recording biases

______________________________________________________________________________________________________________________________________

DATASET SIZE

The initial dataset consists of:

Class            Number of Trials

Rest             50

Thumb            50

Index            50

Total trials: 150

Expected recording time is approximately 20-30 minutes.

Additional sessions may be collected if classifier performance indicates insufficient training data.


______________________________________________________________________________________________________________________________________


ARTIFACT MANAGEMENT

Trials are reviewed for obvious recording artifacts.

Trials may be rejected if any of the folowing occur:

- Loss of EEG signal quality.
- Excessive head movement.
- Excessive blinking during movement periods.
- Incorrect finger movement.
- Accidental wrist or arm movement
- Recording interruptions.

Rejected trials are documented in a session log and excluded from classifier training.

______________________________________________________________________________________________________________________________________

DATA LABELING

Each trial is labeled according to the instructed task.

Event markers are recorded for:

- Trial start.
- Cue onset.
- Movement onset.
- Trial completion.

These markers are used to synchronize EEG data with task labeles during preprocessing and feature extraction.

______________________________________________________________________________________________________________________________________


Relationship to Zlazrai et al. (2019)

The experimental design is inspired by the methodology described by Alazrai et al. (2019), who investigated EEG based decoding of twelve finger movements using an 11-channel EEG system and a hierarchical classification framework.

Because the Muse 2 provides only four channels and lacks direct coverage of the primary motor cortex electrode locations used in the original study, the classification problem is intentionally simplified. This adaptation prioritizes signal quality, reproducibility, and real time feasibility while preserving the central objective of motor intent decoding.


______________________________________________________________________________________________________________________________________

REFERENCE

Alazrai, Rami, Hisham Alwanni, and Mohammad I. Daoud. "EEG-based BCI System for Decoding Finger Movements within the Same Hand." Neuroscience Letters, vol. 698, 2019, pp. 113–120. DOI: 10.1016/j.neulet.2018.12.045.


