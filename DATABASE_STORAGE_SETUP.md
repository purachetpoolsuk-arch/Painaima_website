# 🗄️ คู่มือการตั้งค่า Neon (Database) & Cloudinary (รูปภาพ/วิดีโอ) บน Vercel

นี่คือสแต็กระดับมืออาชีพที่เหมาะสมที่สุดสำหรับ Django บน Vercel:
1. **Neon.tech**: จัดเก็บข้อมูลผู้ใช้ โพสต์ แคปชั่น ไลก์ คอมเมนต์ (PostgreSQL Serverless ฟรี)
2. **Cloudinary**: จัดเก็บไฟล์รูปภาพโปรไฟล์ โพสต์ และวิดีโอสตอรี่บนคลาวด์ CDN อัตโนมัติ (ฟรี)

---

### 1️⃣ ส่วนของ Neon (Database):
1. ไปที่ **[Neon.tech](https://neon.tech/)** &rarr; ล็อกอินด้วย GitHub
2. กด **Create Project** (ตั้งชื่อ เช่น `painaima-db`)
3. ในหน้า Dashboard จะเห็นกล่อง **Connection Details**:
   - เลือกเป็น **`Connection string`** แล้วกดปุ่ม Copy (ตัวอย่าง: `postgresql://neondb_owner:npg_xxx@ep-xxx.ap-southeast-1.aws.neon.tech/neondb?sslmode=require`)

---

### 2️⃣ ส่วนของ Cloudinary (Media Storage):
1. ไปที่ **[Cloudinary.com](https://cloudinary.com/)** &rarr; สมัคร/ล็อกอินบัญชีฟรี
2. ในหน้า **Dashboard** (หรือ Settings) จะเห็นข้อมูล 3 ตัว:
   - **Cloud Name**: (เช่น `dxxxxxxxx`)
   - **API Key**: (ตัวเลข เช่น `123456789012345`)
   - **API Secret**: (เช่น `AbCdEfGhIjKlMnOpQrStUvWxYz`)

---

### 3️⃣ นำค่าทั้งหมดไปใส่ใน Vercel Environment Variables:
1. เข้า **[Vercel Dashboard](https://vercel.com/dashboard)** &rarr; คลิกโปรเจกต์ `Painaima_website`
2. ไปที่ **Settings** &rarr; **Environment Variables**
3. เพิ่มตัวแปรเหล่านี้:
   - `DATABASE_URL`: `(วาง Connection string จาก Neon)`
   - `CLOUDINARY_CLOUD_NAME`: `(วาง Cloud Name จาก Cloudinary)`
   - `CLOUDINARY_API_KEY`: `(วาง API Key จาก Cloudinary)`
   - `CLOUDINARY_API_SECRET`: `(วาง API Secret จาก Cloudinary)`
4. ไปที่แถบ **Deployments** แล้วกด **Redeploy**

🎉 เว็บไซต์จะเชื่อมต่อกับ Database จริง และรูปภาพทั้งหมดจะถูกอัปโหลดขึ้น Cloudinary ทันที 100%!
