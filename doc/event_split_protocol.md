DARS Event-Level Dataset Splitting Protocol

This document describes the event-level splitting strategy used for DARS.

1. Motivation

Images from the same traffic accident event may contain highly similar scene content.

Random image-level splitting could therefore place closely related samples from the same event into different subsets and introduce event-level information leakage.

To reduce this risk, DARS is split at the accident-event level.

2. Event Grouping

All images belonging to the same identified accident event are treated as one indivisible event group.

Event grouping is determined primarily from scene content, including:

vehicle configuration;
collision geometry;
road layout;
background structures;
viewpoint;
distinctive scene details.

Images or extracted video frames belonging to the same event are assigned the same event identifier.

3. Split Ratio

The complete DARS dataset uses an approximate train/validation/test ratio of:

7 : 2 : 1

The final split contains:

Subset

Accident Events

Training

520

Validation

169

Test

81

Total

770

Because each event is treated as an indivisible group, the final image-level ratios may not be exactly equal to the target ratio.

4. Class-Distribution Check

In addition to the target image ratio, the distributions of the six DARS instance classes are considered during splitting:

accident_car

accident_truck

accident_bus

normal_car

normal_truck

normal_bus

The goal is to avoid substantial distribution differences among the training, validation, and test subsets while preserving event-level separation.

5. Public Splitting Script

The repository provides:

scripts/event_level_split.py

The script assumes the default file-name pattern:

<event_id>_<sample_id>

and assigns all samples sharing the same event identifier to the same subset.

Example usage:

python scripts/event_level_split.py \
    --input path/to/labelme_data \
    --ratios 0.7 0.2 0.1 \
    --iterations 5000 \
    --seed 42

To physically copy the selected images and LabelMe JSON files into train, validation, and test folders, add:

--copy

A different file-name separator can be specified with:

--separator

6. Reproducibility Note

The public script reproduces the event-level splitting procedure and balance criteria used for DARS-style data organization.

The public repository does not distribute the train/validation/test file lists of the curated DARS subset.
