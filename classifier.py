"""MediaPipe Gesture Recognizer: separate model inference from game rules.

The bundled model is downloaded by download_model.py and is not committed to Git.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from time import perf_counter

import numpy as np
from PIL import Image

MODEL_PATH = Path(__file__).resolve().parent / "models" / "gesture_recognizer.task"

# Temporary prototype controls, not the final game's decided spell list.
GESTURE_TO_ACTION = {
    "Closed_Fist": "ATTACK（攻撃・仮）",
    "Open_Palm": "DEFEND（防御・仮）",
    "Victory": "MOVE（移動・仮）",
}


def prepare_input(image: Image.Image) -> np.ndarray:
    """Convert an uploaded/camera image to contiguous HWC RGB uint8 [0,255]."""
    rgb = image.convert("RGB")
    return np.ascontiguousarray(np.asarray(rgb, dtype=np.uint8))


def gesture_to_action(label: str | None) -> str:
    """A plain rule: labels outside the supported set never trigger game actions."""
    return GESTURE_TO_ACTION.get(label, "NO_ACTION（発動なし）")


@lru_cache(maxsize=1)
def get_recognizer():
    """Load the model just once; Streamlit reruns must not recreate the model."""
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(
            f"モデルがありません: {MODEL_PATH}\n"
            "先に python download_model.py を実行してください。"
        )
    import mediapipe as mp

    options = mp.tasks.vision.GestureRecognizerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=str(MODEL_PATH)),
        running_mode=mp.tasks.vision.RunningMode.IMAGE,
        num_hands=1,
    )
    return mp.tasks.vision.GestureRecognizer.create_from_options(options)


def predict(image: Image.Image, recognizer=None) -> dict:
    """Actual inference. Returns observable model output and rule output separately."""
    import mediapipe as mp

    arr = prepare_input(image)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=arr)
    recognizer = recognizer if recognizer is not None else get_recognizer()
    started = perf_counter()
    raw = recognizer.recognize(mp_image)
    elapsed_ms = (perf_counter() - started) * 1000.0

    categories = (
        [
            {"label": entry.category_name, "score": float(entry.score)}
            for entry in raw.gestures[0]
        ]
        if raw.gestures else []
    )
    # No hand found and a detected hand with an unrecognized gesture are
    # distinguished in the raw result. Neither will trigger an action.
    raw_label = categories[0]["label"] if categories else None
    label = raw_label if raw_label not in (None, "None") else "None"
    score = categories[0]["score"] if categories else None
    handedness = (
        raw.handedness[0][0].category_name if raw.handedness else None
    )
    return {
        "label": label,
        "raw_label": raw_label,
        "score": score,
        "categories": categories,
        "action": gesture_to_action(label),
        "num_hands": len(raw.hand_landmarks),
        "num_landmarks": len(raw.hand_landmarks[0]) if raw.hand_landmarks else 0,
        "handedness": handedness,
        "input_mode": "RGB",
        "shape": list(arr.shape),
        "dtype": str(arr.dtype),
        "min": int(arr.min()),
        "max": int(arr.max()),
        "inference_ms": elapsed_ms,
        "engine": "MediaPipe Gesture Recognizer / IMAGE / CPU",
    }
