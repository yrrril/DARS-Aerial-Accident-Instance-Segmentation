"""Convert LabelMe polygon annotations to YOLO segmentation labels."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


DEFAULT_CLASSES = [
    "accident_car",
    "accident_truck",
    "accident_bus",
    "normal_car",
    "normal_truck",
    "normal_bus",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert LabelMe polygon JSON files to YOLO segmentation TXT files."
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Directory containing LabelMe JSON files.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Directory in which YOLO TXT labels will be written.",
    )
    parser.add_argument(
        "--classes",
        nargs="+",
        default=DEFAULT_CLASSES,
        help="Class names in YOLO class-ID order. Defaults to the six DARS classes.",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Search for JSON files recursively and preserve subdirectory structure.",
    )
    return parser.parse_args()


def normalize_coordinate(value: float, size: float) -> float:
    return max(0.0, min(1.0, value / size))


def convert_file(json_path: Path, txt_path: Path, class_names: list[str]) -> bool:
    try:
        with json_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[ERROR] Failed to read {json_path}: {exc}")
        return False

    image_width = data.get("imageWidth")
    image_height = data.get("imageHeight")
    if not image_width or not image_height:
        print(f"[WARNING] Missing image dimensions in {json_path}; file skipped.")
        return False

    yolo_lines: list[str] = []

    for shape in data.get("shapes", []):
        label = str(shape.get("label", "")).strip()
        if label not in class_names:
            continue

        points = shape.get("points", [])
        if len(points) < 3:
            continue

        class_id = class_names.index(label)
        normalized_points: list[str] = []

        valid_polygon = True
        for point in points:
            if not isinstance(point, (list, tuple)) or len(point) < 2:
                valid_polygon = False
                break
            x, y = float(point[0]), float(point[1])
            normalized_points.append(f"{normalize_coordinate(x, image_width):.6f}")
            normalized_points.append(f"{normalize_coordinate(y, image_height):.6f}")

        if not valid_polygon:
            continue

        yolo_lines.append(f"{class_id} " + " ".join(normalized_points))

    txt_path.parent.mkdir(parents=True, exist_ok=True)
    txt_path.write_text("\n".join(yolo_lines), encoding="utf-8")
    return True


def main() -> None:
    args = parse_args()
    input_dir = args.input.expanduser().resolve()
    output_dir = args.output.expanduser().resolve()

    if not input_dir.is_dir():
        raise FileNotFoundError(f"Input directory does not exist: {input_dir}")

    pattern = "**/*.json" if args.recursive else "*.json"
    json_files = sorted(input_dir.glob(pattern))
    if not json_files:
        raise RuntimeError(f"No LabelMe JSON files found in: {input_dir}")

    success_count = 0
    for json_path in json_files:
        relative_path = json_path.relative_to(input_dir)
        txt_path = (output_dir / relative_path).with_suffix(".txt")
        if convert_file(json_path, txt_path, args.classes):
            success_count += 1

    print(f"Converted {success_count}/{len(json_files)} annotation files.")
    print(f"Output directory: {output_dir}")
    print("\nYOLO class mapping:")
    for class_id, class_name in enumerate(args.classes):
        print(f"  {class_id}: {class_name}")


if __name__ == "__main__":
    main()
