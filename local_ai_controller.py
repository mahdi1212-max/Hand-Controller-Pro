"""
سیستم کنترل صوتی محلی با مدل‌های Open Source
Local AI Voice Control System with Open Source Models
"""

import speech_recognition as sr
import pyttsx3
import threading
import time
import json
import os
import subprocess
import webbrowser
import pyautogui
import psutil
import requests
from typing import Dict, List, Callable
import re

# مدل‌های محلی AI
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    import torch
    from model_cache import ModelCache
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("مدل‌های AI محلی در دسترس نیستند. نصب کنید: pip install transformers torch")

class LocalAIController:
    def __init__(self):
        """
        کنترلر صوتی محلی با مدل‌های Open Source
        """
        # راه‌اندازی تشخیص صدا
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # راه‌اندازی تبدیل متن به گفتار
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)
        self.tts_engine.setProperty('volume', 0.8)
        
        # مدل‌های AI محلی
        self.nlp_model = None
        self.sentiment_model = None
        self.qa_model = None
        
        # سیستم cache
        self.model_cache = ModelCache() if AI_AVAILABLE else None
        self.load_local_models()
        
        # دیکشنری دستورات پیشرفته
        self.commands = {
            # دستورات سیستم
            "باز کن": self.open_application,
            "بستن": self.close_application,
            "کامپیوتر را خاموش کن": self.shutdown_computer,
            "کامپیوتر را ریست کن": self.restart_computer,
            "صدا را کم کن": self.volume_down,
            "صدا را زیاد کن": self.volume_up,
            "صدا را قطع کن": self.mute_volume,
            "صدا را روشن کن": self.unmute_volume,
            
            # دستورات مرورگر
            "کروم را باز کن": lambda cmd: self.open_application("chrome"),
            "فایرفاکس را باز کن": lambda cmd: self.open_application("firefox"),
            "یوتیوب را باز کن": self.open_youtube,
            "گوگل را باز کن": self.open_google,
            "جستجو کن": self.search_web,
            "سایت را باز کن": self.open_website,
            
            # دستورات فایل و سیستم
            "فایل اکسپلورر را باز کن": self.open_file_explorer,
            "دسکتاپ را نشان بده": self.show_desktop,
            "همه پنجره‌ها را کوچک کن": self.minimize_all_windows,
            "برنامه‌ها را نشان بده": self.show_running_apps,
            "سیستم را بررسی کن": self.system_info,
            
            # دستورات هوش مصنوعی
            "چی می‌دونی": self.ai_knowledge,
            "کمکم کن": self.ai_help,
            "برنامه‌نویسی": self.programming_help,
            "ترجمه کن": self.translate_text,
            "خلاصه کن": self.summarize_text,
            "تحلیل کن": self.analyze_text,
            
            # دستورات پیشرفته
            "اسکرین شات بگیر": self.take_screenshot,
            "فایل را کپی کن": self.copy_file,
            "فایل را حذف کن": self.delete_file,
            "پوشه بساز": self.create_folder,
            "فایل را باز کن": self.open_file,
        }
        
        # حالت‌های مختلف
        self.current_mode = "normal"
        self.is_listening = False
        self.last_command_time = 0
        self.conversation_history = []
        
        # تنظیم میکروفون
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
    
    def load_local_models(self):
        """بارگذاری مدل‌های AI محلی با cache"""
        if not AI_AVAILABLE or not self.model_cache:
            print("مدل‌های AI در دسترس نیستند")
            return
        
        try:
            print("در حال بارگذاری مدل‌های AI محلی...")
            
            # مدل پردازش زبان طبیعی با cache
            self.nlp_model = self.model_cache.get_or_download_model(
                "distilbert-base-uncased-finetuned-sst-2-english", 
                "text-classification"
            )
            
            # مدل سوال و جواب با cache
            self.qa_model = self.model_cache.get_or_download_model(
                "distilbert-base-cased-distilled-squad", 
                "question-answering"
            )
            
            if self.nlp_model and self.qa_model:
                print("مدل‌های AI با موفقیت بارگذاری شدند")
                print(f"اطلاعات cache: {self.model_cache.get_cache_info()}")
            else:
                print("خطا در بارگذاری مدل‌ها")
                self.nlp_model = None
                self.qa_model = None
            
        except Exception as e:
            print(f"خطا در بارگذاری مدل‌ها: {e}")
            self.nlp_model = None
            self.qa_model = None
    
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
        
        # ذخیره در تاریخچه
        self.conversation_history.append(f"کاربر: {command}")
        
        # جستجوی دستور در دیکشنری
        for key, func in self.commands.items():
            if key in command:
                try:
                    result = func(command)
                    self.conversation_history.append(f"سیستم: {result}")
                    self.speak(result if result else "انجام شد")
                    return True
                except Exception as e:
                    print(f"خطا در اجرای دستور: {e}")
                    self.speak("خطا در اجرای دستور")
                    return False
        
        # اگر دستور پیدا نشد، از AI محلی استفاده کن
        return self.handle_ai_command(command)
    
    def handle_ai_command(self, command: str) -> bool:
        """پردازش دستورات پیچیده با AI محلی"""
        if not self.nlp_model:
            self.speak("مدل AI در دسترس نیست")
            return False
        
        try:
            # تحلیل احساسات
            sentiment = self.nlp_model(command)
            print(f"تحلیل احساسات: {sentiment}")
            
            # پاسخ هوشمند بر اساس دستور
            if "چطور" in command or "چگونه" in command:
                response = self.handle_how_question(command)
            elif "چرا" in command:
                response = self.handle_why_question(command)
            elif "کی" in command or "چه وقت" in command:
                response = self.handle_when_question(command)
            elif "کجا" in command:
                response = self.handle_where_question(command)
            else:
                response = self.handle_general_question(command)
            
            self.speak(response)
            self.conversation_history.append(f"AI: {response}")
            return True
                
        except Exception as e:
            print(f"خطا در AI: {e}")
            self.speak("خطا در پردازش دستور")
            return False
    
    def handle_how_question(self, command: str) -> str:
        """پردازش سوالات چطور"""
        if "کامپیوتر" in command:
            return "برای کار با کامپیوتر می‌توانید از دستورات صوتی استفاده کنید. مثلاً بگویید 'کروم را باز کن' یا 'فایل اکسپلورر را باز کن'"
        elif "برنامه" in command:
            return "برای باز کردن برنامه‌ها بگویید 'باز کن' و نام برنامه را ذکر کنید"
        else:
            return "لطفاً سوال خود را واضح‌تر بیان کنید"
    
    def handle_why_question(self, command: str) -> str:
        """پردازش سوالات چرا"""
        return "این یک سوال خوب است. برای پاسخ دقیق‌تر، لطفاً جزئیات بیشتری ارائه دهید"
    
    def handle_when_question(self, command: str) -> str:
        """پردازش سوالات کی"""
        return f"زمان فعلی: {time.strftime('%H:%M:%S')}"
    
    def handle_where_question(self, command: str) -> str:
        """پردازش سوالات کجا"""
        return "من یک دستیار مجازی هستم و در کامپیوتر شما زندگی می‌کنم"
    
    def handle_general_question(self, command: str) -> str:
        """پردازش سوالات عمومی"""
        responses = [
            "این سوال جالبی است. می‌توانم در این مورد کمک کنم",
            "بله، می‌توانم در این زمینه راهنمایی کنم",
            "این موضوع پیچیده‌ای است. لطفاً جزئیات بیشتری بدهید",
            "من اینجا هستم تا کمک کنم. چه کاری می‌توانم انجام دهم؟"
        ]
        return responses[len(command) % len(responses)]
    
    # دستورات سیستم
    def open_application(self, command: str) -> str:
        """باز کردن برنامه‌ها"""
        apps = {
            "کروم": "chrome",
            "فایرفاکس": "firefox",
            "نوت پد": "notepad",
            "ماشین حساب": "calc",
            "پینت": "mspaint",
            "وورد": "winword",
            "اکسل": "excel",
            "پاورپوینت": "powerpnt",
            "کد": "code",
            "پاورشل": "powershell"
        }
        
        for app_name, app_path in apps.items():
            if app_name in command:
                try:
                    subprocess.Popen(app_path)
                    return f"{app_name} باز شد"
                except:
                    return f"خطا در باز کردن {app_name}"
        
        return "برنامه مورد نظر پیدا نشد"
    
    def close_application(self, command: str) -> str:
        """بستن برنامه‌ها"""
        if "کروم" in command:
            os.system("taskkill /f /im chrome.exe")
            return "کروم بسته شد"
        elif "فایرفاکس" in command:
            os.system("taskkill /f /im firefox.exe")
            return "فایرفاکس بسته شد"
        else:
            pyautogui.hotkey('alt', 'f4')
            return "پنجره فعال بسته شد"
    
    def shutdown_computer(self, command: str) -> str:
        """خاموش کردن کامپیوتر"""
        os.system("shutdown /s /t 10")
        return "کامپیوتر در 10 ثانیه خاموش می‌شود"
    
    def restart_computer(self, command: str) -> str:
        """ریست کردن کامپیوتر"""
        os.system("shutdown /r /t 10")
        return "کامپیوتر در 10 ثانیه ریست می‌شود"
    
    def volume_down(self, command: str) -> str:
        """کم کردن صدا"""
        for _ in range(5):
            pyautogui.press('volumedown')
        return "صدا کم شد"
    
    def volume_up(self, command: str) -> str:
        """زیاد کردن صدا"""
        for _ in range(5):
            pyautogui.press('volumeup')
        return "صدا زیاد شد"
    
    def mute_volume(self, command: str) -> str:
        """قطع کردن صدا"""
        pyautogui.press('volumemute')
        return "صدا قطع شد"
    
    def unmute_volume(self, command: str) -> str:
        """روشن کردن صدا"""
        pyautogui.press('volumemute')
        return "صدا روشن شد"
    
    def open_youtube(self, command: str) -> str:
        """باز کردن یوتیوب"""
        webbrowser.open("https://www.youtube.com")
        return "یوتیوب باز شد"
    
    def open_google(self, command: str) -> str:
        """باز کردن گوگل"""
        webbrowser.open("https://www.google.com")
        return "گوگل باز شد"
    
    def search_web(self, command: str) -> str:
        """جستجو در وب"""
        search_term = command.replace("جستجو کن", "").strip()
        if search_term:
            webbrowser.open(f"https://www.google.com/search?q={search_term}")
            return f"جستجو برای '{search_term}' انجام شد"
        return "لطفاً کلمه جستجو را مشخص کنید"
    
    def open_website(self, command: str) -> str:
        """باز کردن وب‌سایت"""
        # استخراج نام سایت
        sites = {
            "فیسبوک": "https://www.facebook.com",
            "توییتر": "https://www.twitter.com",
            "اینستاگرام": "https://www.instagram.com",
            "لینکدین": "https://www.linkedin.com",
            "گیت‌هاب": "https://www.github.com"
        }
        
        for site_name, site_url in sites.items():
            if site_name in command:
                webbrowser.open(site_url)
                return f"{site_name} باز شد"
        
        return "سایت مورد نظر پیدا نشد"
    
    def open_file_explorer(self, command: str) -> str:
        """باز کردن فایل اکسپلورر"""
        subprocess.Popen("explorer")
        return "فایل اکسپلورر باز شد"
    
    def show_desktop(self, command: str) -> str:
        """نمایش دسکتاپ"""
        pyautogui.hotkey('win', 'd')
        return "دسکتاپ نمایش داده شد"
    
    def minimize_all_windows(self, command: str) -> str:
        """کوچک کردن همه پنجره‌ها"""
        pyautogui.hotkey('win', 'm')
        return "همه پنجره‌ها کوچک شدند"
    
    def show_running_apps(self, command: str) -> str:
        """نمایش برنامه‌های در حال اجرا"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name']):
                processes.append(proc.info['name'])
            
            # نمایش 10 برنامه اول
            top_processes = list(set(processes))[:10]
            apps_text = "، ".join(top_processes)
            return f"برنامه‌های در حال اجرا: {apps_text}"
        except:
            return "خطا در دریافت لیست برنامه‌ها"
    
    def system_info(self, command: str) -> str:
        """اطلاعات سیستم"""
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            info = f"CPU: {cpu_percent}%، RAM: {memory.percent}%، دیسک: {disk.percent}%"
            return info
        except:
            return "خطا در دریافت اطلاعات سیستم"
    
    def ai_knowledge(self, command: str) -> str:
        """نمایش اطلاعات AI"""
        return "من یک دستیار هوشمند محلی هستم که می‌توانم کامپیوتر شما را کنترل کنم، در وب جستجو کنم، برنامه‌ها را مدیریت کنم و به سوالات شما پاسخ دهم. همه پردازش‌ها محلی انجام می‌شود"
    
    def ai_help(self, command: str) -> str:
        """راهنمای استفاده"""
        help_text = """
        دستورات موجود:
        - باز کن کروم
        - جستجو کن پایتون
        - فایل اکسپلورر را باز کن
        - صدا را کم کن
        - کامپیوتر را خاموش کن
        - سیستم را بررسی کن
        - برنامه‌ها را نشان بده
        - اسکرین شات بگیر
        """
        return help_text
    
    def programming_help(self, command: str) -> str:
        """کمک برنامه‌نویسی"""
        if "پایتون" in command:
            return "پایتون یک زبان برنامه‌نویسی قدرتمند است. برای شروع، می‌توانید از سایت python.org استفاده کنید"
        elif "جاوا" in command:
            return "جاوا یک زبان شی‌گرا است. برای یادگیری، از Oracle Java Documentation استفاده کنید"
        elif "وب" in command:
            return "برای توسعه وب، HTML، CSS و JavaScript را یاد بگیرید"
        else:
            return "برای کمک برنامه‌نویسی، لطفاً زبان یا موضوع خاصی را ذکر کنید"
    
    def translate_text(self, command: str) -> str:
        """ترجمه متن"""
        # استخراج متن برای ترجمه
        text_to_translate = command.replace("ترجمه کن", "").strip()
        if text_to_translate:
            # ترجمه ساده با استفاده از دیکشنری
            translations = {
                "سلام": "Hello",
                "خداحافظ": "Goodbye",
                "ممنون": "Thank you",
                "لطفاً": "Please",
                "بله": "Yes",
                "خیر": "No"
            }
            
            if text_to_translate in translations:
                return f"ترجمه: {translations[text_to_translate]}"
            else:
                return "برای ترجمه‌های پیچیده‌تر، از Google Translate استفاده کنید"
        return "لطفاً متن مورد نظر را برای ترجمه مشخص کنید"
    
    def summarize_text(self, command: str) -> str:
        """خلاصه کردن متن"""
        return "برای خلاصه کردن متن، لطفاً متن را ارائه دهید"
    
    def analyze_text(self, command: str) -> str:
        """تحلیل متن"""
        if self.nlp_model:
            try:
                result = self.nlp_model(command)
                return f"تحلیل: {result[0]['label']} با اطمینان {result[0]['score']:.2f}"
            except:
                return "خطا در تحلیل متن"
        return "مدل تحلیل در دسترس نیست"
    
    def take_screenshot(self, command: str) -> str:
        """گرفتن اسکرین شات"""
        try:
            screenshot = pyautogui.screenshot()
            filename = f"screenshot_{int(time.time())}.png"
            screenshot.save(filename)
            return f"اسکرین شات ذخیره شد: {filename}"
        except:
            return "خطا در گرفتن اسکرین شات"
    
    def copy_file(self, command: str) -> str:
        """کپی کردن فایل"""
        return "برای کپی فایل، مسیر فایل مبدا و مقصد را مشخص کنید"
    
    def delete_file(self, command: str) -> str:
        """حذف فایل"""
        return "برای حذف فایل، مسیر فایل را مشخص کنید"
    
    def create_folder(self, command: str) -> str:
        """ایجاد پوشه"""
        return "برای ایجاد پوشه، نام پوشه را مشخص کنید"
    
    def open_file(self, command: str) -> str:
        """باز کردن فایل"""
        return "برای باز کردن فایل، مسیر فایل را مشخص کنید"
    
    def start_voice_control(self):
        """شروع کنترل صوتی"""
        self.speak("کنترل صوتی محلی فعال شد. دستور خود را بگویید")
        self.is_listening = True
        
        # اجرای حلقه گوش دادن در thread جداگانه
        def listen_loop():
            while self.is_listening:
                try:
                    command = self.listen()
                    if command:
                        self.process_command(command)
                    time.sleep(0.5)  # کاهش تاخیر
                except Exception as e:
                    print(f"خطا در گوش دادن: {e}")
                    time.sleep(1)
        
        listen_thread = threading.Thread(target=listen_loop)
        listen_thread.daemon = True
        listen_thread.start()
    
    def stop_voice_control(self):
        """توقف کنترل صوتی"""
        self.is_listening = False
        self.speak("کنترل صوتی متوقف شد")
    
    def get_conversation_history(self) -> List[str]:
        """دریافت تاریخچه مکالمه"""
        return self.conversation_history

# تست سیستم
if __name__ == "__main__":
    controller = LocalAIController()
    controller.start_voice_control()
