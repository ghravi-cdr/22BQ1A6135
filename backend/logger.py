import logging
from flask import request, g
from datetime import datetime

class RequestLogger:
    def __init__(self, app=None):
        self.logger = logging.getLogger('url_shortener')
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler('backend/url_shortener.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        if app:
            self.init_app(app)

    def init_app(self, app):
        @app.before_request
        def log_request():
            g.start = datetime.utcnow()
            self.logger.info(f"Request: {request.method} {request.path} Body: {request.get_json(silent=True)}")

        @app.after_request
        def log_response(response):
            duration = (datetime.utcnow() - g.start).total_seconds() if hasattr(g, 'start') else 0
            self.logger.info(f"Response: {response.status_code} Body: {response.get_data(as_text=True)} Duration: {duration}s")
            return response

        @app.teardown_request
        def log_exception(exc):
            if exc:
                self.logger.error(f"Exception: {exc}")
