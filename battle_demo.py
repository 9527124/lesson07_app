
import streamlit as st

st.set_page_config(page_title="战斗原型", page_icon="⚔️")

if "player_hp" not in st.session_state:
    st.session_state.player_hp = 100
    st.session_state.enemy_hp = 100
    st.session_state.position = 1
    st.session_state.message = "战斗开始！"

def act(action):
    s = st.session_state

    if s.player_hp <= 0 or s.enemy_hp <= 0:
        return

    if action == "attack":
        s.enemy_hp = max(0, s.enemy_hp - 20)
        s.message = "你发动攻击，造成20点伤害！"

    elif action == "defend":
        s.message = "你展开护盾，准备抵挡攻击。"

    elif action == "left":
        s.position = max(0, s.position - 1)
        s.message = "你向左移动。"

    elif action == "right":
        s.position = min(2, s.position + 1)
        s.message = "你向右移动。"

    # 暂时用每次操作后的反击来测试战斗规则
    if s.enemy_hp > 0:
        damage = 4 if action == "defend" else 12
        s.player_hp = max(0, s.player_hp - damage)
        s.message += f" 敌人反击，造成{damage}点伤害！"

st.title("⚔️ Gesture Action Game")
st.caption("战斗逻辑测试版 · 暂时使用按钮模拟手势")

st.subheader("敌人")
st.progress(st.session_state.enemy_hp / 100)
st.write(f"敌人 HP：{st.session_state.enemy_hp}/100")

st.divider()

positions = ["左侧", "中央", "右侧"]
st.write(f"📍 当前位置：{positions[st.session_state.position]}")

st.subheader("玩家")
st.progress(st.session_state.player_hp / 100)
st.write(f"玩家 HP：{st.session_state.player_hp}/100")

st.info(st.session_state.message)

if st.session_state.enemy_hp <= 0:
    st.success("🎉 战斗胜利！")
elif st.session_state.player_hp <= 0:
    st.error("💀 战斗失败！")
else:
    col1, col2 = st.columns(2)

    with col1:
        st.button("⚔️ 攻击", on_click=act, args=("attack",))
        st.button("⬅️ 左移", on_click=act, args=("left",))

    with col2:
        st.button("🛡️ 防御", on_click=act, args=("defend",))
        st.button("➡️ 右移", on_click=act, args=("right",))

if st.button("🔄 重新开始"):
    for key in ["player_hp", "enemy_hp", "position", "message"]:
        del st.session_state[key]
    st.rerun()
