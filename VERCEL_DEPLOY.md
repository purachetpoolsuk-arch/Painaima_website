# 🚀 คู่มือการนำ Painaima ขึ้น Vercel (Vercel Deployment Guide)

โปรเจกต์ได้รับการตั้งค่าไฟล์คอนฟิกสำหรับ Vercel (`vercel.json`, `build_files.sh`, `requirements.txt`, `WhiteNoise`) ไว้อย่างสมบูรณ์แล้ว สามารถนำขึ้น Vercel ได้ง่ายๆ ตามขั้นตอนดังนี้:

---

### ขั้นตอนที่ 1: Push โค้ดขึ้น GitHub

1. สร้าง GitHub Repository ใหม่ (เช่น `painaima-web`)
2. รันคำสั่งใน Terminal:
   ```bash
   git init
   git add .
   git commit -m "Deploy Painaima to Vercel"
   git branch -M main
   git remote add origin https://github.com/your-username/painaima-web.git
   git push -u origin main
   ```

---

### ขั้นตอนที่ 2: Import โปรเจกต์เข้า Vercel

1. เข้าไปที่ **[Vercel Dashboard](https://vercel.com/dashboard)**
2. คลิก **Add New...** &rarr; เลือก **Project**
3. เลือก Repository `painaima-web` แล้วคลิก **Import**
4. ในส่วน **Environment Variables** ให้เพิ่มตัวแปรดังนี้:
   - `SECRET_KEY`: `your-django-secret-key`
   - `DEBUG`: `False`
   - `GOOGLE_CLIENT_ID`: `your-google-client-id.apps.googleusercontent.com`
   - `GOOGLE_CLIENT_SECRET`: `your-google-client-secret`
5. คลิก **Deploy** &rarr; รอ Vercel Build ประมาณ 1-2 นาที คุณจะได้ URL เว็บไซต์ เช่น `https://painaima.vercel.app`

---

### ขั้นตอนที่ 3: อัปเดต Authorized Redirect URIs ใน Google Cloud Console

เพื่อให้ Google Login ทำงานบน Domain ของ Vercel ได้อย่างถูกต้อง:
1. ไปที่ **[Google Cloud Console Credentials](https://console.cloud.google.com/apis/credentials)**
2. คลิกแก้ไข Client ID ที่สร้างไว้
3. ในส่วน **Authorized JavaScript origins** เพิ่ม:
   ```
   https://painaima.vercel.app
   ```
4. ในส่วน **Authorized redirect URIs** เพิ่ม:
   ```
   https://painaima.vercel.app/accounts/google/login/callback/
   ```
5. กด **Save**

🎉 เสร็จสมบูรณ์! เว็บไซต์บน Vercel จะพร้อมใช้งานทั้งฟีด, สตอรี่, โพสต์, ไลก์, คอมเมนต์ และระบบ Google Login ของจริง 100%!
