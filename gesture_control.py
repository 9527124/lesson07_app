
class GestureControl:
    def __init__(self, stable_frames=3, reset_frames=3):
        self.stable_frames = stable_frames
        self.reset_frames = reset_frames
        self.candidate = None
        self.count = 0
        self.empty_count = 0
        self.last_trigger = None

    def update(self, label):
        actions = {
            "Closed_Fist": "ATTACK",
            "Open_Palm": "DEFEND",
        }

        # 没有识别到有效的操作手势
        if label not in actions:
            self.empty_count += 1
            self.candidate = None
            self.count = 0

            if self.empty_count >= self.reset_frames:
                self.last_trigger = None

            return None

        self.empty_count = 0

        # 检查手势是否连续稳定出现
        if label == self.candidate:
            self.count += 1
        else:
            self.candidate = label
            self.count = 1

        # 连续识别3帧后，才生成一次操作
        if (
            self.count >= self.stable_frames
            and label != self.last_trigger
        ):
            self.last_trigger = label
            return actions[label]

        return None
