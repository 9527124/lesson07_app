# 第8回 試作品と評価計画

- 学籍番号：g2432047
- 氏名：陳嘉欣
- 提出日：2026/10/25
- 提出file名：`PROTOTYPE_EVAL_PLAN.md`（アプリのrepository直下に置き、commitして提出する）
- 締切：**10/25（日）23:59**

> 本文は実装仕様と評価**計画**を記載したもの。実際の推論出力・時間・正解率は、ローカルでモデルを実行して得られた値だけを記録する。未測定値を推測で埋めない。

---

## 1. 企画からの変更点

| 項目 | 企画（`IDEA_PROPOSAL.md`） | 現在 | 変更した理由 |
|---|---|---|---|
| 操作入力 | Webカメラのリアルタイム映像によるゲーム操作 | 第8回の試作品ではWebカメラで撮影した**1枚の画像**またはuploadした画像を分類し、仮のゲーム指令に変換する | まず入力→DL推論→表示を確実に実行し、モデルの入出力と失敗例を検証するため。最終目標のリアルタイム戦闘は変更しない |
| ゲーム部分 | チュートリアル→リアルタイム戦闘→勝敗表示、連続結印 | 第8回時点では操作指令の表示まで。チュートリアル・戦闘・連続結印は未実装 | 深層学習を用いた入力部分の動作検証を先行するため |

---

## 2. 処理の流れ

```text
Webカメラで静止画を撮影 / PNG・JPEGをupload
  → PIL.Image.open() → RGBへ変換 → uint8 H×W×3の配列
  → [MediaPipe Gesture Recognizer] → ジェスチャー名とscore
  → ルールで仮のゲーム指令に対応付け
  → Streamlitに入力値・生の結果・ゲーム指令を表示
```

| 段階 | 処理の内容 | 深層学習 / ルール | 担当するfile・関数 |
|---|---|---|---|
| 入力 | ブラウザのカメラ撮影または画像upload | ルール（入出力） | `app.py`：`st.camera_input()` / `st.file_uploader()` |
| 前処理 | PILで画像を読込、RGBのuint8 HWC（0〜255）に変換 | ルール。モデル内部のresize等はMediaPipe標準processor | `classifier.py`：`prepare_input()`、`predict()` |
| モデル | 手の検出、21点の手のlandmark推定、ジェスチャーの分類 | **深層学習** | `classifier.py`：`get_recognizer()`、`predict()` |
| 後処理 | `Closed_Fist`→攻撃、`Open_Palm`→防御、`Victory`→移動、それ以外は発動なし（すべて**仮**） | ルール | `classifier.py`：`gesture_to_action()` |
| 表示 | 認識したlabel、score、形状・値域、推論時間、指令を表示 | ルール | `app.py` |

---

## 3. モデルの仕様

- モデル名：MediaPipe **Gesture Recognizer**（Google提供の学習済みbundle、float16）
- 入手元（URL）：`https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/latest/gesture_recognizer.task`
- license：MediaPipe実装codeはApache License 2.0。配布されるモデルbundle自体の利用条件は配布元のモデル情報で別途確認する（**確認未完了**）。
- 入力（形式・shape・値域）：MediaPipe `ImageFormat.SRGB` に変換した RGB・`uint8`・`(H, W, 3)`・0〜255。`H, W` は入力画像によって変わる。内部の画像変換・正規化はMediaPipeの標準処理に委ねる。
- 出力（形式・意味）：`GestureRecognizerResult` のジェスチャー候補と`score`、手のlandmark（検出時21点）、左右の推定。手が見つからない場合は空の結果、未認識の手の形の場合は`None`がある。`score`は**真の正答確率ではない**。
- 実行環境（CPU / CUDA / MPS）と1回の推論時間：WSL2 Ubuntu / Python 3.12 / CPU を予定。**実測時間は以下に記録**。

モデルへ渡す直前と、モデルの出力を表示した結果：

<!-- ACTUAL_INPUT_OUTPUT_BEGIN -->
```text
入力: mode=RGB shape=[396, 704, 3] dtype=uint8 pixel_range=[1, 255]
モデル出力（実測）: label=Open_Palm score=0.613098 num_hands=1 landmarks=21 handedness=Left
生のcategories: [{'label': 'Open_Palm', 'score': 0.6130983829498291}]
推論時間: 39.534 ms / 実行予定環境 CPU
```
<!-- ACTUAL_INPUT_OUTPUT_END -->

---

## 4. 動作確認（入力から出力まで）

```bash
$ cd ~/lesson07_app
$ python download_model.py
$ python -m streamlit run app.py
$ git log --oneline
```

以下の表はアプリで「この試行の実測結果を記録」を押した記録から作る。

<!-- ACTUAL_CHECK_TABLE_BEGIN -->
| 入力 | 画面に表示された結果 | 期待どおりか |
|---|---|---|
| カメラ撮影・normal・正解=Open_Palm（通常照明で手のひらを撮影） | Open_Palm score=0.613098 / DEFEND（防御・仮） | ○ |
| カメラ撮影・normal・正解=Closed_Fist（通常照明で拳を撮影） | None score=0.559702 / NO_ACTION（発動なし） | ×（誤認識） |
| カメラ撮影・normal・正解=None（手が写っていない画像） | None score=N/A / NO_ACTION（発動なし） | ○ |
<!-- ACTUAL_CHECK_TABLE_END -->

