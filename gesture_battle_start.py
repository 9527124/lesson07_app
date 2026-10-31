
import streamlit as st
from time import monotonic

st.set_page_config(page_title="战斗原型", page_icon="⚔️")

if "player_hp" not in st.session_state:
    st.session_state.player_hp = 100
    st.session_state.enemy_hp = 100
    st.session_state.position = 1
    st.session_state.message = "战斗开始！"
    st.session_state.next_enemy_attack = monotonic() + 3.0
    st.session_state.guard_until = 0.0

def act(action):
    s = st.session_state

    if s.player_hp <= 0 or s.enemy_hp <= 0:
        return

    if action == "attack":
        s.enemy_hp = max(0, s.enemy_hp - 20)
        s.message = "你发动攻击，造成20点伤害！"

    elif action == "defend":
        s.message = "你展开护盾，准备抵挡攻击。"
        s.guard_until = monotonic() + 1.8

    elif action == "left":
        s.position = max(0, s.position - 1)
        s.message = "你向左移动。"

    elif action == "right":
        s.position = min(2, s.position + 1)
        s.message = "你向右移动。"



# ===== 实时手势控制 =====
from queue import Queue, Empty
import av
import cv2
from PIL import Image
from streamlit_webrtc import webrtc_streamer

from classifier import predict
from gesture_control import GestureControl

if "gesture_events" not in st.session_state:
    st.session_state.gesture_events = Queue(maxsize=32)

events = st.session_state.gesture_events
controller = GestureControl(stable_frames=3, reset_frames=6)

def video_frame_callback(frame):
    image = frame.to_ndarray(format="bgr24")
    image = cv2.flip(image, 1)

    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    result = predict(Image.fromarray(rgb))

    label = result["label"]
    action = controller.update(label)

    if action:
        if not events.full():
            events.put_nowait(action)

    cv2.putText(
        image,
        f"Gesture: {label}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        (0, 255, 0),
        2,
    )

    return av.VideoFrame.from_ndarray(image, format="bgr24")


@st.fragment(run_every="0.4s")
def game_panel():
    if "game_started" not in st.session_state:
        st.session_state.game_started = False

    camera_ready = bool(webrtc_ctx.state.playing)

    if not camera_ready:
        st.subheader("⚔️ 战斗准备")
        st.info("请先在右侧点击 START，开启摄像头并允许权限。")
        st.caption("确认手部画面正常后，才能开始战斗。")

        # 摄像头断开时立即停止战斗计时
        if st.session_state.game_started:
            st.session_state.game_started = False
            st.session_state.next_enemy_attack = monotonic() + 3.0
        return

    if not st.session_state.game_started:
        st.subheader("⚔️ 战斗准备")
        st.success("✅ 摄像头已启动！")
        st.write("请确认双手在画面内，然后点击开始。")

        if not st.button("▶️ 开始 / 继续战斗"):
            return

        st.session_state.game_started = True
        st.session_state.next_enemy_attack = monotonic() + 3.0

        # 清除准备阶段积累的旧手势
        while True:
            try:
                events.get_nowait()
            except Empty:
                break

    # 只在Streamlit界面线程中修改游戏状态
    for _ in range(16):
        try:
            action = events.get_nowait()
        except Empty:
            break

        if action == "ATTACK":
            act("attack")
        elif action == "DEFEND":
            act("defend")

    s = st.session_state
    now = monotonic()

    if s.player_hp > 0 and s.enemy_hp > 0:
        if now >= s.next_enemy_attack:
            damage = 4 if now < s.guard_until else 12
            s.player_hp = max(0, s.player_hp - damage)
            s.message = f"敌人主动攻击！造成{damage}点伤害。"
            s.next_enemy_attack = now + 3.0

    # 敌人攻击前1.5秒进入蓄力状态
    warning_active = (
        s.player_hp > 0
        and s.enemy_hp > 0
        and 0 < s.next_enemy_attack - monotonic() <= 1.5
    )

    st.title("⚔️ Gesture Action Game")

    if s.player_hp > 0 and s.enemy_hp > 0:
        remaining = max(0, s.next_enemy_attack - monotonic())
        st.caption(f"⚠️ 敌人攻击倒计时：{remaining:.1f}秒")

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

    
        <style>
        @keyframes enemy_charge {{
            from {{
                opacity: 0.45;
                scale: 0.9;
            }}
            to {{
                opacity: 1;
                scale: 1.15;
            }}
        }}
        </style>

        <!-- 敌人蓄力光圈 -->
        <div style="
            display:{"block" if warning_active else "none"};
            position:absolute;
            left:50%;
            top:42%;
            transform:translate(-50%,-50%);
            width:130px;
            height:130px;
            border:4px solid #ff4242;
            border-radius:50%;
            box-shadow:0 0 25px 10px #ff424288;
            animation:enemy_charge 0.6s infinite alternate;
            pointer-events:none;
        "></div>

        <!-- 攻击预警文字 -->
        <div style="
            display:{"block" if warning_active else "none"};
            position:absolute;
            right:12px;
            top:12px;
            padding:8px 12px;
            border-radius:10px;
            background:#a82222;
            color:white;
            font-size:16px;
            font-weight:bold;
            z-index:5;
        ">
            ⚠️ 敌人即将攻击！
        </div>

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
        st.session_state.game_started = False
        for key in ["player_hp", "enemy_hp", "position", "message"]:
            del st.session_state[key]
        st.rerun()

# ===== 并排显示战斗与摄像头 =====
game_column, camera_column = st.columns([3, 2])

with camera_column:
    st.subheader("📷 实时手势控制")
    st.caption("握拳攻击 / 张掌防御")
    webrtc_ctx = webrtc_streamer(
        key="gesture-battle-camera",
        video_frame_callback=video_frame_callback,
        media_stream_constraints={
            "video": True,
            "audio": False,
        },
        async_processing=True,
    )

with game_column:
    game_panel()
