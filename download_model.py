"""Download the official MediaPipe Gesture Recognizer model bundle once."""
from pathlib import Path
from urllib.request import urlopen
from classifier import MODEL_PATH

URL = (
    "https://storage.googleapis.com/mediapipe-models/gesture_recognizer/"
    "gesture_recognizer/float16/latest/gesture_recognizer.task"
)

def main():
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    if MODEL_PATH.exists() and MODEL_PATH.stat().st_size > 1_000_000:
        print(f"既に存在します: {MODEL_PATH} ({MODEL_PATH.stat().st_size} bytes)")
        return
    temp = MODEL_PATH.with_suffix(".task.tmp")
    try:
        with urlopen(URL, timeout=90) as response, temp.open("wb") as dst:
            while block := response.read(1024 * 1024):
                dst.write(block)
        if temp.stat().st_size < 1_000_000:
            raise RuntimeError("モデルが小さすぎます。取得に失敗した可能性があります。")
        temp.replace(MODEL_PATH)
        print(f"取得しました: {MODEL_PATH} ({MODEL_PATH.stat().st_size} bytes)")
        print("モデル取得元:", URL)
    finally:
        temp.unlink(missing_ok=True)

if __name__ == "__main__":
    main()
