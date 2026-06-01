#!/bin/bash
# ─────────────────────────────────────────────────────────────────
# setup_repo.sh
# Run this from the root of your cloned GitHub repository.
# It creates the folder structure and renames all files.
# Place all your original files in the same directory first,
# then run: bash setup_repo.sh
# ─────────────────────────────────────────────────────────────────

echo "Creating folder structure..."

mkdir -p 00_dataset
mkdir -p 01_data_prep/matlab
mkdir -p 02_methods/matlab
mkdir -p 02_methods/python
mkdir -p 03_notes

echo "Moving dataset metadata files..."
mv README                        00_dataset/README.md
mv CHANGES                       00_dataset/CHANGES.md
mv dataset_description.json      00_dataset/dataset_description.json
mv participants.tsv               00_dataset/participants.tsv
mv participants.json              00_dataset/participants.json
mv task-motion_events.json        00_dataset/task-motion_events.json

echo "Moving and renaming data prep files..."
mv segments.m                    01_data_prep/matlab/01_segment_single_file.m
mv Segment_Folder.m              01_data_prep/matlab/02_segment_one_folder.m
mv Segment_all_folders.m         01_data_prep/matlab/03_segment_all_subjects.m
mv Separation_Counts.m           01_data_prep/matlab/04_verify_category_counts.m
mv Sorting_Success.m             01_data_prep/matlab/05_sort_into_class_folders.m
mv convert_to_edf.m              01_data_prep/matlab/06_convert_set_to_edf.m
mv images.m                      01_data_prep/matlab/07_generate_scroll_plots.m

echo "Moving and renaming methods files — MATLAB..."
mv frequency.m                   02_methods/matlab/01_time_domain_exploration.m
mv filter_and_max_amplitude.m    02_methods/matlab/02_fft_peak_frequency.m
mv simplify.m                    02_methods/matlab/03_normalized_amplitude_spectra.m
mv multiple_plots.m              02_methods/matlab/04_sliding_window_frequency.m
mv filter_and_smooth_all.m       02_methods/matlab/05_batch_image_export_3plots.m
mv test.m                        02_methods/matlab/06_seven_plot_single_file.m
mv test2.m                       02_methods/matlab/07_batch_image_export_7plots.m
mv test3.m                       02_methods/matlab/08_extract_avg_fft_features.m

echo "Moving and renaming methods files — Python..."
mv filter.py                     02_methods/python/01_artifact_detection.py
mv EEG_GUI.py                    02_methods/python/02_edf_viewer_gui.py
mv p2.py                         02_methods/python/03_channel_position_mapper.py
mv positions.csv                 02_methods/python/03_channel_positions.csv
mv 64_channel_sharbrough.pdf     02_methods/python/03_64_channel_reference.pdf
mv p.py                          02_methods/python/04_psd_comparison.py
mv p3.py                         02_methods/python/05_topomap_prototype.py
mv p4.py                         02_methods/python/06_topomap_frequency_bands.py
mv test.py                       02_methods/python/07_pattern_match_validation.py
mv Screenshot_2025-10-09_at_3_00_11_PM.png  02_methods/python/07_pattern_match_output.png

echo "Moving notes..."
mv Current_Phase.docx            03_notes/current_phase_notes.docx

echo ""
echo "Done. Your repository structure:"
find . -not -path './.git/*' -not -name 'setup_repo.sh' | sort
