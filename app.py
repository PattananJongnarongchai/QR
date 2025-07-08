import string
import random
import os
import qrcode
import io
from flask import Flask, request, redirect, render_template, flash, url_for, send_from_directory, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

# --- การตั้งค่าเริ่มต้น ---
app = Flask(__name__)
# ตั้งค่า Secret Key สำหรับการใช้ flash messages
app.config['SECRET_KEY'] = 'your-very-secret-key' # ควรเปลี่ยนเป็นค่าที่สุ่มขึ้นมา
# ตั้งค่าฐานข้อมูล SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///qrcodes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ตั้งค่าสำหรับอัพโหลดไฟล์
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'zip', 'rar'}

# สร้างโฟลเดอร์ uploads ถ้ายังไม่มี
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db = SQLAlchemy(app)

# --- โมเดลฐานข้อมูล ---
class QrLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    short_code = db.Column(db.String(10), unique=True, nullable=False)
    original_url = db.Column(db.String(2048), nullable=False)
    scan_count = db.Column(db.Integer, default=0)
    file_name = db.Column(db.String(255), nullable=True)  # เพิ่มฟิลด์สำหรับชื่อไฟล์
    file_type = db.Column(db.String(50), nullable=True)   # เพิ่มฟิลด์สำหรับประเภทไฟล์

    def __repr__(self):
        return f'<QrLink {self.short_code}>'

# --- ฟังก์ชันช่วยเหลือ ---
def generate_short_code(length=7):
    characters = string.ascii_letters + string.digits
    while True:
        short_code = ''.join(random.choice(characters) for i in range(length))
        if QrLink.query.filter_by(short_code=short_code).first() is None:
            return short_code

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_qr_code_image(url, size=400):
    """สร้าง QR Code เป็นรูปภาพ"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    # ปรับขนาดรูปภาพ
    img = img.resize((size, size))
    
    # แปลงเป็น bytes
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    
    return img_io

# --- ส่วนของ Routing ---

# Endpoint สำหรับดาวน์โหลด QR Code
@app.route('/download-qr/<short_code>')
def download_qr_code(short_code):
    link = QrLink.query.filter_by(short_code=short_code).first_or_404()
    
    # สร้าง URL สำหรับ QR Code
    qr_url = request.host_url + short_code
    
    # สร้าง QR Code
    qr_image = generate_qr_code_image(qr_url, size=800)
    
    # สร้างชื่อไฟล์
    filename = f"qr_code_{short_code}.png"
    
    return send_file(
        qr_image,
        mimetype='image/png',
        as_attachment=True,
        download_name=filename
    )

# Endpoint สำหรับดาวน์โหลดไฟล์
@app.route('/download/<short_code>')
def download_file(short_code):
    link = QrLink.query.filter_by(short_code=short_code).first_or_404()
    if link.file_name:
        link.scan_count += 1
        db.session.commit()
        return send_from_directory(app.config['UPLOAD_FOLDER'], link.file_name, as_attachment=True)
    return redirect(link.original_url)

# Endpoint หลักสำหรับการ Redirect (เมื่อมีคนสแกน QR)
@app.route('/<short_code>')
def redirect_to_url(short_code):
    link = QrLink.query.filter_by(short_code=short_code).first_or_404()
    link.scan_count += 1
    db.session.commit()
    
    # ถ้าเป็นไฟล์ ให้ redirect ไปหน้า download
    if link.file_name:
        return redirect(url_for('download_file', short_code=short_code))
    
    return redirect(link.original_url)

# หน้า Dashboard สำหรับจัดการทั้งหมด
@app.route('/')
def dashboard():
    links = QrLink.query.order_by(QrLink.id.desc()).all()
    return render_template('dashboard.html', links=links)

# การสร้าง Link ใหม่ (รับข้อมูลจากฟอร์มใน Dashboard)
@app.route('/create', methods=['POST'])
def create_link():
    original_url = request.form.get('url')
    if not original_url:
        flash('กรุณาใส่ URL ปลายทาง', 'error')
        return redirect(url_for('dashboard'))

    short_code = generate_short_code()
    new_link = QrLink(short_code=short_code, original_url=original_url)
    db.session.add(new_link)
    db.session.commit()
    
    flash(f'สร้าง Dynamic Link สำเร็จ! โค้ดคือ: {short_code}', 'success')
    return redirect(url_for('dashboard'))

# หน้าสำหรับอัพโหลดไฟล์
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # ตรวจสอบว่ามีไฟล์ใน request หรือไม่
        if 'file' not in request.files:
            flash('ไม่พบไฟล์ที่เลือก', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        # ตรวจสอบว่าผู้ใช้เลือกไฟล์หรือไม่
        if file.filename == '':
            flash('ไม่ได้เลือกไฟล์', 'error')
            return redirect(request.url)
        
        # ตรวจสอบประเภทไฟล์
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            
            # สร้างชื่อไฟล์ที่ไม่ซ้ำกัน
            base_name = filename.rsplit('.', 1)[0]
            extension = filename.rsplit('.', 1)[1]
            counter = 1
            original_filename = filename
            
            while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
                filename = f"{base_name}_{counter}.{extension}"
                counter += 1
            
            # บันทึกไฟล์
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            # สร้าง short code และบันทึกลงฐานข้อมูล
            short_code = generate_short_code()
            download_url = url_for('download_file', short_code=short_code, _external=True)
            
            new_link = QrLink(
                short_code=short_code,
                original_url=download_url,
                file_name=filename,
                file_type=extension.upper()
            )
            db.session.add(new_link)
            db.session.commit()
            
            flash(f'อัพโหลดไฟล์สำเร็จ! โค้ด QR คือ: {short_code}', 'success')
            return redirect(url_for('upload_file', success=short_code))
        else:
            flash('ประเภทไฟล์ไม่ได้รับอนุญาต', 'error')
            return redirect(request.url)
    
    return render_template('upload.html')

# หน้าสำหรับแก้ไข Link
@app.route('/edit/<int:link_id>', methods=['GET', 'POST'])
def edit_link(link_id):
    link_to_edit = QrLink.query.get_or_404(link_id)
    
    if request.method == 'POST':
        new_url = request.form.get('new_url')
        if not new_url:
            flash('URL ใหม่ไม่สามารถเป็นค่าว่างได้', 'error')
            return render_template('edit.html', link=link_to_edit)
            
        link_to_edit.original_url = new_url
        db.session.commit()
        flash('อัปเดต URL ปลายทางเรียบร้อยแล้ว!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('edit.html', link=link_to_edit)

# การลบ Link
@app.route('/delete/<int:link_id>', methods=['POST'])
def delete_link(link_id):
    link_to_delete = QrLink.query.get_or_404(link_id)
    
    # ลบไฟล์ถ้ามี
    if link_to_delete.file_name:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], link_to_delete.file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
    
    db.session.delete(link_to_delete)
    db.session.commit()
    flash('ลบ Link เรียบร้อยแล้ว', 'success')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=False)