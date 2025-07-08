# ใช้ Python 3.11 เป็น base image
FROM python:3.11-slim

# ตั้งค่า working directory
WORKDIR /app

# ตั้งค่า environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# ติดตั้ง system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        libjpeg-dev \
        zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# คัดลอก requirements file
COPY requirements.txt .

# ติดตั้ง Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# คัดลอก source code
COPY . .

# สร้างโฟลเดอร์สำหรับ uploads และ instance
RUN mkdir -p uploads instance

# ตั้งค่าสิทธิ์การเข้าถึง
RUN chmod 755 uploads instance

# เปิด port 5000
EXPOSE 5000

# สร้าง user ที่ไม่ใช่ root
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# รันแอปพลิเคชัน
CMD ["gunicorn", "-b", "0.0.0.0:5000", "wsgi:app"] 