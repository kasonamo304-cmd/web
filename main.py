from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from datetime import datetime
import sqlite3
import secrets
import re
import json

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['TEMPLATES_AUTO_RELOAD'] = True

DB = "paper.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

# تهيئة قاعدة البيانات
def init_db():
    conn = get_db()
    
    # جدول المستخدمين
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT UNIQUE,
            password TEXT NOT NULL,
            type TEXT DEFAULT 'individual',
            company_name TEXT,
            governorate TEXT,
            address TEXT,
            role TEXT NOT NULL DEFAULT 'customer',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # جدول المنتجات
    conn.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            min_quantity INTEGER DEFAULT 1,
            unit TEXT DEFAULT 'كجم',
            category TEXT,
            image TEXT,
            features TEXT,
            available BOOLEAN DEFAULT 1,
            company_id INTEGER,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES users(id),
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    ''')
    
    # جدول الطلبات
    conn.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number TEXT UNIQUE,
            user_id INTEGER,
            products TEXT,
            quantity INTEGER,
            subtotal REAL,
            delivery_fee REAL,
            total REAL,
            delivery_date TEXT,
            delivery_time TEXT,
            notes TEXT,
            payment_method TEXT,
            status TEXT DEFAULT 'قيد المراجعة',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # إضافة مستخدمين تجريبيين
    cursor = conn.execute("SELECT * FROM users WHERE email = ?", ("admin@ecopaper.com",))
    if not cursor.fetchone():
        conn.execute("""
            INSERT INTO users (name, email, phone, password, type, governorate, address, role)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ("مدير النظام", "admin@ecopaper.com", "01234567890", "admin123", "admin", "القاهرة", "المنطقة الصناعية", "admin"))
    
    cursor = conn.execute("SELECT * FROM users WHERE email = ?", ("شركة1@ecopaper.com",))
    if not cursor.fetchone():
        conn.execute("""
            INSERT INTO users (name, email, phone, password, type, company_name, governorate, address, role)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("شركة التدوير الأولى", "شركة1@ecopaper.com", "01234567891", "company123", "company", "شركة إعادة التدوير الأولى", "الجيزة", "المنطقة الصناعية", "company"))
    
    cursor = conn.execute("SELECT * FROM users WHERE email = ?", ("user@example.com",))
    if not cursor.fetchone():
        conn.execute("""
            INSERT INTO users (name, email, phone, password, type, governorate, address, role)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ("أحمد محمد", "user@example.com", "01234567892", "user123", "individual", "القاهرة", "مدينة نصر", "customer"))
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

# استدعاء التهيئة
init_db()

# ==================== الصفحات الرئيسية ====================

@app.route("/")
def home():
    if 'user_id' in session:
        return redirect(url_for('base'))
    return redirect(url_for('index'))

@app.route("/index")
def index():
    if 'user_id' in session:
        return redirect(url_for('base'))
    return render_template("index.html")

@app.route("/base")
def base():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    conn.close()
    
    return render_template("home.html", user=user)

# ==================== المصادقة ====================

@app.route("/login")
def login():
    if 'user_id' in session:
        return redirect(url_for('base'))
    return render_template("login.html")

@app.route("/register")
def register():
    if 'user_id' in session:
        return redirect(url_for('base'))
    return render_template("register.html")

@app.route("/forget_password")
def forget_password():
    return render_template("forget_passowrd.html")
@app.route("/otp")
def otp():
    return render_template("otp.html")

@app.route("/reset_password")
def reset_password():
    return render_template("reset_password.html")

@app.route("/dashboard")
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    orders_count = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    conn.close()
    
    return render_template("dashboard.html", user=user, orders_count=orders_count)

@app.route("/submit", methods=["POST"])
def submit():
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    confirm_password = request.form.get("confirmPassword")
    phone = request.form.get("phone")
    userType = request.form.get("userType")
    address = request.form.get("address")
    governorate = request.form.get("governorate")
    company_name = request.form.get("companyName") if userType == "company" else None
    
    if password != confirm_password:
        flash("كلمات المرور غير متطابقة", "error")
        return redirect(url_for("register"))
    
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        flash("البريد الإلكتروني غير صالح", "error")
        return redirect(url_for("register"))
    
    if not re.match(r"^01[0125][0-9]{8}$", phone):
        flash("رقم الهاتف غير صالح", "error")
        return redirect(url_for("register"))
    
    conn = get_db()
    
    existing = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if existing:
        conn.close()
        flash("البريد الإلكتروني مسجل بالفعل", "error")
        return redirect(url_for("register"))
    
    existing = conn.execute("SELECT * FROM users WHERE phone = ?", (phone,)).fetchone()
    if existing:
        conn.close()
        flash("رقم الهاتف مسجل بالفعل", "error")
        return redirect(url_for("register"))
    
    try:
        if userType == "company":
            role = "company"
        else:
            role = "customer"
        
        conn.execute("""
            INSERT INTO users 
            (name, email, password, phone, type, company_name, governorate, address, role, created_at) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, email, password, phone, userType, company_name, governorate, address, role, date))
        
        conn.commit()
        flash("✅ تم إنشاء الحساب بنجاح", "success")
        return redirect(url_for("login"))
    
    except Exception as e:
        flash(f"❌ حدث خطأ: {str(e)}", "error")
        return redirect(url_for("register"))
    
    finally:
        conn.close()

@app.route("/sure", methods=["POST"])
def sure():
    email = request.form.get("email")
    password = request.form.get("password")
    remember = request.form.get("rememberMe")
    
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    
    if not user:
        conn.close()
        flash("❌ البريد الإلكتروني غير مسجل", "error")
        return redirect(url_for("login"))
    
    if user["password"] != password:
        conn.close()
        flash("❌ كلمة المرور غير صحيحة", "error")
        return redirect(url_for("login"))
    
    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    session["user_email"] = user["email"]
    session["user_role"] = user["role"]
    session["user_type"] = user["type"]
    session["company_name"] = user["company_name"]
    
    if remember:
        session.permanent = True
    
    flash(f"✅ تم تسجيل الدخول بنجاح {user['name']}", "success")
    
    if user["role"] == "admin":
        return redirect(url_for("admin_products"))
    elif user["role"] == "company":
        return redirect(url_for("company_products"))
    else:
        return redirect(url_for("base"))

@app.route("/logout")
def logout():
    session.clear()
    flash("✅ تم تسجيل الخروج بنجاح", "success")
    return redirect(url_for("index"))

# ==================== صفحات المستخدم العادي ====================

@app.route("/products")
def product():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template("product.html")

@app.route("/orders-history")
def orders_history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template("orders-history.html")

@app.route("/profile")
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    conn.close()
    
    return render_template("profile.html", user=user)

@app.route("/create-order")
def create_order():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template("order.html")

@app.route("/order-tracking")
def order_tracking():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template("order-tracking.html")

@app.route("/order-confirm")
def order_confirm():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template("order_confirm.html")

@app.route("/payment")
def payment():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template("payment.html")

# ==================== صفحات الشركات (Company) ====================

@app.route("/company/products")
def company_products():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    conn.close()
    
    if user["role"] not in ["company", "admin"]:
        flash("❌ ليس لديك صلاحية الوصول إلى هذه الصفحة", "error")
        return redirect(url_for('base'))
    
    return render_template("company_products.html", user=user)

@app.route("/company/orders")
def company_orders():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    
    if user["role"] not in ["company", "admin"]:
        conn.close()
        flash("❌ ليس لديك صلاحية الوصول إلى هذه الصفحة", "error")
        return redirect(url_for('base'))
    
    orders = conn.execute("""
        SELECT o.*, u.name as user_name, u.phone 
        FROM orders o 
        JOIN users u ON o.user_id = u.id 
        ORDER BY o.created_at DESC
    """).fetchall()
    conn.close()
    
    return render_template("company_orders.html", orders=orders, user=user)

# ==================== صفحات الإدارة (Admin Only) ====================

@app.route("/admin/products")
def admin_products():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    conn.close()
    
    if user["role"] != "admin":
        flash("❌ ليس لديك صلاحية الوصول إلى هذه الصفحة", "error")
        return redirect(url_for('base'))
    
    return render_template("admin_products.html", user=user)

@app.route("/admin/orders")
def admin_orders():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    
    if user["role"] != "admin":
        conn.close()
        flash("❌ ليس لديك صلاحية الوصول إلى هذه الصفحة", "error")
        return redirect(url_for('base'))
    
    orders = conn.execute("""
        SELECT o.*, u.name as user_name, u.email, u.phone, u.type
        FROM orders o 
        JOIN users u ON o.user_id = u.id 
        ORDER BY o.created_at DESC
    """).fetchall()
    conn.close()
    
    return render_template("admin_orders.html", orders=orders, user=user)

@app.route("/admin/order/<int:order_id>/status", methods=["POST"])
def update_order_status(order_id):
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "غير مصرح"})
    
    data = request.get_json()
    new_status = data.get("status")
    
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    
    if user["role"] != "admin":
        conn.close()
        return jsonify({"success": False, "message": "ليس لديك صلاحية"})
    
    conn.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))
    conn.commit()
    conn.close()
    
    return jsonify({"success": True, "message": "تم تحديث حالة الطلب"})

# ==================== API Routes ====================

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()
    email_or_phone = data.get("emailOrPhone")
    password = data.get("password")
    
    conn = get_db()
    
    user = conn.execute(
        "SELECT * FROM users WHERE email = ? OR phone = ?", 
        (email_or_phone, email_or_phone)
    ).fetchone()
    
    if not user:
        conn.close()
        return jsonify({"success": False, "message": "البريد الإلكتروني أو رقم الهاتف غير مسجل"})
    
    if user["password"] != password:
        conn.close()
        return jsonify({"success": False, "message": "كلمة المرور غير صحيحة"})
    
    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    session["user_role"] = user["role"]
    session["user_type"] = user["type"]
    session["company_name"] = user["company_name"]
    
    user_data = {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "phone": user["phone"],
        "type": user["type"],
        "company_name": user["company_name"],
        "governorate": user["governorate"],
        "address": user["address"],
        "role": user["role"],
        "created_at": user["created_at"]
    }
    
    conn.close()
    return jsonify({
        "success": True, 
        "message": f"تم تسجيل الدخول بنجاح {user['name']}",
        "user": user_data
    })

@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json()
    
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    password = data.get("password")
    userType = data.get("userType", "individual")
    governorate = data.get("governorate")
    address = data.get("address")
    company_name = data.get("companyName") if userType == "company" else None
    
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"success": False, "message": "البريد الإلكتروني غير صالح"})
    
    if not re.match(r"^01[0125][0-9]{8}$", phone):
        return jsonify({"success": False, "message": "رقم الهاتف غير صالح"})
    
    conn = get_db()
    
    existing = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if existing:
        conn.close()
        return jsonify({"success": False, "message": "البريد الإلكتروني مسجل بالفعل"})
    
    existing = conn.execute("SELECT * FROM users WHERE phone = ?", (phone,)).fetchone()
    if existing:
        conn.close()
        return jsonify({"success": False, "message": "رقم الهاتف مسجل بالفعل"})
    
    try:
        now = datetime.now().strftime("%Y-%m-%d")
        
        if userType == "company":
            role = "company"
        else:
            role = "customer"
        
        conn.execute("""
            INSERT INTO users 
            (name, email, phone, password, type, company_name, governorate, address, role, created_at) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, email, phone, password, userType, company_name, governorate, address, role, now))
        
        conn.commit()
        
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        session["user_role"] = user["role"]
        session["user_type"] = user["type"]
        session["company_name"] = user["company_name"]
        
        conn.close()
        
        return jsonify({
            "success": True, 
            "message": "تم إنشاء الحساب بنجاح",
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "phone": user["phone"],
                "type": user["type"],
                "company_name": user["company_name"],
                "role": user["role"]
            }
        })
        
    except Exception as e:
        conn.close()
        return jsonify({"success": False, "message": f"حدث خطأ: {str(e)}"})

@app.route("/api/user-data", methods=["GET"])
def api_user_data():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "غير مصرح"})
    
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    conn.close()
    
    if not user:
        return jsonify({"success": False, "message": "المستخدم غير موجود"})
    
    return jsonify({
        "success": True,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "phone": user["phone"],
            "type": user["type"],
            "company_name": user["company_name"],
            "governorate": user["governorate"],
            "address": user["address"],
            "role": user["role"],
            "created_at": user["created_at"]
        }
    })

@app.route("/api/update-password", methods=["POST"])
def api_update_password():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "غير مصرح"})
    
    data = request.get_json()
    user_id = data.get("userId")
    new_password = data.get("newPassword")
    
    if int(user_id) != session["user_id"]:
        return jsonify({"success": False, "message": "غير مصرح"})
    
    conn = get_db()
    
    try:
        conn.execute(
            "UPDATE users SET password = ? WHERE id = ?",
            (new_password, user_id)
        )
        conn.commit()
        
        return jsonify({
            "success": True,
            "message": "تم تحديث كلمة المرور بنجاح"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"حدث خطأ: {str(e)}"
        })
    finally:
        conn.close()

@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"success": True, "message": "تم تسجيل الخروج بنجاح"})

# ==================== Product Management API (للشركات) ====================

@app.route("/api/company/products", methods=["GET"])
def api_get_company_products():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "غير مصرح"})
    
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    
    if user["role"] == "admin":
        products = conn.execute("SELECT * FROM products ORDER BY created_at DESC").fetchall()
    elif user["role"] == "company":
        products = conn.execute("SELECT * FROM products WHERE company_id = ? ORDER BY created_at DESC", (user["id"],)).fetchall()
    else:
        conn.close()
        return jsonify({"success": False, "message": "ليس لديك صلاحية"})
    
    conn.close()
    
    products_list = []
    for p in products:
        product_dict = dict(p)
        if product_dict["features"]:
            try:
                product_dict["features"] = json.loads(product_dict["features"])
            except:
                product_dict["features"] = []
        products_list.append(product_dict)
    
    return jsonify({"success": True, "products": products_list})

@app.route("/api/company/products", methods=["POST"])
def api_create_company_product():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "غير مصرح"})
    
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    
    if user["role"] not in ["company", "admin"]:
        conn.close()
        return jsonify({"success": False, "message": "ليس لديك صلاحية"})
    
    data = request.get_json()
    
    features_json = json.dumps(data.get("features", []))
    
    company_id = user["id"] if user["role"] == "company" else data.get("company_id", user["id"])
    
    conn.execute("""
        INSERT INTO products (name, description, price, min_quantity, unit, category, image, features, company_id, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("name"),
        data.get("description"),
        data.get("price"),
        data.get("minQuantity", 1),
        data.get("unit", "كجم"),
        data.get("category"),
        data.get("image"),
        features_json,
        company_id,
        session["user_id"]
    ))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        "success": True, 
        "message": "تم إضافة المنتج بنجاح",
        "product": data
    })

@app.route("/api/company/products/<int:product_id>", methods=["PUT", "DELETE"])
def api_manage_company_product(product_id):
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "غير مصرح"})
    
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    
    product = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    
    if not product:
        conn.close()
        return jsonify({"success": False, "message": "المنتج غير موجود"})
    
    if user["role"] == "admin":
        pass
    elif user["role"] == "company" and product["company_id"] != user["id"]:
        conn.close()
        return jsonify({"success": False, "message": "ليس لديك صلاحية لتعديل هذا المنتج"})
    else:
        conn.close()
        return jsonify({"success": False, "message": "ليس لديك صلاحية"})
    
    if request.method == "DELETE":
        conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "تم حذف المنتج بنجاح"})
    
    else:
        data = request.get_json()
        features_json = json.dumps(data.get("features", []))
        
        conn.execute("""
            UPDATE products 
            SET name = ?, description = ?, price = ?, min_quantity = ?, 
                unit = ?, category = ?, image = ?, features = ?, available = ?
            WHERE id = ?
        """, (
            data.get("name"),
            data.get("description"),
            data.get("price"),
            data.get("minQuantity"),
            data.get("unit", "كجم"),
            data.get("category"),
            data.get("image"),
            features_json,
            data.get("available", 1),
            product_id
        ))
        
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "تم تحديث المنتج بنجاح"})

# ==================== Orders API ====================

@app.route("/api/orders", methods=["GET", "POST"])
def api_orders():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "غير مصرح"})
    
    if request.method == "GET":
        conn = get_db()
        
        user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
        
        if user["role"] == "admin":
            orders = conn.execute("""
                SELECT o.*, u.name as user_name, u.phone, u.type
                FROM orders o 
                JOIN users u ON o.user_id = u.id 
                ORDER BY o.created_at DESC
            """).fetchall()
        elif user["role"] == "company":
            orders = conn.execute("""
                SELECT o.*, u.name as user_name, u.phone 
                FROM orders o 
                JOIN users u ON o.user_id = u.id 
                ORDER BY o.created_at DESC
            """).fetchall()
        else:
            orders = conn.execute(
                "SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC", 
                (session["user_id"],)
            ).fetchall()
        
        conn.close()
        
        orders_list = []
        for o in orders:
            order_dict = dict(o)
            if order_dict["products"]:
                try:
                    order_dict["products"] = json.loads(order_dict["products"])
                except:
                    order_dict["products"] = []
            orders_list.append(order_dict)
        
        return jsonify({"success": True, "orders": orders_list})
    
    elif request.method == "POST":
        data = request.get_json()
        
        order_number = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}"
        products_json = json.dumps(data.get("products", []))
        
        conn = get_db()
        conn.execute("""
            INSERT INTO orders 
            (order_number, user_id, products, quantity, subtotal, delivery_fee, total, 
             delivery_date, delivery_time, notes, payment_method, status) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            order_number,
            session["user_id"],
            products_json,
            data.get("quantity", 0),
            data.get("subtotal", 0),
            data.get("delivery_fee", 0),
            data.get("total", 0),
            data.get("delivery_date"),
            data.get("delivery_time"),
            data.get("notes", ""),
            data.get("payment_method", "cash_on_delivery"),
            "قيد المراجعة"
        ))
        conn.commit()
        
        order_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.close()
        
        return jsonify({
            "success": True, 
            "message": "تم إنشاء الطلب بنجاح",
            "order_id": order_id,
            "order_number": order_number
        })

@app.route("/api/forgot-password", methods=["POST"])
def api_forgot_password():
    data = request.get_json()
    email_or_phone = data.get("emailOrPhone")
    
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE email = ? OR phone = ?", 
        (email_or_phone, email_or_phone)
    ).fetchone()
    conn.close()
    
    if user:
        return jsonify({
            "success": True, 
            "message": "تم إرسال رابط استعادة كلمة المرور إلى بريدك الإلكتروني"
        })
    else:
        return jsonify({
            "success": False, 
            "message": "لم يتم العثور على حساب مرتبط بهذا البريد الإلكتروني أو رقم الهاتف"
        })

if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5000)