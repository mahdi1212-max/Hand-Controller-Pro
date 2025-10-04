"""
سیستم Cache کردن مدل‌های AI برای جلوگیری از دانلود مجدد
AI Model Caching System to prevent re-downloading
"""

import os
import json
import hashlib
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import logging

# تنظیم logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelCache:
    def __init__(self, cache_dir="model_cache"):
        """
        سیستم cache کردن مدل‌های AI
        
        Args:
            cache_dir: مسیر ذخیره cache
        """
        self.cache_dir = cache_dir
        self.models_info_file = os.path.join(cache_dir, "models_info.json")
        self.models_info = self.load_models_info()
        
        # ایجاد پوشه cache اگر وجود ندارد
        os.makedirs(cache_dir, exist_ok=True)
        
    def load_models_info(self):
        """بارگذاری اطلاعات مدل‌های cache شده"""
        if os.path.exists(self.models_info_file):
            try:
                with open(self.models_info_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_models_info(self):
        """ذخیره اطلاعات مدل‌های cache شده"""
        try:
            with open(self.models_info_file, 'w', encoding='utf-8') as f:
                json.dump(self.models_info, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"خطا در ذخیره اطلاعات مدل‌ها: {e}")
    
    def get_model_hash(self, model_name, task):
        """محاسبه hash برای مدل"""
        return hashlib.md5(f"{model_name}_{task}".encode()).hexdigest()
    
    def is_model_cached(self, model_name, task):
        """بررسی وجود مدل در cache"""
        model_hash = self.get_model_hash(model_name, task)
        return model_hash in self.models_info
    
    def cache_model(self, model_name, task, model, tokenizer=None):
        """ذخیره مدل در cache"""
        try:
            model_hash = self.get_model_hash(model_name, task)
            model_path = os.path.join(self.cache_dir, model_hash)
            
            # ذخیره مدل
            model.save_pretrained(model_path)
            
            # ذخیره tokenizer اگر وجود دارد
            if tokenizer:
                tokenizer.save_pretrained(model_path)
            
            # ذخیره اطلاعات مدل
            self.models_info[model_hash] = {
                "model_name": model_name,
                "task": task,
                "cached_at": str(torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"),
                "path": model_path
            }
            
            self.save_models_info()
            logger.info(f"مدل {model_name} در cache ذخیره شد")
            
        except Exception as e:
            logger.error(f"خطا در cache کردن مدل {model_name}: {e}")
    
    def load_cached_model(self, model_name, task):
        """بارگذاری مدل از cache"""
        try:
            model_hash = self.get_model_hash(model_name, task)
            if model_hash in self.models_info:
                model_path = self.models_info[model_hash]["path"]
                
                if task == "text-classification":
                    model = AutoModelForSequenceClassification.from_pretrained(model_path)
                    tokenizer = AutoTokenizer.from_pretrained(model_path)
                    return pipeline(task, model=model, tokenizer=tokenizer)
                else:
                    return pipeline(task, model=model_path)
            
            return None
            
        except Exception as e:
            logger.error(f"خطا در بارگذاری مدل از cache: {e}")
            return None
    
    def get_or_download_model(self, model_name, task, force_download=False):
        """
        دریافت مدل از cache یا دانلود آن
        
        Args:
            model_name: نام مدل
            task: نوع task
            force_download: آیا مجبور به دانلود مجدد است
            
        Returns:
            مدل بارگذاری شده
        """
        # بررسی وجود در cache
        if not force_download and self.is_model_cached(model_name, task):
            logger.info(f"بارگذاری مدل {model_name} از cache...")
            cached_model = self.load_cached_model(model_name, task)
            if cached_model:
                return cached_model
        
        # دانلود مدل جدید
        logger.info(f"دانلود مدل {model_name}...")
        try:
            model = pipeline(task, model=model_name)
            
            # ذخیره در cache
            if task == "text-classification":
                # برای مدل‌های classification، model و tokenizer جداگانه ذخیره می‌شوند
                model_obj = model.model
                tokenizer = model.tokenizer
                self.cache_model(model_name, task, model_obj, tokenizer)
            else:
                self.cache_model(model_name, task, model)
            
            return model
            
        except Exception as e:
            logger.error(f"خطا در دانلود مدل {model_name}: {e}")
            return None
    
    def clear_cache(self):
        """پاک کردن تمام cache"""
        try:
            import shutil
            if os.path.exists(self.cache_dir):
                shutil.rmtree(self.cache_dir)
            os.makedirs(self.cache_dir, exist_ok=True)
            self.models_info = {}
            self.save_models_info()
            logger.info("Cache پاک شد")
        except Exception as e:
            logger.error(f"خطا در پاک کردن cache: {e}")
    
    def get_cache_info(self):
        """دریافت اطلاعات cache"""
        total_size = 0
        model_count = len(self.models_info)
        
        for model_hash, info in self.models_info.items():
            model_path = info["path"]
            if os.path.exists(model_path):
                for root, dirs, files in os.walk(model_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        total_size += os.path.getsize(file_path)
        
        return {
            "model_count": model_count,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "models": list(self.models_info.values())
        }

# نمونه استفاده
if __name__ == "__main__":
    cache = ModelCache()
    
    # دریافت مدل از cache یا دانلود
    model = cache.get_or_download_model("distilbert-base-uncased-finetuned-sst-2-english", "text-classification")
    
    if model:
        print("مدل با موفقیت بارگذاری شد")
        print(f"اطلاعات cache: {cache.get_cache_info()}")
    else:
        print("خطا در بارگذاری مدل")

