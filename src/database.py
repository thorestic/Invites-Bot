#Don't touch
import sqlite3
import time

conn = sqlite3.connect("bonus.db")
cursor = conn.cursor()

# Tables creation
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        bonus INTEGER DEFAULT 0,
        last_wheel INTEGER DEFAULT 0
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS invited_users (
        invited_id TEXT PRIMARY KEY,
        inviter_id TEXT
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS config (
        guild_id TEXT PRIMARY KEY,
        win_role_id TEXT
    )
""")

conn.commit()


def add_bonus(user_id, amount):
    cursor.execute("SELECT bonus FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if row is None:
        cursor.execute("INSERT INTO users (user_id, bonus) VALUES (?, ?)", (user_id, amount))
    else:
        cursor.execute("UPDATE users SET bonus = bonus + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()


def set_bonus(user_id, amount):
    cursor.execute("INSERT OR REPLACE INTO users (user_id, bonus) VALUES (?, ?)", (user_id, amount))
    conn.commit()


def get_bonus(user_id):
    cursor.execute("SELECT bonus FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else 0


def set_wheel_time(user_id):
    cursor.execute("UPDATE users SET last_wheel = ? WHERE user_id = ?", (int(time.time()), user_id))
    conn.commit()


def get_wheel_time(user_id):
    cursor.execute("SELECT last_wheel FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else 0


def record_invite(invited_id, inviter_id):
    cursor.execute("INSERT INTO invited_users (invited_id, inviter_id) VALUES (?, ?)", (invited_id, inviter_id))
    conn.commit()


def already_invited(invited_id):
    cursor.execute("SELECT inviter_id FROM invited_users WHERE invited_id = ?", (invited_id,))
    return cursor.fetchone() is not None


def set_win_role(guild_id, role_id):
    cursor.execute("INSERT OR REPLACE INTO config (guild_id, win_role_id) VALUES (?, ?)", (guild_id, role_id))
    conn.commit()


def get_win_role(guild_id):
    cursor.execute("SELECT win_role_id FROM config WHERE guild_id = ?", (guild_id,))
    row = cursor.fetchone()
    return int(row[0]) if row else None