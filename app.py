from flask import Flask, request, redirect, render_template, jsonify, abort
import sqlite3, string, random, datetime, qrcode, io, base64

app = Flask(__name__)
DB = "urls.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_url TEXT NOT NULL,
                short_slug TEXT UNIQUE NOT NULL,
                created_at TEXT,
                expires_at TEXT,
                click_count INTEGER DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS clicks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slug TEXT,
                referrer TEXT,
                country TEXT,
                clicked_at TEXT
            )
        """)

def random_slug(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/shorten", methods=["POST"])
def shorten():
    data = request.get_json()
    original = data.get("url", "").strip()
    custom_slug = data.get("slug", "").strip()
    expiry_days = int(data.get("expiry", 0))

    if not original.startswith("http"):
        return jsonify({"error": "Invalid URL"}), 400

    slug = custom_slug if custom_slug else random_slug()
    expires_at = None
    if expiry_days > 0:
        expires_at = (datetime.datetime.now() + datetime.timedelta(days=expiry_days)).isoformat()

    try:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO urls (original_url, short_slug, created_at, expires_at) VALUES (?, ?, ?, ?)",
                (original, slug, datetime.datetime.now().isoformat(), expires_at)
            )
        return jsonify({"short_url": request.host_url + slug, "slug": slug})
    except sqlite3.IntegrityError:
        return jsonify({"error": "Slug already taken"}), 409

@app.route("/<slug>")
def redirect_url(slug):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM urls WHERE short_slug=?", (slug,)).fetchone()
        if not row:
            abort(404)
        if row["expires_at"] and datetime.datetime.fromisoformat(row["expires_at"]) < datetime.datetime.now():
            return "Link has expired", 410
        conn.execute("UPDATE urls SET click_count = click_count + 1 WHERE short_slug=?", (slug,))
        conn.execute(
            "INSERT INTO clicks (slug, referrer, country, clicked_at) VALUES (?, ?, ?, ?)",
            (slug, request.referrer or "Direct", "Unknown", datetime.datetime.now().isoformat())
        )
    return redirect(row["original_url"])

@app.route("/analytics")
def analytics():
    return render_template("analytics.html")

@app.route("/api/analytics")
def api_analytics():
    with get_db() as conn:
        urls = conn.execute("SELECT * FROM urls ORDER BY click_count DESC").fetchall()
        data = [dict(u) for u in urls]
    return jsonify(data)

@app.route("/api/qr/<slug>")
def generate_qr(slug):
    short_url = request.host_url + slug
    img = qrcode.make(short_url)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    encoded = base64.b64encode(buf.getvalue()).decode()
    return jsonify({"qr": "data:image/png;base64," + encoded})

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
