"""Compute instance-area statistics from LabelMe polygon annotations.

This script reports absolute polygon areas, relative areas, COCO-style scale
statistics, percentiles, and area histograms for the DARS label set.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Iterable

import cv2
import numpy as np
import pandas as pd


DEFAULT_CLASSES = [
    "accident_car",
    "accident_truck",
    "accident_bus",
    "normal_car",
    "normal_truck",
    "normal_bus",
]

AREA_BINS = [
    (0, 500),
    (500, 1000),
    (1000, 2000),
    (2000, 4000),
    (4000, 8000),
    (8000, 16000),
    (16000, np.inf),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute polygon-area statistics from LabelMe JSON files."
    )
    parser.add_argument(
        "--labels",
        type=Path,
        required=True,
        help="Directory containing LabelMe JSON annotations.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("statistics_output"),
        help="Directory for generated CSV files (default: statistics_output).",
    )
    parser.add_argument(
        "--classes",
        nargs="+",
        default=DEFAULT_CLASSES,
        help="Class names to include. Defaults to the six DARS classes.",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Search for JSON files recursively below --labels.",
    )
    return parser.parse_args()


def iter_json_files(labels_dir: Path, recursive: bool) -> Iterable[Path]:
    pattern = "**/*.json" if recursive else "*.json"
    yield from sorted(labels_dir.glob(pattern))


def summarize(values: np.ndarray) -> dict[str, float]:
    return {
        "min": float(values.min()),
        "max": float(values.max()),
        "mean": float(values.mean()),
        "median": float(np.median(values)),
        "p25": float(np.percentile(values, 25)),
        "p50": float(np.percentile(values, 50)),
        "p75": float(np.percentile(values, 75)),
        "p90": float(np.percentile(values, 90)),
        "p95": float(np.percentile(values, 95)),
    }


def main() -> None:
    args = parse_args()
    labels_dir = args.labels.expanduser().resolve()
    output_dir = args.output.expanduser().resolve()
    include_classes = set(args.classes)

    if not labels_dir.is_dir():
        raise FileNotFoundError(f"Label directory does not exist: {labels_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    records: list[dict[str, object]] = []
    areas: list[float] = []
    relative_areas: list[float] = []
    class_counter: Counter[str] = Counter()
    hist_counter: Counter[str] = Counter()

    small = 0
    medium = 0
    large = 0
    skipped_files = 0
    skipped_instances = 0

    json_files = list(iter_json_files(labels_dir, args.recursive))
    if not json_files:
        raise RuntimeError(f"No LabelMe JSON files found in: {labels_dir}")

    for json_path in json_files:
        try:
            with json_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[WARNING] Skipping unreadable JSON file {json_path}: {exc}")
            skipped_files += 1
            continue

        img_h = data.get("imageHeight")
        img_w = data.get("imageWidth")
        if not img_h or not img_w:
            print(f"[WARNING] Missing image dimensions in {json_path}; file skipped.")
            skipped_files += 1
            continue

        image_area = float(img_h) * float(img_w)

        for shape in data.get("shapes", []):
            label = str(shape.get("label", "")).strip()
            if label not in include_classes:
                continue

            points = shape.get("points", [])
            if len(points) < 3:
                skipped_instances += 1
                continue

            pts = np.asarray(points, dtype=np.float32)
            if pts.ndim != 2 or pts.shape[1] != 2:
                skipped_instances += 1
                continue

            area = float(cv2.contourArea(pts))
            if area <= 0:
                skipped_instances += 1
                continue

            relative_area = area / image_area

            records.append(
                {
                    "file": json_path.name,
                    "label": label,
                    "area_px2": area,
                    "relative_area": relative_area,
                }
            )
            areas.append(area)
            relative_areas.append(relative_area)
            class_counter[label] += 1

            # COCO-style area thresholds: 32^2 and 96^2 pixels.
            if area < 32**2:
                small += 1
            elif area < 96**2:
                medium += 1
            else:
                large += 1

            for low, high in AREA_BINS:
                if low <= area < high:
                    key = f">={int(low)}" if high == np.inf else f"{int(low)}-{int(high)}"
                    hist_counter[key] += 1
                    break

    if not areas:
        raise RuntimeError("No valid polygon instances were found for the selected classes.")

    areas_np = np.asarray(areas, dtype=np.float64)
    relative_np = np.asarray(relative_areas, dtype=np.float64)
    total = len(areas_np)

    area_summary = summarize(areas_np)
    relative_summary = summarize(relative_np)

    print("\n=== Scale Distribution ===")
    print(f"Total instances: {total}")
    print(f"Small : {small} ({small / total * 100:.2f}%)")
    print(f"Medium: {medium} ({medium / total * 100:.2f}%)")
    print(f"Large : {large} ({large / total * 100:.2f}%)")

    print("\n=== Absolute Area Statistics (pixels^2) ===")
    for key, value in area_summary.items():
        print(f"{key.upper():>6}: {value:.2f}")

    print("\n=== Relative Area Statistics ===")
    for key, value in relative_summary.items():
        print(f"{key.upper():>6}: {value * 100:.4f}%")

    print("\n=== Class Counts ===")
    for class_name in args.classes:
        print(f"{class_name}: {class_counter[class_name]}")

    if skipped_files:
        print(f"\n[WARNING] Skipped files: {skipped_files}")
    if skipped_instances:
        print(f"[WARNING] Skipped invalid instances: {skipped_instances}")

    instance_csv = output_dir / "instance_statistics.csv"
    pd.DataFrame(records).to_csv(instance_csv, index=False, encoding="utf-8")

    histogram_rows = [
        {"area_range_px2": key, "count": hist_counter.get(key, 0)}
        for key in [
            "0-500",
            "500-1000",
            "1000-2000",
            "2000-4000",
            "4000-8000",
            "8000-16000",
            ">=16000",
        ]
    ]
    histogram_csv = output_dir / "area_histogram.csv"
    pd.DataFrame(histogram_rows).to_csv(histogram_csv, index=False, encoding="utf-8")

    summary_rows = [
        {"metric": "total_instances", "value": total},
        {"metric": "small_instances", "value": small},
        {"metric": "medium_instances", "value": medium},
        {"metric": "large_instances", "value": large},
    ]
    summary_rows.extend(
        {"metric": f"area_{key}", "value": value} for key, value in area_summary.items()
    )
    summary_rows.extend(
        {"metric": f"relative_area_{key}", "value": value}
        for key, value in relative_summary.items()
    )
    summary_csv = output_dir / "summary_statistics.csv"
    pd.DataFrame(summary_rows).to_csv(summary_csv, index=False, encoding="utf-8")

    class_csv = output_dir / "class_counts.csv"
    pd.DataFrame(
        [{"class": name, "count": class_counter[name]} for name in args.classes]
    ).to_csv(class_csv, index=False, encoding="utf-8")

    print("\nSaved:")
    print(f"  {instance_csv}")
    print(f"  {histogram_csv}")
    print(f"  {summary_csv}")
    print(f"  {class_csv}")


if __name__ == "__main__":
    main()