# Gesture Action Game — 第8回 動く試作品

第7回の企画（新手tutorial→リアルタイム戦闘→勝敗）を維持したまま、第8回では **Webカメラから撮影した1枚の画像／画像upload → 実際の深層学習推論 → 仮のゲーム指令** を先に実装する。

## 環境

Python 3.12・WSL2 Ubuntu・Streamlit。カメラは**Windows上のブラウザ**から `st.camera_input()` に許可するので、WSLにUSB webcam deviceを直接認識させる必要はない。

## 実行手順

既存の `~/lesson07_app` repositoryの**根目录**にこれらのファイルを置く。

```bash
cd ~/lesson07_app
source .venv/bin/activate
python -m pip install -r requirements.txt
python download_model.py
python -m streamlit run app.py
```

画面に表示された `http://localhost:8501` を開き、カメラ許可を与え、手の形を撮影する。モデル取得に失敗した場合、以下のURLから手動でモデルをダウンロードし `models/gesture_recognizer.task` に配置する。

Model URL: https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/latest/gesture_recognizer.task

## 第8回の実測（自分の結果で記入）

1. 通常照明で `Open_Palm`、`Closed_Fist`、`Victory` のうち1つを撮影。
2. 照明を暗くし、同じ手勢・同じ距離で撮影。
3. 手のない背景などの**対象外**を撮影。
4. 各撮影後、画面で実際のラベル・score・時間を確認して、正解ラベルと照明条件を選択し **「この試行の実測結果を記録」** を押す。
5. 別のterminalから `python update_plan.py` を実行すると、その結果が `PROTOTYPE_EVAL_PLAN.md` に書き込まれる。
6. **必ず文書を開いて実際の結果・成功失敗の理由を確認してからcommitする**。

`logs/dev_observations.csv` は調整用の記録。顔写真のような原画像は自動保存しない。

## 評価用の独立した画像を別途収集する場合

画像を `data/dev/Open_Palm/normal_01.jpg` のように、`data/<dev|test>/<正解ラベル>/<normal|dim>_<番号>.jpg` に保存する。

```bash
python evaluate.py data/dev
# final day only:
python evaluate.py data/test
```

**同一動画の隣接フレームを異なる独立試行として数えない**。dev/testは別の日に撮影する。

## 処理の区分

- `classifier.py` — 前処理、MediaPipeの深層学習推論、ルールベースの指令変換
- `app.py` — 撮影、実測値と指令の表示、開発記録
- `download_model.py` — 正規URLからモデルを取得
- `evaluate.py` — dev/testを別のdirectoryから評価
- `update_plan.py` — 実測値だけを指定された提出文書の表に反映

## ライセンス

MediaPipeプログラム実装はApache-2.0。配布モデルの利用条件はモデルカード・配布元で個別確認し、最終報告書に出典を記載する。

## 注意

**この段階はリアルタイム戦闘ではない**。まだ静止画の試作品であり、最終目標のアクションゲームの仕様は変更していない。モデルの`score`を校正済みの正解確率として扱わない。
