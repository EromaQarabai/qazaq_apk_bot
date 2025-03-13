import sqlite3

# 📌 Дерекқорға қосылу
conn = sqlite3.connect("bot.db")
cursor = conn.cursor()

# 📌 Кестелерді жасау (егер жоқ болса)
cursor.execute("""
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    os TEXT,
    feature TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    is_subscribed INTEGER DEFAULT 0
)
""")

conn.commit()
conn.close()

# 📌 Файлды базаға сақтау функциясы
def add_file(file_id, title, description, os, feature):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO files (file_id, title, description, os, feature) VALUES (?, ?, ?, ?, ?)",
                   (file_id, title, description, os, feature))
    conn.commit()
    conn.close()

# 📌 Файлды базаға қосу (ТЕСТ ҮШІН)
if __name__ == "__main__":
    add_file("FILE_ID", "Test App", "This is a test app", "Android", "Premium")
    print("✅ Дерекқор дайын!")
