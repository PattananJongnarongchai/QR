@echo off
chcp 65001 >nul

echo 🚀 เริ่มต้น Deploy ระบบ Dynamic QR Code...

REM ตรวจสอบว่า Docker ติดตั้งแล้วหรือไม่
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker ไม่ได้ติดตั้ง กรุณาติดตั้ง Docker ก่อน
    pause
    exit /b 1
)

REM ตรวจสอบว่า Docker Compose ติดตั้งแล้วหรือไม่
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose ไม่ได้ติดตั้ง กรุณาติดตั้ง Docker Compose ก่อน
    pause
    exit /b 1
)

REM หยุด container เดิม (ถ้ามี)
echo 🛑 หยุด container เดิม...
docker-compose down

REM Build image ใหม่
echo 🔨 Build Docker image...
docker-compose build

REM รัน container
echo ▶️  รัน container...
docker-compose up -d

REM รอให้ container พร้อมใช้งาน
echo ⏳ รอให้ระบบพร้อมใช้งาน...
timeout /t 10 /nobreak >nul

REM ตรวจสอบสถานะ
docker-compose ps | findstr "Up" >nul
if errorlevel 1 (
    echo ❌ Deploy ล้มเหลว กรุณาตรวจสอบ logs:
    docker-compose logs
) else (
    echo ✅ Deploy สำเร็จ!
    echo 🌐 เข้าถึงแอปพลิเคชันได้ที่: http://localhost:5000
    echo.
    echo 📋 คำสั่งที่มีประโยชน์:
    echo   - ดู logs: docker-compose logs -f
    echo   - หยุดระบบ: docker-compose down
    echo   - รีสตาร์ท: docker-compose restart
)

pause 