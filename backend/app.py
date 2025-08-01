
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import sqlite3
from datetime import datetime, timedelta
import string
import random
import re
from dotenv import load_dotenv
from middleware.logger_middleware import setup_logging
from models import get_db, close_db, init_db

load_dotenv()

app = Flask(__name__)
setup_logging(app)
CORS(app)
app.teardown_appcontext(close_db)
SHORTCODE_REGEX = re.compile(r'^[a-zA-Z0-9]{4,20}$')
DEFAULT_EXPIRY_MINUTES = 30


# Service Layer
class URLService:
    @staticmethod
    def generate_shortcode(length=6):
        chars = string.ascii_letters + string.digits
        db = get_db()
        while True:
            code = ''.join(random.choices(chars, k=length))
            cur = db.execute('SELECT 1 FROM urls WHERE shortcode = ?', (code,))
            if not cur.fetchone():
                return code

    @staticmethod
    def is_shortcode_unique(code):
        db = get_db()
        cur = db.execute('SELECT 1 FROM urls WHERE shortcode = ?', (code,))
        return not cur.fetchone()

    @staticmethod
    def create_short_url(original_url, shortcode=None, expiry_minutes=None):
        db = get_db()
        if shortcode:
            if not SHORTCODE_REGEX.match(shortcode):
                return None, ("Invalid shortcode. Must be alphanumeric and 4-20 chars.", 400)
            if not URLService.is_shortcode_unique(shortcode):
                return None, ("Shortcode already in use.", 409)
        else:
            shortcode = URLService.generate_shortcode()
        expiry = datetime.utcnow() + timedelta(minutes=expiry_minutes or DEFAULT_EXPIRY_MINUTES)
        try:
            db.execute(
                'INSERT INTO urls (original_url, shortcode, expiry, created_at, clicks) VALUES (?, ?, ?, ?, ?)',
                (original_url, shortcode, expiry, datetime.utcnow(), 0)
            )
            db.commit()
        except sqlite3.IntegrityError:
            return None, ("Shortcode already in use.", 409)
        return shortcode, None

    @staticmethod
    def get_url(shortcode):
        db = get_db()
        cur = db.execute('SELECT * FROM urls WHERE shortcode = ?', (shortcode,))
        row = cur.fetchone()
        if not row:
            return None, ("Shortcode not found.", 404)
        if row['expiry'] < datetime.utcnow():
            return None, ("Shortcode expired.", 410)
        return dict(row), None

    @staticmethod
    def increment_click(shortcode):
        db = get_db()
        db.execute('UPDATE urls SET clicks = clicks + 1 WHERE shortcode = ?', (shortcode,))
        db.commit()

    @staticmethod
    def get_analytics(shortcode):
        db = get_db()
        cur = db.execute('SELECT * FROM urls WHERE shortcode = ?', (shortcode,))
        row = cur.fetchone()
        if not row:
            return None, ("Shortcode not found.", 404)
        return {
            "shortcode": row["shortcode"],
            "original_url": row["original_url"],
            "created_at": row["created_at"],
            "expiry": row["expiry"],
            "clicks": row["clicks"]
        }, None

# Add stats endpoint for analytics
@app.route("/stats", methods=["GET"])
def stats():
    db = get_db()
    cur = db.execute('SELECT * FROM urls ORDER BY created_at DESC')
    rows = cur.fetchall()
    result = []
    for row in rows:
        result.append({
            "short_url": f"{request.host_url}{row['shortcode']}",
            "original_url": row["original_url"],
            "created_at": str(row["created_at"]),
            "expiry": str(row["expiry"]),
            "clicks": row["clicks"],
            "shortcode": row["shortcode"]
        })
    return jsonify(result)
# Routes
@app.route("/shorturls", methods=["POST"])
def create_shorturl():
    data = request.get_json()
    if not data or "url" not in data:
        return jsonify({"error": "Missing 'url' in request body."}), 400
    url = data["url"]
    shortcode = data.get("shortcode")
    expiry = data.get("expiry_minutes")
    code, err = URLService.create_short_url(url, shortcode, expiry)
    if err:
        return jsonify({"error": err[0]}), err[1]
    return jsonify({"shortened_url": f"{request.host_url}{code}"}), 201

@app.route("/<shortcode>", methods=["GET"])
def redirect_shorturl(shortcode):
    doc, err = URLService.get_url(shortcode)
    if err:
        return jsonify({"error": err[0]}), err[1]
    URLService.increment_click(shortcode)
    return redirect(doc["original_url"], code=302)

@app.route("/analytics/<shortcode>", methods=["GET"])
def analytics(shortcode):
    data, err = URLService.get_analytics(shortcode)
    if err:
        return jsonify({"error": err[0]}), err[1]
    return jsonify(data)

@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(debug=True)
