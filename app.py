#Wedding Management System

from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import qrcode
import io #data save qr code
import base64 #binary data ne text 
import socket

app = Flask(__name__)#handle webpage and route
app.secret_key = "my_super_secret_key_98765" #data secure 

DB_PATH = "database.db"

# ---------------- DATABASE SETUP ----------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()#only command chalave data mate
 
    # Users table — for login system
    c.execute("""CREATE TABLE IF NOT EXISTS users(
                 id INTEGER PRIMARY KEY AUTOINCREMENT,   
                 username TEXT UNIQUE NOT NULL,
                 password TEXT NOT NULL)""")

    # Weddings table — basic wedding info
    c.execute("""CREATE TABLE IF NOT EXISTS weddings(
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 couple_name TEXT NOT NULL,
                 wedding_date TEXT NOT NULL,
                 location TEXT NOT NULL)""")

    # Vendors table — stores vendor details
    c.execute("""CREATE TABLE IF NOT EXISTS vendors(
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT NOT NULL,
                 service TEXT NOT NULL,
                 contact TEXT NOT NULL)""")

    
    # Guests table — links guests to a wedding ID
    c.execute("""CREATE TABLE IF NOT EXISTS guests(
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 wedding_id INTEGER NOT NULL,
                 name TEXT NOT NULL,
                 email TEXT,
                 phone TEXT,
                 FOREIGN KEY(wedding_id) REFERENCES weddings(id))""")

    # Budget table
    c.execute("""CREATE TABLE IF NOT EXISTS budget(
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 wedding_id INTEGER NOT NULL,
                 category TEXT NOT NULL,
                 amount INTEGER NOT NULL,
                 FOREIGN KEY(wedding_id) REFERENCES weddings(id))""")

    conn.commit() #table create data save
    conn.close()

init_db()

# ---------------- DASHBOARD ----------------
@app.route('/')
def dashboard():
    # User login validation
    if 'user_id' not in session:
        flash("Please login first!", "warning")
        return redirect(url_for('login'))

    # Theme selection    
    theme = session.get("theme", "light")
    return render_template('index.html', theme=theme)

# ---------------- LOGIN SYSTEM ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor() 

        # Check user exists or not
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()

        # If not exist → insert new user
        if not user:
            c.execute("INSERT INTO users(username, password) VALUES(?,?)",
                      (username, password))
            conn.commit()

        conn.close()

        # Login session start
        session['user_id'] = username
        flash("Login successful!", "success") #success colour deside 
        return redirect(url_for('dashboard'))

    return render_template('login.html')

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.pop('user_id', None)#Remove session
    flash("Logged out!", "info")
    return redirect(url_for('login'))

# ---------------- WEDDINGS CRUD ----------------
@app.route('/weddings')
def view_weddings():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM weddings")
    weddings = c.fetchall() #list ma store
    conn.close()
    return render_template('index.html', weddings=weddings, theme=session.get("theme", "light")) # aa return get request hoy to 


@app.route('/weddings/add', methods=['GET', 'POST'])
def add_wedding():
    if request.method == 'POST':
        # Getting form inputs
        couple_name = request.form.get('couple_name')
        date = request.form.get('wedding_date')
        location = request.form.get('location')

        # Insert into DB
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO weddings(couple_name, wedding_date, location) VALUES(?,?,?)",
                  (couple_name, date, location))
        conn.commit() #data save
        conn.close()

        flash("Wedding added!", "success")
        return redirect(url_for('view_weddings'))

    return render_template('index.html', theme=session.get("theme", "light"))

# ---------------- VENDORS CRUD ----------------
@app.route('/vendors')
def view_vendors():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM vendors")
    vendors = c.fetchall()
    conn.close()
    return render_template('index.html', vendors=vendors, theme=session.get("theme", "light"))

@app.route('/vendors/add', methods=['GET', 'POST'])
def add_vendor():
    if request.method == 'POST':
        name = request.form.get('name')
        service = request.form.get('service')
        contact = request.form.get('contact')

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO vendors(name, service, contact) VALUES(?,?,?)",
                  (name, service, contact))
        conn.commit()
        conn.close()

        flash("Vendor added!", "success")
        return redirect(url_for('view_vendors'))

    return render_template('index.html', theme=session.get("theme", "light"))

# ---------------- GUESTS CRUD ----------------
@app.route('/guests')
def view_guests():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Join query to show guest + wedding name
    c.execute("""
        SELECT guests.id, guests.name, guests.email, guests.phone,
               weddings.couple_name
        FROM guests 
        JOIN weddings ON guests.wedding_id = weddings.id
    """)
    guests = c.fetchall()
    conn.close()
    return render_template('index.html', guests=guests, theme=session.get("theme", "light"))

