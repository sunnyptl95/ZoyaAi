# social_db.py
import sqlite3
import time
import random
import config

DB_FILE = "zoya_social.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # 1. Users Table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        first_name TEXT,
        username TEXT,
        last_group_name TEXT,
        last_seen_time INTEGER,
        balance INTEGER DEFAULT 130,
        protect_until INTEGER DEFAULT 0,
        steals INTEGER DEFAULT 0
    )''')

    # Migrations
    try: c.execute("ALTER TABLE users ADD COLUMN balance INTEGER DEFAULT 130")
    except: pass
    try: c.execute("ALTER TABLE users ADD COLUMN protect_until INTEGER DEFAULT 0")
    except: pass
    try: c.execute("ALTER TABLE users ADD COLUMN steals INTEGER DEFAULT 0")
    except: pass

    # 2. Logs Table
    c.execute('''CREATE TABLE IF NOT EXISTS logs (
        user_id INTEGER,
        first_name TEXT,
        group_name TEXT,
        message TEXT,
        timestamp INTEGER
    )''')
    
    # 3. Rob Cooldown Table
    c.execute('''CREATE TABLE IF NOT EXISTS rob_cooldowns (
        robber_id INTEGER,
        victim_id INTEGER,
        timestamp INTEGER,
        PRIMARY KEY (robber_id, victim_id)
    )''')


    # 4. Welcome Settings Table
    c.execute('''CREATE TABLE IF NOT EXISTS welcome_settings (
        chat_id INTEGER PRIMARY KEY,
        status INTEGER DEFAULT 1
    )''')

    conn.commit()
    conn.close()

def set_welcome_status(chat_id, status):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO welcome_settings (chat_id, status) VALUES (?, ?)", (chat_id, status))
    conn.commit()
    conn.close()

def get_welcome_status(chat_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT status FROM welcome_settings WHERE chat_id = ?", (chat_id,))
    res = c.fetchone()
    conn.close()
    return res[0] if res else 1

def log_user(user_id, first_name, username, group_name, message_text):
    if not message_text: return
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    current_time = int(time.time())

    c.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    existing_user = c.fetchone()
    
    if existing_user:
        if group_name == "DM" or message_text.startswith("/"):
            reward = 0 
        else:
            reward = random.randint(config.CHAT_REWARD_MIN, config.CHAT_REWARD_MAX)
        
        c.execute('''UPDATE users SET 
                     first_name = ?, username = ?, last_group_name = ?, last_seen_time = ?, balance = balance + ?
                     WHERE user_id = ?''', 
                     (first_name, username, group_name, current_time, reward, user_id))
    else:
        c.execute('''INSERT INTO users (user_id, first_name, username, last_group_name, last_seen_time, balance, protect_until, steals)
                     VALUES (?, ?, ?, ?, ?, ?, 0, 0)''', 
                     (user_id, first_name, username, group_name, current_time, config.START_BALANCE))

    c.execute("INSERT INTO logs (user_id, first_name, group_name, message, timestamp) VALUES (?, ?, ?, ?, ?)",
              (user_id, first_name, group_name, message_text, current_time))

    conn.commit()
    conn.close()

def register_user_if_not_exists(user_id, first_name, username):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    if not c.fetchone():
        current_time = int(time.time())
        c.execute('''INSERT INTO users (user_id, first_name, username, last_group_name, last_seen_time, balance, protect_until, steals)
                     VALUES (?, ?, ?, ?, ?, ?, 0, 0)''', 
                     (user_id, first_name, username, "Unknown", current_time, config.START_BALANCE))
        conn.commit()
    conn.close()

# --- ECONOMY FUNCTIONS ---
def get_wallet(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT first_name, balance, protect_until, steals FROM users WHERE user_id = ?", (user_id,))
    res = c.fetchone()
    conn.close()
    return res if res else ("User", 0, 0, 0)

def update_balance(user_id, amount):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def increment_steals(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET steals = steals + 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def set_protection(user_id, days, cost):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    expiry = int(time.time()) + (days * 86400)
    c.execute("UPDATE users SET balance = balance - ?, protect_until = ? WHERE user_id = ?", (cost, expiry, user_id))
    conn.commit()
    conn.close()
    return expiry

def check_rob_cooldown(robber_id, victim_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT timestamp FROM rob_cooldowns WHERE robber_id = ? AND victim_id = ?", (robber_id, victim_id))
    res = c.fetchone()
    conn.close()
    
    if not res: return True, 0
    
    last_rob_time = res[0]
    current_time = int(time.time())
    cooldown_time = 3600 # 1 Hour
    
    if current_time - last_rob_time < cooldown_time:
        minutes_left = int((cooldown_time - (current_time - last_rob_time)) / 60)
        return False, minutes_left
    
    return True, 0

def add_rob_cooldown(robber_id, victim_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    current_time = int(time.time())
    c.execute("INSERT OR REPLACE INTO rob_cooldowns (robber_id, victim_id, timestamp) VALUES (?, ?, ?)", 
              (robber_id, victim_id, current_time))
    conn.commit()
    conn.close()

# --- INFO & STATS ---
def get_top_rich():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT first_name, balance FROM users ORDER BY balance DESC LIMIT 10")
    rows = c.fetchall()
    conn.close()
    return rows

def get_top_thieves():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT first_name, steals FROM users WHERE steals > 0 ORDER BY steals DESC LIMIT 10")
    rows = c.fetchall()
    conn.close()
    return rows

def get_rank(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users ORDER BY balance DESC")
    all_users = [r[0] for r in c.fetchall()]
    conn.close()
    if user_id in all_users:
        return all_users.index(user_id) + 1
    return "Unknown"

def get_user_info(query):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    query = query.replace("@", "").lower()
    c.execute("SELECT * FROM users WHERE LOWER(username) = ? OR LOWER(first_name) LIKE ?", (query, f"%{query}%"))
    user = c.fetchone()
    if user:
        user_id = user[0]
        c.execute("SELECT message FROM logs WHERE user_id = ? ORDER BY timestamp DESC LIMIT 3", (user_id,))
        msgs = [row[0] for row in c.fetchall()]
        info = {
            "name": user[1],
            "username": user[2],
            "last_group": user[3],
            "last_seen_ago": int((int(time.time()) - user[4]) / 60),
            "recent_chats": msgs
        }
        conn.close()
        return info
    conn.close()
    return None

def get_gossip_context():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    start_of_day = int(time.time()) - 86400
    c.execute("""
        SELECT first_name, group_name, message 
        FROM logs 
        WHERE timestamp >= ? AND group_name != 'DM'
        ORDER BY timestamp DESC LIMIT 15
    """, (start_of_day,))
    rows = c.fetchall()
    conn.close()
    if not rows: return "Aaj groups mein shanti thi, koi khaas baat nahi hui."
    text = "Recent Group Activity (Secret Info):\n"
    for r in rows: text += f"- {r[0]} in {r[1]}: '{r[2]}'\n"
    return text

def get_stats():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    u = c.fetchone()[0]
    c.execute("SELECT COUNT(DISTINCT group_name) FROM logs WHERE group_name != 'DM'")
    g = c.fetchone()[0]
    conn.close()
    return u, g

def get_group_list_formatted():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT DISTINCT group_name FROM logs WHERE group_name != 'DM'")
    groups = [row[0] for row in c.fetchall()]
    conn.close()
    if not groups: return "📭 Abhi tak kisi group me nahi gayi."
    text = "📂 **Groups I Know:**\n\n"
    for i, g in enumerate(groups, 1): text += f"{i}. {g}\n"
    return text

def get_user_list_formatted():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT first_name, username FROM users LIMIT 100") 
    users = c.fetchall()
    conn.close()
    if not users: return "📭 Abhi tak koi dost nahi bana."
    text = "👥 **Users I Know (Top 100):**\n\n"
    for u in users:
        name = u[0]
        handle = f"(@{u[1]})" if u[1] else ""
        text += f"👤 {name} {handle}\n"
    return text

# --- 🔥 THIS WAS MISSING BEFORE (Now Added) ---
def fetch_user_history(user_id):
    """Fetches past messages of a user across DM and Groups"""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        # Limit set to 20 for context
        c.execute("SELECT group_name, message FROM logs WHERE user_id = ? ORDER BY timestamp DESC LIMIT 20", (user_id,))
        rows = c.fetchall()
        conn.close()
        
        if not rows: return ""

        text = "\n[🧠 MEMORY RECALL - This User's Past Context]:\n"
        for group, msg in reversed(rows):
            source = "DM" if group == "DM" else f"Group ({group})"
            text += f"- (in {source}): {msg}\n"
        return text
    except Exception as e:
        print(f"DB Error: {e}")
        return ""

init_db()

