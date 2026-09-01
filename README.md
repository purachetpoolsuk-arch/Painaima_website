# 📸 Painaima (ไปไหนมา) - Lifestyle & Travel Social Platform

เว็บแอปพลิเคชัน Social Platform สไตล์ Instagram ผสมผสาน Lifestyle & Travel Diary สำหรับแชร์รูปภาพ วิดีโอสตอรี่ รีวิวสถานที่ คาเฟ่ ท่องเที่ยว พร้อมระบบติด Hashtag `#`, เช็คอิน Location, ไลก์, คอมเมนต์, ติดตามเพื่อน และระบบความปลอดภัยมาตรฐาน

---

## 🌟 ฟีเจอร์เด่น (Key Features)

- 📸 **Feed & Posts**: โพสต์รูปภาพพร้อมแคปชั่น, แท็ก `#`, และเช็คอินสถานที่
- 🎬 **Instagram Stories**: ลงรูป/วิดีโอสตอรี่, กดหัวใจลอย, ส่งข้อความตอบกลับสตอรี่ และระบบนำทางข้ามสตอรี่แบบต่อเนื่อง (Seamless Story Navigation)
- 🧭 **Explore & Search**: ค้นหาโพสต์ตามสถานที่ แฮชแท็ก และค้นหาเพื่อน
- 👤 **Profile & Follow**: หน้าโปรไฟล์ส่วนตัว, แก้ไขข้อมูล/รูปโปรไฟล์, ดูโพสต์ที่บันทึกไว้ และระบบกดติดตามเพื่อน
- 🔐 **Authentication & Security**: เข้าสู่ระบบ, สมัครสมาชิกพร้อมระบบตรวจสอบความปลอดภัยของรหัสผ่าน 4 ระดับ และรองรับการเข้าสู่ระบบด้วย Google (Google OAuth 2.0)
- 📱 **Mobile-First Design**: แถบนำทางด้านล่าง (Bottom Navigation Bar) สไตล์ Instagram รองรับทั้งจอมือถือ แท็บเล็ต และคอมพิวเตอร์

---

## 🚀 เทคโนโลยีที่ใช้ (Tech Stack)

- **Backend**: Python, Django 6
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **Auth**: Django-Allauth (Email & Google OAuth 2.0)
- **Frontend**: HTML5, CSS3 (Modern Glassmorphism & Instagram Dark Theme), Vanilla JavaScript
- **Static Assets**: WhiteNoise
- **Deployment**: Vercel Ready (`vercel.json`, `build_files.sh`)

---

## 💻 วิธีการรันบนเครื่อง Local (Development)

1. ติดตั้ง Dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. รัน Migration:
   ```bash
   python manage.py migrate
   ```
3. รันข้อมูลจำลองเริ่มต้น (Optional):
   ```bash
   python seed_data.py
   ```
4. เริ่มต้นเซิร์ฟเวอร์:
   ```bash
   python manage.py runserver
   ```
5. เปิดเบราว์เซอร์เข้าที่: `http://127.0.0.1:8000/`
