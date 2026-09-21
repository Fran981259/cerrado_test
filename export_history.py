import json
import sqlite3

conn = sqlite3.connect("data/portal_cerrado.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("SELECT * FROM news_articles")
rows = cur.fetchall()

articles = []
for row in rows:
    articles.append(dict(row))

with open("history_dump.json", "w", encoding="utf-8") as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

print(f"Exported {len(articles)} articles.")
