"""
AI 健身教练 — 实时姿态检测 + 深蹲计数 + 动作评分
MediaPipe 0.10.x Tasks API + OpenCV，纯本地运行，无需 GPU

使用方式：
  python ai_coach.py

运行后面对摄像头做深蹲，侧面站效果最好。
按 Q 退出 | 按 R 重置计数
"""

import cv2
import numpy as np
import math
import time
from collections import deque

# ---------- MediaPipe Tasks API ----------
from mediapipe.tasks import python as mp_task
from mediapipe.tasks.python import vision
from mediapipe import Image, ImageFormat


# ---------- 配置 ----------
MODEL_PATH = "pose_landmarker_lite.task"
MIN_ANGLE = 85       # 深蹲到底膝盖角度（度）
MAX_ANGLE = 155      # 站立膝盖角度（度）
SMOOTH_WINDOW = 5

# ---------- 下载模型（首次运行）----------
import urllib.request
import os

if not os.path.exists(MODEL_PATH):
    print(">> 首次运行，下载 Pose Landmarker 模型 (~5MB)...")
    url = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task"
    urllib.request.urlretrieve(url, MODEL_PATH)
    print(">> 模型下载完成")

# ---------- MediaPipe Tasks 初始化 ----------
base_options = mp_task.BaseOptions(model_asset_path=MODEL_PATH)
options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    running_mode=mp_task.vision.RunningMode.VIDEO,
    num_poses=1,
    min_pose_detection_confidence=0.7,
    min_pose_presence_confidence=0.7,
    min_tracking_confidence=0.7,
)
landmarker = vision.PoseLandmarker.create_from_options(options)

# ---------- 骨骼连接定义 ----------
BONE_PAIRS = [
    (11, 12), (11, 23), (12, 24), (23, 24),
    (23, 25), (24, 26), (25, 27), (26, 28),
    (11, 13), (13, 15), (12, 14), (14, 16),
]

LEFT_HIP, RIGHT_HIP = 23, 24
LEFT_KNEE, RIGHT_KNEE = 25, 26
LEFT_ANKLE, RIGHT_ANKLE = 27, 28
LEFT_SHOULDER, RIGHT_SHOULDER = 11, 12
LEFT_ELBOW, RIGHT_ELBOW = 13, 14
LEFT_WRIST, RIGHT_WRIST = 15, 16


# ---------- 工具函数 ----------

def angle_between(a, b, c):
    """计算三点夹角，a-b 和 c-b 之间的角度（度）"""
    ba = (a[0] - b[0], a[1] - b[1])
    bc = (c[0] - b[0], c[1] - b[1])
    dot = ba[0] * bc[0] + ba[1] * bc[1]
    mag_ba = math.sqrt(ba[0]**2 + ba[1]**2)
    mag_bc = math.sqrt(bc[0]**2 + bc[1]**2)
    if mag_ba < 1e-6 or mag_bc < 1e-6:
        return 0
    cos_a = max(-1.0, min(1.0, dot / (mag_ba * mag_bc)))
    return math.degrees(math.acos(cos_a))


def get_landmark_xy(lm, w, h):
    """归一化坐标 → 像素坐标"""
    return (lm.x * w, lm.y * h)


class RepCounter:
    def __init__(self):
        self.count = 0
        self.state = "up"
        self.angle_history = deque(maxlen=SMOOTH_WINDOW)

    def smooth(self, angle):
        self.angle_history.append(angle)
        return sum(self.angle_history) / len(self.angle_history)

    def update(self, raw_angle):
        angle = self.smooth(raw_angle)
        if self.state == "up" and angle < MIN_ANGLE:
            self.state = "down"
        elif self.state == "down" and angle > MAX_ANGLE:
            self.state = "up"
            self.count += 1
            return True
        return False


# ---------- 绘制 ----------

def draw_skeleton(img, landmarks, w, h):
    """画骨骼线 + 关节点"""
    pts = {}
    for i, lm in enumerate(landmarks):
        if lm.visibility > 0.5:
            pts[i] = (int(lm.x * w), int(lm.y * h))
    for a, b in BONE_PAIRS:
        if a in pts and b in pts:
            cv2.line(img, pts[a], pts[b], (0, 255, 100), 3, cv2.LINE_AA)
    for pt in pts.values():
        cv2.circle(img, pt, 7, (0, 220, 80), 2, cv2.LINE_AA)
        cv2.circle(img, pt, 3, (0, 255, 100), -1, cv2.LINE_AA)


