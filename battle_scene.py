
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


# ===== 2.5D 战斗场景 =====
positions = ["左侧", "中央", "右侧"]
player_position = st.session_state.position

player_x = [18, 50, 82][player_position]
enemy_hp = st.session_state.enemy_hp

hit_animation = (
    f"enemy_hit_{enemy_hp} 0.45s ease-out"
    if "你发动攻击" in st.session_state.message
    else "none"
)
st.html(
    f"""
<style>
@keyframes enemy_hit_{enemy_hp} {{
    0%, 100% {{
        translate: 0 0;
        filter: brightness(1);
    }}

    25% {{
        translate: -14px 0;
        filter: brightness(1.8);
    }}
    50% {{
        translate: 14px 0;
        filter: brightness(1.5);
    }}
    75% {{
        translate: -7px 0;
    }}
}}
</style>
    
<div style="
        position:relative;
        height:360px;
        overflow:hidden;
        border-radius:16px;
        background:linear-gradient(
            #aacbd2 0%,
            #d9e1d5 48%,
            #b5a98d 100%
        );
        border:2px solid #849e9b;
    ">
        <!-- 远景：山峦 -->
        <div style="
            position:absolute;
            bottom:30%;
            width:100%;
            height:45%;
            background:#789990;
            opacity:0.5;
            clip-path:polygon(
                0% 100%, 0% 75%, 20% 20%,
                38% 80%, 60% 10%,
                80% 80%, 100% 35%, 100% 100%
            );
        "></div>

        <!-- 中景：演武场 -->
        <div style="
            position:absolute;
            bottom:0;
            width:100%;
            height:39%;
            background:linear-gradient(#c5b79a,#8b8c7b);
            clip-path:polygon(
                25% 0%,75% 0%,100% 100%,0% 100%
            );
        "></div>

        <!-- 敌人 -->
        <div style="
            position:absolute;
            left:50%;
            top:42%;
            transform:translate(-50%,-50%);
            text-align:center;
            font-size:62px;
            animation:{hit_animation};
        ">
            🥷
            <div style="font-size:15px;color:#343434">
                守关者
            </div>
        </div>

        <!-- 玩家当前位置 -->
        <div style="
            position:absolute;
            left:{player_x}%;
            bottom:8%;
            transform:translateX(-50%);
            text-align:center;
            font-size:31px;
            transition:left 0.3s;
        ">
            🔵
            <div style="font-size:13px;color:white">
                玩家
            </div>
        </div>

        <!-- 场景标题 -->
        <div style="
            position:absolute;
            top:12px;
            left:15px;
            color:#314d4a;
            font-weight:bold;
        ">
            演武场 · 战斗试炼
        </div>
    </div>
    """,
)
st.subheader("敌人")
st.progress(st.session_state.enemy_hp / 100)
st.write(f"敌人 HP：{st.session_state.enemy_hp}/100")


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
