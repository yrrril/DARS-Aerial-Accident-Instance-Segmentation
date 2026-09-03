"""Create an event-level train/validation/test split for DARS-style data.

The script assumes the default naming convention ``<event_id>_<sample_id>``.
All samples from the same event are assigned to exactly one subset. A random
search is used to find a split that approximately matches both the requested
image ratios and the per-class instance ratios.
"""

from __future__ import annotations

import argparse
import json
import random
import shutil
from collections import defaultdict
from pathlib import Path


DEFAULT_CLASSES = [
    "accident_car",
    "accident_truck",
    "accident_bus",
    "normal_car",
    "normal_truck",
    "normal_bus",
]

IMAGE_SUFFIXES = (".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Split LabelMe data by accident event with approximate class balance."
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Directory containing source images and LabelMe JSON files.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("split_output"),
        help="Output directory used when --copy is enabled (default: split_output).",
    )
    parser.add_argument(
        "--ratios",
        nargs=3,
        type=float,
        metavar=("TRAIN", "VAL", "TEST"),
        default=(0.7, 0.2, 0.1),
        help="Train/validation/test ratios (default: 0.7 0.2 0.1).",
    )
    parser.add_argument(
        "--classes",
        nargs="+",
        default=DEFAULT_CLASSES,
        help="Class names used when evaluating split balance.",
    )
    parser.add_argument(
        "--separator",
        default="_",
        help="Separator between event ID and sample ID in file names (default: _).",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=5000,
        help="Number of randomized candidate splits to evaluate (default: 5000).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed (default: 42).",
    )
    parser.add_argument(
        "--copy",
        action="store_true",
        help="Copy images and JSON files into train/val/test directories.",
    )
    return parser.parse_args()


def normalize_ratios(ratios: tuple[float, float, float]) -> tuple[float, float, float]:
    if any(r <= 0 for r in ratios):
        raise ValueError("All split ratios must be positive.")
    total = sum(ratios)
    return tuple(r / total for r in ratios)  # type: ignore[return-value]


def extract_event_id(stem: str, separator: str) -> str:
    """Extract event ID from ``<event_id><separator><sample_id>``."""
    if separator not in stem:
        return stem
    event_id, _ = stem.rsplit(separator, 1)
    return event_id or stem


def find_image(json_path: Path) -> Path | None:
    for suffix in IMAGE_SUFFIXES:
        candidate = json_path.with_suffix(suffix)
        if candidate.is_file():
            return candidate
    return None


def build_event_index(
    input_dir: Path,
    class_names: list[str],
    separator: str,
) -> tuple[dict[str, list[Path]], dict[str, dict[str, object]], dict[str, int]]:
    event_to_jsons: dict[str, list[Path]] = defaultdict(list)
    class_totals = {name: 0 for name in class_names}

    json_files = sorted(input_dir.glob("*.json"))
    if not json_files:
        raise RuntimeError(f"No LabelMe JSON files found in: {input_dir}")

    for json_path in json_files:
        event_id = extract_event_id(json_path.stem, separator)
        event_to_jsons[event_id].append(json_path)

    event_stats: dict[str, dict[str, object]] = {}
    for event_id, files in event_to_jsons.items():
        counts = {name: 0 for name in class_names}
        for json_path in files:
            try:
                with json_path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
            except (OSError, json.JSONDecodeError) as exc:
                raise RuntimeError(f"Failed to read {json_path}: {exc}") from exc

            for shape in data.get("shapes", []):
                label = str(shape.get("label", "")).strip()
                if label in counts:
                    counts[label] += 1
                    class_totals[label] += 1

        event_stats[event_id] = {
            "image_count": len(files),
            "class_counts": counts,
        }

    return dict(event_to_jsons), event_stats, class_totals


def make_candidate_split(
    events: list[str],
    event_stats: dict[str, dict[str, object]],
    ratios: tuple[float, float, float],
    rng: random.Random,
) -> dict[str, list[str]]:
    shuffled = events.copy()
    rng.shuffle(shuffled)

    total_images = sum(int(event_stats[e]["image_count"]) for e in shuffled)
    targets = {
        "train": total_images * ratios[0],
        "val": total_images * ratios[1],
        "test": total_images * ratios[2],
    }
    subsets = {"train": [], "val": [], "test": []}
    counts = {"train": 0, "val": 0, "test": 0}

    for event_id in shuffled:
        event_images = int(event_stats[event_id]["image_count"])

        # Assign the event to the subset with the largest normalized image deficit.
        deficits = {
            name: (targets[name] - counts[name]) / max(targets[name], 1.0)
            for name in subsets
        }
        subset = max(deficits, key=deficits.get)
        subsets[subset].append(event_id)
        counts[subset] += event_images

    return subsets


