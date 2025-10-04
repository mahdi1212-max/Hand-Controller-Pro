"""
فایل اجرایی اصلاح شده برای Hand Controller Pro v3.0
Fixed Runner for Hand Controller Pro v3.0
"""

import sys
import os
import cv2
import mediapipe as mp
import time
import numpy as np
import pyautogui
import math
import threading
import json
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import customtkinter as ctk
from PIL import Image, ImageTk

# اضافه کردن مسیر فعلی به sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from local_ai_controller import LocalAIController
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("کنترلر AI در دسترس نیست.........................")

class FixedHandController:
    def __init__(self):
        """کنترلر دست اصلاح شده"""
        print("🚀 در حال راه‌اندازی Hand Controller Pro v3.0...")
        
        # راه‌اندازی اولیه
        self.setup_camera()
        self.setup_mediapipe()
        self.setup_audio()
        self.setup_ai_controller()
        
        # متغیرهای کنترل
        self.state = "CALIBRATING"
        self.last_state_change_time = 0
        self.calibration_step = 0
        self.calibration_timer = time.time()
        
        # متغیرهای ماوس
        self.smoothening = 5
        self.plocX, self.plocY = 0, 0
        self.is_dragging = False
        self.click_cooldown = 0
        self.CLICK_DELAY = 0.25
        
        # تنظیمات کالیبراسیون
        self.calibrated_thresholds = {
            "CLICK_DISTANCE": 35,
            "VOL_MIN_DIST": 30,
            "VOL_MAX_DIST": 200,
        }
        
        # متغیرهای رابط کاربری
        self.root = None
        self.setup_gui()
        
        # متغیرهای تجاری
        self.session_data = {
            "start_time": time.time(),
            "commands_executed": 0,
            "gestures_detected": 0,
            "errors": 0
        }
        
        # کیبورد مجازی پیشرفته
        self.setup_virtual_keyboard()
        
        # قابلیت‌های پیشرفته
        self.gesture_history = []
        self.performance_metrics = {}
        self.previous_hand_landmarks = {'left': None, 'right': None} # برای ردیابی ژست‌های پیچیده‌تر
        
        print("✅ راه‌اندازی کامل شد!")
        
    def setup_camera(self):
        """راه‌اندازی دوربین"""
        self.wCam, self.hCam = 1280, 720
        # تلاش برای باز کردن دوربین‌های مختلف
        for camera_id in [ 1, 2]:
            self.cap = cv2.VideoCapture(camera_id)
            if self.cap.isOpened():
                print(f"✅ دوربین {camera_id} با موفقیت باز شد")
                break
        else:
            print("❌ هیچ دوربینی پیدا نشد!")
            self.cap = cv2.VideoCapture(0)  # fallback به دوربین پیش‌فرض
            
        self.cap.set(3, self.wCam)
        self.cap.set(4, self.hCam)
        self.frame_reduction = 100
        
    def setup_mediapipe(self):
        """راه‌اندازی MediaPipe"""
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2, 
            min_detection_confidence=0.7,  # کاهش حساسیت برای تشخیص بهتر
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        print("✅ MediaPipe با موفقیت راه‌اندازی شد")
        
    def setup_audio(self):
        """راه‌اندازی کنترل صدا"""
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume = cast(interface, POINTER(IAudioEndpointVolume))
            volRange = self.volume.GetVolumeRange()
            self.minVol, self.maxVol = volRange[0], volRange[1]
            self.volume_control_enabled = True
            print("✅ کنترل صدا فعال شد")
        except Exception as e:
            print(f"❌ خطا در راه‌اندازی کنترل صدا: {e}")
            self.volume_control_enabled = False
            
    def setup_ai_controller(self):
        """راه‌اندازی کنترلر AI"""
        if AI_AVAILABLE:
            try:
                self.ai_controller = LocalAIController()
                print("✅ کنترلر AI فعال شد")
            except Exception as e:
                print(f"❌ خطا در راه‌اندازی AI: {e}")
                self.ai_controller = None
        else:
            self.ai_controller = None
            print("⚠️ کنترلر AI در دسترس نیست")
        
    def setup_gui(self):
        """راه‌اندازی رابط کاربری"""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("Advanced Hand Controller Pro v3.0 - Fixed")
        self.root.geometry("400x600")
        
        # ایجاد ویجت‌ها
        self.create_gui_widgets()
        
    def create_gui_widgets(self):
        """ایجاد ویجت‌های رابط کاربری"""
        # عنوان
        title_label = ctk.CTkLabel(
            self.root, 
            text="Hand Controller Pro v3.0",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # وضعیت
        self.status_label = ctk.CTkLabel(
            self.root,
            text="Status: Ready",
            font=ctk.CTkFont(size=16)
        )
        self.status_label.pack(pady=10)
        
        # دکمه‌های کنترل
        self.start_button = ctk.CTkButton(
            self.root,
            text="Start Control",
            command=self.start_control,
            width=200,
            height=40
        )
        self.start_button.pack(pady=10)
        
        self.stop_button = ctk.CTkButton(
            self.root,
            text="Stop Control",
            command=self.stop_control,
            width=200,
            height=40,
            state="disabled"
        )
        self.stop_button.pack(pady=10)
        
        # دکمه کنترل صوتی
        if self.ai_controller:
            self.voice_button = ctk.CTkButton(
                self.root,
                text="Start Voice Control",
                command=self.toggle_voice_control,
                width=200,
                height=40
            )
            self.voice_button.pack(pady=10)
        
        # نمایش آمار
        self.stats_frame = ctk.CTkFrame(self.root)
        self.stats_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        self.stats_label = ctk.CTkLabel(
            self.stats_frame,
            text="Statistics:\nCommands: 0\nGestures: 0\nErrors: 0",
            font=ctk.CTkFont(size=14)
        )
        self.stats_label.pack(pady=10)
        
    def setup_virtual_keyboard(self):
        """راه‌اندازی کیبورد مجازی پیشرفته"""
        class AdvancedButton:
            def __init__(self, pos, text, size=[80, 80], color=(100, 0, 100)):
                self.pos = pos
                self.size = size
                self.text = text
                self.color = color
                self.is_pressed = False
                
        # کیبورد فارسی و انگلیسی
        self.keys = [
            ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
            ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"],
            ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
        ]
        
        self.buttonList = []
        for i in range(len(self.keys)):
            for j, key in enumerate(self.keys[i]):
                self.buttonList.append(AdvancedButton([100 * j + 50, 100 * i + 150], key))
        
        # دکمه‌های ویژه
        self.buttonList.append(AdvancedButton([50, 450], "Space", [400, 80], (0, 100, 100)))
        self.buttonList.append(AdvancedButton([460, 450], "<-", [100, 80], (100, 100, 0)))
        self.buttonList.append(AdvancedButton([570, 450], "Enter", [100, 80], (0, 100, 0)))
        self.buttonList.append(AdvancedButton([680, 450], "Exit", [150, 80], (100, 0, 0)))
        
        self.final_text = ""
        
    def detect_advanced_gestures(self, image, left_hand_landmarks, right_hand_landmarks):
        """تشخیص ژست‌های پیشرفته (مانند اسکرول، زوم) و اجرای دستورات مربوطه"""
        if left_hand_landmarks and right_hand_landmarks:
            # ژست با دو دست (مثلاً زوم)
            # محاسبه مرکز هر دست
            left_cx = int(sum([lm.x for lm in left_hand_landmarks.landmark]) / len(left_hand_landmarks.landmark) * self.wCam)
            left_cy = int(sum([lm.y for lm in left_hand_landmarks.landmark]) / len(left_hand_landmarks.landmark) * self.hCam)
            right_cx = int(sum([lm.x for lm in right_hand_landmarks.landmark]) / len(right_hand_landmarks.landmark) * self.wCam)
            right_cy = int(sum([lm.y for lm in right_hand_landmarks.landmark]) / len(right_hand_landmarks.landmark) * self.hCam)

            # محاسبه فاصله بین مراکز دو دست
            current_hands_distance = math.hypot(right_cx - left_cx, right_cy - left_cy)

            if self.previous_hand_landmarks['left'] and self.previous_hand_landmarks['right']:
                prev_left_cx = int(sum([lm.x for lm in self.previous_hand_landmarks['left'].landmark]) / len(self.previous_hand_landmarks['left'].landmark) * self.wCam)
                prev_left_cy = int(sum([lm.y for lm in self.previous_hand_landmarks['left'].landmark]) / len(self.previous_hand_landmarks['left'].landmark) * self.hCam)
                prev_right_cx = int(sum([lm.x for lm in self.previous_hand_landmarks['right'].landmark]) / len(self.previous_hand_landmarks['right'].landmark) * self.wCam)
                prev_right_cy = int(sum([lm.y for lm in self.previous_hand_landmarks['right'].landmark]) / len(self.previous_hand_landmarks['right'].landmark) * self.hCam)

                prev_hands_distance = math.hypot(prev_right_cx - prev_left_cx, prev_right_cy - prev_left_cy)

                distance_diff = current_hands_distance - prev_hands_distance
                zoom_threshold = 15 # حداقل تغییر فاصله برای تشخیص زوم

                if abs(distance_diff) > zoom_threshold:
                    if distance_diff > 0: # دست‌ها از هم دور می‌شوند: زوم به بیرون
                        pyautogui.hotkey('ctrl', '-')
                        self.draw_text_with_bg(image, "Zoom Out", (self.wCam // 2 - 100, 50), color=(0, 255, 255))
                        print("🔍 زوم به بیرون")
                    else: # دست‌ها به هم نزدیک می‌شوند: زوم به داخل
                        pyautogui.hotkey('ctrl', '+')
                        self.draw_text_with_bg(image, "Zoom In", (self.wCam // 2 - 100, 50), color=(0, 255, 255))
                        print("🔎 زوم به داخل")
                    self.session_data["commands_executed"] += 1
                    self.last_state_change_time = time.time() # جلوگیری از تغییر حالت ناخواسته


        elif right_hand_landmarks:
            current_right_hand_data = self.get_finger_states(right_hand_landmarks, "right")
            current_right_fingers = current_right_hand_data["finger_states"]
            current_thumb_index_dist = current_right_hand_data["thumb_index_dist"]

            # ژست اسکرول با دست راست (انگشت اشاره و میانی به سمت بالا/پایین)
            # تنها انگشت اشاره و میانی باز باشند و فاصله بین آنها ثابت و نزدیک باشد
            if current_right_fingers[1] == 1 and current_right_fingers[2] == 1 and sum(current_right_fingers) == 2:
                # بررسی حرکت عمودی انگشت اشاره
                if self.previous_hand_landmarks['right']:
                    prev_index_tip_y = self.previous_hand_landmarks['right'].landmark[8].y * self.hCam
                    current_index_tip_y = right_hand_landmarks.landmark[8].y * self.hCam

                    delta_y = current_index_tip_y - prev_index_tip_y
                    scroll_threshold = 10 # حداقل حرکت برای تشخیص اسکرول

                    if abs(delta_y) > scroll_threshold:
                        if delta_y < 0: # حرکت به بالا
                            pyautogui.scroll(100)
                            self.draw_text_with_bg(image, "Scroll Up", (self.wCam - 200, 50), color=(0, 255, 0))
                            print("⬆️ اسکرول به بالا")
                        else: # حرکت به پایین
                            pyautogui.scroll(-100)
                            self.draw_text_with_bg(image, "Scroll Down", (self.wCam - 200, 50), color=(0, 255, 0))
                            print("⬇️ اسکرول به پایین")
                        self.session_data["commands_executed"] += 1
                        self.last_state_change_time = time.time() # جلوگیری از تغییر حالت ناخواسته

            # اضافه کردن ژست‌های دیگر تک دستی راست در اینجا

        elif left_hand_landmarks:
            # ژست‌های تک دستی با دست چپ (فعلاً فقط برای تغییر حالت استفاده می‌شود)
            pass
        
    def get_finger_states(self, hand_landmarks, hand_type):
        """تشخیص وضعیت انگشتان و محاسبه فواصل کلیدی بین انگشتان"""
        finger_tips = [4, 8, 12, 16, 20]
        states = []
        
        # انگشت شست
        if hand_type.lower() == 'right':
            states.append(1 if hand_landmarks.landmark[finger_tips[0]].x > hand_landmarks.landmark[finger_tips[0] - 1].x else 0)
        else:
            states.append(1 if hand_landmarks.landmark[finger_tips[0]].x < hand_landmarks.landmark[finger_tips[0] - 1].x else 0)
        
        # 4 انگشت دیگر
        for i in range(1, 5):
            states.append(1 if hand_landmarks.landmark[finger_tips[i]].y < hand_landmarks.landmark[finger_tips[i] - 2].y else 0)
            
        # محاسبه فواصل کلیدی
        thumb_tip = (hand_landmarks.landmark[finger_tips[0]].x * self.wCam, hand_landmarks.landmark[finger_tips[0]].y * self.hCam)
        index_tip = (hand_landmarks.landmark[finger_tips[1]].x * self.wCam, hand_landmarks.landmark[finger_tips[1]].y * self.hCam)
        middle_tip = (hand_landmarks.landmark[finger_tips[2]].x * self.wCam, hand_landmarks.landmark[finger_tips[2]].y * self.hCam)
        ring_tip = (hand_landmarks.landmark[finger_tips[3]].x * self.wCam, hand_landmarks.landmark[finger_tips[3]].y * self.hCam)
        pinky_tip = (hand_landmarks.landmark[finger_tips[4]].x * self.wCam, hand_landmarks.landmark[finger_tips[4]].y * self.hCam)

        thumb_index_dist = math.hypot(index_tip[0] - thumb_tip[0], index_tip[1] - thumb_tip[1])
        index_middle_dist = math.hypot(middle_tip[0] - index_tip[0], middle_tip[1] - index_tip[1])
        
        return {"finger_states": states, "thumb_index_dist": thumb_index_dist, "index_middle_dist": index_middle_dist}
        
    def draw_text_with_bg(self, image, text, position, font_scale=1, color=(255, 255, 255), thickness=2, bg_color=(0, 0, 0, 128)):
        """رسم متن با پس‌زمینه"""
        (text_width, text_height), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
        top_left = (position[0] - 5, position[1] - text_height - 10)
        bottom_right = (position[0] + text_width + 5, position[1] + baseline)
        
        overlay = image.copy()
        cv2.rectangle(overlay, top_left, bottom_right, bg_color[:3], cv2.FILLED)
        alpha = bg_color[3] / 255.0 if len(bg_color) > 3 else 0.5
        cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)
        
        cv2.putText(image, text, position, cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness, cv2.LINE_AA)
        
    def run_calibration(self, image, hand_landmarks):
        """کالیبراسیون پیشرفته"""
        if self.calibration_step == 0:
            self.draw_text_with_bg(image, "Step 1: Show OPEN HAND for 3 sec", (50, 50), bg_color=(200,0,0,150))
            if hand_landmarks:
                if time.time() - self.calibration_timer > 3:
                    tx, ty = hand_landmarks.landmark[4].x * self.wCam, hand_landmarks.landmark[4].y * self.hCam
                    ix, iy = hand_landmarks.landmark[8].x * self.wCam, hand_landmarks.landmark[8].y * self.hCam
                    self.calibrated_thresholds["VOL_MAX_DIST"] = max(150, math.hypot(ix - tx, iy - ty))
                    self.calibration_step = 1
                    self.calibration_timer = time.time()
                    print(f"✅ کالیبراسیون MAX distance: {self.calibrated_thresholds['VOL_MAX_DIST']:.2f}")
            else:
                self.calibration_timer = time.time()
        
        elif self.calibration_step == 1:
            self.draw_text_with_bg(image, "Step 2: Bring Thumb & Index together for 3 sec", (50, 50), bg_color=(200,0,0,150))
            if hand_landmarks:
                if time.time() - self.calibration_timer > 3:
                    tx, ty = hand_landmarks.landmark[4].x * self.wCam, hand_landmarks.landmark[4].y * self.hCam
                    ix, iy = hand_landmarks.landmark[8].x * self.wCam, hand_landmarks.landmark[8].y * self.hCam
                    self.calibrated_thresholds["VOL_MIN_DIST"] = math.hypot(ix - tx, iy - ty) + 10
                    
                    ix_tip, iy_tip = hand_landmarks.landmark[8].x * self.wCam, hand_landmarks.landmark[8].y * self.hCam
                    mx_tip, my_tip = hand_landmarks.landmark[12].x * self.wCam, hand_landmarks.landmark[12].y * self.hCam
                    self.calibrated_thresholds["CLICK_DISTANCE"] = math.hypot(ix_tip-mx_tip, iy_tip-my_tip) + 15
                    
                    self.calibration_step = 2
                    print(f"✅ کالیبراسیون MIN distance: {self.calibrated_thresholds['VOL_MIN_DIST']:.2f}")
                    print(f"✅ کالیبراسیون CLICK distance: {self.calibrated_thresholds['CLICK_DISTANCE']:.2f}")
            else:
                self.calibration_timer = time.time()
                
        elif self.calibration_step == 2:
            self.draw_text_with_bg(image, "Calibration Complete!", (50, 50), color=(0, 255, 0), bg_color=(0,100,0,150))
            if time.time() - self.calibration_timer > 2:
                self.state = "IDLE"
                self.update_status("Ready")
                print("✅ کالیبراسیون کامل شد!")
                
    def run_mouse_control(self, image, hand_landmarks):
        """کنترل ماوس پیشرفته"""
        self.draw_text_with_bg(image, "MOUSE CONTROL", (10, 40), color=(0, 255, 255))
        cv2.rectangle(image, (self.frame_reduction, self.frame_reduction), 
                     (self.wCam - self.frame_reduction, self.hCam - self.frame_reduction), (0, 255, 255), 2)

        fingers = self.get_finger_states(hand_landmarks, "right")
        
        # حرکت ماوس
        if fingers["finger_states"][1] == 1 and fingers["finger_states"][2] == 0:
            if self.is_dragging:
                pyautogui.mouseUp(button='left')
                self.is_dragging = False
            
            ix, iy = hand_landmarks.landmark[8].x * self.wCam, hand_landmarks.landmark[8].y * self.hCam
            
            screen_w, screen_h = pyautogui.size()
            x_mapped = np.interp(ix, (self.frame_reduction, self.wCam - self.frame_reduction), (0, screen_w))
            y_mapped = np.interp(iy, (self.frame_reduction, self.hCam - self.frame_reduction), (0, screen_h))
            
            clocX = self.plocX + (x_mapped - self.plocX) / self.smoothening
            clocY = self.plocY + (y_mapped - self.plocY) / self.smoothening
            
            pyautogui.moveTo(clocX, clocY)
            self.plocX, self.plocY = clocX, clocY
            self.session_data["gestures_detected"] += 1

        # کلیک چپ
        if fingers["finger_states"][1] == 1 and fingers["finger_states"][2] == 1:
            ix, iy = hand_landmarks.landmark[8].x * self.wCam, hand_landmarks.landmark[8].y * self.hCam
            mx, my = hand_landmarks.landmark[12].x * self.wCam, hand_landmarks.landmark[12].y * self.hCam
            distance = math.hypot(mx - ix, my - iy)
            
            if distance < self.calibrated_thresholds["CLICK_DISTANCE"] and time.time() > self.click_cooldown:
                pyautogui.click()
                self.click_cooldown = time.time() + self.CLICK_DELAY
                self.session_data["commands_executed"] += 1
                print("🖱️ کلیک چپ انجام شد")

        # کلیک راست
        if fingers["finger_states"][0] == 1 and fingers["finger_states"][1] == 1:
            tx, ty = hand_landmarks.landmark[4].x * self.wCam, hand_landmarks.landmark[4].y * self.hCam
            ix, iy = hand_landmarks.landmark[8].x * self.wCam, hand_landmarks.landmark[8].y * self.hCam
            distance = math.hypot(tx - ix, ty - iy)

            if distance < self.calibrated_thresholds["CLICK_DISTANCE"] and time.time() > self.click_cooldown:
                pyautogui.rightClick()
                self.click_cooldown = time.time() + self.CLICK_DELAY + 0.2
                self.session_data["commands_executed"] += 1
                print("🖱️ کلیک راست انجام شد")

        # Drag and Drop
        if all(f == 0 for f in fingers["finger_states"]):
            if not self.is_dragging:
                pyautogui.mouseDown(button='left')
                self.is_dragging = True
        else:
            if self.is_dragging and not (fingers["finger_states"][1] == 1 and fingers["finger_states"][2] == 0):
                pyautogui.mouseUp(button='left')
                self.is_dragging = False
                
    def run_system_control(self, image, hand_landmarks):
        """کنترل سیستم پیشرفته"""
        self.draw_text_with_bg(image, "SYSTEM CONTROL", (10, 40), color=(0, 255, 0))
        if not self.volume_control_enabled:
            self.draw_text_with_bg(image, "Volume control disabled", (10, 80), color=(255, 0, 0))
            return

        tx, ty = hand_landmarks.landmark[4].x * self.wCam, hand_landmarks.landmark[4].y * self.hCam
        ix, iy = hand_landmarks.landmark[8].x * self.wCam, hand_landmarks.landmark[8].y * self.hCam
        
        cv2.circle(image, (int(tx), int(ty)), 10, (0, 255, 0), cv2.FILLED)
        cv2.circle(image, (int(ix), int(iy)), 10, (0, 255, 0), cv2.FILLED)
        cv2.line(image, (int(tx), int(ty)), (int(ix), int(iy)), (0, 255, 0), 3)

        length_vol = math.hypot(ix - tx, iy - ty)
        
        vol = np.interp(length_vol, [self.calibrated_thresholds["VOL_MIN_DIST"], self.calibrated_thresholds["VOL_MAX_DIST"]], [self.minVol, self.maxVol])
        vol_bar = np.interp(length_vol, [self.calibrated_thresholds["VOL_MIN_DIST"], self.calibrated_thresholds["VOL_MAX_DIST"]], [400, 150])
        vol_per = np.interp(length_vol, [self.calibrated_thresholds["VOL_MIN_DIST"], self.calibrated_thresholds["VOL_MAX_DIST"]], [0, 100])
        
        self.volume.SetMasterVolumeLevel(vol, None)
        
        cv2.rectangle(image, (50, 150), (85, 400), (0, 255, 0), 3)
        cv2.rectangle(image, (50, int(vol_bar)), (85, 400), (0, 255, 0), cv2.FILLED)
        cv2.putText(image, f'{int(vol_per)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)
        
    def run_keyboard_mode(self, image, hand_landmarks):
        """حالت کیبورد پیشرفته"""
        image = self.draw_keyboard(image, self.buttonList)
        ix, iy = hand_landmarks.landmark[8].x * self.wCam, hand_landmarks.landmark[8].y * self.hCam
        
        for button in self.buttonList:
            x, y = button.pos
            w, h = button.size
            if x < ix < x + w and y < iy < y + h:
                cv2.rectangle(image, (x - 5, y - 5), (x + w + 5, y + h + 5), (175, 0, 175), cv2.FILLED)
                cv2.putText(image, button.text, (x + 20, y + 60), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                
                fingers = self.get_finger_states(hand_landmarks, "right")
                if fingers["finger_states"][1] == 1 and fingers["finger_states"][2] == 1:
                    mx, my = hand_landmarks.landmark[12].x * self.wCam, hand_landmarks.landmark[12].y * self.hCam
                    distance = math.hypot(mx - ix, my - iy)
                    
                    if distance < self.calibrated_thresholds["CLICK_DISTANCE"] * 1.2 and time.time() > self.click_cooldown:
                        if button.text == "Exit": 
                            self.state = "IDLE"
                        elif button.text == "<-": 
                            pyautogui.press('backspace')
                            self.final_text = self.final_text[:-1]
                        elif button.text == "Space": 
                            pyautogui.press('space')
                            self.final_text += " "
                        elif button.text == "Enter":
                            pyautogui.press('enter')
                            self.final_text += "\n"
                        else: 
                            pyautogui.press(button.text)
                            self.final_text += button.text
                        
                        self.click_cooldown = time.time() + self.CLICK_DELAY + 0.3
                        cv2.rectangle(image, (x - 5, y - 5), (x + w + 5, y + h + 5), (0, 255, 0), cv2.FILLED)
                        self.session_data["commands_executed"] += 1
                        print(f"⌨️ کلید {button.text} فشرده شد")

        cv2.rectangle(image, (50, 550), (1200, 650), (50, 50, 50), cv2.FILLED)
        cv2.putText(image, self.final_text, (60, 620), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
        return image
        
    def draw_keyboard(self, image, buttonList):
        """رسم کیبورد مجازی"""
        img_new = np.zeros_like(image, np.uint8)
        for button in buttonList:
            x, y = button.pos
            w, h = button.size
            color = button.color if hasattr(button, 'color') else (100, 0, 100)
            cv2.rectangle(img_new, (x, y), (x + w, y + h), color, cv2.FILLED)
            cv2.putText(img_new, button.text, (x + 20, y + 60), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
        
        out = image.copy()
        alpha = 0.5
        mask = img_new.astype(bool)
        out[mask] = cv2.addWeighted(image, alpha, img_new, 1 - alpha, 0)[mask]
        return out
        
    def start_control(self):
        """شروع کنترل"""
        self.state = "CALIBRATING"
        self.calibration_step = 0
        self.calibration_timer = time.time()
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.update_status("Calibrating...")
        
        # شروع حلقه اصلی در thread جداگانه
        self.control_thread = threading.Thread(target=self.main_loop)
        self.control_thread.daemon = True
        self.control_thread.start()
        
    def stop_control(self):
        """توقف کنترل"""
        self.state = "STOPPED"
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.update_status("Stopped")
        
    def toggle_voice_control(self):
        """تغییر حالت کنترل صوتی"""
        if not hasattr(self, 'voice_control_active'):
            self.voice_control_active = False
            
        if not self.voice_control_active:
            self.voice_control_active = True
            self.voice_button.configure(text="Stop Voice Control")
            if self.ai_controller:
                self.ai_controller.start_voice_control()
        else:
            self.voice_control_active = False
            self.voice_button.configure(text="Start Voice Control")
            if self.ai_controller:
                self.ai_controller.stop_voice_control()
            
    def update_status(self, status):
        """به‌روزرسانی وضعیت"""
        self.status_label.configure(text=f"Status: {status}")
        
    def update_stats(self):
        """به‌روزرسانی آمار"""
        stats_text = f"""Statistics:
Commands: {self.session_data['commands_executed']}
Gestures: {self.session_data['gestures_detected']}
Errors: {self.session_data['errors']}
Uptime: {int(time.time() - self.session_data['start_time'])}s"""
        self.stats_label.configure(text=stats_text)
        
    def main_loop(self):
        """حلقه اصلی برنامه"""
        print("🎯 شروع حلقه اصلی...")
        while self.state != "STOPPED":
            try:
                success, image = self.cap.read()
                if not success: 
                    print("❌ خطا در خواندن تصویر از دوربین")
                    continue
                    
                image = cv2.flip(image, 1)
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = self.hands.process(image_rgb)
                
                left_hand, right_hand = None, None
                
                if results.multi_hand_landmarks:
                    for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                        hand_type = results.multi_handedness[i].classification[0].label
                        if hand_type == "Left":
                            left_hand = hand_landmarks
                        else:
                            right_hand = hand_landmarks
                    
                    if left_hand:
                        self.mp_drawing.draw_landmarks(image, left_hand, self.mp_hands.HAND_CONNECTIONS)
                        self.previous_hand_landmarks['left'] = left_hand # ذخیره برای ردیابی ژست‌های پیشرفته
                    if right_hand:
                        self.mp_drawing.draw_landmarks(image, right_hand, self.mp_hands.HAND_CONNECTIONS)
                        self.previous_hand_landmarks['right'] = right_hand # ذخیره برای ردیابی ژست‌های پیشرفته
                else:
                    self.previous_hand_landmarks = {'left': None, 'right': None} # اگر دستی شناسایی نشد، ریست کن

                # تشخیص ژست‌های پیشرفته قبل از کنترل حالت عادی
                self.detect_advanced_gestures(image, left_hand, right_hand)

                # اجرای حالت‌ها
                if self.state == "CALIBRATING":
                    active_hand = left_hand or right_hand
                    self.run_calibration(image, active_hand)
                
                elif self.state == "IDLE":
                    self.draw_text_with_bg(image, "IDLE", (10, 40), color=(255, 255, 0))
                    self.draw_text_with_bg(image, "Use Left Hand to Select Mode:", (10, 80), 0.7)
                    self.draw_text_with_bg(image, "1 Finger: Mouse | 2 Fingers: System | 3 Fingers: Keyboard", (10, 110), 0.7)
                    self.draw_text_with_bg(image, "Open Palm (5 Fingers): Back to IDLE", (10, 140), 0.7)

                # کنترل حالت‌های ماوس، سیستم و کیبورد فقط اگر ژست پیشرفته فعال نباشد
                elif right_hand and time.time() - self.last_state_change_time > 0.5: # تاخیر برای جلوگیری از تداخل با ژست‌های پیشرفته
                    if self.state == "MOUSE_CONTROL":
                        self.run_mouse_control(image, right_hand)
                    elif self.state == "SYSTEM_CONTROL":
                        self.run_system_control(image, right_hand)
                    elif self.state == "KEYBOARD_MODE":
                        image = self.run_keyboard_mode(image, right_hand)
                elif self.state != "CALIBRATING" and self.state != "IDLE":
                     self.draw_text_with_bg(image, f"Show Right Hand to use {self.state}", (self.wCam//2 - 200, self.hCam//2), color=(0,0,255))

                # کنترل تغییر حالت با دست چپ
                if left_hand and time.time() - self.last_state_change_time > 1.0:
                    left_fingers_data = self.get_finger_states(left_hand, "Left")
                    left_fingers = left_fingers_data["finger_states"]
                    
                    if sum(left_fingers) == 5 and self.state != "IDLE" and self.state != "CALIBRATING":
                        self.state = "IDLE"
                        self.final_text = ""
                        self.last_state_change_time = time.time()
                        self.update_status("IDLE")
                        print("🔄 بازگشت به حالت IDLE")
                    
                    elif self.state == "IDLE":
                        if sum(left_fingers) == 1 and left_fingers[1] == 1:
                            self.state = "MOUSE_CONTROL"
                            self.last_state_change_time = time.time()
                            self.update_status("Mouse Control")
                            print("🖱️ تغییر به حالت کنترل ماوس")
                        elif sum(left_fingers) == 2 and left_fingers[1] == 1 and left_fingers[2] == 1:
                            self.state = "SYSTEM_CONTROL"
                            self.last_state_change_time = time.time()
                            self.update_status("System Control")
                            print("🔊 تغییر به حالت کنترل سیستم")
                        elif sum(left_fingers) == 3 and left_fingers[1] == 1 and left_fingers[2] == 1 and left_fingers[3] == 1:
                            self.state = "KEYBOARD_MODE"
                            self.last_state_change_time = time.time()
                            self.update_status("Keyboard Mode")
                            print("⌨️ تغییر به حالت کیبورد")

                # به‌روزرسانی آمار
                self.update_stats()
                
                cv2.imshow("Advanced Hand Controller Pro v3.0 - Fixed", image)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("🛑 خروج از برنامه...")
                    break
                    
            except Exception as e:
                print(f"❌ خطا در حلقه اصلی: {e}")
                self.session_data["errors"] += 1
                time.sleep(0.1)
                
        self.cap.release()
        cv2.destroyAllWindows()
        print("✅ برنامه با موفقیت بسته شد")
        
    def run(self):
        """اجرای برنامه"""
        print("🚀 شروع برنامه...")
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("🛑 برنامه توسط کاربر متوقف شد")
        except Exception as e:
            print(f"❌ خطای غیرمنتظره: {e}")
        finally:
            if hasattr(self, 'cap'):
                self.cap.release()
            cv2.destroyAllWindows()

def main():
    """تابع اصلی"""
    print("=" * 50)
    print("Hand Controller Pro v3.0 - Fixed Version")
    print("=" * 50)
    
    try:
        controller = FixedHandController()
        controller.run()
    except Exception as e:
        print(f"❌ خطا در راه‌اندازی: {e}")
        input("برای خروج Enter را فشار دهید...")

if __name__ == "__main__":
    main()
