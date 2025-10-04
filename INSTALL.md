# راهنمای نصب Hand Controller Pro v3.0

## نصب سریع (Windows)

### مرحله 1: نصب Python
1. از [python.org](https://www.python.org/downloads/) Python 3.8+ دانلود کنید
2. هنگام نصب، گزینه "Add Python to PATH" را انتخاب کنید
3. Python را نصب کنید

### مرحله 2: نصب وابستگی‌ها
```cmd
# باز کردن Command Prompt به عنوان Administrator
pip install --upgrade pip
pip install -r requirements.txt
```

### مرحله 3: اجرای برنامه
```cmd
python main.py
```

## نصب کامل (تمام سیستم‌عامل‌ها)

### پیش‌نیازها
- Python 3.8 یا بالاتر
- pip (مدیر بسته Python)
- Git (اختیاری)

### مرحله 1: کلون کردن پروژه
```bash
git clone https://github.com/yourusername/hand-controller-pro.git
cd hand-controller-pro
```

### مرحله 2: ایجاد محیط مجازی (توصیه می‌شود)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### مرحله 3: نصب وابستگی‌ها
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### مرحله 4: دانلود مدل‌های AI (اولین بار)
```bash
python -c "from model_cache import ModelCache; ModelCache().get_or_download_model('distilbert-base-uncased-finetuned-sst-2-english', 'text-classification')"
```

### مرحله 5: اجرای برنامه
```bash
python main.py
```

## نصب دستی وابستگی‌ها

### وابستگی‌های اصلی
```bash
pip install opencv-python==4.8.1.78
pip install mediapipe==0.10.7
pip install numpy==1.24.3
pip install pyautogui==0.9.54
```

### وابستگی‌های صدا
```bash
pip install speechrecognition==3.10.0
pip install pyttsx3==2.90
pip install pyaudio==0.2.11
```

### وابستگی‌های AI
```bash
pip install transformers==4.35.0
pip install torch==2.1.0
pip install torchaudio==2.1.0
pip install sentence-transformers==2.2.2
pip install spacy==3.7.2
pip install vosk==0.3.45
pip install onnxruntime==1.16.3
```

### وابستگی‌های رابط کاربری
```bash
pip install customtkinter==5.2.0
pip install pillow==10.1.0
```

### وابستگی‌های اضافی
```bash
pip install requests==2.31.0
pip install beautifulsoup4==4.12.2
pip install selenium==4.15.2
pip install webdriver-manager==4.0.1
pip install psutil==5.9.6
pip install keyboard==0.13.5
pip install mouse==0.7.1
```

## عیب‌یابی نصب

### خطای PyAudio در Windows
```bash
# نصب Microsoft Visual C++ Build Tools
# سپس:
pip install pipwin
pipwin install pyaudio
```

### خطای PyAudio در macOS
```bash
brew install portaudio
pip install pyaudio
```

### خطای PyAudio در Linux
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

### خطای OpenCV
```bash
pip uninstall opencv-python
pip install opencv-python-headless
```

### خطای MediaPipe
```bash
pip install --upgrade mediapipe
```

### خطای Transformers
```bash
pip install --upgrade transformers torch
```

## تنظیمات سیستم

### Windows
1. **فعال‌سازی دوربین**:
   - Settings > Privacy > Camera > Allow apps to access camera

2. **فعال‌سازی میکروفون**:
   - Settings > Privacy > Microphone > Allow apps to access microphone

3. **فعال‌سازی دسترسی‌های سیستم**:
   - Settings > Privacy > Other devices > Allow apps to access other devices

### macOS
1. **دسترسی دوربین**:
   - System Preferences > Security & Privacy > Camera

2. **دسترسی میکروفون**:
   - System Preferences > Security & Privacy > Microphone

3. **دسترسی دسترسی‌ها**:
   - System Preferences > Security & Privacy > Accessibility

### Linux
1. **دسترسی دوربین**:
   ```bash
   sudo usermod -a -G video $USER
   ```

2. **دسترسی میکروفون**:
   ```bash
   sudo usermod -a -G audio $USER
   ```

## تست نصب

### تست دوربین
```python
import cv2
cap = cv2.VideoCapture(0)
if cap.isOpened():
    print("دوربین کار می‌کند")
    cap.release()
else:
    print("مشکل در دوربین")
```

### تست میکروفون
```python
import speech_recognition as sr
r = sr.Recognizer()
with sr.Microphone() as source:
    print("میکروفون کار می‌کند")
```

### تست AI
```python
from transformers import pipeline
classifier = pipeline("text-classification")
result = classifier("Hello world")
print("AI کار می‌کند:", result)
```

## بهینه‌سازی عملکرد

### تنظیمات GPU (اختیاری)
```bash
# برای NVIDIA GPU
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### تنظیمات حافظه
```python
# در main.py
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
```

### تنظیمات دوربین
```python
# در advanced_hand_controller.py
self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
self.cap.set(cv2.CAP_PROP_FPS, 30)
```

## پشتیبانی

اگر با مشکلی مواجه شدید:

1. **بررسی لاگ‌ها**: خطاها در کنسول نمایش داده می‌شوند
2. **بررسی وابستگی‌ها**: `pip list` برای بررسی نصب
3. **بررسی سیستم**: مطمئن شوید همه پیش‌نیازها نصب شده‌اند
4. **تماس با پشتیبانی**: support@handcontroller.pro

## به‌روزرسانی

### به‌روزرسانی خودکار
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

### به‌روزرسانی دستی
1. دانلود آخرین نسخه
2. جایگزینی فایل‌ها
3. نصب وابستگی‌های جدید

---

**نکته**: برای بهترین عملکرد، از Python 3.9+ و آخرین نسخه pip استفاده کنید.