def score_split(
    split: dict[str, list[str]],
    event_stats: dict[str, dict[str, object]],
    class_totals: dict[str, int],
    class_names: list[str],
    ratios: tuple[float, float, float],
) -> float:
    subset_names = ("train", "val", "test")
    ratio_map = dict(zip(subset_names, ratios))

    total_images = sum(int(v["image_count"]) for v in event_stats.values())
    image_error = 0.0
    class_error = 0.0

    for subset in subset_names:
        events = split[subset]
        image_count = sum(int(event_stats[e]["image_count"]) for e in events)
        image_error += abs(image_count / total_images - ratio_map[subset])

        for class_name in class_names:
            total_class = class_totals[class_name]
            if total_class == 0:
                continue
            subset_class = sum(
                int(event_stats[e]["class_counts"][class_name])  # type: ignore[index]
                for e in events
            )
            class_error += abs(subset_class / total_class - ratio_map[subset])

    # Image-ratio agreement is given slightly more weight.
    return 5.0 * image_error + class_error


def search_best_split(
    event_stats: dict[str, dict[str, object]],
    class_totals: dict[str, int],
    class_names: list[str],
    ratios: tuple[float, float, float],
    iterations: int,
    seed: int,
) -> tuple[dict[str, list[str]], float]:
    events = list(event_stats)
    if len(events) < 3:
        raise RuntimeError("At least three events are required for a train/val/test split.")

    rng = random.Random(seed)
    best_split: dict[str, list[str]] | None = None
    best_score = float("inf")

    for _ in range(iterations):
        candidate = make_candidate_split(events, event_stats, ratios, rng)
        if any(len(candidate[name]) == 0 for name in ("train", "val", "test")):
            continue
        score = score_split(candidate, event_stats, class_totals, class_names, ratios)
        if score < best_score:
            best_split = {name: events.copy() for name, events in candidate.items()}
            best_score = score

    if best_split is None:
        raise RuntimeError("Failed to generate a valid three-way event split.")

    return best_split, best_score


def print_summary(
    split: dict[str, list[str]],
    event_stats: dict[str, dict[str, object]],
    class_totals: dict[str, int],
    class_names: list[str],
) -> None:
    total_images = sum(int(v["image_count"]) for v in event_stats.values())
    total_events = len(event_stats)

    print("\n=== Event-Level Split Summary ===")
    print(f"Total events: {total_events}")
    print(f"Total images: {total_images}")

    for subset in ("train", "val", "test"):
        events = split[subset]
        image_count = sum(int(event_stats[e]["image_count"]) for e in events)
        print(
            f"\n{subset.upper()}: {len(events)} events, "
            f"{image_count} images ({image_count / total_images:.2%})"
        )
        for class_name in class_names:
            total_class = class_totals[class_name]
            subset_class = sum(
                int(event_stats[e]["class_counts"][class_name])  # type: ignore[index]
                for e in events
            )
            ratio = subset_class / total_class if total_class else 0.0
            print(f"  {class_name}: {subset_class} ({ratio:.2%} of all {class_name})")


def copy_split(
    split: dict[str, list[str]],
    event_to_jsons: dict[str, list[Path]],
    output_dir: Path,
) -> None:
    for subset in ("train", "val", "test"):
        subset_dir = output_dir / subset
        subset_dir.mkdir(parents=True, exist_ok=True)

        for event_id in split[subset]:
            for json_path in event_to_jsons[event_id]:
                shutil.copy2(json_path, subset_dir / json_path.name)
                image_path = find_image(json_path)
                if image_path is None:
                    print(f"[WARNING] No matching image found for {json_path.name}")
                    continue
                shutil.copy2(image_path, subset_dir / image_path.name)


def main() -> None:
    args = parse_args()
    input_dir = args.input.expanduser().resolve()
    output_dir = args.output.expanduser().resolve()
    ratios = normalize_ratios(tuple(args.ratios))

    if not input_dir.is_dir():
        raise FileNotFoundError(f"Input directory does not exist: {input_dir}")
    if args.iterations <= 0:
        raise ValueError("--iterations must be greater than zero.")

    event_to_jsons, event_stats, class_totals = build_event_index(
        input_dir=input_dir,
        class_names=args.classes,
        separator=args.separator,
    )

    best_split, best_score = search_best_split(
        event_stats=event_stats,
        class_totals=class_totals,
        class_names=args.classes,
        ratios=ratios,
        iterations=args.iterations,
        seed=args.seed,
    )

    print_summary(best_split, event_stats, class_totals, args.classes)
    print(f"\nBalance score: {best_score:.6f}")
    print(
        "The assignment is deterministic for a fixed input directory, naming convention, "
        "iteration count, and random seed."
    )

    if args.copy:
        copy_split(best_split, event_to_jsons, output_dir)
        print(f"\nCopied split files to: {output_dir}")
    else:
        print("\nDry run only. Use --copy to create train/val/test directories.")


if __name__ == "__main__":
    main()