---

## 5. 評価計画

### 評価データ

| 区分 | 件数 | 集め方・条件 | 置き場所 |
|---|---:|---|---|
| dev（調整用） | **24件予定（未収集）** | `Closed_Fist` / `Open_Palm` / `Victory` / `None` の4条件×照明2条件×各3回。独立した撮影で正解を記録 | `data/dev/<正解ラベル>/<normal・dim>_<番号>.jpg` および `logs/dev_observations.csv` |
| test（最終確認用） | **40件予定（未収集）** | 同じ4条件×照明2条件×各5回。**devとは別の日に撮影** | `data/test/<正解ラベル>/<normal・dim>_<番号>.jpg` |

- devとtestが重ならないようにした方法：撮影日・撮影sessionを分離し、同一画像や隣接frameを両方に入れない。件数は動画frame数ではなく**独立した試行回数**で数える。
- testを最終評価まで使わない方法：ジェスチャー選定やしきい値等の調整はdevだけで実施する。testでの結果を見た後に、その結果に合わせて設定を変えない。

### 指標と比較対象

- 指標：指定ジェスチャーの**認識成功率**（正しく識別した試行数 / 全試行数）、対象外の入力による**誤発動回数**、**推論時間（ms）**。最終ゲームでは操作発動までの時間も別途測定する。
- 比較対象（正解・baseline）：試行の前に人間が指定・確認した正解ラベルと、モデルが出力した予測ラベルを比較する。照明条件では通常照明を基準（baseline）とし、低照度との差を比較する。

### 比較する条件

| 条件 | 水準1 | 水準2 | 変えないもの |
|---|---|---|---|
| 室内照明 | 通常照明（`normal`） | 低照度（`dim`） | モデル、カメラ、撮影距離、背景、実施者、ジェスチャーの種類、各条件の試行数 |

### 評価の実行方法

```bash
# 入力画像の分類: 前処理、実際の推論値、仮のゲーム指令を確認する
$ python -m streamlit run app.py

# data/dev/以下に独立した画像を保存した後に実行する
$ python evaluate.py data/dev

# 最終評価のときだけ（開発中には実行しない）
$ python evaluate.py data/test

# アプリで保存した本物のdev観察結果を提出文書に反映する
$ python update_plan.py
```

---

## 6. 初期結果（devで可）

<!-- ACTUAL_DEV_RESULT_BEGIN -->
```text
dev 実測の合計: 3 独立試行
normal: 認識成功=2/3 (66.7%), 対象外誤発動=0, 平均推論=72.4 ms
条件比較: 片方の照明データが不足。比較結果はまだ出せない。
```
<!-- ACTUAL_DEV_RESULT_END -->

- 気づいたこと：低照度で手が見つからない、対象外を別のgestureと判定する等の可能性を検証する。**実際に起きた失敗だけを結果として記載する。**

---

## 7. 開発記録の候補

`DEV_LOG.md` に書く候補を記録しておく。

| 日付 | AIへの依頼 | 問題 | 確認方法 | 修正 |
|---|---|---|---|---|
| 10/25 | 第8回の資料に沿って、既存のStreamlit画面を残しつつMediaPipeでジェスチャーを推論する試作品を作成 | 実行前の段階で、カメラ画像が実際に認識できるか未確認 | `st.camera_input()`→モデル入力のshape・値域→出力label・scoreを記録予定 | 推論とゲームのルールを分け、対象外は発動なしとする設計。**実際に起きた修正の事例は実行後に追記する** |

---

## 8. 残りの作業計画（10/26〜11/3）

| 期間 | 作業 | 完了条件 |
|---|---|---|
| 10/26〜10/29 | 10/26〜27にtest用画像を別の日に撮影、10/28にリアルタイム入力と連続結印の処理を実装、10/29に通常照明と低照度の条件比較を実施 | dev/testの独立性を確認、ゲームへの手勢指令を動作検証、条件別の結果表を作成 |
| 10/30〜11/2 | チュートリアル・戦闘・勝敗表示を連携し、失敗分析から1件以上改善。`README.md`、`REPORT.md`、`DEV_LOG.md`、3〜5分のデモ動画を作成 | 入力からゲームの終了まで実行でき、成功例と失敗例および評価表を記録できる |
| 11/3 | 最終提出 | repository、`REPORT.md`、`DEV_LOG.md`、デモ動画を揃え、GitHubへpushし提出を確認 |

---

## 提出前の確認

- [x] 企画からの変更点と理由を書いた
- [x] 処理の流れで、深層学習の部分とルールの部分を分けた
- [x] モデルの入出力を、実際に表示した値で確認した（ローカル実行ログ）
- [x] 入力から出力までの動作確認を、対象外の入力も含めて記録した（ローカル実行ログ）
- [x] devとtestを分け、testを最後まで使わない方法を書いた
- [x] 指標・比較対象・比較する条件を書いた
- [x] 残りの作業計画を書いた
- [x] repository直下に `PROTOTYPE_EVAL_PLAN.md` として保存し、commitした（**実際のローカル操作後**）
