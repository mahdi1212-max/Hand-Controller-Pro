"""
فایل اصلی اجرای کنترلر دست پیشرفته
Main execution file for Advanced Hand Controller
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
import time

# اضافه کردن مسیر فعلی به sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from advanced_hand_controller import AdvancedHandController
    from local_ai_controller import LocalAIController
except ImportError as e:
    print(f"خطا در import کردن ماژول‌ها: {e}")
    print("لطفاً ابتدا requirements.txt را نصب کنید:")
    print("pip install -r requirements.txt")
    sys.exit(1)

class MainApplication:
    def __init__(self):
        """برنامه اصلی"""
        self.root = tk.Tk()
        self.root.title("Hand Controller Pro v3.0 - Launcher")
        self.root.geometry("600x500")
        self.root.configure(bg='#2b2b2b')
        
        # متغیرهای کنترل
        self.hand_controller = None
        self.ai_controller = None
        self.is_running = False
        
        # ایجاد رابط کاربری
        self.create_launcher_ui()
        
    def create_launcher_ui(self):
        """ایجاد رابط کاربری launcher"""
        # عنوان اصلی
        title_label = tk.Label(
            self.root,
            text="Hand Controller Pro v3.0",
            font=("Arial", 24, "bold"),
            fg="white",
            bg="#2b2b2b"
        )
        title_label.pack(pady=20)
        
        # توضیحات
        desc_label = tk.Label(
            self.root,
            text="کنترلر دست پیشرفته با هوش مصنوعی\nAdvanced Hand Gesture Controller with AI",
            font=("Arial", 12),
            fg="lightgray",
            bg="#2b2b2b"
        )
        desc_label.pack(pady=10)
        
        # دکمه‌های اصلی
        button_frame = tk.Frame(self.root, bg="#2b2b2b")
        button_frame.pack(pady=30)
        
        # دکمه شروع کنترل دست
        self.start_hand_btn = tk.Button(
            button_frame,
            text="شروع کنترل دست\nStart Hand Control",
            font=("Arial", 14, "bold"),
            bg="#4CAF50",
            fg="white",
            width=20,
            height=3,
            command=self.start_hand_control
        )
        self.start_hand_btn.pack(pady=10)
        
        # دکمه شروع کنترل صوتی
        self.start_voice_btn = tk.Button(
            button_frame,
            text="شروع کنترل صوتی\nStart Voice Control",
            font=("Arial", 14, "bold"),
            bg="#2196F3",
            fg="white",
            width=20,
            height=3,
            command=self.start_voice_control
        )
        self.start_voice_btn.pack(pady=10)
        
        # دکمه شروع ترکیبی
        self.start_combined_btn = tk.Button(
            button_frame,
            text="شروع ترکیبی\nStart Combined Mode",
            font=("Arial", 14, "bold"),
            bg="#FF9800",
            fg="white",
            width=20,
            height=3,
            command=self.start_combined_mode
        )
        self.start_combined_btn.pack(pady=10)
        
        # دکمه تنظیمات
        self.settings_btn = tk.Button(
            button_frame,
            text="تنظیمات\nSettings",
            font=("Arial", 12),
            bg="#9C27B0",
            fg="white",
            width=15,
            height=2,
            command=self.open_settings
        )
        self.settings_btn.pack(pady=10)
        
        # دکمه خروج
        self.exit_btn = tk.Button(
            button_frame,
            text="خروج\nExit",
            font=("Arial", 12),
            bg="#F44336",
            fg="white",
            width=15,
            height=2,
            command=self.exit_application
        )
        self.exit_btn.pack(pady=10)
        
        # وضعیت
        self.status_label = tk.Label(
            self.root,
            text="آماده برای شروع\nReady to Start",
            font=("Arial", 10),
            fg="lightgreen",
            bg="#2b2b2b"
        )
        self.status_label.pack(pady=20)
        
        # اطلاعات نسخه
        version_label = tk.Label(
            self.root,
            text="Version 3.0 | Powered by AI | Open Source",
            font=("Arial", 8),
            fg="gray",
            bg="#2b2b2b"
        )
        version_label.pack(side="bottom", pady=5)
        
    def start_hand_control(self):
        """شروع کنترل دست"""
        try:
            self.update_status("در حال راه‌اندازی کنترل دست...")
            self.hand_controller = AdvancedHandController()
            
            # مخفی کردن launcher و نمایش کنترلر دست
            self.root.withdraw()
            
            # اجرای کنترلر دست در thread اصلی
            self.hand_controller.run()
            
            self.is_running = True
            self.update_status("کنترل دست فعال شد")
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در شروع کنترل دست: {str(e)}")
            self.update_status("خطا در راه‌اندازی")
            # نمایش مجدد launcher در صورت خطا
            self.root.deiconify()
            
    def start_voice_control(self):
        """شروع کنترل صوتی"""
        try:
            self.update_status("در حال راه‌اندازی کنترل صوتی...")
            self.ai_controller = LocalAIController()
            
            # اجرا در thread جداگانه
            voice_thread = threading.Thread(target=self.ai_controller.start_voice_control)
            voice_thread.daemon = True
            voice_thread.start()
            
            self.is_running = True
            self.update_status("کنترل صوتی فعال شد")
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در شروع کنترل صوتی: {str(e)}")
            self.update_status("خطا در راه‌اندازی")
            
    def start_combined_mode(self):
        """شروع حالت ترکیبی"""
        try:
            self.update_status("در حال راه‌اندازی حالت ترکیبی...")
            
            # راه‌اندازی هر دو سیستم
            self.hand_controller = AdvancedHandController()
            self.ai_controller = LocalAIController()
            
            # اجرا در thread های جداگانه
            hand_thread = threading.Thread(target=self.hand_controller.run)
            hand_thread.daemon = True
            hand_thread.start()
            
            time.sleep(2)  # تاخیر کوتاه
            
            voice_thread = threading.Thread(target=self.ai_controller.start_voice_control)
            voice_thread.daemon = True
            voice_thread.start()
            
            self.is_running = True
            self.update_status("حالت ترکیبی فعال شد - دست + صدا")
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در شروع حالت ترکیبی: {str(e)}")
            self.update_status("خطا در راه‌اندازی")
            
    def open_settings(self):
        """باز کردن تنظیمات"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("تنظیمات - Settings")
        settings_window.geometry("500x400")
        settings_window.configure(bg='#2b2b2b')
        
        # عنوان تنظیمات
        title_label = tk.Label(
            settings_window,
            text="تنظیمات پیشرفته",
            font=("Arial", 18, "bold"),
            fg="white",
            bg="#2b2b2b"
        )
        title_label.pack(pady=20)
        
        # تنظیمات دوربین
        camera_frame = tk.LabelFrame(
            settings_window,
            text="تنظیمات دوربین",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#2b2b2b"
        )
        camera_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Label(camera_frame, text="کیفیت تصویر:", fg="white", bg="#2b2b2b").pack(anchor="w", padx=10)
        quality_var = tk.StringVar(value="720p")
        quality_combo = tk.OptionMenu(camera_frame, quality_var, "480p", "720p", "1080p")
        quality_combo.pack(anchor="w", padx=10, pady=5)
        
        # تنظیمات تشخیص
        detection_frame = tk.LabelFrame(
            settings_window,
            text="تنظیمات تشخیص",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#2b2b2b"
        )
        detection_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Label(detection_frame, text="حساسیت تشخیص:", fg="white", bg="#2b2b2b").pack(anchor="w", padx=10)
        sensitivity_var = tk.StringVar(value="متوسط")
        sensitivity_combo = tk.OptionMenu(detection_frame, sensitivity_var, "کم", "متوسط", "زیاد")
        sensitivity_combo.pack(anchor="w", padx=10, pady=5)
        
        # دکمه ذخیره
        save_btn = tk.Button(
            settings_window,
            text="ذخیره تنظیمات",
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            command=lambda: self.save_settings(quality_var.get(), sensitivity_var.get())
        )
        save_btn.pack(pady=20)
        
    def save_settings(self, quality, sensitivity):
        """ذخیره تنظیمات"""
        messagebox.showinfo("موفق", "تنظیمات ذخیره شد")
        
    def update_status(self, message):
        """به‌روزرسانی وضعیت"""
        self.status_label.config(text=message)
        self.root.update()
        
    def exit_application(self):
        """خروج از برنامه"""
        if self.is_running:
            result = messagebox.askyesno("تأیید خروج", "آیا مطمئن هستید که می‌خواهید خارج شوید؟")
            if result:
                self.cleanup()
                self.root.quit()
        else:
            self.root.quit()
            
    def cleanup(self):
        """پاکسازی منابع"""
        if self.hand_controller:
            self.hand_controller.stop_control()
        if self.ai_controller:
            self.ai_controller.stop_voice_control()
            
    def run(self):
        """اجرای برنامه اصلی"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.exit_application)
            self.root.mainloop()
        except KeyboardInterrupt:
            self.cleanup()
        except Exception as e:
            messagebox.showerror("خطای غیرمنتظره", f"خطا: {str(e)}")
            self.cleanup()

def check_dependencies():
    """بررسی وابستگی‌ها"""
    required_packages = [
        'cv2', 'mediapipe', 'numpy', 'pyautogui', 
        'pycaw', 'pyttsx3'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("بسته‌های زیر نصب نشده‌اند:")
        for package in missing_packages:
            print(f"- {package}")
        print("\nبرای نصب، دستور زیر را اجرا کنید:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def main():
    """تابع اصلی"""
    print("Hand Controller Pro v3.0")
    print("=" * 40)
    
    # بررسی وابستگی‌ها
    if not check_dependencies():
        input("برای خروج Enter را فشار دهید...")
        return
    
    print("همه وابستگی‌ها موجود است")
    print("در حال راه‌اندازی...")
    
    # اجرای برنامه
    app = MainApplication()
    app.run()

if __name__ == "__main__":
    main()
