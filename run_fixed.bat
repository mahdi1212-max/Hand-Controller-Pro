@echo off
echo ========================================
echo Hand Controller Pro v3.0 - Fixed Version
echo ========================================
echo.
echo در حال راه‌اندازی...
echo.

cd /d "%~dp0"

python run_fixed.py

if %errorlevel% neq 0 (
    echo.
    echo خطا در اجرای برنامه!
    echo لطفاً مطمئن شوید که Python و تمام وابستگی‌ها نصب شده‌اند.
    echo.
    pause
)

echo.
echo برنامه بسته شد.
pause
