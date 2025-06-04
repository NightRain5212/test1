import cv2
import mediapipe as mp
import numpy as np

class VideoAnalyzer:
    def __init__(self):
        """初始化视频分析器"""
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )
        self.pose = mp.solutions.pose.Pose()
        self.drawing = mp.solutions.drawing_utils
        
    def analyze_frame(self, frame):
        """分析单帧图像"""
        if frame is None:
            return {
                "eyebrow_raise": 0.0,
                "posture_stability": 0.0,
                "hand_movement": 0.0
            }
            
        try:
            # 转换颜色空间
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 微表情分析
            face_results = self.face_mesh.process(rgb_frame)
            eyebrow_ratio = self._calc_eyebrow_raise(face_results)
            
            # 肢体语言分析
            pose_results = self.pose.process(rgb_frame)
            posture_score = self._calc_posture(pose_results)
            hand_movement = self._detect_hand_gestures(pose_results)
            
            # 确保所有值都是浮点数
            return {
                "eyebrow_raise": float(eyebrow_ratio),
                "posture_stability": float(posture_score),
                "hand_movement": float(hand_movement)
            }
        except Exception as e:
            print(f"帧分析错误: {str(e)}")
            return {
                "eyebrow_raise": 0.0,
                "posture_stability": 0.0,
                "hand_movement": 0.0
            }
    
    def _calc_eyebrow_raise(self, results):
        if not results or not results.multi_face_landmarks:
            return 0.0
        try:
            landmarks = results.multi_face_landmarks[0].landmark
            # 计算眉毛和眼睛关键点的相对位置
            left_eyebrow = landmarks[65].y - landmarks[159].y
            right_eyebrow = landmarks[295].y - landmarks[386].y
            return float((left_eyebrow + right_eyebrow) / 2)
        except Exception as e:
            print(f"眉毛分析错误: {str(e)}")
            return 0.0
    
    def _calc_posture(self, results):
        if not results or not results.pose_landmarks:
            return 0.0
        try:
            landmarks = results.pose_landmarks.landmark
            # 计算肩膀倾斜度
            shoulder_slope = abs(landmarks[11].y - landmarks[12].y)
            # 计算头部稳定性
            head_stability = abs(landmarks[0].y - (landmarks[11].y + landmarks[12].y) / 2)
            
            return float(1.0 - (shoulder_slope + head_stability) / 2)
        except Exception as e:
            print(f"姿势分析错误: {str(e)}")
            return 0.0
    
    def _detect_hand_gestures(self, results):
        if not results or not results.pose_landmarks:
            return 0.0
        try:    
            landmarks = results.pose_landmarks.landmark
            # 计算手部移动幅度
            left_hand = np.array([landmarks[19].x, landmarks[19].y, landmarks[19].z])
            right_hand = np.array([landmarks[20].x, landmarks[20].y, landmarks[20].z])
            
            # 计算手部移动的标准差作为手势频率指标
            movement = np.std(np.concatenate([left_hand, right_hand]))
            return float(movement)
        except Exception as e:
            print(f"手势分析错误: {str(e)}")
            return 0.0 