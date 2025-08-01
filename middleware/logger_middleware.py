from flask import request
from datetime import datetime

def setup_logging(app):
    @app.before_request
    def log_request():
        app.logger.info(
            f"[REQUEST] {datetime.utcnow().isoformat()} {request.method} {request.path} "
            f"Body: {request.get_json(silent=True)}"
        )

    @app.after_request
    def log_response(response):
        app.logger.info(
            f"[RESPONSE] {datetime.utcnow().isoformat()} {response.status} {response.get_data(as_text=True)}"
        )
        return response

    @app.teardown_request
    def log_teardown(error=None):
        if error:
            app.logger.error(f"[ERROR] {datetime.utcnow().isoformat()} {str(error)}")
