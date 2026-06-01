EEG Finger Movement BCI Experiment System

This project implements a structured EEG data collection pipeline designed for motor intention decoding using a Muse 2 EEG headset. It is inspired by:

Alazrai, Rami, et al. “EEG-based BCI System for Decoding Finger Movements within the Same Hand.” Neuroscience Letters, 2019.

The goal of this system is to generate high-quality, time-locked EEG markers for training machine learning models such as SVM classifiers to distinguish between finger movements and rest states.

Objective

The purpose of this system is to create a controlled and reproducible experimental environment for:

EEG motor activity recording using Muse 2
Classification of finger movements (INDEX, THUMB)
Rest state comparison (REST)
Structured trial timing for machine learning datasets
Future integration with EEG signal processing pipelines
System Overview
Experimental Structure

The experiment is organized into blocks and trials.

Each block contains randomized trials of:

THUMB movement
INDEX movement
REST state

Blocks are separated by a manual pause screen to allow cognitive rest and reduce fatigue effects.

This structure improves:

subject attention stability
dataset segmentation clarity
reduction of cognitive drift across long sessions
Trial Flow

Each trial follows a fixed, time-locked sequence designed for EEG alignment:

Baseline (rest stabilization)
→ Cue (instruction display)
→ Preparation window (motor planning)
→ Movement execution
→ Recovery period
→ Inter-trial settling period

Approximate Timing
Baseline: ~3 seconds
Cue: ~1 second
Preparation: ~2 seconds
Movement: ~3 seconds
Recovery: ~2 seconds
Inter-trial gap: ~1 second

These timings are designed to reduce EEG overlap between cognitive states.

Data Logging

All experimental events are recorded in a timestamped CSV file:

timestamp,event,label

Example:

10.085,baseline_start,THUMB
13.088,cue_start,THUMB
15.091,movement_start,THUMB
18.101,movement_end,THUMB
20.104,trial_end,THUMB
Event Types

The system logs the following events:

session_start
block_pause
block_resume
baseline_start
cue_start
movement_start
movement_end
trial_end

These markers are intended for synchronization with EEG recordings.

Experimental Design Features
Strengths
Temporal Structure

The experiment is strictly time-ordered, enabling accurate alignment with EEG signals.

Balanced Sampling

Trials are randomized and approximately balanced across:

REST
INDEX
THUMB

This improves classifier stability and reduces bias.

Block-Based Design

Blocks reduce fatigue and allow natural cognitive resets between sessions.

Cognitive Timing Control

The system includes:

preparation time for motor planning
recovery periods after movement
inter-trial settling time

These reduce contamination between EEG states.

Known Limitations
REST State Ambiguity

REST is currently treated both as:

a baseline cognitive state
a classification label

This can introduce overlap in interpretation between true rest and task-related rest periods.

Temporal Bias Risk

Although trials are randomized, short-range clustering of labels may still occur. This can introduce weak temporal learning bias in machine learning models.

No EEG Signal Integration

The current system only generates behavioral markers.

It does not yet include:

real-time EEG streaming (MuseLSL)
signal preprocessing
feature extraction
classification models
No Artifact Handling

There is currently no handling for:

eye blinks
muscle artifacts
motion noise

These will need to be addressed in downstream signal processing.

System Evaluation
Category	Rating
Timing accuracy	Excellent
Experimental structure	Excellent
Machine learning readiness	Strong
EEG readiness	Moderate to strong
Publication readiness	Near-ready (with EEG integration)
Future Work
EEG Integration
MuseLSL real-time EEG streaming
synchronization of EEG signals with markers
Feature Extraction
FFT-based spectral features
bandpower in mu, alpha, beta ranges
time-frequency analysis methods
Classification Pipeline
SVM classifier implementation
optional hierarchical classification structure
Data Quality Improvements
timing jitter for anti-overfitting
explicit inter-trial markers
artifact detection and rejection
REST State Redesign
separation of true baseline rest vs task-related rest
improved physiological consistency in labeling
Summary

This project provides a structured experimental framework for EEG-based motor decoding research using Muse 2.

It is designed to produce synchronized, time-stamped behavioral markers that can later be aligned with EEG signals for machine learning analysis.

While EEG integration is not yet implemented, the system provides a stable experimental backbone for building motor imagery and motor execution classification datasets.
