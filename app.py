
import streamlit as st

st.set_page_config(
    page_title="Gesture Action Game",
    page_icon="⚔️",
    layout="centered",
)

st.title("⚔️ Gesture Action Game")
st.write("手のジェスチャーで技を発動するアクションゲーム")

st.divider()

st.subheader("ゲームについて")
st.write(
    "Webカメラでプレイヤーのジェスチャーを認識し、"
    "攻撃・防御・特殊技を使用するゲームです。"
)

st.subheader("ゲームメニュー")

if st.button("📖 チュートリアルを開始", use_container_width=True):
    st.info("チュートリアル機能は今後実装する予定です。")

if st.button("⚔️ 戦闘を開始", use_container_width=True):
    st.info("リアルタイム戦闘機能は今後実装する予定です。")

st.divider()
st.caption("第7回：アプリ開発課題① — 初期画面")