@app.route('/guests/add', methods=['GET', 'POST'])
def add_guest():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Fetch wedding list for dropdown
    c.execute("SELECT id, couple_name FROM weddings")
    weddings = c.fetchall()

    if request.method == 'POST':
        wid = request.form.get('wedding_id')
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        
        # Insert guest
        c.execute("INSERT INTO guests(wedding_id,name,email,phone) VALUES(?,?,?,?)",
                  (wid, name, email, phone))
        conn.commit()
        conn.close()

        flash("Guest added!", "success")
        return redirect(url_for('view_guests'))

    conn.close()
    return render_template('index.html', weddings=weddings, add_guest_page=True, theme=session.get("theme", "light"))

# ---------------- QR CODE SYSTEM----------------
@app.route('/generate_qr/<int:guest_id>')
def generate_qr(guest_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT guests.name, weddings.couple_name, weddings.wedding_date, weddings.location
        FROM guests 
        JOIN weddings ON guests.wedding_id = weddings.id
        WHERE guests.id = ?
    """, (guest_id,))
    data = c.fetchone()
    conn.close()

    if not data:
        flash("Guest not found", "danger")
        return redirect(url_for('view_guests'))

    guest_name, couple, date, location = data

    detail_url = url_for('wedding_detail', guest_id=guest_id, _external=True)

    qr = qrcode.make(detail_url)

    buf = io.BytesIO()
    qr.save(buf)
    qr_code = base64.b64encode(buf.getvalue()).decode()

    return render_template("qr.html",
                           qr_code=qr_code,
                           guest_name=guest_name)

    # Local system IP for QR link
    local_ip = socket.gethostbyname(socket.gethostname())#compute ip address 
    detail_url = f"http://{local_ip}:5000/wedding_detail/{guest_id}"#mobile link

    # Generate QR code
    qr = qrcode.QRCode(box_size=8, border=4)
    qr.add_data(detail_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
     # Convert to base64 to show on HTML
    buf = io.BytesIO()
    img.save(buf)
    qr_code = base64.b64encode(buf.getvalue()).decode()

    return render_template("qr.html", qr_code=qr_code, guest_name=guest_name, detail_url=detail_url)

@app.route('/wedding_detail/<int:guest_id>')
def wedding_detail(guest_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT guests.name, weddings.couple_name, weddings.wedding_date, weddings.location
        FROM guests 
        JOIN weddings ON guests.wedding_id = weddings.id
        WHERE guests.id = ?
    """, (guest_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        return "<h3>Details not found</h3>"

    gname, cname, date, loc = row
    
    # Simple HTML response
    return f"""
        <h1>Wedding Invitation</h1>
        <p><b>Guest:</b> {gname}</p>
        <p><b>Couple:</b> {cname}</p>
        <p><b>Date:</b> {date}</p>
        <p><b>Location:</b> {loc}</p>
        <h3>Thank you!</h3>
    """

# ---------------- BUDGET ----------------
@app.route('/budget')
def view_budget():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Join with wedding name
    c.execute("""
        SELECT budget.id, budget.wedding_id, budget.category, budget.amount, weddings.couple_name
        FROM budget
        JOIN weddings ON budget.wedding_id = weddings.id
    """)
    data = c.fetchall()
    conn.close()
    return render_template("index.html", budget=data, theme=session.get("theme", "light"))

@app.route('/budget/add', methods=['GET', 'POST'])
def add_budget():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Wedding dropdown
    c.execute("SELECT id, couple_name FROM weddings")
    weddings = c.fetchall()

    if request.method == 'POST':
        wedding_id = request.form.get('wedding_id')
        category = request.form.get('category')
        amount = request.form.get('amount')

        c.execute("INSERT INTO budget(wedding_id, category, amount) VALUES(?,?,?)",
                  (wedding_id, category, amount))
        conn.commit()
        conn.close()

        flash("Budget added!", "success")
        return redirect(url_for('view_budget'))

    conn.close()
    return render_template('index.html', weddings=weddings, add_budget_page=True, theme=session.get("theme", "light"))

# ---------------- THEME SYSTEM ----------------
@app.route('/theme')
def theme_page():
    return render_template("index.html", theme_page=True, theme=session.get("theme", "light"))

@app.route('/set_theme/<mode>')
def set_theme(mode): #user theme click kare ae aa mode ma aave
    # Only allow valid theme names
    if mode not in ["light", "dark"]:
        flash("Invalid theme!", "danger")
        return redirect(url_for("dashboard"))

    session["theme"] = mode #theme change thy
    flash(f"Theme changed to {mode}!", "success")
    return redirect(url_for("dashboard"))

# ---------------- RUN APP ----------------
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")