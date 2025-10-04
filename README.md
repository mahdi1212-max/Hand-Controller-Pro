# Hand Controller Pro v3.0

## کنترلر دست پیشرفته با هوش مصنوعی

یک سیستم کنترل کامپیوتر پیشرفته که از حرکات دست و دستورات صوتی برای کنترل کامپیوتر استفاده می‌کند. این سیستم با استفاده از مدل‌های AI محلی و open source، قابلیت‌های تجاری و قابل فروش ارائه می‌دهد.

## ویژگی‌های اصلی

### 🎯 کنترل دست
- **تشخیص دو دستی**: کنترل جداگانه با دست چپ و راست
- **ژست‌های پیشرفته**: 15+ ژست مختلف برای کنترل
- **دقت بالا**: کالیبراسیون هوشمند برای دقت بیشتر
- **حالت‌های مختلف**: ماوس، سیستم، کیبورد مجازی

### 🎤 کنترل صوتی
- **تشخیص صدا محلی**: بدون نیاز به اینترنت
- **دستورات فارسی**: پشتیبانی کامل از زبان فارسی
- **AI محلی**: پردازش هوشمند با مدل‌های open source
- **دستورات پیشرفته**: کنترل برنامه‌ها، جستجو، مدیریت فایل

### 🤖 هوش مصنوعی
- **مدل‌های محلی**: بدون نیاز به API خارجی
- **Cache هوشمند**: جلوگیری از دانلود مجدد مدل‌ها
- **پردازش زبان طبیعی**: درک و پاسخ به سوالات
- **تحلیل احساسات**: تشخیص احساسات در گفتار

### 💼 قابلیت‌های تجاری
- **سیستم لایسنس**: مدیریت مجوزها
- **آنالیتیکس**: ردیابی استفاده و عملکرد
- **تنظیمات کاربر**: شخصی‌سازی کامل
- **امنیت**: کنترل دسترسی‌ها

## نصب و راه‌اندازی

### پیش‌نیازها
- Python 3.8 یا بالاتر
- دوربین وب
- میکروفون
- سیستم عامل: Windows 10/11, macOS, Linux

### نصب
```bash
# کلون کردن پروژه
git clone https://github.com/yourusername/hand-controller-pro.git
cd hand-controller-pro

# نصب وابستگی‌ها
pip install -r requirements.txt

# اجرای برنامه
python main.py
```

### نصب دستی وابستگی‌ها
```bash
pip install opencv-python mediapipe numpy pyautogui pycaw comtypes
pip install speechrecognition pyttsx3 pyaudio
pip install transformers torch torchaudio sentence-transformers
pip install spacy vosk onnxruntime
pip install customtkinter pillow requests beautifulsoup4
pip install selenium webdriver-manager psutil keyboard mouse
```

## راهنمای استفاده

### شروع سریع
1. برنامه را اجرا کنید: `python main.py`
2. دوربین و میکروفون را فعال کنید
3. کالیبراسیون را انجام دهید
4. از ژست‌ها و دستورات صوتی استفاده کنید

### ژست‌های دست

#### دست چپ (کنترل حالت)
- **1 انگشت**: حالت ماوس
- **2 انگشت**: کنترل سیستم
- **3 انگشت**: کیبورد مجازی
- **5 انگشت (کف دست)**: بازگشت به حالت آماده

#### دست راست (اجرای دستورات)
- **انگشت اشاره**: حرکت ماوس
- **انگشت اشاره + میانی**: کلیک چپ
- **انگشت شست + اشاره**: کلیک راست
- **مشت**: کشیدن و رها کردن

### دستورات صوتی

#### دستورات سیستم
- "کروم را باز کن"
- "فایل اکسپلورر را باز کن"
- "صدا را کم کن"
- "کامپیوتر را خاموش کن"

#### دستورات جستجو
- "جستجو کن پایتون"
- "یوتیوب را باز کن"
- "گوگل را باز کن"

