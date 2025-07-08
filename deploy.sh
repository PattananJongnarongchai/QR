#!/bin/bash

# Script สำหรับ Deploy ระบบ Dynamic QR Code

echo "🚀 เริ่มต้น Deploy ระบบ Dynamic QR Code..."

# ตรวจสอบว่า Docker ติดตั้งแล้วหรือไม่
if ! command -v docker &> /dev/null; then
    echo "❌ Docker ไม่ได้ติดตั้ง กรุณาติดตั้ง Docker ก่อน"
    exit 1
fi

# ตรวจสอบว่า Docker Compose ติดตั้งแล้วหรือไม่
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose ไม่ได้ติดตั้ง กรุณาติดตั้ง Docker Compose ก่อน"
    exit 1
fi

# หยุด container เดิม (ถ้ามี)
echo "🛑 หยุด container เดิม..."
docker-compose down

# Build image ใหม่
echo "🔨 Build Docker image..."
docker-compose build

# รัน container
echo "▶️  รัน container..."
docker-compose up -d

# รอให้ container พร้อมใช้งาน
echo "⏳ รอให้ระบบพร้อมใช้งาน..."
sleep 10

# ตรวจสอบสถานะ
if docker-compose ps | grep -q "Up"; then
    echo "✅ Deploy สำเร็จ!"
    echo "🌐 เข้าถึงแอปพลิเคชันได้ที่: http://localhost:5000"
    echo ""
    echo "📋 คำสั่งที่มีประโยชน์:"
    echo "  - ดู logs: docker-compose logs -f"
    echo "  - หยุดระบบ: docker-compose down"
    echo "  - รีสตาร์ท: docker-compose restart"
else
    echo "❌ Deploy ล้มเหลว กรุณาตรวจสอบ logs:"
    docker-compose logs
fi 