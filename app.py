"""第8回 prototype: real model inference from camera snapshots / uploaded photos.

Not yet a live-frame action game. The first-person real-time game from the
approved idea proposal remains the final target.
"""
from io import BytesIO
from hashlib import sha256

from PIL import Image, UnidentifiedImageError
import streamlit as st

from classifier import MODEL_PATH, gesture_to_action, predict
from observations import read_observations, write_observation

st.set_page_config(page_title="Gesture Action Game", page_icon="⚔️", layout="centered")
st.title("⚔️ Gesture Action Game")
st.caption("第8回 試作品｜カメラ画像 → MediaPipe（深層学習）→ ゲーム指令")
st.write("最終目標：チュートリアル → リアルタイム戦闘 → 勝敗表示")

with st.expander("モデルと処理の役割"):
    st.write("画像を RGB・uint8 に変換し、MediaPipe Gesture Recognizer で手の形を認識します。")
    st.write("予測ラベルをゲーム指令に対応付ける部分は通常のルール処理です。")
    st.write("仮の操作：Closed_Fist → ATTACK / Open_Palm → DEFEND / Victory → MOVE")
    st.write("この3種類の対応は試作のための仮設定であり、最終ゲームの技を確定するものではありません。")

st.subheader("① ジェスチャー入力")
source = st.radio("入力方法", ["カメラ撮影", "画像アップロード"], horizontal=True)
if source == "カメラ撮影":
    uploaded = st.camera_input("手を写して撮影（ブラウザのカメラ許可が必要）")
else:
    uploaded = st.file_uploader("手の画像、または対象外の画像", type=["png", "jpg", "jpeg"])

if not MODEL_PATH.is_file():
    st.warning("モデル未取得です。ターミナルで `python download_model.py` を実行してください。")

if uploaded is not None:
    data = uploaded.getvalue()
    digest = sha256(data).hexdigest()
    try:
        image = Image.open(BytesIO(data))
        image.load()
    except (UnidentifiedImageError, OSError) as exc:
        st.error(f"画像を開けません: {exc}")
        st.stop()

    st.image(image, caption="入力画像", use_container_width=True)
    if not MODEL_PATH.is_file():
        st.stop()
    try:
        # Each new snapshot is inferred only once per session; displaying widgets
        # does not change the result or silently run new trials.
        if st.session_state.get("last_digest") != digest:
            with st.spinner("深層学習モデルで推論しています..."):
                st.session_state.last_result = predict(image)
                st.session_state.last_digest = digest
        result = st.session_state.last_result
    except Exception as exc:
        st.error(f"推論に失敗しました: {type(exc).__name__}: {exc}")
        st.stop()

    st.subheader("② 実際のモデル出力")
    c1, c2, c3 = st.columns(3)
    c1.metric("認識結果", result["label"])
    c2.metric("モデルscore", "—" if result["score"] is None else f'{result["score"]:.3f}')
    c3.metric("推論時間（ms）", f'{result["inference_ms"]:.1f}')
    st.write("**暫定ゲーム指令（ルール処理）:**", result["action"])
    if result["action"].startswith("NO_ACTION"):
        st.info("対象外 / 未認識: 技は発動しません。")
    else:
        st.success(f'試作で指令を生成: {result["action"]}')
    with st.expander("入力直前の実測値・生の出力（提出用）"):
        st.json({
            "input_mode": result["input_mode"], "input_shape": result["shape"],
            "dtype": result["dtype"], "value_min": result["min"],
            "value_max": result["max"], "model_categories": result["categories"],
            "num_hands": result["num_hands"],
            "num_landmarks": result["num_landmarks"],
            "handedness": result["handedness"],
            "inference_ms": round(result["inference_ms"], 2),
        })
    st.caption("scoreはモデルの出力値であり、現実の正答確率を保証しません。")

    st.divider()
    st.subheader("③ devでの動作確認記録")
    st.write("表示を確認してから、実際に行った動作を選んで保存します。写真自体は保存しません。")
    lighting = st.selectbox("照明条件", ["normal", "dim"], format_func=lambda x: {"normal":"通常照明", "dim":"低照度"}[x])
    expected = st.selectbox("実際に行ったジェスチャー（正解）", ["Closed_Fist", "Open_Palm", "Victory", "None"])
    notes = st.text_input("入力の説明（例：手を映さない、照明が暗い）", "")
    if st.button("この試行の実測結果を記録", type="primary"):
        write_observation(source, lighting, expected, result, notes)
        st.success("logs/dev_observations.csv に実測値を保存しました。")

count = len(read_observations())
st.caption(f"保存済み dev 試行: {count} 件。testは別の撮影日に収集し、最後まで調整に使用しません。")
st.divider()
st.subheader("開発予定のゲーム機能")
c1, c2 = st.columns(2)
if c1.button("📖 チュートリアルを開始", use_container_width=True):
    st.info("チュートリアルは今後実装します。")
if c2.button("⚔️ 戦闘を開始", use_container_width=True):
    st.info("リアルタイム戦闘は今後実装します。")