#### دستورات هوش مصنوعی
- "چی می‌دونی"
- "کمکم کن"
- "برنامه‌نویسی"
- "ترجمه کن"

## ساختار پروژه

```
AdvancedHandController/
├── main.py                      # فایل اصلی اجرا
├── advanced_hand_controller.py  # کنترلر دست پیشرفته
├── local_ai_controller.py       # کنترلر صوتی محلی
├── model_cache.py              # سیستم cache مدل‌ها
├── commercial_features.py      # قابلیت‌های تجاری
├── requirements.txt            # وابستگی‌ها
├── README.md                   # مستندات
└── model_cache/               # پوشه cache مدل‌ها
```

## تنظیمات پیشرفته

### تنظیمات دوربین
```python
# در advanced_hand_controller.py
self.wCam, self.hCam = 1280, 720  # رزولوشن
self.frame_reduction = 100        # حاشیه
```

### تنظیمات تشخیص صدا
```python
# در local_ai_controller.py
self.recognizer.energy_threshold = 300
self.recognizer.dynamic_energy_threshold = True
```

### تنظیمات AI
```python
# در model_cache.py
cache_dir = "model_cache"  # مسیر cache
```

## API و توسعه

### اضافه کردن ژست جدید
```python
def custom_gesture(self, hand_landmarks):
    fingers = self.get_finger_states(hand_landmarks, "right")
    # منطق ژست جدید
    if fingers[0] == 1 and fingers[1] == 0:  # فقط شست
        # انجام عمل
        pass
```

### اضافه کردن دستور صوتی
```python
# در local_ai_controller.py
self.commands["دستور جدید"] = self.new_command_function

def new_command_function(self, command: str) -> str:
    # منطق دستور جدید
    return "انجام شد"
```

## عیب‌یابی

### مشکلات رایج

#### دوربین کار نمی‌کند
```python
# بررسی شماره دوربین
cap = cv2.VideoCapture(0)  # یا 1, 2, ...
```

#### تشخیص صدا کار نمی‌کند
```python
# بررسی میکروفون
import pyaudio
p = pyaudio.PyAudio()
print(p.get_device_count())
```

#### مدل‌های AI دانلود نمی‌شوند
```python
# پاک کردن cache و دانلود مجدد
from model_cache import ModelCache
cache = ModelCache()
cache.clear_cache()
```

## مجوز و لایسنس

### نسخه رایگان
- کنترل دست پایه
- دستورات صوتی محدود
- بدون قابلیت‌های تجاری

### نسخه تجاری
- تمام قابلیت‌ها
- پشتیبانی فنی
- به‌روزرسانی‌های منظم
- لایسنس سازمانی

## مشارکت

ما از مشارکت‌های شما استقبال می‌کنیم! لطفاً:

1. پروژه را fork کنید
2. شاخه جدید ایجاد کنید
3. تغییرات را commit کنید
4. Pull Request ارسال کنید

## پشتیبانی

- **ایمیل**: support@handcontroller.pro
- **GitHub Issues**: [اینجا کلیک کنید](https://github.com/yourusername/hand-controller-pro/issues)
- **مستندات**: [docs.handcontroller.pro](https://docs.handcontroller.pro)

## تغییرات نسخه

### v3.0 (فعلی)
- اضافه شدن AI محلی
- سیستم cache مدل‌ها
- قابلیت‌های تجاری
- رابط کاربری بهبود یافته

### v2.0
- کنترل دو دستی
- بهبود دقت ماوس
- ژست‌های جدید

### v1.0
- نسخه اولیه
- کنترل دست پایه

## تیم توسعه

- **مدیر پروژه**: [نام شما]
- **توسعه‌دهنده اصلی**: [نام شما]
- **طراح UI/UX**: [نام شما]
- **متخصص AI**: [نام شما]

---

**Hand Controller Pro v3.0** - کنترل کامپیوتر با حرکات دست و صدا

© 2024 Hand Controller Pro. تمام حقوق محفوظ است.

