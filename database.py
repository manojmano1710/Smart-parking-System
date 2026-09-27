import os, sqlite3
from datetime import datetime
BASE_DIR=os.path.dirname(os.path.abspath(__file__)); DATABASE_PATH=os.path.join(BASE_DIR,'parking.db')
def get_connection():
    c=sqlite3.connect(DATABASE_PATH); c.row_factory=sqlite3.Row; return c
def row_to_dict(r): return dict(r) if r else None
def init_database():
    c=get_connection(); cur=c.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT UNIQUE NOT NULL,password TEXT NOT NULL,full_name TEXT DEFAULT '',email TEXT DEFAULT '',phone TEXT DEFAULT '',created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS parking_slots(id INTEGER PRIMARY KEY AUTOINCREMENT,slot_number TEXT UNIQUE NOT NULL,status TEXT DEFAULT 'AVAILABLE',pixel_ratio REAL DEFAULT 0,x1 INTEGER,y1 INTEGER,x2 INTEGER,y2 INTEGER,last_updated TEXT DEFAULT CURRENT_TIMESTAMP)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS detection_history(id INTEGER PRIMARY KEY AUTOINCREMENT,total_slots INTEGER,occupied_slots INTEGER,available_slots INTEGER,occupancy_percentage REAL,detection_time TEXT DEFAULT CURRENT_TIMESTAMP)''')
    if not cur.execute('SELECT id FROM users WHERE username=?',('admin',)).fetchone():
        from auth import hash_password
        cur.execute('INSERT INTO users(username,password,full_name,email) VALUES(?,?,?,?)',('admin',hash_password('admin123'),'Administrator','admin@example.com'))
    for n in range(1,17):
        row=(n-1)//4; col=(n-1)%4; x1=60+col*270; y1=70+row*170; x2=x1+250; y2=y1+140
        cur.execute('INSERT OR IGNORE INTO parking_slots(slot_number,x1,y1,x2,y2) VALUES(?,?,?,?,?)',(f'Slot {n:02d}',x1,y1,x2,y2))
    c.commit(); c.close()
initialize_database=init_database
