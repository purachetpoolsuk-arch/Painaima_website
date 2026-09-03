# วิธีตั้งค่า Google OAuth Login สำหรับ Painaima (ไปไหนมา)

ระบบรองรับการเข้าสู่ระบบด้วย Google ผ่านแพ็กเกจ `django-allauth` คุณสามารถเปิดใช้งานได้ง่ายๆ ตามขั้นตอนดังนี้:

---

### ขั้นตอนที่ 1: สร้าง Google OAuth 2.0 Client ID

1. ไปที่ **[Google Cloud Console](https://console.cloud.google.com/)**
2. สร้างโปรเจกต์ใหม่ (เช่น `Painaima Web`) หรือเลือกโปรเจกต์เดิมที่มีอยู่
3. ไปที่เมนู **APIs & Services** &rarr; **OAuth consent screen (หน้าจอยินยอม)**
   - เลือก User Type เป็น **External**
   - กรอกชื่อแอป เช่น `Painaima` และใส่อีเมลติดต่อ
   - กด Save and Continue
4. ไปที่เมนู **Credentials (ข้อมูลรับรอง)** &rarr; คลิก **Create Credentials** &rarr; เลือก **OAuth client ID**
   - Application type: เลือก **Web application**
   - Name: `Painaima Web Client`
   - **Authorized JavaScript origins**:
     - `http://127.0.0.1:8000`
     - `http://localhost:8000`
     - `https://painaima.vercel.app`
   - **Authorized redirect URIs**:
     - `http://127.0.0.1:8000/accounts/google/login/callback/`
     - `http://localhost:8000/accounts/google/login/callback/`
     - `https://painaima.vercel.app/accounts/google/login/callback/`
5. คลิก **Create** จะได้รับ **Client ID** และ **Client Secret**

---

### ขั้นตอนที่ 2: ใส่ข้อมูลลงในไฟล์ `.env`

เปิดไฟล์ `.env` ในโฟลเดอร์โปรเจกต์ แล้วใส่ค่าที่ได้:

```env
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

---

### ขั้นตอนที่ 3: (ทางเลือก) หรือตั้งค่าผ่าน Django Admin

1. เข้าหน้า Django Admin: `http://127.0.0.1:8000/admin/`
2. ไปที่หัวข้อ **Social Accounts** &rarr; **Social applications** &rarr; คลิก **Add Social Application**
   - Provider: `Google`
   - Name: `Google Auth`
   - Client id: *(ใส่ Client ID จากขั้นตอนที่ 1)*
   - Secret key: *(ใส่ Client Secret จากขั้นตอนที่ 1)*
   - Sites: เลือก `example.com` หรือ Domain ของคุณ ย้ายมาฝั่ง Chosen sites
3. กด **Save**

เมื่อตั้งค่าเสร็จแล้ว ปุ่ม **"เข้าสู่ระบบด้วย Google"** ในหน้า Login และ Register จะทำงานได้ทันที!
