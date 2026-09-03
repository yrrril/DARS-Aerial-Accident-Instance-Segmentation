# DARS: Drone-oriented Accident Recognition and Segmentation Dataset

DARS is an aerial-view road traffic accident instance segmentation dataset developed for fine-grained vehicle perception in accident scenes.

The complete DARS dataset contains **7,603 images** and **49,613 annotated vehicle instances**. Each vehicle instance is jointly labeled according to vehicle type and accident-involvement status, resulting in six categories:

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

The complete dataset contains real-world aerial-view accident scenes with diverse accident configurations, vehicle scales, viewpoints, and environmental conditions.

Due to copyright, licensing, and redistribution restrictions associated with part of the source material, the complete DARS image dataset cannot be publicly redistributed.

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

Accident-involved vehicles account for approximately **25.7%** of all annotated instances, while non-accident-involved vehicles account for approximately **74.3%**.

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

The current repository provides documentation for the naming convention, data screening criteria, and event-level splitting procedure.

---

## 4. Naming Convention

Each image and its corresponding annotation file use the same base name.

The default naming pattern is:

```text
<event_id>_<sample_id>
```

Images originating from the same accident event share the same `<event_id>` and are kept in the same dataset subset during splitting.

More details are provided in:

[`docs/naming_convention.md`](docs/naming_convention.md)

---

## 5. Data Screening

All collected images are manually screened before annotation.

The screening procedure considers:

- relevance to road traffic accident scenes;
- visibility of target vehicles;
- suitability for instance-level annotation;
- image quality;
- duplicate and near-duplicate removal;
- accident-event identity;
- scene redundancy.

Exact duplicate images and visually redundant near-duplicate samples are removed. When multiple images from the same accident event contain complementary visual information, they may be retained but are assigned to the same event group.

For video-based source materials, representative frames are extracted and stored as individual images before screening and annotation.

More details are provided in:

[`docs/screening_criteria.md`](docs/screening_criteria.md)

---

## 6. Event-Level Dataset Split

The complete DARS dataset is divided into training, validation, and test sets using an approximate **7:2:1** ratio.

The split is performed at the **accident-event level rather than the individual-image level**. Images or extracted video frames identified as belonging to the same accident event are assigned exclusively to one subset to reduce event-level information leakage.

The final event-level split contains:

| Subset | Number of Accident Events |
| --- | ---: |
| Training | 520 |
| Validation | 169 |
| Test | 81 |
| **Total** | **770** |

Event grouping is primarily determined according to scene content, including:

- vehicle configuration;
- collision geometry;
- road layout;
- background structures;
- viewpoint;
- distinctive scene details.

The distributions of the six instance classes are also considered during splitting to avoid substantial differences among the three subsets.

More details are provided in:

[`docs/event_split_protocol.md`](docs/event_split_protocol.md)

The public repository does **not** distribute the train/validation/test file lists of the curated DARS subset.

---

## 7. Annotation

Vehicle instances are manually annotated using LabelMe-compatible polygon masks.

Each annotated vehicle is assigned one of six labels according to:

- vehicle type: car, truck, or bus;
- accident-involvement status: accident-involved or non-accident-involved.

Polygon masks are drawn closely along visible vehicle boundaries. Shadows and detached vehicle components are excluded. Vehicles that are almost fully occluded or cannot be reliably identified are not annotated.

The original LabelMe annotations can be converted to YOLO segmentation format using the script provided in this repository.

---

## 8. Data Availability

Due to copyright, licensing, and redistribution restrictions associated with part of the source material, the **complete DARS image dataset cannot be publicly released**.

A **curated subset of DARS**, containing images and corresponding annotations that are permitted to be shared for academic research, will be made available **upon reasonable request and with permission for non-commercial academic research**.

The curated subset is **not directly distributed through this GitHub repository**.

Materials subject to redistribution restrictions, including relevant purchased or individually authorized source images, are excluded from the available subset. Copyright of third-party source images remains with the respective rights holders.

Researchers interested in accessing the curated subset may contact:

**Xuyang Zhai**  
Email: zhaixuyang@tute.edu.cn

**Xiaofeng Liu**  
Email: xfliu@tute.edu.cn

Suggested email subject:

```text
DARS Dataset Access Request
```

---

## 9. Repository Contents

The current repository is organized as follows:

```text
DARS/
├── README.md
├── docs/
│   ├── naming_convention.md
│   ├── screening_criteria.md
│   └── event_split_protocol.md
└── scripts/
    ├── event_level_split.py
    ├── labelme_to_yolo.py
    └── dataset_statistics.py
```

### Documentation

- [`naming_convention.md`](docs/naming_convention.md): naming and correspondence rules for images, annotations, and event identifiers.
- [`screening_criteria.md`](docs/screening_criteria.md): data screening, duplicate-removal, and event-grouping criteria.
- [`event_split_protocol.md`](docs/event_split_protocol.md): event-level grouping and train/validation/test splitting procedure.

### Scripts

- [`event_level_split.py`](scripts/event_level_split.py): performs event-level train/validation/test splitting while considering image ratios and class distributions.
- [`labelme_to_yolo.py`](scripts/labelme_to_yolo.py): converts LabelMe polygon annotations into YOLO segmentation labels.
- [`dataset_statistics.py`](scripts/dataset_statistics.py): calculates instance-level area and relative-area statistics from LabelMe polygon annotations.

---

## 10. Citation

If you use DARS or the materials provided in this repository in your research, please cite the associated paper:

```bibtex
@article{zhai2026dars,
  title   = {Frequency-Guided Feature Representation for Instance Segmentation in Aerial-View Traffic Accident Scenes},
  author  = {Zhai, Xuyang and Liu, Xiaofeng and Cao, Weiwei and Liu, Junli},
  journal = {Sustainability},
  year    = {2026}
}
```

The citation information will be updated after publication.

---

## 11. Copyright and Use

The source images included in DARS originate from multiple permitted research sources and may be subject to different copyright or licensing conditions.

Only materials that can be shared for academic research are included in the curated subset available upon request.

Materials for which redistribution is not permitted are not provided.

The curated subset and the materials in this repository are intended for **non-commercial academic research**. Users are responsible for complying with the applicable copyright, licensing, and data-use conditions.

---

## 12. Contact

For questions about DARS, the repository, or data access, please contact:

**Xuyang Zhai**  
Email: zhaixuyang@tute.edu.cn

**Xiaofeng Liu**  
Email: xfliu@tute.edu.cn
