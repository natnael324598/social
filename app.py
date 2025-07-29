from flask import Flask, render_template, request, jsonify
from cs50 import SQL
from datetime import datetime, timezone
import os

app = Flask(__name__)
db = SQL("sqlite:///data.db")

#table for post
db.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER,
        name TEXT,
        content TEXT,
        timestamp TEXT,
        likes INTEGER DEFAULT 0
    )
""")

# Create likes table
db.execute("""
    CREATE TABLE IF NOT EXISTS likes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER,
        post_id INTEGER
    )
""")

# Create comments table
db.execute("""
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER,
        telegram_id INTEGER,
        name TEXT,
        content TEXT,
        timestamp TEXT,
        likes INTEGER DEFAULT 0
    )
""")



@app.route("/")
def home():
    posts = db.execute("SELECT * FROM posts ORDER BY likes DESC, timestamp DESC")

    for post in posts:
        post["likes"] = db.execute("SELECT COUNT(*) AS count FROM likes WHERE post_id = ?", post["id"])[0]["count"]
        post["comments"] = db.execute("""
        SELECT name, content, timestamp, likes
        FROM comments
        WHERE post_id = ?
        ORDER BY likes DESC, timestamp DESC
        
    """, post["id"])
    return render_template("home.html", posts=posts)

@app.route("/like", methods=["POST"])
def like():
    data = request.get_json()
    existing = db.execute("SELECT * FROM likes WHERE telegram_id = ? AND post_id = ?", data["telegram_id"], data["post_id"])
    if not existing:
        db.execute("INSERT INTO likes (telegram_id, post_id) VALUES (?, ?)", data["telegram_id"], data["post_id"])
    return jsonify(success=True)


@app.route("/comment", methods=["POST"])
def comment():
    data = request.get_json()
    db.execute("""
        INSERT INTO comments (post_id, telegram_id, name, content, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, data["post_id"], data["telegram_id"], data["name"], data["content"], datetime.now(timezone.utc).isoformat().isoformat())
    return jsonify(success=True)

@app.route("/comments/<int:post_id>")
def get_comments(post_id):
    comments = db.execute("""
        SELECT name, content, timestamp, likes
        FROM comments
        WHERE post_id = ?
        ORDER BY likes DESC, timestamp DESC
    """, post_id)
    return jsonify(comments)


@app.route("/post", methods=["POST"])
def post():
    data = request.get_json()
    db.execute(
        "INSERT INTO posts (telegram_id, name, content, timestamp) VALUES (?, ?, ?, ?)",
        data["telegram_id"],
        data["name"],
        data["content"],
        datetime.utcnow().isoformat()
    )
    return jsonify(success=True)




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
