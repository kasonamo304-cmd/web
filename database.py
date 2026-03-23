import sqlite3
import os

def init_database():
    """إنشاء قاعدة البيانات والجداول"""
    
    # حذف قاعدة البيانات القديمة إذا وجدت (اختياري)
    if os.path.exists("paper.db"):
        print("⚠️  قاعدة البيانات موجودة بالفعل")
        response = input("هل تريد إنشاء قاعدة بيانات جديدة؟ (y/n): ")
        if response.lower() == 'y':
            os.remove("paper.db")
            print("🗑️  تم حذف قاعدة البيانات القديمة")
        else:
            print("✅ استخدام قاعدة البيانات الموجودة")
            return
    
    conn = sqlite3.connect("paper.db")
    cur = conn.cursor()

    # جدول المستخدمين
    cur.execute('''
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

    # جدول الطلبات
    cur.execute('''
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
    print("👤 جاري إضافة مستخدمين تجريبيين...")
    
    # مستخدم عادي
    cur.execute("SELECT * FROM users WHERE email = ?", ("user@example.com",))
    if not cur.fetchone():
        cur.execute("""
            INSERT INTO users (name, email, phone, password, type, governorate, address, role)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ("أحمد محمد", "user@example.com", "01234567890", "123456", "individual", "القاهرة", "شارع النصر، مدينة نصر", "customer"))
        print("  ✅ مستخدم عادي: user@example.com / 123456")
    
    # مستخدم شركة
    cur.execute("SELECT * FROM users WHERE email = ?", ("company@example.com",))
    if not cur.fetchone():
        cur.execute("""
            INSERT INTO users (name, email, phone, password, type, company_name, governorate, address, role)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("شركة التدوير", "company@example.com", "01234567891", "123456", "company", "شركة إعادة التدوير", "الجيزة", "المنطقة الصناعية", "company_admin"))
        print("  ✅ مستخدم شركة: company@example.com / 123456")
    
    # مشرف
    cur.execute("SELECT * FROM users WHERE email = ?", ("admin@example.com",))
    if not cur.fetchone():
        cur.execute("""
            INSERT INTO users (name, email, phone, password, type, governorate, address, role)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ("مدير النظام", "admin@example.com", "01234567892", "123456", "individual", "الإسكندرية", "شارع البحر", "admin"))
        print("  ✅ مشرف: admin@example.com / 123456")
    
    # إضافة طلبات تجريبية
    print("📦 جاري إضافة طلبات تجريبية...")
    
    # الحصول على معرف المستخدم
    user = cur.execute("SELECT id FROM users WHERE email = ?", ("user@example.com",)).fetchone()
    if user:
        user_id = user[0]
        
        # طلب مكتمل
        cur.execute("""
            INSERT INTO orders (order_number, user_id, products, quantity, subtotal, delivery_fee, total, 
                              delivery_date, delivery_time, payment_method, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "ORD2024001",
            user_id,
            '[{"name":"ورق كرتون","quantity":20,"price":8.5}]',
            20,
            170,
            20,
            190,
            "2024-01-15",
            "9:00-12:00",
            "cash_on_delivery",
            "مكتمل",
            "2024-01-10 10:30:00"
        ))
        
        # طلب في الطريق
        cur.execute("""
            INSERT INTO orders (order_number, user_id, products, quantity, subtotal, delivery_fee, total, 
                              delivery_date, delivery_time, payment_method, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "ORD2024002",
            user_id,
            '[{"name":"ورق مكتبي","quantity":15,"price":6.5},{"name":"جرائد","quantity":10,"price":4.0}]',
            25,
            137.5,
            25,
            162.5,
            "2024-03-20",
            "12:00-15:00",
            "vodafone_cash",
            "في الطريق",
            "2024-03-18 09:15:00"
        ))
        
        # طلب قيد المراجعة
        cur.execute("""
            INSERT INTO orders (order_number, user_id, products, quantity, subtotal, delivery_fee, total, 
                              delivery_date, delivery_time, payment_method, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "ORD2024003",
            user_id,
            '[{"name":"ورق كرتون","quantity":30,"price":8.5}]',
            30,
            255,
            0,
            255,
            "2024-03-25",
            "15:00-18:00",
            "cash_on_delivery",
            "قيد المراجعة",
            "2024-03-19 14:20:00"
        ))
        
        print(f"  ✅ تم إضافة 3 طلبات تجريبية للمستخدم {user_id}")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*50)
    print("✅ تم تهيئة قاعدة البيانات بنجاح!")
    print("="*50)
    print("\n📊 بيانات الدخول للتجربة:")
    print("  • مستخدم عادي: user@example.com / 123456")
    print("  • شركة: company@example.com / 123456")
    print("  • مشرف: admin@example.com / 123456")
    print("\n🚀 شغل التطبيق: python app.py")
    print("="*50)

if __name__ == "__main__":
    init_database()