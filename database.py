import sqlite3
import hashlib
import os

DB_PATH = "users.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_configs (
            user_id INTEGER PRIMARY KEY,
            chat_id TEXT DEFAULT '',
            name_prefix TEXT DEFAULT '',
            delay INTEGER DEFAULT 35,
            cookies TEXT DEFAULT '',
            messages TEXT DEFAULT 'Hello!\nHow are you?',
            automation_running BOOLEAN DEFAULT 0,
            admin_e2ee_thread_id TEXT,
            chat_type TEXT DEFAULT 'INSTAGRAM',
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            return False, "Username exists!"
        
        hashed = hash_password(password)
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
        user_id = cursor.lastrowid
        
        cursor.execute('''
            INSERT INTO user_configs (user_id, chat_id, name_prefix, delay, cookies, messages)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, "", "", 35, "", "Hello!\nHow are you?"))
        
        conn.commit()
        return True, "Account created!"
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        conn.close()

def verify_user(username, password):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        hashed = hash_password(password)
        cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, hashed))
        result = cursor.fetchone()
        return result[0] if result else None
    except:
        return None
    finally:
        conn.close()

def get_user_config(user_id):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT chat_id, name_prefix, delay, cookies, messages, automation_running FROM user_configs WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        if result:
            return {
                'chat_id': result[0] or '',
                'name_prefix': result[1] or '',
                'delay': result[2] or 35,
                'cookies': result[3] or '',
                'messages': result[4] or 'Hello!\nHow are you?',
                'automation_running': bool(result[5])
            }
        return None
    except:
        return None
    finally:
        conn.close()

def update_user_config(user_id, chat_id, name_prefix, delay, cookies, messages):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE user_configs 
            SET chat_id = ?, name_prefix = ?, delay = ?, cookies = ?, messages = ?
            WHERE user_id = ?
        ''', (chat_id, name_prefix, delay, cookies, messages, user_id))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def set_automation_running(user_id, status):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE user_configs SET automation_running = ? WHERE user_id = ?', (1 if status else 0, user_id))
    conn.commit()
    conn.close()

def get_automation_running(user_id):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT automation_running FROM user_configs WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return bool(result[0]) if result else False

def get_username(user_id):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_admin_e2ee_thread_id(user_id):
    return None

def set_admin_e2ee_thread_id(user_id, thread_id, cookies, chat_type):
    pass
