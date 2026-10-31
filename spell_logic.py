
class SpellCaster:
    def __init__(self, stable_frames=3):
        self.sequence = [
            "Thumb_Up",
            "Victory",
            "Pointing_Up",
        ]
        self.stable_frames = stable_frames
        self.progress = 0
        self.candidate = None
        self.count = 0

    def reset(self):
        self.progress = 0
        self.candidate = None
        self.count = 0

    def update(self, label):
        if label == self.candidate:
            self.count += 1
        else:
            self.candidate = label
            self.count = 1

        # 手势需要连续稳定识别3帧
        if self.count < self.stable_frames:
            return None

        expected = self.sequence[self.progress]

        if label == expected:
            self.progress += 1
            self.count = 0

            if self.progress == len(self.sequence):
                self.reset()
                return "CAST"

            return "PROGRESS"

        return None
