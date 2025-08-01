from flask import Flask, request, jsonify, redirect
from flask_pymongo import PyMongo
from datetime import datetime, timedelta
import string
import random
import re
import os

from dotenv import load_dotenv
from middleware.logger_middleware import setup_logging


load_dotenv()


app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/urlshortener")
mongo = PyMongo(app)
setup_logging(app)

SHORTCODE_REGEX = re.compile(r'^[a-zA-Z0-9]{4,20}$')
DEFAULT_EXPIRY_MINUTES = 30

# Service Layer
class URLService:
    @staticmethod
    def generate_shortcode(length=6):
        chars = string.ascii_letters + string.digits
        while True:
            code = ''.join(random.choices(chars, k=length))
            if not mongo.db.urls.find_one({"shortcode": code}):
                return code

    @staticmethod
    def is_shortcode_unique(code):
        return not mongo.db.urls.find_one({"shortcode": code})

    @staticmethod
    def create_short_url(original_url, shortcode=None, expiry_minutes=None):
        if shortcode:
            if not SHORTCODE_REGEX.match(shortcode):
                return None, ("Invalid shortcode. Must be alphanumeric and 4-20 chars.", 400)
            if not URLService.is_shortcode_unique(shortcode):
                return None, ("Shortcode already in use.", 409)
        else:
            shortcode = URLService.generate_shortcode()
        expiry = datetime.utcnow() + timedelta(minutes=expiry_minutes or DEFAULT_EXPIRY_MINUTES)
        doc = {
            "original_url": original_url,
            "shortcode": shortcode,
            "expiry": expiry,
            "created_at": datetime.utcnow(),
            "clicks": 0
        }
        mongo.db.urls.insert_one(doc)
        return shortcode, None

    @staticmethod
    def get_url(shortcode):
        doc = mongo.db.urls.find_one({"shortcode": shortcode})
        if not doc:
            return None, ("Shortcode not found.", 404)
        if doc["expiry"] < datetime.utcnow():
            return None, ("Shortcode expired.", 410)
        return doc, None

    @staticmethod
    def increment_click(shortcode):
        mongo.db.urls.update_one({"shortcode": shortcode}, {"$inc": {"clicks": 1}})

    @staticmethod
    def get_analytics(shortcode):
        doc = mongo.db.urls.find_one({"shortcode": shortcode})
        if not doc:
            return None, ("Shortcode not found.", 404)
        return {
            "shortcode": shortcode,
            "original_url": doc["original_url"],
            "created_at": doc["created_at"],
            "expiry": doc["expiry"],
            "clicks": doc["clicks"]
        }, None

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
    app.run(debug=True)
