"""
فایل اجرای سریع Hand Controller Pro v3.0
Quick launch file for Hand Controller Pro v3.0
"""

import sys
import os
import subprocess
import time

def check_python_version():
    """بررسی نسخه Python"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 یا بالاتر مورد نیاز است")
        print(f"نسخه فعلی: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} - OK")
    return True

def check_dependencies():
    """بررسی وابستگی‌های اصلی"""
    required = ['cv2', 'mediapipe', 'numpy', 'pyautogui']
    missing = []
    
    for dep in required:
        try:
            __import__(dep)
            print(f"✅ {dep} - OK")
        except ImportError:
            missing.append(dep)
            print(f"❌ {dep} - Missing")
    
    if missing:
        print(f"\n❌ وابستگی‌های زیر نصب نشده‌اند: {', '.join(missing)}")
        print("برای نصب، دستور زیر را اجرا کنید:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def install_dependencies():
    """نصب خودکار وابستگی‌ها"""
    print("🔄 در حال نصب وابستگی‌ها...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ وابستگی‌ها با موفقیت نصب شدند")
        return True
    except subprocess.CalledProcessError:
        print("❌ خطا در نصب وابستگی‌ها")
        return False

def check_camera():
    """بررسی دوربین"""
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✅ دوربین - OK")
            cap.release()
            return True
        else:
            print("❌ دوربین - Not Found")
            return False
    except:
        print("❌ خطا در بررسی دوربین")
        return False

def check_microphone():
    """بررسی میکروفون"""
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("✅ میکروفون - OK")
            return True
    except:
        print("❌ میکروفون - Not Found")
        return False

def download_ai_models():
    """دانلود مدل‌های AI"""
    print("🔄 در حال دانلود مدل‌های AI...")
    try:
        from model_cache import ModelCache
        cache = ModelCache()
        
        # دانلود مدل‌های اصلی
        print("📥 دانلود مدل تشخیص احساسات...")
        cache.get_or_download_model("distilbert-base-uncased-finetuned-sst-2-english", "text-classification")
        
        print("📥 دانلود مدل سوال و جواب...")
        cache.get_or_download_model("distilbert-base-cased-distilled-squad", "question-answering")
        
        print("✅ مدل‌های AI دانلود شدند")
        return True
    except Exception as e:
        print(f"❌ خطا در دانلود مدل‌ها: {e}")
        return False

def run_application():
    """اجرای برنامه اصلی"""
    try:
        print("🚀 در حال راه‌اندازی Hand Controller Pro v3.0...")
        from main import MainApplication
        app = MainApplication()
        app.run()
    except Exception as e:
        print(f"❌ خطا در اجرای برنامه: {e}")
        return False
    return True

def main():
    """تابع اصلی"""
    print("=" * 60)
    print("🎯 Hand Controller Pro v3.0 - Quick Launcher")
    print("=" * 60)
    
    # بررسی نسخه Python
    if not check_python_version():
        input("برای خروج Enter را فشار دهید...")
        return
    
    # بررسی وابستگی‌ها
    if not check_dependencies():
        print("\n🤔 آیا می‌خواهید وابستگی‌ها را نصب کنید؟ (y/n)")
        choice = input().lower()
        if choice == 'y':
            if not install_dependencies():
                input("برای خروج Enter را فشار دهید...")
                return
        else:
            input("برای خروج Enter را فشار دهید...")
            return
    
    # بررسی سخت‌افزار
    print("\n🔍 بررسی سخت‌افزار...")
    camera_ok = check_camera()
    mic_ok = check_microphone()
    
    if not camera_ok:
        print("⚠️  دوربین پیدا نشد. برنامه ممکن است کار نکند.")
    
    if not mic_ok:
        print("⚠️  میکروفون پیدا نشد. کنترل صوتی کار نخواهد کرد.")
    
    # دانلود مدل‌های AI
    print("\n🤖 بررسی مدل‌های AI...")
    try:
        from model_cache import ModelCache
        cache = ModelCache()
        cache_info = cache.get_cache_info()
        
        if cache_info["model_count"] == 0:
            print("📥 مدل‌های AI یافت نشد. دانلود شروع می‌شود...")
            download_ai_models()
        else:
            print(f"✅ {cache_info['model_count']} مدل در cache موجود است")
    except:
        print("⚠️  مدل‌های AI در دسترس نیستند")
    
    # اجرای برنامه
    print("\n" + "=" * 60)
    print("🎉 همه چیز آماده است!")
    print("=" * 60)
    
    input("برای شروع برنامه Enter را فشار دهید...")
    run_application()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 خداحافظ!")
    except Exception as e:
        print(f"\n❌ خطای غیرمنتظره: {e}")
        input("برای خروج Enter را فشار دهید...")

