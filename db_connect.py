import sqlite3

conn = sqlite3.connect("music.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM albums")

rows = cursor.fetchall()

for row in rows: print(row)





