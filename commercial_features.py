"""
قابلیت‌های تجاری و قابل فروش
Commercial and Marketable Features
"""

import json
import time
import os
from datetime import datetime
from typing import Dict, List, Any
import hashlib
import base64

class CommercialFeatures:
    def __init__(self):
        """قابلیت‌های تجاری"""
        self.license_key = None
        self.user_data = {}
        self.usage_stats = {
            "total_sessions": 0,
            "total_commands": 0,
            "total_gestures": 0,
            "session_duration": 0,
            "last_used": None
        }
        self.features_enabled = {
            "basic_gestures": True,
            "voice_control": True,
            "ai_processing": True,
            "advanced_ui": True,
            "commercial_features": False
        }
        
    def validate_license(self, license_key: str) -> bool:
        """اعتبارسنجی کلید لایسنس"""
        try:
            # رمزگشایی کلید لایسنس
            decoded_key = base64.b64decode(license_key.encode()).decode()
            key_data = json.loads(decoded_key)
            
            # بررسی اعتبار
            if self._verify_license_signature(key_data):
                self.license_key = license_key
                self.features_enabled["commercial_features"] = True
                return True
            return False
            
        except:
            return False
    
    def _verify_license_signature(self, key_data: Dict) -> bool:
        """بررسی امضای لایسنس"""
        # اینجا می‌توانید الگوریتم پیچیده‌تری برای بررسی امضا پیاده‌سازی کنید
        required_fields = ["user_id", "expiry_date", "signature"]
        return all(field in key_data for field in required_fields)
    
    def get_license_info(self) -> Dict:
        """دریافت اطلاعات لایسنس"""
        if not self.license_key:
            return {"status": "no_license", "features": self.features_enabled}
        
        try:
            decoded_key = base64.b64decode(self.license_key.encode()).decode()
            key_data = json.loads(decoded_key)
            return {
                "status": "licensed",
                "user_id": key_data.get("user_id", "Unknown"),
                "expiry_date": key_data.get("expiry_date", "Unknown"),
                "features": self.features_enabled
            }
        except:
            return {"status": "invalid_license", "features": self.features_enabled}
    
    def track_usage(self, command_type: str, success: bool = True):
        """ردیابی استفاده"""
        self.usage_stats["total_commands"] += 1
        if command_type == "gesture":
            self.usage_stats["total_gestures"] += 1
        
        if not success:
            self.usage_stats["errors"] = self.usage_stats.get("errors", 0) + 1
        
        self.usage_stats["last_used"] = datetime.now().isoformat()
    
    def start_session(self):
        """شروع جلسه"""
        self.usage_stats["total_sessions"] += 1
        self.usage_stats["session_start"] = time.time()
    
    def end_session(self):
        """پایان جلسه"""
        if "session_start" in self.usage_stats:
            duration = time.time() - self.usage_stats["session_start"]
            self.usage_stats["session_duration"] += duration
            del self.usage_stats["session_start"]
    
    def get_usage_report(self) -> Dict:
        """گزارش استفاده"""
        return {
            "usage_stats": self.usage_stats,
            "license_info": self.get_license_info(),
            "system_info": self._get_system_info()
        }
    
    def _get_system_info(self) -> Dict:
        """اطلاعات سیستم"""
        import platform
        import psutil
        
        return {
            "os": platform.system(),
            "os_version": platform.version(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "disk_usage": psutil.disk_usage('/').percent
        }
    
    def export_data(self, file_path: str):
        """صادرات داده‌ها"""
        export_data = {
            "usage_stats": self.usage_stats,
            "license_info": self.get_license_info(),
            "export_date": datetime.now().isoformat(),
            "version": "3.0"
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    def generate_demo_license(self) -> str:
        """تولید لایسنس دمو (فقط برای تست)"""
        demo_data = {
            "user_id": "demo_user",
            "expiry_date": "2024-12-31",
            "signature": "demo_signature_12345",
            "features": ["basic_gestures", "voice_control", "ai_processing"]
        }
        
        json_str = json.dumps(demo_data)
        encoded = base64.b64encode(json_str.encode()).decode()
        return encoded

class Analytics:
    def __init__(self):
        """سیستم آنالیتیکس"""
        self.events = []
        self.performance_metrics = {}
        
    def log_event(self, event_type: str, data: Dict = None):
        """ثبت رویداد"""
        event = {
            "timestamp": time.time(),
            "event_type": event_type,
            "data": data or {}
        }
        self.events.append(event)
    
    def log_performance(self, operation: str, duration: float, success: bool = True):
        """ثبت عملکرد"""
        if operation not in self.performance_metrics:
            self.performance_metrics[operation] = {
                "total_time": 0,
                "count": 0,
                "success_count": 0,
                "avg_time": 0
            }
        
        metrics = self.performance_metrics[operation]
        metrics["total_time"] += duration
        metrics["count"] += 1
        if success:
            metrics["success_count"] += 1
        metrics["avg_time"] = metrics["total_time"] / metrics["count"]
    
    def get_analytics_report(self) -> Dict:
        """گزارش آنالیتیکس"""
        return {
            "total_events": len(self.events),
            "performance_metrics": self.performance_metrics,
            "recent_events": self.events[-10:] if self.events else []
        }

class UserPreferences:
    def __init__(self):
        """تنظیمات کاربر"""
        self.preferences = {
            "language": "fa",
            "theme": "dark",
            "gesture_sensitivity": "medium",
            "voice_speed": 150,
            "voice_volume": 0.8,
            "auto_calibration": True,
            "show_tutorial": True
        }
        self.load_preferences()
    
    def load_preferences(self):
        """بارگذاری تنظیمات"""
        prefs_file = "user_preferences.json"
        if os.path.exists(prefs_file):
            try:
                with open(prefs_file, 'r', encoding='utf-8') as f:
                    saved_prefs = json.load(f)
                    self.preferences.update(saved_prefs)
            except:
                pass
    
    def save_preferences(self):
        """ذخیره تنظیمات"""
        prefs_file = "user_preferences.json"
        try:
            with open(prefs_file, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"خطا در ذخیره تنظیمات: {e}")
    
    def get_preference(self, key: str, default=None):
        """دریافت تنظیم"""
        return self.preferences.get(key, default)
    
    def set_preference(self, key: str, value: Any):
        """تنظیم مقدار"""
        self.preferences[key] = value
        self.save_preferences()

class SecurityManager:
    def __init__(self):
        """مدیریت امنیت"""
        self.allowed_commands = [
            "open_application", "close_application", "volume_control",
            "mouse_control", "keyboard_input", "web_search"
        ]
        self.blocked_apps = ["cmd", "powershell", "regedit", "taskmgr"]
        
    def is_command_allowed(self, command: str) -> bool:
        """بررسی مجاز بودن دستور"""
        return command in self.allowed_commands
    
    def is_app_blocked(self, app_name: str) -> bool:
        """بررسی مسدود بودن برنامه"""
        return app_name.lower() in self.blocked_apps
    
    def validate_gesture(self, gesture_data: Dict) -> bool:
        """اعتبارسنجی ژست"""
        # بررسی‌های امنیتی برای ژست‌ها
        required_fields = ["hand_type", "fingers", "landmarks"]
        return all(field in gesture_data for field in required_fields)

# نمونه استفاده
if __name__ == "__main__":
    # تست قابلیت‌های تجاری
    commercial = CommercialFeatures()
    
    # تولید لایسنس دمو
    demo_license = commercial.generate_demo_license()
    print(f"لایسنس دمو: {demo_license}")
    
    # اعتبارسنجی لایسنس
    if commercial.validate_license(demo_license):
        print("لایسنس معتبر است")
        print(f"اطلاعات لایسنس: {commercial.get_license_info()}")
    else:
        print("لایسنس نامعتبر است")
    
    # تست آنالیتیکس
    analytics = Analytics()
    analytics.log_event("app_start", {"version": "3.0"})
    analytics.log_performance("gesture_detection", 0.1, True)
    
    print(f"گزارش آنالیتیکس: {analytics.get_analytics_report()}")
    
    # تست تنظیمات کاربر
    prefs = UserPreferences()
    prefs.set_preference("language", "en")
    print(f"زبان: {prefs.get_preference('language')}")

