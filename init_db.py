import sqlite3
con = sqlite3.connect("database.db")
with open("schema.sql", encoding="utf-8") as f:
    con.executescript(f.read())
con.commit()
con.close()
print("Database initialized successfully!")