def draw_ui(img, w, rep_count, knee_angle, status, fps):
    """UI 面板"""
    overlay = img.copy()

    # 顶部面板
    cv2.rectangle(overlay, (0, 0), (w, 95), (20, 20, 20), -1)
    img = cv2.addWeighted(overlay, 0.7, img, 0.3, 0)

    cv2.putText(img, "AI COACH", (20, 38),
                cv2.FONT_HERSHEY_DUPLEX, 0.7, (100, 100, 100), 1, cv2.LINE_AA)
    cv2.putText(img, "SQUAT  ANALYSIS", (20, 72),
                cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(img, f"FPS {fps:.0f}", (w - 120, 35),
                cv2.FONT_HERSHEY_DUPLEX, 0.6, (100, 100, 100), 1, cv2.LINE_AA)

    # 右侧：REPS 计数
    rx = w - 190
    cv2.putText(img, "REPS", (rx, 180),
                cv2.FONT_HERSHEY_DUPLEX, 0.55, (150, 150, 150), 1, cv2.LINE_AA)
    cv2.putText(img, str(rep_count), (rx, 260),
                cv2.FONT_HERSHEY_DUPLEX, 3.0, (255, 255, 255), 4, cv2.LINE_AA)

    # 右侧：角度面板
    py = 340
    cv2.rectangle(overlay, (rx - 20, py), (w - 10, py + 125), (30, 30, 30), -1)
    img = cv2.addWeighted(overlay, 0.6, img, 0.4, 0)

    if status == "good":
        ac, st, sc = (0, 255, 100), "GOOD DEPTH", (0, 255, 100)
    elif status == "shallow":
        ac, st, sc = (60, 160, 255), "GO LOWER", (60, 160, 255)
    else:
        ac, st, sc = (150, 150, 150), "STAND BY", (150, 150, 150)

    cv2.putText(img, "KNEE ANGLE", (rx, py + 28),
                cv2.FONT_HERSHEY_DUPLEX, 0.5, (150, 150, 150), 1, cv2.LINE_AA)
    cv2.putText(img, f"{knee_angle:.0f} deg", (rx, py + 70),
                cv2.FONT_HERSHEY_DUPLEX, 1.8, ac, 3, cv2.LINE_AA)
    cv2.putText(img, st, (rx, py + 105),
                cv2.FONT_HERSHEY_DUPLEX, 0.7, sc, 2, cv2.LINE_AA)

    # 底部品牌
    cv2.putText(img, "10-YEAR GYM  |  AI POWERED",
                (20, img.shape[0] - 18),
                cv2.FONT_HERSHEY_DUPLEX, 0.5, (80, 80, 80), 1, cv2.LINE_AA)
    return img


# ---------- 主循环 ----------

def main():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    cv2.namedWindow("AI Coach — Gym", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("AI Coach — Gym", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    counter = RepCounter()
    prev_time = time.time()
    fps_q = deque(maxlen=30)
    frame_idx = 0

    print("=" * 50)
    print("  AI 健身教练已启动 — 深蹲模式")
    print("  侧面面对摄像头 | Q 退出 | R 重置")
    print("=" * 50)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        # FPS
        now = time.time()
        fps_q.append(1 / max(now - prev_time, 0.001))
        fps = sum(fps_q) / len(fps_q)
        prev_time = now

        # MediaPipe 推理 (Tasks API 需要 mp.Image + 时间戳)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = Image(image_format=ImageFormat.SRGB, data=rgb)
        result = landmarker.detect_for_video(mp_image, frame_idx)
        frame_idx += 1

        if result.pose_landmarks and len(result.pose_landmarks) > 0:
            lms = result.pose_landmarks[0]

            draw_skeleton(frame, lms, w, h)

            # 右膝角度
            r_hip = get_landmark_xy(lms[RIGHT_HIP], w, h)
            r_knee = get_landmark_xy(lms[RIGHT_KNEE], w, h)
            r_ankle = get_landmark_xy(lms[RIGHT_ANKLE], w, h)
            knee_angle = angle_between(r_hip, r_knee, r_ankle)

            if knee_angle >= MAX_ANGLE:
                status = "stand"
            elif knee_angle <= MIN_ANGLE:
                status = "good"
            else:
                status = "shallow"

            triggered = counter.update(knee_angle)

            # 膝盖角度标注
            ac = (0, 255, 100) if status == "good" else (60, 160, 255)
            cv2.putText(frame, f"{knee_angle:.0f}",
                        (int(r_knee[0]) + 20, int(r_knee[1]) - 20),
                        cv2.FONT_HERSHEY_DUPLEX, 0.8, ac, 2, cv2.LINE_AA)

            if triggered:
                flash = np.zeros_like(frame)
                flash[:] = (0, 255, 100)
                frame = cv2.addWeighted(frame, 0.75, flash, 0.25, 0)

            frame = draw_ui(frame, w, counter.count, knee_angle, status, fps)
        else:
            cv2.putText(frame, "STAND IN FRAME", (w // 2 - 200, h // 2),
                        cv2.FONT_HERSHEY_DUPLEX, 1.5, (150, 150, 150), 2, cv2.LINE_AA)
            cv2.putText(frame, "Face camera sideways for squat detection",
                        (w // 2 - 260, h // 2 + 45),
                        cv2.FONT_HERSHEY_DUPLEX, 0.6, (100, 100, 100), 1, cv2.LINE_AA)

        cv2.imshow("AI Coach — Gym", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break
        elif key == ord('r'):
            counter.count = 0
            counter.state = "up"
            print(">> 计数已重置")

    cap.release()
    cv2.destroyAllWindows()
    print("AI Coach 已退出")


if __name__ == "__main__":
    main()
