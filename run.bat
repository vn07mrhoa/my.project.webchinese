@echo off
chcp 65001 >nul
echo ========================================================
echo       ĐANG KHỞI CHẠY HỆ THỐNG WEB HỌC TIẾNG TRUNG HANZII
echo ========================================================
echo.
echo Website đang chạy tại địa chỉ: http://localhost:8000
echo Mở trình duyệt và truy cập: http://localhost:8000
echo.
echo Nhấn Ctrl+C để dừng server.
echo.

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
