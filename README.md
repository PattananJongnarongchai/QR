# ระบบ Dynamic QR Code

ระบบสร้างและจัดการ QR Code แบบ Dynamic พร้อมฟีเจอร์อัพโหลดไฟล์

## ฟีเจอร์

- ✅ สร้าง QR Code สำหรับ URL
- ✅ อัพโหลดไฟล์และสร้าง QR Code
- ✅ ดาวน์โหลด QR Code เป็นไฟล์ PNG
- ✅ ติดตามจำนวนการสแกน
- ✅ แก้ไขและลบ QR Code
- ✅ UI/UX ที่สวยงามและ Responsive

## การติดตั้งด้วย Docker

### วิธีที่ 1: ใช้ Docker Compose (แนะนำ)

```bash
# Clone repository
git clone <repository-url>
cd QR

# รันด้วย Docker Compose
docker-compose up -d

# เข้าถึงแอปพลิเคชัน
# เปิดเบราว์เซอร์ไปที่ http://localhost:5000
```

### วิธีที่ 2: ใช้ Docker โดยตรง

```bash
# Build Docker image
docker build -t qr-code-app .

# รัน container
docker run -d \
  --name qr-app \
  -p 5000:5000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/instance:/app/instance \
  qr-code-app

# เข้าถึงแอปพลิเคชัน
# เปิดเบราว์เซอร์ไปที่ http://localhost:5000
```

## การใช้งาน

### สร้าง QR Code สำหรับ URL
1. ไปที่หน้า Dashboard
2. ใส่ URL ปลายทาง
3. คลิก "สร้าง QR Code"
4. ดาวน์โหลด QR Code ได้ทันที

### อัพโหลดไฟล์
1. คลิก "อัพโหลดไฟล์"
2. เลือกไฟล์ที่ต้องการ (รองรับ PDF, DOC, รูปภาพ, ZIP, etc.)
3. ระบบจะสร้าง QR Code อัตโนมัติ
4. ดาวน์โหลด QR Code ได้ทันที

### จัดการ QR Code
- **แก้ไข**: เปลี่ยน URL ปลายทาง
- **ลบ**: ลบ QR Code และไฟล์ที่เกี่ยวข้อง
- **ดาวน์โหลด**: ดาวน์โหลด QR Code เป็นไฟล์ PNG

## ข้อมูลเทคนิค

### Ports
- **5000**: Web application

### Volumes
- **./uploads**: ไฟล์ที่อัพโหลด
- **./instance**: ฐานข้อมูล SQLite

### Environment Variables
- `FLASK_ENV`: production
- `FLASK_APP`: app.py

## การพัฒนา

### รันในโหมด Development
```bash
# สร้าง virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# หรือ
venv\Scripts\activate     # Windows

# ติดตั้ง dependencies
pip install -r requirements.txt

# รันแอปพลิเคชัน
python app.py
```

### การ Build ใหม่
```bash
# หยุด container
docker-compose down

# Build ใหม่
docker-compose build

# รันใหม่
docker-compose up -d
```

## การ Backup

### Backup ฐานข้อมูล
```bash
# Copy ฐานข้อมูลออกมา
docker cp qr-app:/app/instance/qrcodes.db ./backup/
```

### Backup ไฟล์ที่อัพโหลด
```bash
# Copy โฟลเดอร์ uploads ออกมา
docker cp qr-app:/app/uploads ./backup/
```

## การ Troubleshoot

### ดู Logs
```bash
# ดู logs ของ container
docker-compose logs -f

# หรือ
docker logs qr-app
```

### เข้าไปใน Container
```bash
# เข้าไปใน container
docker exec -it qr-app bash
```

### รีเซ็ตฐานข้อมูล
```bash
# หยุด container
docker-compose down

# ลบฐานข้อมูล
rm -rf instance/uploads

# รันใหม่
docker-compose up -d
```

## License

MIT License 