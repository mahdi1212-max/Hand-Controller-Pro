"""
سیستم کنترل صوتی پیشرفته با هوش مصنوعی
Advanced AI Voice Control System
"""

import speech_recognition as sr
import pyttsx3
import openai
import threading
import time
import json
import os
from typing import Dict, List, Callable
import requests
import subprocess
import webbrowser
import pyautogui
import psutil

class AIVoiceController:
    def __init__(self, openai_api_key: str = None):
        """
        کنترلر صوتی هوش مصنوعی پیشرفته
        
        Args:
            openai_api_key: کلید API OpenAI (اختیاری)
        """
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        
        # راه‌اندازی تشخیص صدا
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # راه‌اندازی تبدیل متن به گفتار
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)
        self.tts_engine.setProperty('volume', 0.8)
        
        # تنظیمات OpenAI
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        
        # دیکشنری دستورات
        self.commands = {
            # دستورات سیستم
            "باز کن": self.open_application,
            "بستن": self.close_application,
            "کامپیوتر را خاموش کن": self.shutdown_computer,
            "کامپیوتر را ریست کن": self.restart_computer,
            "صدا را کم کن": self.volume_down,
            "صدا را زیاد کن": self.volume_up,
            "صدا را قطع کن": self.mute_volume,
            
            # دستورات مرورگر
            "کروم را باز کن": lambda: self.open_application("chrome"),
            "فایرفاکس را باز کن": lambda: self.open_application("firefox"),
            "یوتیوب را باز کن": self.open_youtube,
            "گوگل را باز کن": self.open_google,
            "جستجو کن": self.search_web,
            
            # دستورات فایل
            "فایل اکسپلورر را باز کن": self.open_file_explorer,
            "دسکتاپ را نشان بده": self.show_desktop,
            "همه پنجره‌ها را کوچک کن": self.minimize_all_windows,
            
            # دستورات هوش مصنوعی
            "چی می‌دونی": self.ai_knowledge,
            "کمکم کن": self.ai_help,
            "برنامه‌نویسی": self.programming_help,
            "ترجمه کن": self.translate_text,
        }
        
        # حالت‌های مختلف
        self.current_mode = "normal"  # normal, programming, web, system
        self.is_listening = False
        self.last_command_time = 0
        
        # تنظیم میکروفون
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
    
    def speak(self, text: str):
        """تبدیل متن به گفتار"""
        def speak_thread():
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        
        thread = threading.Thread(target=speak_thread)
        thread.daemon = True
        thread.start()
    
    def listen(self) -> str:
        """شنیدن و تشخیص دستور صوتی"""
        try:
            with self.microphone as source:
                print("گوش می‌دهم...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            # تشخیص با Google Speech Recognition
            text = self.recognizer.recognize_google(audio, language='fa-IR')
            print(f"تشخیص داده شد: {text}")
            return text.lower()
            
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            print(f"خطا در تشخیص صدا: {e}")
            return ""
    
    def process_command(self, command: str) -> bool:
        """پردازش دستور صوتی"""
        if not command:
            return False
        
        # جستجوی دستور در دیکشنری
        for key, func in self.commands.items():
            if key in command:
                try:
                    func(command)
                    self.speak("انجام شد")
                    return True
                except Exception as e:
                    print(f"خطا در اجرای دستور: {e}")
                    self.speak("خطا در اجرای دستور")
                    return False
        
        # اگر دستور پیدا نشد، از AI استفاده کن
        return self.handle_ai_command(command)
    
    def handle_ai_command(self, command: str) -> bool:
        """پردازش دستورات پیچیده با AI"""
        if not self.openai_api_key:
            self.speak("کلید API OpenAI تنظیم نشده است")
            return False
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "شما یک دستیار هوشمند فارسی هستید که دستورات کاربر را اجرا می‌کنید. فقط کد پایتون ساده برای اجرای دستورات ارائه دهید."},
                    {"role": "user", "content": f"این دستور را اجرا کن: {command}"}
                ],
                max_tokens=500
            )
            
            ai_response = response.choices[0].message.content
            print(f"پاسخ AI: {ai_response}")
            
            # اجرای کد تولید شده توسط AI
            if "pyautogui" in ai_response or "subprocess" in ai_response:
                exec(ai_response)
                self.speak("دستور اجرا شد")
                return True
            else:
                self.speak(ai_response)
                return True
                
        except Exception as e:
            print(f"خطا در AI: {e}")
            self.speak("خطا در پردازش دستور")
            return False
    
    # دستورات سیستم
    def open_application(self, command: str):
        """باز کردن برنامه‌ها"""
        apps = {
            "کروم": "chrome",
            "فایرفاکس": "firefox",
            "نوت پد": "notepad",
            "ماشین حساب": "calc",
            "پینت": "mspaint",
            "وورد": "winword",
            "اکسل": "excel",
            "پاورپوینت": "powerpnt"
        }
        
        for app_name, app_path in apps.items():
            if app_name in command:
                subprocess.Popen(app_path)
                break
    
    def close_application(self, command: str):
        """بستن برنامه‌ها"""
        if "کروم" in command:
            os.system("taskkill /f /im chrome.exe")
        elif "فایرفاکس" in command:
            os.system("taskkill /f /im firefox.exe")
        else:
            # بستن پنجره فعال
            pyautogui.hotkey('alt', 'f4')
    
    def shutdown_computer(self, command: str):
        """خاموش کردن کامپیوتر"""
        os.system("shutdown /s /t 10")
        self.speak("کامپیوتر در 10 ثانیه خاموش می‌شود")
    
    def restart_computer(self, command: str):
        """ریست کردن کامپیوتر"""
        os.system("shutdown /r /t 10")
        self.speak("کامپیوتر در 10 ثانیه ریست می‌شود")
    
    def volume_down(self, command: str):
        """کم کردن صدا"""
        for _ in range(5):
            pyautogui.press('volumedown')
    
    def volume_up(self, command: str):
        """زیاد کردن صدا"""
        for _ in range(5):
            pyautogui.press('volumeup')
    
    def mute_volume(self, command: str):
        """قطع کردن صدا"""
        pyautogui.press('volumemute')
    
    def open_youtube(self, command: str):
        """باز کردن یوتیوب"""
        webbrowser.open("https://www.youtube.com")
    
    def open_google(self, command: str):
        """باز کردن گوگل"""
        webbrowser.open("https://www.google.com")
    
    def search_web(self, command: str):
        """جستجو در وب"""
        # استخراج کلمه جستجو
        search_term = command.replace("جستجو کن", "").strip()
        if search_term:
            webbrowser.open(f"https://www.google.com/search?q={search_term}")
    
    def open_file_explorer(self, command: str):
        """باز کردن فایل اکسپلورر"""
        subprocess.Popen("explorer")
    
    def show_desktop(self, command: str):
        """نمایش دسکتاپ"""
        pyautogui.hotkey('win', 'd')
    
    def minimize_all_windows(self, command: str):
        """کوچک کردن همه پنجره‌ها"""
        pyautogui.hotkey('win', 'm')
    
    def ai_knowledge(self, command: str):
        """نمایش اطلاعات AI"""
        self.speak("من یک دستیار هوشمند هستم که می‌توانم کامپیوتر شما را کنترل کنم، در وب جستجو کنم، برنامه‌ها را باز و بسته کنم و به سوالات شما پاسخ دهم")
    
    def ai_help(self, command: str):
        """راهنمای استفاده"""
        help_text = """
        می‌توانید این دستورات را استفاده کنید:
        - باز کن کروم
        - جستجو کن پایتون
        - فایل اکسپلورر را باز کن
        - صدا را کم کن
        - کامپیوتر را خاموش کن
        و هر دستور دیگری که می‌خواهید
        """
        self.speak(help_text)
    
    def programming_help(self, command: str):
        """کمک برنامه‌نویسی"""
        if self.openai_api_key:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "شما یک برنامه‌نویس متخصص هستید که به فارسی پاسخ می‌دهید."},
                        {"role": "user", "content": command}
                    ],
                    max_tokens=300
                )
                self.speak(response.choices[0].message.content)
            except:
                self.speak("خطا در اتصال به AI")
        else:
            self.speak("کلید API تنظیم نشده است")
    
    def translate_text(self, command: str):
        """ترجمه متن"""
        if self.openai_api_key:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "متن را از فارسی به انگلیسی ترجمه کن."},
                        {"role": "user", "content": command}
                    ],
                    max_tokens=200
                )
                self.speak(response.choices[0].message.content)
            except:
                self.speak("خطا در ترجمه")
        else:
            self.speak("کلید API تنظیم نشده است")
    
    def start_voice_control(self):
        """شروع کنترل صوتی"""
        self.speak("کنترل صوتی فعال شد. دستور خود را بگویید")
        self.is_listening = True
        
        while self.is_listening:
            command = self.listen()
            if command:
                self.process_command(command)
                time.sleep(1)  # تاخیر کوتاه بین دستورات
    
    def stop_voice_control(self):
        """توقف کنترل صوتی"""
        self.is_listening = False
        self.speak("کنترل صوتی متوقف شد")

# تست سیستم
if __name__ == "__main__":
    controller = AIVoiceController()
    controller.start_voice_control()


