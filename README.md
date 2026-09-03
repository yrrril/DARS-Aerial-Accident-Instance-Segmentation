# DARS: Drone-oriented Accident Recognition and Segmentation Dataset

DARS is an aerial-view road traffic accident instance segmentation dataset developed for fine-grained vehicle perception in accident scenes.

The complete DARS dataset contains **7,603 images** and **49,613 annotated vehicle instances**. Each vehicle instance is jointly labeled according to its vehicle type and accident-involved status, resulting in six categories:

- `accident_car`
- `accident_truck`
- `accident_bus`
- `normal_car`
- `normal_truck`
- `normal_bus`

DARS is designed to support instance-level perception in aerial-view traffic accident scenes, particularly the joint recognition and segmentation of accident-involved and non-accident-involved vehicles.

---

## 1. Dataset Overview

Existing traffic accident datasets mainly focus on event-level accident detection, temporal localization, or object-level localization. DARS is constructed to support finer-grained visual perception by providing vehicle instance masks together with accident-involvement labels.

The dataset contains real-world aerial-view accident scenes with diverse accident configurations, vehicle scales, viewpoints, and environmental conditions.

The complete dataset is used in our associated study for model training and evaluation. Due to copyright and redistribution restrictions associated with part of the source material, however, the complete image dataset cannot be publicly redistributed.

---

## 2. Dataset Categories

DARS contains six instance categories jointly defined by vehicle type and accident-involvement status.

| Category | Number of Instances |
| --- | ---: |
| `accident_car` | 10,259 |
| `accident_truck` | 1,553 |
| `accident_bus` | 914 |
| `normal_car` | 32,932 |
| `normal_truck` | 3,041 |
| `normal_bus` | 914 |
| **Total** | **49,613** |


---

## 3. Dataset Construction

The construction of DARS includes the following main stages:

1. image collection;
2. data screening;
3. duplicate and near-duplicate checking;
4. accident-event grouping;
5. manual instance annotation;
6. annotation review;
7. event-level dataset splitting;
8. annotation format conversion and statistical processing.

The corresponding screening, annotation, and splitting principles are documented in this repository.

---

## 4. Event-Level Dataset Split

The split is performed at the **accident-event level rather than the individual-image level**.

Images or extracted video frames identified as belonging to the same accident event are assigned exclusively to one subset to reduce event-level data leakage.

The complete dataset contains:

| Subset | Number of Accident Events |
| --- | ---: |
| Training | 520 |
| Validation | 169 |
| Test | 81 |
| **Total** | **770** |

Accident-event grouping is primarily determined according to scene content, including:

- vehicle configuration;
- collision geometry;
- road layout;
- background structures;
- viewpoint;
- distinctive scene details.

Exact duplicate images and visually redundant near-duplicates are removed during data screening.

When different images contain complementary visual information from the same accident event, they may be retained, but all such images are assigned to the same event group.

Samples identified as representing the same accident event are grouped together regardless of the platform or source through which they were encountered.

Detailed rules are provided in:

`docs/event_split_protocol.md`

The repository also provides the code used to implement the event-level dataset splitting procedure.

**The train/validation/test file lists of the curated data subset are not publicly distributed.**

---

## 5. Annotation

Vehicle instances are manually annotated using polygon masks.

Each annotated vehicle is assigned one of six labels according to:

### Vehicle type

- car
- truck
- bus

### Accident-involvement status

- accident-involved
- non-accident-involved

The original annotations are generated in a LabelMe-compatible polygon format and can be converted into formats required by different instance segmentation frameworks using the scripts provided in this repository.

The annotation guidelines include rules for:

- annotation of fully and partially visible vehicles;
- treatment of partially and heavily occluded vehicles;
- handling of discontinuous visible regions caused by occlusion;
- exclusion of detached vehicle parts and accident debris;
- determination of accident-involvement status;
- assignment of vehicle-type labels.

Detailed annotation rules are provided in:

`docs/annotation_guidelines.md`

---

## 6. Data Screening

Images are manually screened before annotation.

The screening procedure considers:

- relevance to road traffic accident scenes;
- visibility of target vehicles;
- suitability for instance-level annotation;
- image quality;
- duplication and near-duplication;
- accident-event identity;
- scene redundancy.

Exact duplicates and visually redundant near-duplicates are removed.

For samples originating from videos, selected frames are stored and processed as still images. Frames originating from the same accident event remain within the same event group during dataset splitting.

Detailed screening criteria are provided in:

`docs/screening_criteria.md`

---

## 7. Naming Convention

To support consistent organization and processing, DARS images and annotations follow a unified naming convention.

The repository provides documentation describing:

- image naming rules;
- annotation filename correspondence;
- unique sample identifiers;
- event identifiers;
- image–annotation matching rules.

See:

`docs/naming_convention.md`

The naming convention is provided to support dataset organization and processing and does not reveal restricted source information.

---

## 8. Data Availability

Due to copyright, licensing, and redistribution restrictions associated with part of the source material, the **complete DARS image dataset cannot be publicly released**.

A **curated subset of DARS**, containing images and corresponding annotations for which research sharing is permitted, is available to researchers **upon reasonable request for non-commercial academic research**.

The curated subset is **not directly distributed through this GitHub repository**.

Images subject to redistribution restrictions, including relevant purchased materials and other materials whose permissions do not allow redistribution, are excluded from the available subset.

The copyright of third-party source images remains with the respective rights holders.

To support methodological reproducibility without redistributing restricted source materials, this repository provides:

- dataset naming conventions;
- data screening criteria;
- event-level dataset splitting principles;
- annotation guidelines;
- dataset splitting code;
- annotation format conversion code;
- dataset processing scripts;
- dataset statistical analysis scripts.

---

## 9. Data Access

Researchers interested in obtaining the curated DARS subset may submit a request for access.

The request should include:

- applicant name;
- institutional affiliation;
- contact information;
- research purpose;
- brief description of the intended use of the dataset.

The curated subset is provided only for **non-commercial academic research** and is subject to the applicable data-use conditions.

To request access, please contact:

xfliu@tute.edu.cn

Please use a clear email subject such as:

`DARS Dataset Access Request`

---

## 10. Repository Contents

The repository is organized as follows:

```text
DARS/
│
├── README.md
│
├── docs/
│   ├── naming_convention.md
│   ├── screening_criteria.md
│   ├── event_split_protocol.md
│   ├── annotation_guidelines.md
│   └── data_access.md
│
└── scripts/
    ├── dataset_statistics.py
    ├── event_level_split.py
    └── labelme2yolo.py
