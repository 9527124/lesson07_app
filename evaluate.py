"""Evaluate separate photographed images stored under data/dev or data/test.

Usage:
    python evaluate.py data/dev
    python evaluate.py data/test     # Use only for final evaluation, never tuning.

Folder format: data/dev/<ground_truth>/<normal|dim>_01.jpg
"""
from collections import defaultdict
from pathlib import Path
from statistics import mean
import argparse
from PIL import Image
from classifier import predict


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", help="e.g. data/dev ; do not use test for tuning")
    args = parser.parse_args()
    root = Path(args.folder)
    if not root.is_dir():
        raise SystemExit(f"画像フォルダがありません: {root}")
    rows = defaultdict(list)
    supported = {"Closed_Fist", "Open_Palm", "Victory", "None"}
    for label_dir in sorted(root.iterdir()):
        if not label_dir.is_dir() or label_dir.name not in supported:
            continue
        for img_path in sorted(label_dir.glob("*")):
            if img_path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
                continue
            cond = img_path.stem.split("_")[0]
            if cond not in {"normal", "dim"}:
                continue
            with Image.open(img_path) as img:
                pred = predict(img)
            correct = pred["label"] == label_dir.name
            rows[cond].append((correct, label_dir.name, pred["label"], pred["inference_ms"]))
            print(f"{img_path}: expected={label_dir.name} predicted={pred['label']} "
                  f"correct={correct} time_ms={pred['inference_ms']:.1f}")
    if not rows:
        raise SystemExit("評価用の画像がありません。data/dev/<正解>/<normal|dim>_01.jpg の形式で保存してください。")
    print("\n=== 条件別評価（実測） ===")
    for condition, items in sorted(rows.items()):
        hits = sum(int(x[0]) for x in items)
        false_triggers = sum(x[1] == "None" and x[2] != "None" for x in items)
        ms = mean(x[3] for x in items)
        print(f"{condition}: {hits}/{len(items)} = {hits/len(items):.3f}, "
              f"対象外の誤発動={false_triggers}, 平均推論={ms:.1f} ms")

if __name__ == "__main__":
    main()
