import cv2
import mediapipe as mp
import numpy as np

class VideoAnalyzer:
    def __init__(self):
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )
        self.pose = mp.solutions.pose.Pose()
        self.drawing = mp.solutions.drawing_utils
        
    def analyze_frame(self, frame):
        if frame is None:
            return None
            
        # 转换颜色空间
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 微表情分析
        face_results = self.face_mesh.process(rgb_frame)
        eyebrow_ratio = self._calc_eyebrow_raise(face_results)
        
        # 肢体语言分析
        pose_results = self.pose.process(rgb_frame)
        posture_score = self._calc_posture(pose_results)
        hand_movement = self._detect_hand_gestures(pose_results)
        
        return {
            "eyebrow_raise": eyebrow_ratio,  # 眉毛挑起频率（紧张指标）
            "posture_stability": posture_score,  # 坐姿稳定性
            "hand_movement": hand_movement  # 手势频率
        }
    
    def _calc_eyebrow_raise(self, results):
        if not results.multi_face_landmarks:
            return 0.0
        landmarks = results.multi_face_landmarks[0].landmark
        # 计算眉毛和眼睛关键点的相对位置
        left_eyebrow = landmarks[65].y - landmarks[159].y
        right_eyebrow = landmarks[295].y - landmarks[386].y
        return (left_eyebrow + right_eyebrow) / 2
    
    def _calc_posture(self, results):
        if not results.pose_landmarks:
            return 0.0
        
        landmarks = results.pose_landmarks.landmark
        # 计算肩膀倾斜度
        shoulder_slope = abs(landmarks[11].y - landmarks[12].y)
        # 计算头部稳定性
        head_stability = abs(landmarks[0].y - (landmarks[11].y + landmarks[12].y) / 2)
        
        return 1.0 - (shoulder_slope + head_stability) / 2
    
    def _detect_hand_gestures(self, results):
        if not results.pose_landmarks:
            return 0.0
            
        landmarks = results.pose_landmarks.landmark
        # 计算手部移动幅度
        left_hand = np.array([landmarks[19].x, landmarks[19].y, landmarks[19].z])
        right_hand = np.array([landmarks[20].x, landmarks[20].y, landmarks[20].z])
        
        # 计算手部移动的标准差作为手势频率指标
        movement = np.std(np.concatenate([left_hand, right_hand]))
        return movement 