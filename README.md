# 💍 Wedding Management System

A modern Flask-based Wedding Management System with QR-based invitation system, guest management, vendor tracking, budget management, and dynamic light/dark theme UI.

---

## 🚀 Features

- 🔐 Login System (Auto-register if user not exists)
- 🎉 Wedding Management (Add / View Weddings)
- 🤝 Vendor Management
- 👥 Guest Management (Linked with Wedding)
- 📊 Budget Tracking
- 📱 QR Code Invitation System
- 🎨 Light / Dark Theme Toggle
- ✨ Animated UI + Particle Background
- 💾 SQLite Database (Local Storage)

---

## 🛠 Tech Stack

- Backend: Python (Flask)
- Database: SQLite3
- Frontend: HTML, CSS, JavaScript
- QR Code: qrcode library
- Session Management: Flask session

---

## 📂 Project Structure

Wedding-Management-System/
│
├── app.py
├── database.db
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── qr.html
│
├── static/
│   ├── style.css
│
└── README.md

---

## ⚙️ Installation Guide

### 1️⃣ Clone Repository

git clone https://github.com/your-username/wedding-management-system.git  
cd wedding-management-system  

### 2️⃣ Create Virtual Environment (Optional)

python -m venv venv  

Activate:

Windows:
venv\Scripts\activate  

Mac/Linux:
source venv/bin/activate  

### 3️⃣ Install Dependencies

pip install flask qrcode pillow  

### 4️⃣ Run Application

python app.py  

App runs on:

http://127.0.0.1:5000/  

or  

http://YOUR_LOCAL_IP:5000/  

---

## 🗄 Database Tables

### Users
- id
- username
- password

### Weddings
- id
- couple_name
- wedding_date
- location

### Vendors
- id
- name
- service
- contact

### Guests
- id
- wedding_id (Foreign Key)
- name
- email
- phone

### Budget
- id
- wedding_id (Foreign Key)
- category
- amount

---

## 📱 QR Code System

Each guest has a unique QR code.

QR redirects to:

/wedding_detail/<guest_id>

Displays:
- Guest Name
- Couple Name
- Wedding Date
- Location

Perfect for:
- Digital Invitations
- Entry Verification
- Contactless Event Check-in

---

## 🎨 Theme System

Users can toggle between:

Light Mode  
Dark Mode  

Theme preference stored in session.

---

## 🔒 Security Note

⚠ Passwords are currently stored in plain text.  
For production, use password hashing:

Example:

from werkzeug.security import generate_password_hash, check_password_hash

---

## 🧠 Future Improvements

- Wedding Edit/Delete
- Guest RSVP Status
- CSV Export
- Email Invitations
- Admin Role System
- Deployment on Render / Railway

---

## 👨‍💻 Author

Wedding Management System Project – 2025  
Built using Flask + SQLite  

---

## 📜 License

This project is for educational purposes.  
You can modify and use freely.