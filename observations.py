"""Write only real, user-confirmed experiment measurements to a CSV file."""
import csv
from datetime import datetime
from pathlib import Path

LOG_PATH = Path(__file__).resolve().parent / "logs" / "dev_observations.csv"
FIELDS = [
    "timestamp", "source", "lighting", "expected_label", "predicted_label",
    "score", "action", "correct", "inference_ms", "input_mode", "shape",
    "dtype", "min", "max", "num_hands", "num_landmarks", "handedness",
    "raw_categories", "notes",
]


def write_observation(input_source: str, lighting: str, expected: str, prediction: dict,
                      notes: str = "", path: Path = LOG_PATH) -> None:
    """Persist one independent camera action, not a stream of duplicate frames."""
    path.parent.mkdir(parents=True, exist_ok=True)
    first_write = not path.exists()
    row = {
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "source": input_source,
        "lighting": lighting,
        "expected_label": expected,
        "predicted_label": prediction["label"],
        "score": "" if prediction["score"] is None else f'{prediction["score"]:.6f}',
        "action": prediction["action"],
        "correct": int(expected == prediction["label"]),
        "inference_ms": f'{prediction["inference_ms"]:.3f}',
        "input_mode": prediction["input_mode"],
        "shape": str(prediction["shape"]),
        "dtype": prediction["dtype"],
        "min": prediction["min"],
        "max": prediction["max"],
        "num_hands": prediction["num_hands"],
        "num_landmarks": prediction["num_landmarks"],
        "handedness": prediction["handedness"] or "",
        "raw_categories": repr(prediction["categories"]),
        "notes": notes.replace("\n", " ")[:300],
    }
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if first_write:
            writer.writeheader()
        writer.writerow(row)


def read_observations(path: Path = LOG_PATH) -> list[dict]:
    if not path.is_file():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))
