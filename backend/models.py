import sqlite3
from flask import g
import os

DATABASE = os.path.join(os.path.dirname(__file__), 'urls.db')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
        db.row_factory = sqlite3.Row
    return db

def close_db(e=None):
    db = g.pop('_database', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    db.execute('''CREATE TABLE IF NOT EXISTS urls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        original_url TEXT NOT NULL,
        shortcode TEXT UNIQUE NOT NULL,
        expiry TIMESTAMP NOT NULL,
        created_at TIMESTAMP NOT NULL,
        clicks INTEGER DEFAULT 0
    )''')
    db.commit()
