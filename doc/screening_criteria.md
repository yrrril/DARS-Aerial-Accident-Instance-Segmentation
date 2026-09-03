# DARS Data Screening Criteria

This document summarizes the main screening criteria used during construction of DARS.

## 1. Scene Relevance

Candidate images were reviewed for their relevance to road traffic accident scenes or non-accident traffic scenes used as negative samples.

Images were retained only when the scene content was suitable for vehicle-level visual analysis.

## 2. Image Quality

Images were excluded when severe image degradation prevented reliable vehicle interpretation or annotation.

Typical exclusion conditions included:

- severe blur;
- insufficient visible vehicle information;
- unsuitable viewpoints;
- image quality that prevented reliable instance annotation.

## 3. Duplicate and Redundancy Screening

Exact duplicate images were removed.

Visually redundant near-duplicate samples were also removed when they did not provide meaningful additional scene information.

When multiple images from the same accident event contained complementary visual information, they could be retained, but they were assigned to the same event group.

## 4. Event Grouping

Images identified as originating from the same accident event were grouped before dataset splitting.

Event identity was assessed primarily from scene content, including:

- vehicle configuration;
- collision geometry;
- road layout;
- background structures;
- viewpoint;
- distinctive scene details.

Images identified as representing the same event were grouped together regardless of the platform or source through which they were encountered.

For source videos, representative frames were extracted and stored as individual images before screening and annotation. Frames from the same accident event remained within the same event group.

## 5. Annotation Suitability

Images were excluded when target vehicles could not be reliably identified or when the visible information was insufficient for meaningful instance-level annotation.

The detailed rules used during annotation are provided in `annotation_guidelines.md`.

## 6. Privacy Protection

Where necessary, visible license plates, facial features, and other privacy-sensitive information were manually blurred before the retained images were used for annotation and model development.
